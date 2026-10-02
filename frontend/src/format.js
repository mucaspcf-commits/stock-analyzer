export const fmt=(v,d=2)=>Number.isFinite(v)?v.toLocaleString('pt-BR',{minimumFractionDigits:d,maximumFractionDigits:d}):'—';
export const money=v=>Number.isFinite(v)?v.toLocaleString('pt-BR',{style:'currency',currency:'BRL',maximumFractionDigits:0}):'—';
export const date=v=>v?new Date(v.includes('T')?v:v+'T12:00:00').toLocaleDateString('pt-BR'):'Sem referência';
export const storage={read(k,f){try{return JSON.parse(localStorage.getItem('stock2-'+k))??f;}catch{return f;}},write(k,v){try{localStorage.setItem('stock2-'+k,JSON.stringify(v));return true;}catch{return false;}}};
export function download(name,text,type='text/csv'){const url=URL.createObjectURL(new Blob(['\uFEFF'+text],{type}));const a=document.createElement('a');a.href=url;a.download=name;a.click();URL.revokeObjectURL(url);}
