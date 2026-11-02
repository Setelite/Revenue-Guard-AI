const assert = require('node:assert/strict');
const fs = require('node:fs');
const { JSDOM } = require('jsdom');

const html = fs.readFileSync('index.html', 'utf8');
const app = new JSDOM(html, {
  url: 'http://127.0.0.1:8000/',
  runScripts: 'dangerously',
  pretendToBeVisual: true,
  beforeParse(window) {
    window.scrollTo = () => {};
    window.confirm = () => true;
    window.SpeechRecognition = undefined;
  }
});
const { document: d, localStorage } = app.window;
const click = (sel) => {
  const el = d.querySelector(sel);
  assert.ok(el, 'Missing interactive element '+sel);
  el.click();
};
const tick = () => new Promise(r=>setTimeout(r,10));

(async()=>{
  assert.match(d.querySelector('h1').textContent,/Ваша следующая идея/);
  const input=d.querySelector('#taskText');
  assert.ok(input);
  input.value='Нужно заполнить свободные окна в салоне завтра, без скидок.';
  click('#createButton');
  await tick();
  assert.equal(d.querySelectorAll('[data-select]').length,3,'Three offers expected');
  const titles=[...d.querySelectorAll('.offer h3')].map(x=>x.textContent);
  assert.equal(new Set(titles).size,3,'Three distinct fallback angles');
  click('[data-select="1"]');
  click('#selectOffer');
  await tick();
  assert.ok(d.querySelector('#storyPreview'),'Story creative preview should be visible');
  assert.equal(d.querySelectorAll('[data-theme]').length,3);
  click('[data-theme="ink"]');
  assert.ok(d.querySelector('#storyPreview').classList.contains('theme-ink'));
  const title=d.querySelector('#offerTitle');
  title.value='Тестовый новый заголовок';
  title.dispatchEvent(new app.window.Event('input',{bubbles:true}));
  assert.equal(d.querySelector('#storyTitle').textContent,title.value);
  click('#approveOffer');
  await tick();
  assert.ok(d.querySelector('#markPublished'),'Approval should precede publication');
  click('#markPublished');
  await tick();
  assert.ok(d.querySelector('#paidAmount'),'Payment can be recorded after marking published');
  d.querySelector('#paidAmount').value='4500';
  click('#addPayment');
  await tick();
  assert.match(d.querySelector('#view').textContent,/4\s?500/,'Recorded payment is visible');
  assert.ok(localStorage.getItem('rg-clean-v2'),'Local data should persist');
  console.log('PASS: home → 3 offers → story themes → approval → manual publication → payment');
  app.window.close();
})().catch(e=>{console.error(e);process.exitCode=1});
