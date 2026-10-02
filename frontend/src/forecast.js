export const MODELS={naive:'Último valor (referência)',drift:'Passeio aleatório com drift',linear:'Regressão linear',ses:'Suavização exponencial',holt:'Tendência amortecida de Holt'};
export function predict(values,steps,model){
 if(values.length<3||!values.every(Number.isFinite)||steps<1||steps>90)throw new Error('Dados insuficientes ou horizonte inválido.');
 const n=values.length,last=values.at(-1);
 if(model==='naive')return Array(steps).fill(last);
 if(model==='drift')return Array.from({length:steps},(_,i)=>last+(i+1)*(last-values[0])/(n-1));
 if(model==='linear'){const xm=(n-1)/2,ym=values.reduce((a,b)=>a+b,0)/n;let num=0,den=0;values.forEach((y,x)=>{num+=(x-xm)*(y-ym);den+=(x-xm)**2;});const slope=num/den;return Array.from({length:steps},(_,i)=>ym+slope*(n+i-xm));}
 if(model==='ses'){let level=values[0];for(const y of values.slice(1))level=.3*y+.7*level;return Array(steps).fill(level);}
 if(model==='holt'){let level=values[0],trend=values[1]-values[0];for(const y of values.slice(1)){const old=level;level=.3*y+.7*(level+.9*trend);trend=.1*(level-old)+.9*.9*trend;}return Array.from({length:steps},(_,i)=>level+trend*.9*(1-.9**(i+1))/(1-.9));}
 throw new Error('Modelo desconhecido.');
}
export function forecast(rows,steps=20){
 if(rows.length<60)throw new Error('Use pelo menos 60 observações para comparar projeções.');
 if(!Number.isInteger(steps)||steps<1||steps>90)throw new Error('Horizonte deve ser inteiro entre 1 e 90 observações.');
 const values=rows.map(r=>r.close??r.value);if(!values.every(v=>Number.isFinite(v)&&v>0))throw new Error('A série deve ter valores positivos e finitos.');
 const horizon=Math.min(steps,Math.floor(values.length/6),30),folds=3;
 const results=Object.entries(MODELS).map(([id,name])=>{const errors=[],absolutePct=[];for(let f=folds;f>=1;f--){const end=values.length-f*horizon;const train=values.slice(0,end);const test=values.slice(end,end+horizon);const prediction=predict(train,horizon,id);test.forEach((actual,i)=>{errors.push(prediction[i]-actual);absolutePct.push(Math.abs((prediction[i]-actual)/actual)*100);});}const mae=errors.reduce((a,b)=>a+Math.abs(b),0)/errors.length;const rmse=Math.sqrt(errors.reduce((a,b)=>a+b*b,0)/errors.length);const future=predict(values,steps,id);return {id,name,mae,rmse,mape:absolutePct.reduce((a,b)=>a+b,0)/absolutePct.length,future,valid:future.every(Number.isFinite)};}).filter(r=>r.valid).sort((a,b)=>a.mae-b.mae);
 return {results,best:results[0],horizon,folds,observations:folds*horizon,series:Array.from({length:steps+1},(_,i)=>({step:i,...Object.fromEntries(results.map(r=>[r.id,i===0?values.at(-1):r.future[i-1]]))}))};
}
