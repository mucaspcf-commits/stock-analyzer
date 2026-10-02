// Direct calls only to the fixed public provider registry. Failed CORS/network calls preserve the edition.
export async function refreshPublic(snapshot){
 let updated=0,failed=0;
 const allowed=new Set(['api.bcb.gov.br','fred.stlouisfed.org','api.worldbank.org']);
 const requests=new Map(),today=new Date().toISOString().slice(0,10);
 const originals=snapshot.indicators.filter(i=>!['ipca12','igpm12','inpc12'].includes(i.id));
 const queue=[...originals],results=[];
 async function read(item){try{
  if(!item.dataUrl||!allowed.has(new URL(item.dataUrl).hostname))throw new Error('Fonte não configurada');
  let url=item.dataUrl;
  if(item.provider==='BCB'){const u=new URL(url);const to=new Date();const from=new Date(to);from.setUTCDate(from.getUTCDate()-760);const format=d=>`${String(d.getUTCDate()).padStart(2,'0')}/${String(d.getUTCMonth()+1).padStart(2,'0')}/${d.getUTCFullYear()}`;u.searchParams.set('dataInicial',format(from));u.searchParams.set('dataFinal',format(to));url=u.href;}
  if(!requests.has(url))requests.set(url,fetch(url,{signal:AbortSignal.timeout(12000)}).then(r=>{if(!r.ok)throw new Error('Fonte indisponível');return r.text();}));
  const raw=await requests.get(url);let rows;
  if(item.provider==='BCB')rows=JSON.parse(raw).map(r=>({date:r.data.split('/').reverse().join('-'),value:Number(r.valor)}));
  else if(item.provider==='Banco Mundial')rows=(JSON.parse(raw)[1]||[]).filter(r=>r.country.id===item.countryCode&&r.value!==null&&Number(r.date)<new Date().getFullYear()).map(r=>({date:r.date+'-01-01',value:Number(r.value)}));
  else {const lines=raw.trim().split(/\r?\n/);const header=lines.shift().split(',');const index=header.indexOf(item.code);if(index<0)throw new Error('Formato inválido');rows=lines.map(l=>l.split(',')).filter(r=>r[index]!=='.'&&r[index]!=='').map(r=>({date:r[0],value:Number(r[index])}));}
  rows=rows.filter(r=>r.date<=today&&Number.isFinite(r.value)).sort((a,b)=>a.date.localeCompare(b.date));
  if(!rows.length||rows.at(-1).date<(item.date||''))throw new Error('Fonte regressiva ou vazia');
  const last=rows.at(-1);updated++;return {...item,history:rows,value:last.value,date:last.date,fetchedAt:new Date().toISOString(),status:(Date.now()-Date.parse(last.date))/86400000>item.lag?'old':'ok'};
 }catch{failed++;return {...item,status:item.value===null?'unavailable':'cached'};}}
 async function worker(){while(queue.length){results.push(await read(queue.shift()));}}
 await Promise.all(Array.from({length:4},worker));
 const map=new Map(results.map(i=>[i.id,i]));
 for(const id of ['ipca','igpm','inpc']){const base=map.get(id),old=snapshot.indicators.find(i=>i.id===id+'12');if(!base||!old)continue;const history=[];for(let n=11;n<base.history.length;n++){const window=base.history.slice(n-11,n+1);const ord=window.map(r=>Number(r.date.slice(0,4))*12+Number(r.date.slice(5,7)));if(ord.slice(1).every((v,i)=>v-ord[i]===1))history.push({date:window.at(-1).date,value:(window.reduce((a,r)=>a*(1+r.value/100),1)-1)*100});}map.set(old.id,history.length?{...old,history,value:history.at(-1).value,date:history.at(-1).date,status:base.status,fetchedAt:base.fetchedAt}:old);}
 return {snapshot:{...snapshot,indicators:snapshot.indicators.map(i=>map.get(i.id)||i)},updated,failed};
}
