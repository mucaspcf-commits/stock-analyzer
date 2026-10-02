"""Public, attributed macro series and headline links. No paid article scraping.
Uses standard library only, including in GitHub Actions.
"""
import csv
import hashlib
import io
import json
import math
import os
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'frontend/public/data/snapshot.json'
CACHE = ROOT / '.data-cache/snapshot.json'
TODAY = datetime.now(timezone.utc).date()

# Unit, periodicity and publication lag are explicit for each source.
INDICATORS = [
 dict(id='selic', name='Selic meta', code='432', provider='BCB', unit='% a.a.', group='Juros', lag=5, meaning='Meta definida pelo Copom; não é uma promessa de rendimento de um produto.'),
 dict(id='selic-efetiva', name='Selic efetiva', code='1178', provider='BCB', unit='% a.a.', group='Juros', lag=5, meaning='Taxa Selic efetiva anualizada, base de 252 dias úteis.'),
 dict(id='cdi', name='CDI diário', code='12', provider='BCB', unit='% ao dia', group='Juros', lag=5, meaning='Taxa diária de depósitos interfinanceiros. Compare períodos e unidades antes de usar.'),
 dict(id='ipca', name='IPCA mensal', code='433', provider='BCB', unit='% no mês', group='Inflação', lag=70, meaning='Inflação ao consumidor do IBGE, distribuída pelo SGS. A data representa o mês de referência.'),
 dict(id='inpc', name='INPC mensal', code='188', provider='BCB', unit='% no mês', group='Inflação', lag=70, meaning='Índice do IBGE para famílias de menor renda; variação mensal.'),
 dict(id='igpm', name='IGP-M mensal', code='189', provider='BCB', unit='% no mês', group='Inflação', lag=70, meaning='Índice Geral de Preços do Mercado, FGV, distribuído pelo SGS.'),
 dict(id='usd', name='Dólar / Real', code='1', provider='BCB', unit='R$/US$', group='Câmbio', lag=5, meaning='Cotação de venda do dólar no SGS. Não inclui spread, IOF ou tarifa de câmbio ao consumidor.'),
 dict(id='eur', name='Euro / Real', code='21619', provider='BCB', unit='R$/€', group='Câmbio', lag=5, meaning='Cotação de venda do euro no SGS; não equivale à taxa de turismo.'),
 dict(id='fed', name='Fed funds efetiva', code='FEDFUNDS', provider='FRED', unit='% a.a.', group='Exterior', lag=70, meaning='Média mensal da taxa efetiva dos fundos federais dos EUA.'),
 dict(id='treasury', name='Treasury de 10 anos', code='DGS10', provider='FRED', unit='% a.a.', group='Exterior', lag=7, meaning='Taxa de mercado de títulos do Tesouro dos EUA de maturidade constante de 10 anos.'),
 dict(id='unemployment', name='Desemprego EUA', code='UNRATE', provider='FRED', unit='%', group='Exterior', lag=70, meaning='Taxa de desemprego mensal, ajustada sazonalmente, BLS via FRED.'),
 dict(id='cpi', name='Inflação EUA · CPI', code='CPIAUCSL', provider='FRED', unit='índice 1982–84=100', group='Exterior', lag=70, meaning='Índice de preços ao consumidor, ajustado sazonalmente, BLS via FRED. É um nível de índice, não uma taxa percentual.'),
]
NEWS = [
 ('Reuters','reuters.com','Global'), ('Bloomberg','bloomberg.com','Global'),
 ('Financial Times','ft.com','Global'), ('The Wall Street Journal','wsj.com','Global'),
 ('The Economist','economist.com','Global'), ('CNBC','cnbc.com','Global'),
 ('MarketWatch','marketwatch.com','Global'), ('Valor Econômico','valor.globo.com','Brasil'),
 ('InfoMoney','infomoney.com.br','Brasil'), ('Brazil Journal','braziljournal.com','Brasil'),
]

def fetch(url):
    request = urllib.request.Request(url, headers={'User-Agent':'StockAnalyzer/2.0 (public-data research)', 'Accept':'application/json, application/xml, text/csv, */*'})
    with urllib.request.urlopen(request, timeout=25) as response:
        return response.read(5_000_000).decode('utf-8-sig')

def load_indicator(meta):
    if meta['provider'] == 'BCB':
        start = (TODAY - timedelta(days=760)).strftime('%d/%m/%Y')
        end = TODAY.strftime('%d/%m/%Y')
        url = f"https://api.bcb.gov.br/dados/serie/bcdata.sgs.{meta['code']}/dados?" + urllib.parse.urlencode(dict(formato='json', dataInicial=start, dataFinal=end))
        raw = json.loads(fetch(url))
        rows = [{'date':datetime.strptime(p['data'], '%d/%m/%Y').date().isoformat(), 'value':float(p['valor'])} for p in raw]
        source_url = f"https://www3.bcb.gov.br/sgspub/consultarvalores/consultarValoresSeries.do?method=consultarGraficoPorId&hdOidSeriesSelecionadas={meta['code']}"
    else:
        url = f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={meta['code']}&cosd={TODAY-timedelta(days=760)}&coed={TODAY}"
        records = csv.DictReader(io.StringIO(fetch(url)))
        rows = [{'date':p.get('DATE',p.get('observation_date','')), 'value':float(p[meta['code']])} for p in records if p.get(meta['code']) not in (None,'.','')]
        source_url = f"https://fred.stlouisfed.org/series/{meta['code']}"
    rows = sorted({r['date']:r for r in rows if (TODAY-timedelta(days=760)).isoformat() <= r['date'] <= TODAY.isoformat() and math.isfinite(r['value'])}.values(), key=lambda p:p['date'])
    if not rows: raise ValueError('Nenhuma observação válida disponível')
    age = (TODAY-datetime.fromisoformat(rows[-1]['date']).date()).days
    return {**meta, 'country':'Brasil' if meta['provider']=='BCB' else 'Estados Unidos', 'continent':'América do Sul' if meta['provider']=='BCB' else 'América do Norte', 'history':rows, 'value':rows[-1]['value'], 'date':rows[-1]['date'], 'sourceUrl':source_url, 'dataUrl':url, 'status':'old' if age > meta['lag'] else 'ok', 'fetchedAt':datetime.now(timezone.utc).isoformat()}

def load_news(config):
    name, domain, region = config
    query = f'site:{domain} (economia OR mercado OR juros OR bolsas)' if region == 'Brasil' else f'site:{domain} (markets OR economy OR finance)'
    query += ' when:7d'
    url = 'https://news.google.com/rss/search?' + urllib.parse.urlencode(dict(q=query, hl='pt-BR' if region=='Brasil' else 'en-US', gl='BR' if region=='Brasil' else 'US', ceid='BR:pt-419' if region=='Brasil' else 'US:en'))
    tree = ET.fromstring(fetch(url))
    items = []
    for item in tree.findall('.//item')[:10]:
        title, link = item.findtext('title','').strip(), item.findtext('link','').strip()
        source = item.find('source')
        if source is None: continue
        host = urllib.parse.urlparse(source.get('url','')).hostname or ''
        if not (host == domain or host.endswith('.'+domain)): continue
        try: date = parsedate_to_datetime(item.findtext('pubDate','')).astimezone(timezone.utc)
        except (ValueError,TypeError): continue
        if date.date() > TODAY or (TODAY-date.date()).days > 8: continue
        if urllib.parse.urlparse(link).scheme != 'https': continue
        suffix = ' - '+(source.text or '')
        if title.endswith(suffix): title = title[:-len(suffix)]
        items.append(dict(id=hashlib.sha256(link.encode()).hexdigest()[:16], title=title, url=link, source=name, region=region, country='Brasil' if region=='Brasil' else 'Global',continent='América do Sul' if region=='Brasil' else 'Global', date=date.isoformat()))
    return items

def preserve(meta, previous):
    old = next((r for r in previous if r['id']==meta['id'] and r.get('history')), None)
    return {**old, 'status':'cached'} if old else {**meta,'value':None,'date':None,'history':[],'status':'unavailable','sourceUrl':'https://www.bcb.gov.br/' if meta['provider']=='BCB' else 'https://fred.stlouisfed.org/'}

def worldbank(geography, previous):
    output=[]
    for code,name,unit in [('NY.GDP.MKTP.KD.ZG','Crescimento do PIB','% no ano'),('FP.CPI.TOTL.ZG','Inflação anual','% no ano'),('SL.UEM.TOTL.ZS','Desemprego','% da força de trabalho')]:
        url='https://api.worldbank.org/v2/country/'+ ';'.join(g[0] for g in geography)+'/indicator/'+code+'?format=json&per_page=2000&date='+str(TODAY.year-12)+':'+str(TODAY.year)
        try:
            raw=json.loads(fetch(url))[1]
            if not isinstance(raw,list): raise ValueError('Dados anuais ausentes')
        except Exception:
            raw=[]
        for iso,country,continent,_ in geography:
            meta=dict(id=f'wb-{iso}-{code}',name=name,unit=unit,group='Economia anual',country=country,continent=continent,provider='Banco Mundial',code=code,countryCode=iso,lag=900,sourceUrl=f'https://data.worldbank.org/indicator/{code}?locations={iso}',dataUrl=url,meaning='Série anual comparável do Banco Mundial. Observe o ano de referência, revisões e a definição original; não é dado em tempo real.')
            rows=sorted([dict(date=str(r['date'])+'-01-01',value=float(r['value'])) for r in raw if r.get('country',{}).get('id')==iso and r.get('value') is not None and int(r['date'])<TODAY.year],key=lambda r:r['date'])
            output.append({**meta,'history':rows,'value':rows[-1]['value'],'date':rows[-1]['date'],'status':'old' if TODAY.year-int(rows[-1]['date'][:4])>2 else 'ok','fetchedAt':datetime.now(timezone.utc).isoformat()} if rows else preserve(meta,previous))
    return output

def country_news(geo):
    iso,country,continent,english=geo
    query=f'"{english}" (economy OR inflation OR stocks OR interest rates) when:7d'
    url='https://news.google.com/rss/search?'+urllib.parse.urlencode(dict(q=query,hl='en-US',gl='US',ceid='US:en'))
    items=[]
    for item in ET.fromstring(fetch(url)).findall('.//item')[:6]:
        try: published=parsedate_to_datetime(item.findtext('pubDate','')).astimezone(timezone.utc)
        except (ValueError,TypeError): continue
        link=item.findtext('link','');title=item.findtext('title','');source=item.findtext('source','Fonte não informada')
        if published.date()>TODAY or (TODAY-published.date()).days>8 or not link.startswith('https://'):continue
        if title.endswith(' - '+source):title=title[:-len(' - '+source)]
        items.append(dict(id=hashlib.sha256((link+iso).encode()).hexdigest()[:16],title=title,url=link,source=source,country=country,continent=continent,region=continent,date=published.isoformat()))
    return items

def collect():
    previous = {}
    for file in [CACHE,OUT]:
        try: previous = json.loads(file.read_text(encoding='utf-8')); break
        except (OSError,ValueError): pass
    def safe_indicator(meta):
        try: return load_indicator(meta)
        except Exception as error:
            print(f"Indicador {meta['id']}: {type(error).__name__}; preservar último dado")
            return preserve(meta,previous.get('indicators',[]))
    def safe_news(config):
        try: return {'source':config[0],'status':'ok','items':load_news(config)}
        except Exception as error:
            print(f"Notícias {config[0]}: {type(error).__name__}")
            old = [n for n in previous.get('news',[]) if n['source']==config[0] and (TODAY-datetime.fromisoformat(n['date']).date()).days <= 8]
            return {'source':config[0],'status':'cached' if old else 'unavailable','items':old}
    with ThreadPoolExecutor(max_workers=4) as pool: indicators = list(pool.map(safe_indicator,INDICATORS))
    # Derived inflation uses compounded monthly changes, not their sum.
    for parent in ['ipca','igpm','inpc']:
        base = next(r for r in indicators if r['id']==parent)
        history = base['history']
        derived = []
        for i in range(11,len(history)):
            window = history[i-11:i+1]
            ordinals = [int(r['date'][:4])*12+int(r['date'][5:7]) for r in window]
            if all(b-a==1 for a,b in zip(ordinals,ordinals[1:])):
                derived.append({'date':window[-1]['date'],'value':(math.prod(1+r['value']/100 for r in window)-1)*100})
        indicators.append({**base,'id':parent+'12','name':parent.upper().replace('IGPM','IGP-M')+' · 12 meses','unit':'% em 12 meses','history':derived,'value':derived[-1]['value'] if derived else None,'date':derived[-1]['date'] if derived else None,'status':base['status'] if derived else 'unavailable','meaning':'Acumulado calculado pelo produto das 12 variações mensais consecutivas. Fonte original: '+base['provider']+'.'})
    geography=json.loads((ROOT/'scripts/geography.json').read_text(encoding='utf-8'))
    indicators.extend(worldbank(geography,previous.get('indicators',[])))
    with ThreadPoolExecutor(max_workers=4) as pool: feeds = list(pool.map(safe_news,NEWS))
    def safe_country(geo):
        try:return {'source':geo[1],'status':'ok','items':country_news(geo)}
        except Exception:return {'source':geo[1],'status':'unavailable','items':[n for n in previous.get('news',[]) if n.get('country')==geo[1] and (TODAY-datetime.fromisoformat(n['date']).date()).days<=8]}
    with ThreadPoolExecutor(max_workers=4) as pool: feeds.extend(list(pool.map(safe_country,geography)))
    news = sorted({n['id']:n for feed in feeds for n in feed['items']}.values(),key=lambda n:n['date'],reverse=True)
    snapshot = dict(updatedAt=datetime.now(timezone.utc).isoformat(), indicators=indicators, news=news, newsStatus=[{k:v for k,v in f.items() if k!='items'} for f in feeds], geography=geography,scheduleHours=3)
    # The publication must have at least some validated official observations.
    if not any(r['status'] in ('ok','old') for r in indicators): raise RuntimeError('Nenhuma coleta oficial válida: publicação anterior preservada.')
    for file in [OUT,CACHE]:
        file.parent.mkdir(parents=True,exist_ok=True)
        file.write_text(json.dumps(snapshot,ensure_ascii=False,allow_nan=False),encoding='utf-8')
    print(json.dumps({'indicators':len(indicators),'available':sum(r['value'] is not None for r in indicators),'news':len(news),'status':{r['id']:r['status'] for r in indicators}},ensure_ascii=False))
    return snapshot

if __name__ == '__main__': collect()
