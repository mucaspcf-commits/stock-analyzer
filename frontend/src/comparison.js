import {priceMetrics} from './finance.js';
export function compareHistories(reference,alternatives,periods=252,tolerance=1){
 if(!Number.isFinite(tolerance)||tolerance<0||tolerance>10)throw new Error('Tolerância deve estar entre 0 e 10 pontos percentuais.');
 const included=[reference,...alternatives.filter(a=>a.currency===reference.currency)];
 if(included.length<2)throw new Error('Adicione ao menos uma alternativa na mesma moeda.');
 let common=new Set(reference.rows.map(r=>r.date));for(const item of included.slice(1)){const dates=new Set(item.rows.map(r=>r.date));common=new Set([...common].filter(d=>dates.has(d)));}
 const dates=[...common].sort();if(dates.length<3)throw new Error('São necessárias três datas comuns entre todos os históricos.');
 const metrics=included.map(item=>{const rows=item.rows.filter(r=>common.has(r.date)).sort((a,b)=>a.date.localeCompare(b.date));return {name:item.name,...priceMetrics(rows,periods),start:rows[0].close,end:rows.at(-1).close};});
 const base=metrics[0].returnPct;
 return {dates,currency:reference.currency,results:metrics.map((r,i)=>({...r,difference:r.returnPct-base,relation:i===0?'Referência':Math.abs(r.returnPct-base)<=tolerance?'Semelhante':r.returnPct>base?'Maior rentabilidade passada':'Menor rentabilidade passada'})).sort((a,b)=>b.returnPct-a.returnPct),excluded:alternatives.filter(a=>a.currency!==reference.currency).map(a=>a.name)};
}
