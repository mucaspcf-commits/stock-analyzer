import test from 'node:test';
import assert from 'node:assert/strict';
import {rankRadar,CLASSES} from '../frontend/src/radar.js';
test('rankings never mix class, currency, reference date or method',()=>{
  const base={type:'ETF',currency:'USD',asOf:'2026-08-31',method:'Total return'};
  const groups=rankRadar([{...base,symbol:'A',r1:3},{...base,symbol:'B',r1:8},{...base,symbol:'C',currency:'BRL',r1:50},{...base,symbol:'D',type:'Ação',r1:25},{...base,symbol:'E',asOf:'2026-09-30',r1:25},{...base,symbol:'F',method:'Price only',r1:25},{...base,symbol:'G',r1:null}], 'r1');
  assert.equal(groups.length,5);assert.deepEqual(groups[0].map(r=>r.symbol),['B','A']);assert.equal(groups.flat().length,6);
});
test('negative historical returns are retained and absent metrics never rank',()=>{
  assert.equal(rankRadar([{type:'Cripto',currency:'USD',asOf:'2026-10-01',method:'Price',r5:-20},{type:'Cripto',currency:'USD',asOf:'2026-10-01',method:'Price',r5:NaN}], 'r5')[0][0].r5,-20);
  assert.ok(CLASSES.some(([name])=>name==='Derivativo'));assert.ok(CLASSES.some(([name])=>name==='Alternativo / privado'));
});
