// Discovery catalog only: no stored prices, yields or buy/sell rankings.
const br=(s,n,t='Ação')=>({symbol:s+'.SA',tv:'BMFBOVESPA:'+s,name:n,type:t,country:'Brasil',continent:'América do Sul',currency:'BRL'});
const us=(s,n,t='Ação',exchange='NASDAQ')=>({symbol:s,tv:exchange+':'+s,name:n,type:t,country:'Estados Unidos',continent:'América do Norte',currency:'USD'});
export const ASSETS=[br('PETR4','Petrobras'),br('VALE3','Vale'),br('ITUB4','Itaú Unibanco'),br('BBDC4','Bradesco'),br('BBAS3','Banco do Brasil'),br('WEGE3','WEG'),br('ABEV3','Ambev'),br('MGLU3','Magazine Luiza'),br('RENT3','Localiza'),br('SUZB3','Suzano'),br('B3SA3','B3'),br('BPAC11','BTG Pactual'),br('BBSE3','BB Seguridade'),br('BOVA11','iShares Ibovespa','ETF'),br('IVVB11','iShares S&P 500','ETF'),br('SMAL11','iShares Small Cap','ETF'),br('WRLD11','Investo Global','ETF'),br('DIVO11','It Now IDIV','ETF'),br('GOLD11','Trend Ouro','ETF'),br('HASH11','Hashdex Cripto','ETF'),br('LFTS11','Investo Tesouro Selic','ETF'),br('IMAB11','It Now IMA-B','ETF'),br('HGLG11','FII Logística','FII'),br('KNRI11','FII Kinea Renda Imobiliária','FII'),br('MXRF11','FII Maxi Renda','FII'),br('XPML11','FII XP Malls','FII'),us('AAPL','Apple'),us('MSFT','Microsoft'),us('NVDA','NVIDIA'),us('AMZN','Amazon'),us('GOOGL','Alphabet'),us('META','Meta Platforms'),us('TSLA','Tesla'),us('JPM','JPMorgan Chase','Ação','NYSE'),us('BAC','Bank of America','Ação','NYSE'),us('XOM','Exxon Mobil','Ação','NYSE'),us('KO','Coca-Cola','Ação','NYSE'),us('SPY','SPDR S&P 500','ETF','AMEX'),us('VOO','Vanguard S&P 500','ETF','AMEX'),us('VTI','Vanguard Total Stock Market','ETF','AMEX'),us('QQQ','Invesco Nasdaq 100','ETF'),us('VXUS','Vanguard Total International','ETF'),us('BND','Vanguard Total Bond Market','ETF'),us('GLD','SPDR Gold Shares','ETF','AMEX'),us('TLT','iShares 20+ Year Treasury','ETF'),
 {symbol:'BTC-USD',tv:'COINBASE:BTCUSD',name:'Bitcoin',type:'Cripto',country:'Global',continent:'Global',currency:'USD'},
 {symbol:'ETH-USD',tv:'COINBASE:ETHUSD',name:'Ethereum',type:'Cripto',country:'Global',continent:'Global',currency:'USD'},
 {symbol:'^BVSP',tv:'BMFBOVESPA:IBOV',name:'Ibovespa',type:'Índice',country:'Brasil',continent:'América do Sul',currency:'BRL'},
 {symbol:'^GSPC',tv:'SP:SPX',name:'S&P 500',type:'Índice',country:'Estados Unidos',continent:'América do Norte',currency:'USD'},
 {symbol:'^IXIC',tv:'NASDAQ:IXIC',name:'Nasdaq Composite',type:'Índice',country:'Estados Unidos',continent:'América do Norte',currency:'USD'},
 {symbol:'^DJI',tv:'DJ:DJI',name:'Dow Jones',type:'Índice',country:'Estados Unidos',continent:'América do Norte',currency:'USD'},
 {symbol:'^FTSE',tv:'TVC:UKX',name:'FTSE 100',type:'Índice',country:'Reino Unido',continent:'Europa',currency:'GBP'},
 {symbol:'^GDAXI',tv:'XETR:DAX',name:'DAX',type:'Índice',country:'Alemanha',continent:'Europa',currency:'EUR'},
 {symbol:'^N225',tv:'TVC:NI225',name:'Nikkei 225',type:'Índice',country:'Japão',continent:'Ásia',currency:'JPY'},
 {symbol:'^AXJO',tv:'ASX:XJO',name:'S&P/ASX 200',type:'Índice',country:'Austrália',continent:'Oceania',currency:'AUD'},
 {symbol:'SAP.DE',tv:'XETR:SAP',name:'SAP',type:'Ação',country:'Alemanha',continent:'Europa',currency:'EUR'},
 {symbol:'7203.T',tv:'TSE:7203',name:'Toyota',type:'Ação',country:'Japão',continent:'Ásia',currency:'JPY'},
 {symbol:'BHP.AX',tv:'ASX:BHP',name:'BHP',type:'Ação',country:'Austrália',continent:'Oceania',currency:'AUD'},
 {symbol:'NPN.JO',tv:'JSE:NPN',name:'Naspers',type:'Ação',country:'África do Sul',continent:'África',currency:'ZAR'},
];
