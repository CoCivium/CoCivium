'use strict';
// RickPublic queue admission checks. This reads local checkout only.
// It never publishes, sends, touches accounts, or grants approval.
const fs=require('node:fs');
const path=require('node:path');
const crypto=require('node:crypto');
const assert=require('node:assert/strict');
const SERIES=path.resolve(__dirname,'..');
const REPO=path.resolve(SERIES,'../../../..');
const ARTICLES=path.join(SERIES,'articles');
const QUEUE=path.join(SERIES,'queue.json');
const slug=/^[a-z0-9]+(?:-[a-z0-9]+)*$/;
function fail(msg){throw Error('RICKPUBLIC_QUEUE_HELD: '+msg);}
function check(data,load) {
  if(!data||!Array.isArray(data.items)||data.series!=='rickpublic_substack_seed_v1')
    fail('invalid series or items');
  const seenOrdinal=new Set(),seenSlug=new Set(),seenPath=new Set();
  for(const row of data.items) {
    if(!Number.isSafeInteger(row.ordinal)||row.ordinal<1||seenOrdinal.has(row.ordinal))
      fail('duplicate or invalid ordinal');
    if(typeof row.slug!=='string'||!slug.test(row.slug)||seenSlug.has(row.slug))
      fail('duplicate or invalid slug');
    if(typeof row.title!=='string'||!row.title.trim()||typeof row.article_path!=='string')
      fail('missing title or article path');
    if(!['draft_ready','queued','seed_stub','published'].includes(row.status))
      fail('unrecognized state for '+row.slug);
    if(typeof row.approved_to_publish!=='boolean')fail('implicit approval for '+row.slug);
    const resolved=path.resolve(REPO,row.article_path);
    const rel=path.relative(ARTICLES,resolved);
    if(rel===''||rel.startsWith('..')||path.isAbsolute(rel)||!rel.endsWith('.md')||seenPath.has(resolved))
      fail('unsafe or reused article path for '+row.slug);
    let body;
    try{body=load(resolved);}catch(err){fail('unreadable article '+row.slug);}
    if(typeof body!=='string'||!body.startsWith('# '+row.title+'\n'))
      fail('article heading mismatches queue for '+row.slug);
    if(row.article_git_blob_sha){
      const actual=crypto.createHash('sha1')
        .update('blob '+Buffer.byteLength(body,'utf8')+'\0').update(body,'utf8').digest('hex');
      if(actual!==row.article_git_blob_sha)fail('exact article blob changed for '+row.slug);
    }
    if(row.approved_to_publish &&
       (!row.approval_actor_id||!row.approval_receipt_ref))
      fail('approval lacks actor/receipt for '+row.slug);
    if(row.status==='published'&&
       (typeof row.published_url!=='string'||!/^https:\/\/[^ ]+/.test(row.published_url)||
        !row.publication_readback_receipt))
      fail('published state without URL and independent readback');
    if(row.publication_status==='EXACT_PUBLICATION_UNVERIFIED' &&
       (row.approved_to_publish||row.status==='published'||row.published_url))
      fail('unverified publication was promoted for '+row.slug);
    seenOrdinal.add(row.ordinal);seenSlug.add(row.slug);seenPath.add(resolved);
  }
  return {items:data.items.length,approved:data.items.filter(x=>x.approved_to_publish).length,
    published:data.items.filter(x=>x.status==='published').length};
}
function selftest() {
  const article=path.join(ARTICLES,'01__The_Meaning_of_Lif.md');
  const base={series:'rickpublic_substack_seed_v1',items:[{ordinal:1,title:'The Meaning of Lif',
    slug:'the-meaning-of-lif',article_path:path.relative(REPO,article).split(path.sep).join('/'),
    status:'draft_ready',approved_to_publish:false}]};
  const load=()=> '# The Meaning of Lif\n\nSynthetic test only.\n';
  assert.equal(check(base,load).items,1);
  function reject(modifier){
    const copy=JSON.parse(JSON.stringify(base));modifier(copy.items[0],copy);
    assert.throws(()=>check(copy,load),/RICKPUBLIC_QUEUE_HELD/);
  }
  reject(x=>{x.approved_to_publish=true;});
  reject(x=>{x.status='published';});
  reject(x=>{x.publication_status='EXACT_PUBLICATION_UNVERIFIED';x.published_url='https://example.com/fake';});
  reject(x=>{x.article_path='../../../../../../etc/passwd';});
  reject(x=>{x.article_git_blob_sha='0'.repeat(40);});
  reject((x,b)=>{b.items.push({...x});});
  console.log('PASS RickPublic queue gate: seven synthetic invariants');
}
if(require.main===module){
  try{
    if(process.argv.includes('--selftest'))selftest();
    else{
      const result=check(JSON.parse(fs.readFileSync(QUEUE,'utf8')),(p)=>fs.readFileSync(p,'utf8'));
      console.log('PASS RickPublic queue contract: '+result.items+' items, '+result.approved+
        ' approved, '+result.published+' verified as published in queue');
    }
  }catch(err){console.error(err.message);process.exitCode=1;}
}
module.exports={check};
