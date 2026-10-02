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
python -m unittest discover -s tests -p test_collector.py
npm run lint --prefix frontend
npm run build --prefix frontend
```

## GitHub Pages

Em Settings → Pages, selecione GitHub Actions. O workflow publica ao enviar para main, permite execução manual e coleta novas edições a cada três horas. Agendamentos dependem da disponibilidade do GitHub Actions e podem atrasar. A interface oferece atualização manual e automática; restrições de rede/CORS podem impedir atualização direta e a edição anterior permanece visível.

## Limites

Rentabilidade passada e erros medidos em testes não garantem desempenho futuro. Notícias podem exigir assinatura para leitura integral. Valores de planos pagos são referências datadas: confirme no site oficial. Favoritos e configurações ficam no navegador. Nunca envie credenciais ou dados pessoais para este repositório.
