"""Derived personal-research observations; absent data stays absent."""
from datetime import date, timedelta
import math


def finite(value):
    try:
        value = float(value)
        return value if math.isfinite(value) else None
    except (TypeError, ValueError):
        return None


def trailing_return(rows, years):
    end = date.fromisoformat(rows[-1]['date'])
    try:
        start = end.replace(year=end.year-years)
    except ValueError:
        start = end.replace(year=end.year-years, day=28)
    eligible = [r for r in rows if date.fromisoformat(r['date']) <= start]
    if not eligible:
        return None
    first = eligible[-1]
    if (start-date.fromisoformat(first['date'])).days > 7:
        return None
    elapsed = (end-date.fromisoformat(first['date'])).days/365.25
    ratio = rows[-1]['close']/first['close']
    return (ratio-1)*100 if years == 1 else (ratio**(1/elapsed)-1)*100


def summarize(rows, payments, spot, info):
    if len(rows) < 3:
        raise ValueError('Histórico insuficiente')
    end = date.fromisoformat(rows[-1]['date'])
    payouts = [p for p in payments if end-timedelta(days=365) < date.fromisoformat(p['date']) <= end]
    amount = sum(p['amount'] for p in payouts) if payouts else None
    spot = finite(spot)
    count = finite(info.get('numberOfAnalystOpinions'))
    target = finite(info.get('targetMeanPrice'))
    analyst = None
    if count and count > 0 and target and target > 0 and spot and spot > 0:
        analyst = {'target':target,'count':int(count),'upside':(target/spot-1)*100,
                   'low':finite(info.get('targetLowPrice')),'high':finite(info.get('targetHighPrice')),
                   'referenceDate':None,'notice':'Data de referência e justificativas individuais não fornecidas pelo agregador. Não tratar como consenso atual confirmado.'}
    return {'asOf':rows[-1]['date'],'r1':trailing_return(rows,1),'r3':trailing_return(rows,3),'r5':trailing_return(rows,5),
            'method':'Variação do fechamento ajustado pela fonte',
            'incomeTTM':amount,'yieldTTM':amount/spot*100 if amount is not None and spot and spot>0 else None,
            'paymentCount':len(payouts),'payments':payouts[-12:],'analyst':analyst}
