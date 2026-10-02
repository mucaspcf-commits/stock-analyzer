// Pure calculations. Rates are user hypotheses, never market forecasts.
export function projectGoal(input) {
  const { initial, monthly, years, rate, inflation, target, fee = 0, tax = 0 } = input;
  if (![initial, monthly, years, rate, inflation, target, fee, tax].every(Number.isFinite) || initial < 0 || monthly < 0 || target < 0 || years < 1 || years > 60 || rate < -50 || rate > 50 || inflation < -10 || inflation > 50 || fee < 0 || fee > 10 || tax < 0 || tax > 50) throw new Error('Confira os valores e os limites dos campos.');
  const months = Math.round(years * 12);
  const annual = (1 + rate / 100) * (1 - fee / 100) - 1;
  const r = Math.pow(1 + annual, 1 / 12) - 1;
  const factor = Math.pow(1 + r, months);
  const annuity = Math.abs(r) < 1e-12 ? months : (factor - 1) / r;
  const futureTarget = target * Math.pow(1 + inflation / 100, years);
  const netAt = (contribution) => { const gross = initial * factor + contribution * annuity; const invested = initial + contribution * months; return gross - Math.max(0, gross - invested) * tax / 100; };
  let lo = 0, hi = Math.max(1, futureTarget / months);
  while (netAt(hi) < futureTarget && hi < 1e15) hi *= 2;
  for (let k = 0; k < 100; k++) { const mid = (lo + hi) / 2; if (netAt(mid) < futureTarget) lo = mid; else hi = mid; }
  const required = netAt(0) >= futureTarget ? 0 : hi;
  let balance = initial;
  const series = [{ year: 0, balance: initial, invested: initial, real: initial }];
  for (let m = 1; m <= months; m++) {
    balance = balance * (1 + r) + monthly;
    if (m % 12 === 0 || m === months) { const invested = initial + monthly * m; const net = balance - Math.max(0, balance - invested) * tax / 100; series.push({ year: m / 12, balance: net, invested, real: net / Math.pow(1 + inflation / 100, m / 12) }); }
  }
  return { series, final: netAt(monthly), real: netAt(monthly) / Math.pow(1 + inflation / 100, years), invested: initial + monthly * months, futureTarget, required, reached: netAt(monthly) >= futureTarget };
}

export function retirementCapital(income, withdrawal) {
  if (!Number.isFinite(income) || income < 0 || !Number.isFinite(withdrawal) || withdrawal < 1 || withdrawal > 10) throw new Error('Revise renda e taxa de retirada.');
  return income * 12 / (withdrawal / 100);
}

export function parseCSV(text) {
  const lines = text.trim().replace(/^\uFEFF/, '').split(/\r?\n/);
  if (lines.length > 15001) throw new Error('Limite de 15.000 observações.');
  const separator = lines[0].includes(';') ? ';' : ',';
  const header = lines.shift().toLowerCase().split(separator).map(s => s.trim().replaceAll('"', ''));
  const dateIndex = header.findIndex(s => ['date', 'data'].includes(s));
  const closeIndex = header.findIndex(s => ['close', 'fechamento', 'adj close', 'price', 'preco'].includes(s));
  if (dateIndex < 0 || closeIndex < 0) throw new Error('Use colunas Date,Close ou Data;Fechamento e datas AAAA-MM-DD.');
  const seen = new Map();
  for (const line of lines.filter(s => s.trim())) {
    const cells = line.split(separator).map(s => s.trim().replaceAll('"', ''));
    const date = cells[dateIndex];
    const value = Number(separator === ';' ? cells[closeIndex]?.replace(',', '.') : cells[closeIndex]);
    if (!/^\d{4}-\d{2}-\d{2}$/.test(date) || !Number.isFinite(Date.parse(date)) || new Date(date).toISOString().slice(0, 10) !== date || !Number.isFinite(value) || value <= 0) throw new Error('Há uma data ou preço inválido no CSV.');
    if (seen.has(date)) throw new Error('Há datas duplicadas no CSV.');
    seen.set(date, value);
  }
  if (seen.size < 3) throw new Error('Informe pelo menos três observações.');
  return [...seen].sort(([a], [b]) => a.localeCompare(b)).map(([date, close]) => ({ date, close }));
}

export function priceMetrics(rows, periods = 252) {
  if (rows.length < 3) throw new Error('Histórico insuficiente.');
  let peak = rows[0].close, drawdown = 0;
  const returns = rows.slice(1).map((row, i) => row.close / rows[i].close - 1);
  for (const row of rows) { peak = Math.max(peak, row.close); drawdown = Math.min(drawdown, row.close / peak - 1); }
  const mean = returns.reduce((a, b) => a + b, 0) / returns.length;
  const variance = returns.reduce((a, b) => a + (b - mean) ** 2, 0) / (returns.length - 1);
  const recent = rows.slice(-20);
  return { returnPct: (rows.at(-1).close / rows[0].close - 1) * 100, volatility: Math.sqrt(variance * periods) * 100, drawdown: drawdown * 100, average: recent.reduce((sum, row) => sum + row.close, 0) / recent.length,
    series: rows.map((row, i) => ({ ...row, average: i >= 19 ? rows.slice(i - 19, i + 1).reduce((sum, p) => sum + p.close, 0) / 20 : null })) };
}

export function normalizeSearch(value) { return value.normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase(); }
