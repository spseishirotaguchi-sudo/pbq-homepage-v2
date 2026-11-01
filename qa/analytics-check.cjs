const test = require('node:test');
const assert = require('node:assert/strict');
const vm = require('node:vm');
const fs = require('node:fs');
const source = fs.readFileSync(__dirname + '/../public/assets/analytics.js', 'utf8');

function fixture(options = {}) {
  const events = {}, globalEvents = {}, tags = [], controls = [], statuses = [];
  const state = new Map(Object.entries(options.storage || {}));
  const button = {textContent: '', disabled: false, attributes: {}, listeners: {}, setAttribute(k,v){this.attributes[k]=v;},addEventListener(k,v){this.listeners[k]=v;}};
  if (options.preference) {controls.push(button);statuses.push({textContent:''});}
  const question = {open:false,addEventListener(k,v){this.listener=v;}};
  const document = {
    currentScript: {dataset: {measurementId: options.id || 'G-PBQTEST123', pbqSite: options.site || 'hp'}},
    referrer: 'https://www.instagram.com/?email=private@example.com',
    head: {appendChild(tag){tags.push(tag);}},
    documentElement: {scrollHeight: 4000}, body: {scrollHeight: 4000},
    createElement(){return {};},
    querySelectorAll(selector){return selector==='[data-analytics-toggle]'?controls:selector==='[data-analytics-status]'?statuses:[question];},
    addEventListener(k,v){events[k]=v;}
  };
  const location = new URL(options.url || 'https://pbq-fukuoka-20261022.s-taguchi323.chatgpt.site/about?email=private@example.com&uid=U123&utm_source=instagram&utm_campaign=winter_2026#secret');
  const window = {scrollY:1000};
  const context = vm.createContext({window,document,location,navigator:{globalPrivacyControl:!!options.gpc},URL,Set,Date,innerHeight:1000,localStorage:{getItem(k){if(options.storageError)throw Error('denied');return state.get(k)||null;},setItem(k,v){state.set(k,v);}},addEventListener(k,v){globalEvents[k]=v;},requestAnimationFrame(fn){fn();}});
  vm.runInContext(source,context);
  const rows=()=>Array.from(window.dataLayer||[], x=>Array.from(x));
  const sent=(name)=>rows().filter(x=>x[0]==='event'&&x[1]===name);
  const click=(url,where='',text='参加する')=>{
    const anchor={href:url,textContent:text,closest(selector){return selector.split(',').map(x=>x.trim()).includes(where)?{}:null;}};
    events.click?.({target:{closest(){return anchor;}}});
  };
  return {window,document,context,events,globalEvents,tags,button,statuses,state,question,rows,sent,click};
}

test('production initializes once with same stream, restricted ads and cross-domain linker',()=>{
 const f=fixture(); vm.runInContext(source,f.context);
 assert.equal(f.tags.length,1); assert.equal(f.rows().filter(r=>r[0]==='config').length,1);
 const config=f.rows().find(r=>r[0]==='config');
 assert.equal(config[1],'G-PBQTEST123');assert.equal(config[2].content_group,'hp');
 assert.equal(config[2].allow_google_signals,false);assert.equal(config[2].allow_ad_personalization_signals,false);
 assert.equal(f.rows().find(r=>r[0]==='consent')[2].ad_user_data,'denied');
 assert.equal(f.rows().find(r=>r[1]==='linker')[2].domains.length,2);
});
test('page and referrer remove private queries and hashes but preserve safe attribution',()=>{
 const f=fixture();const config=f.rows().find(r=>r[0]==='config')[2];
 assert.equal(config.page_location,'https://pbq-fukuoka-20261022.s-taguchi323.chatgpt.site/about?utm_source=instagram&utm_campaign=winter_2026');
 assert.equal(config.page_referrer,'https://www.instagram.com/');
 assert.ok(!JSON.stringify(f.rows()).includes('private@example.com'));
});
test('LP variants use content_group lp and share one measurement ID',()=>{
 const f=fixture({url:'https://spseishirotaguchi-sudo.github.io/pbq-lp/sports/',site:'lp'});
 assert.equal(f.tags.length,1);assert.equal(f.rows().find(r=>r[0]==='config')[2].content_group,'lp');
});
test('preview, unrelated GitHub projects and invalid ID never contact Google',()=>{
 for(const opts of [{url:'http://127.0.0.1:8783/'},{url:'https://spseishirotaguchi-sudo.github.io/pbq-liff/'},{id:'not-a-measurement-id'}]){
  const f=fixture(opts);assert.equal(f.tags.length,0);assert.equal(f.rows().length,0);
 }
});
test('LINE and Instagram clicks carry button location without personal values or blocking navigation',()=>{
 const f=fixture();f.click('https://lin.ee/OFk6v075','.hero');f.click('https://lin.ee/rdgWlbC','footer','問い合わせる');f.click('https://www.instagram.com/p.b.q_fukuoka/','footer');
 assert.equal(f.sent('line_click').length,1);assert.equal(f.sent('line_click')[0][2].button_position,'hero');
 assert.equal(f.sent('line_contact_click').length,1);assert.equal(f.sent('instagram_click').length,1);
 assert.ok(!JSON.stringify(f.sent('line_click')).includes('OFk6v075'));
});
test('scroll progress records each threshold once and requires an actual scroll',()=>{
 const f=fixture();assert.equal(f.sent('content_progress').length,0);
 f.globalEvents.scroll();f.globalEvents.scroll();assert.equal(f.sent('content_progress').length,2);
 f.window.scrollY=2800;f.globalEvents.scroll();assert.equal(f.sent('content_progress').length,4);
});
test('only opened FAQ emits its index',()=>{
 const f=fixture();f.question.listener();assert.equal(f.sent('faq_open').length,0);
 f.question.open=true;f.question.listener();assert.equal(f.sent('faq_open')[0][2].faq_index,1);
});
test('saved opt-out and GPC block Google loading and custom events',()=>{
 for(const options of [{storage:{'pbq.analytics.disabled':'1'}},{gpc:true}]){
  const f=fixture({...options,preference:true});f.click('https://lin.ee/rdgWlbC');assert.equal(f.tags.length,0);assert.equal(f.rows().length,0);
  assert.equal(f.window['ga-disable-G-PBQTEST123'],true);
 }
});
test('visitor can stop and reenable future analytics without duplicate page view',()=>{
 const f=fixture({preference:true});f.button.listeners.click();f.click('https://lin.ee/rdgWlbC');assert.equal(f.sent('line_click').length,0);assert.equal(f.state.get('pbq.analytics.disabled'),'1');
 f.button.listeners.click();f.click('https://lin.ee/rdgWlbC');assert.equal(f.sent('line_click').length,1);assert.equal(f.tags.length,1);
});
test('unavailable localStorage never breaks public website',()=>{
 const f=fixture({preference:true,storageError:true});assert.equal(f.tags.length,1);assert.doesNotThrow(()=>f.button.listeners.click());
});
