"""Optional local Yahoo Finance connector. No shared API keys or recommendations."""
from datetime import datetime, timezone
from typing import Literal
import math
import os
import re
import threading
import time
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import yfinance as yf
from radar_metrics import summarize, finite

app=FastAPI(title='Stock Analyzer · conector pessoal',version='2.0.0')
app.add_middleware(CORSMiddleware,allow_origins=os.getenv('ALLOWED_ORIGINS','http://localhost:5173,http://127.0.0.1:5173').split(','),allow_credentials=False,allow_methods=['GET'],allow_headers=['Content-Type'])
cache={}
lock=threading.Lock()
limit=threading.BoundedSemaphore(4)

def validate_ticker(ticker):
    value=ticker.strip().upper()
    if not re.fullmatch(r'[A-Z0-9^][A-Z0-9.^=\-]{0,19}',value):
        raise HTTPException(422,'Código de ativo inválido.')
    if re.fullmatch(r'[A-Z]{4}\d{1,2}',value):value+='.SA'
    return value

def normalize_history(frame):
    rows=[]
    for index,row in frame.iterrows():
        close=float(row['Close'])
        day=index.date()
        if math.isfinite(close) and close>0 and day<=datetime.now(timezone.utc).date():
            rows.append({'date':day.isoformat(),'close':close})
    return sorted({r['date']:r for r in rows}.values(),key=lambda r:r['date'])

@app.get('/api/health')
def health():return {'status':'ok','version':'2.0.0','mode':'personal-research','recommendations':False}

@app.get('/api/stocks/history')
def history(ticker:str=Query(min_length=1,max_length=20),period:Literal['3mo','6mo','1y','2y','5y']='1y'):
    symbol=validate_ticker(ticker)
    key=(symbol,period)
    with lock:
        saved=cache.get(key)
        if saved and time.monotonic()-saved[0]<900:return saved[1]
    if not limit.acquire(blocking=False):raise HTTPException(429,'Muitas consultas simultâneas. Aguarde e tente novamente.')
    try:
        asset=yf.Ticker(symbol)
        frame=asset.history(period=period,auto_adjust=True,timeout=20,raise_errors=True)
        rows=normalize_history(frame)
        if len(rows)<3:raise HTTPException(404,'Ativo sem histórico suficiente na fonte.')
        metadata=asset.history_metadata or {}
        currency=metadata.get('currency')
        if not currency:raise HTTPException(502,'Moeda não informada pela fonte; comparação indisponível.')
        result={'symbol':symbol,'currency':currency,'history':rows,'asOf':rows[-1]['date'],'fetchedAt':datetime.now(timezone.utc).isoformat(),'source':'Yahoo Finance via yfinance','adjusted':True,'notice':'Uso pessoal e educativo. Preços ajustados; sem indicação de investimento ou garantia.'}
        with lock:
            if len(cache)>100:cache.clear()
            cache[key]=(time.monotonic(),result)
        return result
    except HTTPException:raise
    except Exception:raise HTTPException(502,'Yahoo indisponível, sem permissão ou sem dados. Nenhum preço foi estimado.')
    finally:limit.release()

@app.get('/api/stocks/search')
def search(q:str=Query(min_length=1,max_length=50)):
    if not limit.acquire(blocking=False):raise HTTPException(429,'Aguarde e tente novamente.')
    try:
        results=yf.Search(q,max_results=12,news_count=0,timeout=15).quotes
        return {'results':[{'symbol':r.get('symbol'),'name':r.get('shortname') or r.get('longname') or r.get('symbol'),'type':r.get('quoteType'),'exchange':r.get('exchange')} for r in results if r.get('symbol')]}
    except Exception:raise HTTPException(502,'Busca na fonte indisponível.')
    finally:limit.release()

@app.get('/api/assets/radar')
def asset_radar(ticker:str=Query(min_length=1,max_length=20)):
    symbol=validate_ticker(ticker)
    key=('radar',symbol)
    with lock:
        saved=cache.get(key)
        if saved and time.monotonic()-saved[0]<900:return saved[1]
    if not limit.acquire(blocking=False):raise HTTPException(429,'Aguarde antes de consultar outro ativo.')
    try:
        asset=yf.Ticker(symbol)
        adjusted=asset.history(period='10y',auto_adjust=True,timeout=20,raise_errors=True)
        rows=normalize_history(adjusted)
        if len(rows)<3:raise HTTPException(404,'Sem histórico suficiente na fonte.')
        raw=asset.history(period='1y',auto_adjust=False,actions=True,timeout=20,raise_errors=True)
        spot=finite(raw['Close'].iloc[-1]) if not raw.empty else None
        payments=[]
        if 'Dividends' in raw.columns:
            for index,row in raw.iterrows():
                amount=finite(row['Dividends'])
                if amount is not None and amount>0:
                    payments.append({'date':index.date().isoformat(),'amount':amount})
        try:info=asset.info or {}
        except Exception:info={}
        metadata=asset.history_metadata or {}
        currency=info.get('currency') or metadata.get('currency')
        if not currency:raise HTTPException(502,'Moeda não confirmada pela fonte.')
        types={'EQUITY':'Ação','ETF':'ETF','MUTUALFUND':'Fundo de investimento','CRYPTOCURRENCY':'Cripto','INDEX':'Índice','CURRENCY':'Câmbio','FUTURE':'Derivativo'}
        kind=types.get(info.get('quoteType'),'Classe não identificada')
        if info.get('industry','').startswith('REIT') or re.fullmatch(r'[A-Z]{4}11\.SA',symbol) and 'FII' in info.get('longName','').upper():kind='FII / REIT'
        result={'symbol':symbol,'name':info.get('longName') or symbol,'type':kind,'currency':currency,
                'source':'Yahoo Finance via yfinance · pesquisa pessoal','url':'https://finance.yahoo.com/quote/'+symbol+'/',
                'fetchedAt':datetime.now(timezone.utc).isoformat(),**summarize(rows,payments,spot,info)}
        with lock:
            if len(cache)>100:cache.clear()
            cache[key]=(time.monotonic(),result)
        return result
    except HTTPException:raise
    except Exception:raise HTTPException(502,'Fonte indisponível. Nenhum retorno, provento ou alvo foi estimado.')
    finally:limit.release()
