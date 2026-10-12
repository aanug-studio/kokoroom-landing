const assert = require('node:assert/strict');
const vm = require('node:vm');
const fs = require('node:fs');
const {test} = require('node:test');
const script = fs.readFileSync('assets/site.js', 'utf8');
function run({generic=true, locale='en', page='privacy', search='', hash='#analytics-consent', languages=['ko-KR'], saved=null, blocked=false}={}) {
  let replaced, stored, hashListener;
  const links=['ko','ja','zh-CN','zh-TW','en'].map(language=>({dataset:{language},events:{},addEventListener(k,f){this.events[k]=f;}}));
  const location={search,hash,replace(value){replaced=value;}};
  vm.runInNewContext(script,{
    URLSearchParams,location,navigator:{languages},
    document:{documentElement:{dataset:{generic:String(generic),locale,page}},querySelectorAll(){return links;}},
    localStorage:{getItem(){if(blocked)throw Error('blocked');return saved;},setItem(k,v){if(blocked)throw Error('blocked');stored=v;}},
    window:{addEventListener(k,f){hashListener=f;}}
  });
  return {get replaced(){return replaced;},get stored(){return stored;},links,location,hashChanged(){hashListener();}};
}
test('generic entry selects browser language and retains detail anchor',()=>assert.equal(run().replaced,'/ko/privacy/#analytics-consent'));
test('Chinese script and regional variants choose the correct page',()=>{
  for(const language of ['zh-TW','zh-HK','zh-MO','zh-Hant','zh-Hant-HK'])assert.equal(run({languages:[language]}).replaced,'/zh-TW/privacy/#analytics-consent');
  for(const language of ['zh','zh-CN','zh-SG','zh-Hans-TW'])assert.equal(run({languages:[language]}).replaced,'/zh-CN/privacy/#analytics-consent');
});
test('unsupported languages fall through to next preference or English',()=>{
  assert.equal(run({languages:['fr','ja-JP']}).replaced,'/ja/privacy/#analytics-consent');
  assert.equal(run({languages:['fr']}).replaced,'/en/privacy/#analytics-consent');
});
test('explicit query overrides stored choice and survives other parameters',()=>assert.equal(run({search:'?lang=ja&source=app',saved:'ko'}).replaced,'/ja/privacy/?source=app#analytics-consent'));
test('remembered choice wins over browser language',()=>assert.equal(run({saved:'en'}).replaced,'/en/privacy/#analytics-consent'));
test('an explicit localized URL remains stable despite saved language',()=>assert.equal(run({generic:false,locale:'ja',saved:'ko'}).replaced,undefined));
test('blocked storage does not break links or auto selection',()=>{
  assert.equal(run({blocked:true}).replaced,'/ko/privacy/#analytics-consent');
  const app=run({generic:false,blocked:true});assert.doesNotThrow(()=>app.links[1].events.click());
});
test('manual switch preserves page/anchor and saves choice',()=>{
  const app=run({generic:false,page:'terms',hash:'#article-11'});
  assert.equal(app.links[1].href,'/ja/terms/#article-11');app.links[1].events.click();assert.equal(app.stored,'ja');
});
test('fragment updates are included when switching later',()=>{
  const app=run({generic:false});app.location.hash='#deletion';app.hashChanged();assert.equal(app.links[4].href,'/en/privacy/#deletion');
});
