const assert=require('node:assert/strict');
const fs=require('node:fs');
const {JSDOM}=require('jsdom');
const html=fs.readFileSync('index.html','utf8');
const app=new JSDOM(html,{
 url:'http://127.0.0.1:8000/',runScripts:'dangerously',pretendToBeVisual:true,
 beforeParse(w){
  w.scrollTo=()=>{};
  w.confirm=()=>true;
  // Historical counter-only entries must NOT count as overdue real tickets.
  w.localStorage.setItem('rg-clean-v2',JSON.stringify({
   business:{name:'Магазин света',industry:'retail',service:'Светильники',price:3500,channel:'Instagram',budget:0},
   campaigns:[],payments:[],
   leads:[{id:'old-count-1',campaignId:'campaign1',date:'2025-01-01T00:00:00Z'}]
  }));
 }
});
const d=app.window.document;
const click=x=>{const el=d.querySelector(x);assert.ok(el,'Missing '+x);el.click()};
const set=(x,v)=>{const e=d.querySelector(x);assert.ok(e,'Missing '+x);e.value=v;e.dispatchEvent(new app.window.Event('change',{bubbles:true}))};
(async()=>{
 click('#bottomnav [data-route="losses"]');
 assert.match(d.querySelector('h1').textContent,/Клиенты и/);
 assert.equal(d.querySelector('#riskCount').textContent,'0');
 assert.equal(d.querySelector('#openCount').textContent,'0');
 assert.match(d.querySelector('.loss-legacy').textContent,/1 старых записей/);
 assert.equal(d.querySelectorAll('.loss-lead').length,0);
 // Owner enters an anonymized lead received 36 hours earlier.
 const past=new Date(Date.now()-36*3600000);
 const inputDate=new Date(past.getTime()-past.getTimezoneOffset()*60000).toISOString().slice(0,16);
 set('#clientName','Тестовый Клиент');
 set('#clientPhone','+7 000 111-22-33');
 set('#clientEmail','test@example.com');
 set('#clientSocial','@demo');
 set('#clientInterest','Светильник');
 set('#clientComment','Вымышленный запрос для проверки интерфейса');
 set('#clientContactMethod','telegram');
 set('#newLeadSource','instagram');
 set('#newLeadEstimate','3500');
 set('#newLeadDate',inputDate);
 d.querySelector('#leadForm').dispatchEvent(new app.window.Event('submit',{bubbles:true,cancelable:true}));
 assert.equal(d.querySelector('#riskCount').textContent,'1','Past-due ticket detected');
 assert.equal(d.querySelector('#openCount').textContent,'1');
 assert.match(d.querySelector('#riskValue').textContent,/3\s?500/);
 assert.match(d.querySelector('.loss-status').textContent,/Требует внимания/);
 let state=JSON.parse(app.window.localStorage.getItem('rg-clean-v2'));
 assert.equal(state.leads.length,2,'Legacy counters preserved');
 assert.equal(state.leads[0].tracked,true);
 assert.equal(state.leads[0].source,'instagram');
 assert.equal(state.leads[0].estimate,3500);
 assert.doesNotMatch(app.window.localStorage.getItem('rg-clean-v2'),/Тестовый Клиент|111-22-33|test@example.com|@demo|Вымышленный запрос/,'No personal contact stored in browser persistence');
 assert.match(d.querySelector('.loss-profile-name').textContent,/Тестовый Клиент/);
 assert.match(d.querySelector('.client-profile').textContent,/test@example.com/);
 assert.match(d.querySelector('.client-profile').textContent,/@demo/);

 set('#riskHours','48');
 assert.equal(d.querySelector('#riskCount').textContent,'0','Adjusting SLA updates risk');
 set('#riskHours','12');
 assert.equal(d.querySelector('#riskCount').textContent,'1');
 click('[data-lead-action="working"]');
 assert.equal(d.querySelector('#riskCount').textContent,'0','Acknowledging resets timeout');
 assert.match(d.querySelector('.loss-status').textContent,/В работе/);
 click('[data-lead-action="won"]');
 assert.equal(d.querySelector('#openCount').textContent,'0');
 assert.equal(d.querySelector('#riskValue').textContent,'0 ₽');
 assert.equal(JSON.parse(app.window.localStorage.getItem('rg-clean-v2')).payments.length,0,'Closing as won does not invent received payment');
 click('.loss-reopen');
 assert.equal(d.querySelector('#openCount').textContent,'1','Accidentally closed leads can be reopened');
 assert.equal(d.querySelector('#riskCount').textContent,'0','Reopen logs a fresh action timestamp');
 click('[data-lead-action="lost"]');
 assert.equal(d.querySelector('#openCount').textContent,'0');
 // Input validation: future timestamps cannot be logged.
 const before=JSON.parse(app.window.localStorage.getItem('rg-clean-v2')).leads.length;
 const tomorrow=new Date(Date.now()+24*3600000);
 const futureInput=new Date(tomorrow.getTime()-tomorrow.getTimezoneOffset()*60000).toISOString().slice(0,16);
 set('#newLeadDate',futureInput);
 d.querySelector('#leadForm').dispatchEvent(new app.window.Event('submit',{bubbles:true,cancelable:true}));
 assert.equal(JSON.parse(app.window.localStorage.getItem('rg-clean-v2')).leads.length,before,'Reject future ticket date');
 click('#bottomnav [data-route="home"]');
 assert.match(d.querySelector('h1').textContent,/Что будем/);
 console.log('PASS: stale ticket, SLA, risk estimate, acknowledging, closing, old records, invalid date');
 app.window.close();
})().catch(e=>{console.error(e);process.exitCode=1});
