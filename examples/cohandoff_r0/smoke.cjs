// Source-level VM test of the actual browser script with a synthetic channel and DOM.
// Not a browser-origin, provider, X2, or independent-host test.
const assert=require('node:assert/strict');
const fs=require('node:fs');
const vm=require('node:vm');
const {webcrypto}=require('node:crypto');
const html=fs.readFileSync(__dirname+'/index.html','utf8');
const code=html.match(/<script>([\s\S]*?)<\/script>/)?.[1];
assert(code,'script must exist');new vm.Script(code);
const groups=new Map();
function addChannel(name){
 let q=groups.get(name);if(!q){q=new Set();groups.set(name,q);}
 const mine={name,onmessage:null,closed:false,postMessage(data){
  if(mine.closed)throw new Error('closed channel');
  for(const other of q)if(other!==mine&&!other.closed&&other.onmessage)queueMicrotask(()=>other.onmessage({data:structuredClone(data)}));
 },close(){mine.closed=true;q.delete(mine)}};
 q.add(mine);return mine;
}
function elem(id){return {id,hidden:false,value:'',checked:false,disabled:false,textContent:'',innerText:'',href:'',children:[],onclick:null,append(a){this.children.push(a)}};}
function boot(role,session,cryptoShim=webcrypto){
 const elements=new Map(),e=id=>{if(!elements.has(id))elements.set(id,elem(id));return elements.get(id)};
 e('message').value='Improve first use';e('to-ux').checked=true;e('to-theory').checked=true;
 const context={window:{BroadcastChannel:addChannel,open(){return null}},document:{getElementById:e,createElement(tag){return elem(tag)}},location:{hash:'#'+role+'/'+session,href:'https://example.invalid/index.html#'+role+'/'+session},history:{replaceState(){}},crypto:cryptoShim,TextEncoder,Uint8Array,Set,Array,Map,Number,String,JSON,queueMicrotask,structuredClone,console};
 context.BroadcastChannel=addChannel;context.window.crypto=cryptoShim;
 vm.createContext(context);vm.runInContext(code,context,{timeout:2000});
 return {e,context};
}
const sleep=()=>new Promise(resolve=>setTimeout(resolve,20));
(async()=>{
 const session='0'.repeat(32);const sender=boot('sender',session),ux=boot('ux',session),theory=boot('theory',session);
 await sleep();assert.match(sender.e('state').textContent,/SOURCE READY/);
 assert.match(ux.e('state').textContent,/RECEIVER UX READY/);
 await sender.e('send').onclick();await sleep();
 assert.match(sender.e('source-log').textContent,/ACK accepted role=ux cursor=1/);
 assert.match(sender.e('source-log').textContent,/ACK accepted role=theory cursor=1/);
 assert.equal(ux.e('received').textContent,'Improve first use');
 assert.equal(theory.e('received').textContent,'Improve first use');
 console.log('PASS actual source logic: two per-role SHA256 ACKs');
 sender.e('replay').onclick();await sleep();
 assert.match(theory.e('receiver-log').textContent,/STALE_OR_REPLAY/);
 assert.match(sender.e('source-log').textContent,/ACK held role=theory cursor=1 reason=STALE_OR_REPLAY/);
 console.log('PASS actual source logic: stale replay HELD');
 sender.e('to-theory').checked=false;sender.e('message').value='UX only';
 await sender.e('send').onclick();await sleep();
 assert.equal(ux.e('received').textContent,'UX only');
 assert.equal(theory.e('received').textContent,'Improve first use');
 assert.match(ux.e('receiver-log').textContent,/ACCEPTED cursor=2/);
 console.log('PASS actual source logic: role-scoped receiver isolation');
 sender.e('stop').onclick();await sleep();
 assert.match(ux.e('state').textContent,/STOPPED BY SOURCE/);
 assert.match(theory.e('state').textContent,/STOPPED BY SOURCE/);
 assert(sender.e('send').disabled);console.log('PASS actual source logic: stop closes channels');
 const alone=boot('sender','1'.repeat(32));await sleep();
 await alone.e('send').onclick();await sleep();
 assert.match(alone.e('source-log').textContent,/SENT role=ux/);
 assert.doesNotMatch(alone.e('source-log').textContent,/ACK accepted/);
 const forgery=addChannel('coomni-r0-'+'1'.repeat(32)+'-ux');
 forgery.postMessage({kind:'ACK',work_id:'coomni-local-'+'1'.repeat(32),role:'ux',seq:1,packet_sha256:'0'.repeat(64),result:'ACCEPTED'});
 await sleep();assert.match(alone.e('source-log').textContent,/REJECT unexpected ACK/);
 forgery.close();alone.e('stop').onclick();
 console.log('PASS actual source logic: missing receiver is NOT ACK and mismatched ACK rejected');


 // Ensure a stop during delayed digest cannot revive a previously cancelled send.
 const raceSession='2'.repeat(32);
 let unblockSender;
 const senderCrypto={getRandomValues:webcrypto.getRandomValues.bind(webcrypto),subtle:{digest:async(...args)=>{await new Promise(resolve=>{unblockSender=resolve});return webcrypto.subtle.digest(...args)}}};
 const delayedSender=boot('sender',raceSession,senderCrypto);
 const raceUx=boot('ux',raceSession);
 await sleep();
 const inFlight=delayedSender.e('send').onclick();await sleep();
 assert.equal(typeof unblockSender,'function');
 delayedSender.e('stop').onclick();unblockSender();
 await inFlight;await sleep();
 assert.doesNotMatch(delayedSender.e('source-log').textContent,/SENT role=/);
 assert.doesNotMatch(delayedSender.e('source-log').textContent,/ACK accepted/);
 console.log('PASS actual source logic: STOP during sender hash prevents posting and false ACK');

 // Ensure receiver cannot accept/ACK a packet after STOP if hash calculation was delayed.
 const delayedSession='3'.repeat(32);
 let unblockReceiver;
 const receiverCrypto={getRandomValues:webcrypto.getRandomValues.bind(webcrypto),subtle:{digest:async(...args)=>{await new Promise(resolve=>{unblockReceiver=resolve});return webcrypto.subtle.digest(...args)}}};
 const delayedSource=boot('sender',delayedSession);
 const delayedReceiver=boot('ux',delayedSession,receiverCrypto);
 await sleep();delayedSource.e('to-theory').checked=false;
 await delayedSource.e('send').onclick();await sleep();
 assert.equal(typeof unblockReceiver,'function');
 delayedSource.e('stop').onclick();await sleep();unblockReceiver();await sleep();
 assert.doesNotMatch(delayedReceiver.e('receiver-log').textContent,/ACCEPTED cursor=/);
 assert.doesNotMatch(delayedSource.e('source-log').textContent,/ACK accepted/);
 console.log('PASS actual source logic: STOP during receiver hash prevents late acceptance');

})().catch(e=>{console.error('FAIL',e);process.exitCode=1});
