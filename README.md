# Stock Analyzer

Painel de pesquisa e educação financeira em português. Não constitui indicação de investimento nem garantia de retorno.

## Recursos

- Indicadores do Banco Central, FRED e Banco Mundial, com fonte, data e histórico; 99 séries em 28 países na configuração inicial.
- Filtros por país e continente, notícias com links para os veículos e favoritos locais.
- Trilhas para iniciantes, intermediários e avançados, planejamento de 12 objetivos e simulação com inflação, custos e impostos.
- Importação de CSV, comparação de rentabilidade histórica na mesma moeda e período, projeções com validação cronológica e gráficos.
- Diretório de fontes gratuitas e opções pagas informativas; nenhuma assinatura é feita pelo projeto.

## Executar

Requer Node.js 22.12+ e Python 3.11+.

```sh
python scripts/collect.py
cd frontend
npm ci
npm run dev
```

A coleta usa apenas a biblioteca padrão do Python. Falhas preservam dados anteriores quando disponíveis. Verifique a data de referência: dados anuais não são cotações atuais.

## Conector pessoal opcional

```sh
python -m venv .venv
# Ative o ambiente virtual conforme seu sistema
pip install -r backend/requirements.txt
cd backend
uvicorn main:app --host 127.0.0.1 --port 8000
```

Yahoo Finance via yfinance serve à pesquisa pessoal, sujeito às condições do fornecedor. O conector não é hospedado pelo GitHub Pages; a versão pública permite análise de CSV e acesso às fontes externas.

## Verificação

```sh
node --test tests/*.test.mjs
python -m unittest discover -s tests -p 'test_*.py'
npm run lint --prefix frontend
npm run build --prefix frontend
```

## GitHub Pages

Em Settings → Pages, selecione GitHub Actions. O workflow publica ao enviar para main, permite execução manual e coleta novas edições a cada três horas. Agendamentos dependem da disponibilidade do GitHub Actions e podem atrasar. A interface oferece atualização manual e automática; restrições de rede/CORS podem impedir atualização direta e a edição anterior permanece visível.

## Limites

Rentabilidade passada e erros medidos em testes não garantem desempenho futuro. Notícias podem exigir assinatura para leitura integral. Valores de planos pagos são referências datadas: confirme no site oficial. Favoritos e configurações ficam no navegador. Nunca envie credenciais ou dados pessoais para este repositório.

## Radar de ativos e finalidade educativa

O radar distingue histórico, distribuições e opiniões atribuídas. Tem 21 referências de ativos e famílias de produtos, critérios por 12 classes e rankings separados por classe, moeda, referência e metodologia. Famílias como debêntures e FIP são referências educativas, sem código de consulta automática. Não cobre todos os produtos existentes e não indica melhores investimentos.

Para consultar outros ativos com dados pessoais Yahoo, configure frontend/.env.local com VITE_API_URL=http://127.0.0.1:8000 e reinicie o frontend. O endpoint GET /api/assets/radar?ticker=SCHD aceita um ativo por consulta, usa cache de 15 minutos e preserva indisponibilidade. A aba local atualiza os ativos consultados a cada 15 minutos. A edição pública não redistribui essa coleta. Fundos privados e títulos individuais dependem de documentos próprios; nenhuma taxa é inventada.

Retorno de um ano é acumulado; 3 e 5 anos são anualizados. O histórico ajustado não recebe dividendos novamente. A distribuição de 12 meses dividida pelo fechamento bruto é histórica e não equivale ao SEC yield ou a um rendimento futuro. Preços-alvo agregados sem data de referência são explicitamente marcados como não confirmados; suas justificativas não são inventadas.

Referências editoriais consultadas em 03/10/2026, com suas próprias datas: Schwab/SCHD, Vanguard, RI dos emissores, Reuters via Schwab, LSEG e Banco Mundial. Elas precisam de revisão editorial; não se atualizam automaticamente como indicadores e manchetes.

