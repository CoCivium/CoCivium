#!/usr/bin/env python3
"""CoCopy+ CoAckRewise+ explicit local day trail, no hooks, scraping or network."""
import argparse
import hashlib
import html
import json
import os
import re
import stat
from collections import Counter
from datetime import date, datetime
from pathlib import Path

SCHEMA="CoCivium.CoCopyAckDay.R0"
KINDS=("RAW","REWISE","ACK","CHALLENGE","OUTCOME")
ID_RE=re.compile(r"^[A-Za-z0-9_.:/#-]{3,128}$")
MAX_NOTE=16384
MAX_LOG=4194304
MAX_EVENTS=4096
REQUIRED={"schema","seq","day","kind","source_id","source_time","observed_at",
          "parent_id","content_sha256","content_bytes","retained_text","privacy",
          "authority","receiver_ack","prev_sha256","record_sha256"}

def canonical(value):
    return json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(",",":")).encode("utf8")

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

def valid_day(day):
    if not isinstance(day,str) or len(day)!=10 or date.fromisoformat(day).isoformat()!=day:
        raise ValueError("INVALID_DAY")
    return day

def valid_time(value):
    if value is None:
        return None
    v=datetime.fromisoformat(value)
    if v.tzinfo is None or v.utcoffset() is None:
        raise ValueError("MISSING_TIME_OFFSET")
    return value

def location(root,day,create=False):
    valid_day(day)
    folder=Path(root).expanduser().absolute()
    if folder.is_symlink():
        raise ValueError("ROOT_SYMLINK_FORBIDDEN")
    if create:
        folder.mkdir(parents=True,exist_ok=True,mode=0o700)
    if not folder.is_dir():
        raise ValueError("MISSING_ROOT")
    return folder/(day+".jsonl")

def read_day(root,day):
    file=location(root,day)
    if not file.exists():
        return []
    if file.is_symlink() or not stat.S_ISREG(file.lstat().st_mode):
        raise ValueError("JOURNAL_NOT_REGULAR")
    if file.stat().st_size>MAX_LOG:
        raise ValueError("JOURNAL_TOO_LARGE")
    rows=[]
    prev=None
    with file.open("rb") as handle:
        for raw in handle:
            if len(rows)>=MAX_EVENTS:
                raise ValueError("TOO_MANY_EVENTS")
            if not raw.endswith(b"\n"):
                raise ValueError("TRUNCATED_JSONL")
            try:
                row=json.loads(raw)
            except (UnicodeDecodeError,json.JSONDecodeError) as exc:
                raise ValueError("BROKEN_JSONL") from exc
            if not isinstance(row,dict) or set(row)!=REQUIRED:
                raise ValueError("UNKNOWN_FIELDS")
            if row["schema"]!=SCHEMA or row["seq"]!=len(rows)+1 or row["day"]!=day:
                raise ValueError("WRONG_SCOPE_OR_SEQUENCE")
            if row["kind"] not in KINDS or row["privacy"]!="LOCAL_PRIVATE":
                raise ValueError("UNKNOWN_KIND_OR_PRIVACY")
            if row["authority"]!="NONE" or row["receiver_ack"] is not None:
                raise ValueError("FORGED_AUTHORITY")
            if not isinstance(row["source_id"],str) or not ID_RE.fullmatch(row["source_id"]):
                raise ValueError("BAD_SOURCE_ID")
            valid_time(row["observed_at"])
            valid_time(row["source_time"])
            if row["prev_sha256"]!=prev:
                raise ValueError("BROKEN_CHAIN")
            if row["parent_id"] is not None and row["parent_id"] not in {r["record_sha256"] for r in rows}:
                raise ValueError("UNKNOWN_PARENT")
            size=row["content_bytes"]
            if type(size) is not int or not 0<=size<=MAX_NOTE:
                raise ValueError("BAD_CONTENT_SIZE")
            text=row["retained_text"]
            if text is not None:
                if not isinstance(text,str) or len(text.encode("utf8"))!=size or sha(text.encode("utf8"))!=row["content_sha256"]:
                    raise ValueError("RAW_CONTENT_MISMATCH")
            if not isinstance(row["content_sha256"],str) or len(row["content_sha256"])!=64:
                raise ValueError("BAD_CONTENT_HASH")
            actual=sha(canonical({k:v for k,v in row.items() if k!="record_sha256"}))
            if row["record_sha256"]!=actual:
                raise ValueError("TAMPER_OR_INVALID_HASH")
            prev=actual
            rows.append(row)
    return rows

def append(root,day,kind,source_id,data=b"",retain=False,parent=None,source_time=None):
    valid_day(day)
    if kind not in KINDS or not isinstance(source_id,str) or not ID_RE.fullmatch(source_id):
        raise ValueError("BAD_KIND_OR_SOURCE")
    if not isinstance(data,bytes) or len(data)>MAX_NOTE:
        raise ValueError("CONTENT_OVER_LIMIT")
    retained=None
    if retain:
        try:
            retained=data.decode("utf8")
        except UnicodeDecodeError as exc:
            raise ValueError("NOT_UTF8") from exc
    valid_time(source_time)
    file=location(root,day,create=True)
    lock=file.with_suffix(".lock")
    owned=False
    try:
        lock_fd=os.open(lock,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
        owned=True
        os.close(lock_fd)
        records=read_day(root,day)
        if len(records)>=MAX_EVENTS:
            raise ValueError("TOO_MANY_EVENTS")
        if parent is not None and parent not in {r["record_sha256"] for r in records}:
            raise ValueError("UNKNOWN_PARENT")
        if file.exists() and (file.is_symlink() or not stat.S_ISREG(file.lstat().st_mode)):
            raise ValueError("JOURNAL_NOT_REGULAR")
        row={"schema":SCHEMA,"seq":len(records)+1,"day":day,"kind":kind,
             "source_id":source_id,"source_time":source_time,
             "observed_at":datetime.now().astimezone().isoformat(timespec="seconds"),
             "parent_id":parent,"content_sha256":sha(data),"content_bytes":len(data),
             "retained_text":retained,"privacy":"LOCAL_PRIVATE","authority":"NONE",
             "receiver_ack":None,
             "prev_sha256":records[-1]["record_sha256"] if records else None}
        row["record_sha256"]=sha(canonical(row))
        buf=canonical(row)+b"\n"
        if file.exists() and file.stat().st_size+len(buf)>MAX_LOG:
            raise ValueError("JOURNAL_OVER_LIMIT")
        flags=os.O_WRONLY|os.O_CREAT|os.O_APPEND|getattr(os,"O_NOFOLLOW",0)
        fd=os.open(file,flags,0o600)
        try:
            if os.write(fd,buf)!=len(buf):
                raise OSError("PARTIAL_APPEND")
            os.fsync(fd)
        finally:
            os.close(fd)
        return row
    finally:
        if owned:
            lock.unlink()

def summary(root,day):
    records=read_day(root,day)
    return {"schema":SCHEMA,"day":day,"state":"LOCAL_CHAIN_VERIFIED",
            "events":len(records),"kind_counts":dict(Counter(r["kind"] for r in records)),
            "last_record_sha256":records[-1]["record_sha256"] if records else None,
            "receiver_ack":None,"nonclaims":["LOCAL_HASH_CHAIN_NE_DURABLE_BACKUP",
                                           "ACK_KIND_NE_RECEIVER_ACK",
                                           "NO_LOG_EVENT_NE_NO_THOUGHT_OR_WORK"]}

def render(root,day):
    records=read_day(root,day)
    counts=Counter(r["kind"] for r in records)
    badges="".join("<span class=chip>"+html.escape(k)+": "+str(counts[k])+"</span>" for k in KINDS)
    items=[]
    for r in records:
        txt=r["retained_text"]
        body=("<details><summary>Opt-in retained note</summary><pre>"+html.escape(txt)+"</pre></details>") if txt is not None else "<em>Content intentionally not retained</em>"
        items.append("<li><article><h2>"+str(r["seq"])+" · "+html.escape(r["kind"])+"</h2><p><b>"+
                     html.escape(r["source_id"])+"</b></p><p><small>Observed: "+
                     html.escape(r["observed_at"])+"; source-time: "+
                     html.escape(r["source_time"] or "UNKNOWN")+"</small></p>"+
                     body+"<p><small>Local proof "+html.escape(r["record_sha256"][:16])+
                     "…; receiver ACK: NONE</small></p></article></li>")
    return ('<!doctype html><html lang="en"><head><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width,initial-scale=1">'
            '<meta http-equiv="Content-Security-Policy" content="default-src &#39;none&#39;; style-src &#39;unsafe-inline&#39;; base-uri &#39;none&#39;; form-action &#39;none&#39;">'
            '<title>CoCopy+ · CoAckRewise+ day trail</title>'
            '<style>body{background:#11281e;color:#f1f8f3;font:16px system-ui;line-height:1.5;padding:1rem}'
            'main{max-width:56rem;margin:auto}h1{font-size:clamp(1.6rem,4vw,2.5rem)}'
            '.chip{display:inline-block;background:#2b553e;border:1px solid #9bc7a8;padding:.4rem .7rem;border-radius:1rem;margin:.25rem}'
            'article{background:#193c2d;border:1px solid #679b78;border-radius:.7rem;padding:1rem;margin:.7rem 0}'
            'pre{white-space:pre-wrap;overflow-wrap:anywhere}ol{padding-left:1.5rem}'
            'small,em{color:#d8ecdd}p{overflow-wrap:anywhere}summary:focus{outline:3px solid white}'
            '</style></head><body><main><h1>◎ CoCopy+ / CoAckRewise+ day trail</h1>'
            '<p>'+html.escape(day)+' · private local read-only projection · '+str(len(records))+
            ' explicitly supplied records</p><div>'+badges+
            '</div><p>RAW → REWISE → ACK → CHALLENGE → OUTCOME. An ACK label is not receiver readproof. No provider messages, clipboard, typing, or thoughts were automatically read.</p>'
            '<ol>'+''.join(items)+'</ol><footer>'+
            ('No entries: this is not evidence that no work happened.' if not records else 'Local hash chain verified, independent custody not demonstrated.')+
            '</footer></main></body></html>')

def cli():
    p=argparse.ArgumentParser(description="Explicit local CoCopy/CoAckRewise day trail")
    p.add_argument("--root",required=True,help="explicit private directory, not a public repository")
    sub=p.add_subparsers(dest="command",required=True)
    a=sub.add_parser("append")
    a.add_argument("--day",default=date.today().isoformat())
    a.add_argument("--kind",required=True,choices=KINDS)
    a.add_argument("--source-id",required=True)
    a.add_argument("--source-time")
    a.add_argument("--parent-id")
    a.add_argument("--input-file",type=Path)
    a.add_argument("--retain-raw",action="store_true")
    for name in ("verify","render"):
        b=sub.add_parser(name)
        b.add_argument("--day",default=date.today().isoformat())
        if name=="render":
            b.add_argument("--output",type=Path,required=True)
    args=p.parse_args()
    try:
        if args.command=="append":
            data=b""
            if args.input_file:
                f=args.input_file
                if f.is_symlink() or not f.is_file() or f.stat().st_size>MAX_NOTE:
                    raise ValueError("INPUT_NOT_QUALIFIED")
                data=f.read_bytes()
            row=append(args.root,args.day,args.kind,args.source_id,data,
                       args.retain_raw,args.parent_id,args.source_time)
            print(json.dumps({"state":"APPENDED_LOCAL_ONLY","day":args.day,
                              "seq":row["seq"],"record_sha256":row["record_sha256"],
                              "raw_retained":args.retain_raw}))
        elif args.command=="verify":
            print(json.dumps(summary(args.root,args.day),sort_keys=True))
        else:
            page=render(args.root,args.day)
            path=args.output.expanduser().absolute()
            if path.is_symlink():
                raise ValueError("OUTPUT_SYMLINK_FORBIDDEN")
            with path.open("x",encoding="utf8") as f:
                f.write(page)
            print(json.dumps({"state":"RENDERED_LOCAL_ONLY",
                              "day":args.day,"bytes":len(page.encode("utf8")),
                              "receiver_ack":None}))
    except (OSError,ValueError) as exc:
        p.exit(2,"HELD: "+str(exc)+"\n")

if __name__=="__main__":
    cli()
