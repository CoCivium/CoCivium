#!/usr/bin/env python3
"""CoOmniIO source-structure checks only, never a Windows execution substitute."""
from pathlib import Path
import hashlib
import json
import re
import sys

ROOT = Path(__file__).resolve().parent
n=(ROOT/'CoOmniCycleR0.mjs').read_text(encoding='utf-8')
h=(ROOT/'CoOrbIOHotkeyR0.ps1').read_text(encoding='utf-8')
i=(ROOT/'Setup-CoOrbIO_R0.ps1').read_text(encoding='utf-8')
p=(ROOT/'CoCopyRichPaletteR0.ps1').read_text(encoding='utf-8')
checks={
'node_whitelist_tasks': all(x in n for x in ['HASH_OBJECT','INSPECT_JSON','COPY_PLAN']),
'node_no_spawn_import': not re.search(r'from\s+[\'\"]node:(?:child_process|net|http|https)',n),
'node_no_fetch_invocation': not re.search(r'\bfetch\s*\(',n),
'node_no_eval_exec': not re.search(r'\beval\s*\(|\bnew\s+Function\s*\(',n),
'node_bounded_four_tasks':'maxTasksPerCycle:4' in n,
'node_bounded_two_active':'maxActive:2' in n,
'node_bytes_streaming':'createReadStream' in n,
'node_source_path_guard':'SYMLINK_ESCAPE_FORBIDDEN' in n,
'node_absolute_rejection':'ABSOLUTE_PATH_FORBIDDEN' in n,
'node_lease_lock_wx':"fs.openSync(lock,'wx'" in n,
'node_receipt_wx':'createOnce(dst,' in n,
'node_pause_resume':all(x in n for x in ['export function pause','export function resume']),
'node_receivers_null':'receiver_readproof:null' in n,
'node_no_provider_sessions':'provider_sessions_started:0' in n,
'node_no_clipboard_writes':'Clipboard' not in n,
'hotkey_one_specific_chord':'RegisterHotKey' in h and '0x4e' in h,
'hotkey_no_mouse_hook':all(x not in h for x in ['SetWindowsHookEx','WH_MOUSE','mouse_event','SendInput','SendKeys']),
'hotkey_no_clipboard_read':all(x not in h for x in ['GetText(','GetDataObject(','Clipboard]::Get']),
'hotkey_tray_pausing':'Pause hotkey' in h and 'Resume hotkey' in h,
'hotkey_visible_tray':'$script:Tray.Visible=$true' in h,
'hotkey_explicit_palette_only':'CoCopyRichPaletteR0.ps1' in h and "'-NoProfile','-STA','-File'" in h,
'hotkey_stop_marker':'HOTKEY_STOP' in h,
'installer_user_local':'New-ScheduledTaskPrincipal' in i and 'LogonType Interactive' in i,
'installer_cycle_fifteen_minutes':'New-TimeSpan -Minutes 15' in i,
'installer_no_clobber':'HOLD_NO_CLOBBER' in i,
'installer_rollback':"'Remove'" in i and 'Unregister-ScheduledTask' in i,
'installer_no_admin_services':'New-Service' not in i and '-RunLevel Highest' not in i,
'installer_no_logi_mutation':not re.search(r'(?im)^\s*(?:&|Start-Process|Invoke-Expression)\b[^\n]*(?:Logi|OptionsPlus|Options\+)',i),
'installer_no_unconditional_exec':'Invoke-Expression' not in i and 'IEX ' not in i,
'palette_file_references_only':'SetFileDropList' in p,
'palette_no_auto_paste':'SendKeys' not in p and 'Ctrl+V' not in p,
'palette_selected_bitmap':'Clipboard]::SetImage' in p and 'Image]::FromFile' in p,
'palette_no_clipboard_read':'[System.Windows.Forms.Clipboard]::Get' not in p,
'palette_visible_close':'Close (Esc)' in p,
}
result={'schema':'CoCivium.CoOmniIO.StaticAudit.R0','environment':'Linux/portable Python structural inspection; real Windows PowerShell parser, GUI and device runtime not executed','total':len(checks),'passed':sum(checks.values()),'failed':len(checks)-sum(checks.values()),'source_sha256':{a:hashlib.sha256((ROOT/a).read_bytes()).hexdigest() for a in ['CoOmniCycleR0.mjs','CoOrbIOHotkeyR0.ps1','Setup-CoOrbIO_R0.ps1','CoCopyRichPaletteR0.ps1']},'checks':[{'id':k,'status':'PASS' if v else 'FAIL'} for k,v in checks.items()],'nonclaims':['STATIC_AUDIT_NE_WINDOWS_RUNTIME','SOURCE_PRESENT_NE_DEVICE_CONTROL','TEST_PASS_NE_RECEIVER_PICKUP']}
print(json.dumps(result,indent=2))
if result['failed']:sys.exit(1)
