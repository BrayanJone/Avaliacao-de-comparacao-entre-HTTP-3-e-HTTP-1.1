# Avaliação de comparação entre HTTP/3 e HTTP/1.1

Este projeto realiza experimentos comparativos entre os protocolos HTTP/1.1 e HTTP/3, analisando métricas de desempenho — tempo de download, vazão (throughput) e variabilidade dos resultados — em diferentes condições de rede simuladas.

## Tecnologias utilizadas

- **Python** — cliente HTTP/1.1 (biblioteca `requests`, com conexão persistente) e cliente HTTP/3 (biblioteca `aioquic`)
- **Docker / Docker Compose** — ambiente isolado de experimentação
- **Caddy** — servidor com suporte a HTTP/1.1 (porta 8443) e HTTP/3 (porta 443), com TLS via certificado interno
- **tc/netem** — simulação de latência e perda de pacotes
- **Pandas / Matplotlib** — consolidação dos resultados e geração dos gráficos comparativos

## Metodologia

Foram simulados downloads de 5 "livros digitais" com tamanhos diferentes (aproximadamente 500KB, 1MB, 2MB, 3MB e 5MB). Em cada cenário, os 5 livros foram baixados em sequência, e esse ciclo foi repetido 10 vezes por protocolo (50 downloads por protocolo, por cenário).

Foram testados 3 cenários de rede, todos com **100ms de latência artificial** (via tc/netem), variando apenas a taxa de perda de pacotes:

| Cenário | Latência | Perda de pacotes |
|---|---|---|
| 1 | 100ms | 0% |
| 2 | 100ms | 3% |
| 3 | 100ms | 5% |

A degradação de rede foi aplicada no lado do servidor (não do cliente), já que é o lado que envia o volume principal de dados (o conteúdo dos livros).

## Métricas coletadas

- **Tempo total de download** por requisição
- **Vazão** (throughput, em KB/s)
- **Desvio padrão do tempo** entre as repetições, como indicador de consistência/variabilidade

## Limitações

Os testes foram realizados em ambiente local (Docker, comunicação entre containers via rede bridge), com degradação artificial de rede via tc/netem. Os resultados não representam completamente o comportamento dos protocolos em redes reais da Internet, onde fatores como congestionamento, roteamento, variabilidade de caminho e distância física influenciam significativamente o desempenho.

Além disso, os clientes não aplicam timeout curto às requisições — portanto todas as requisições eventualmente completaram em todos os cenários, mesmo sob perda. A taxa de sucesso não foi utilizada como métrica de comparação; o impacto da perda de pacotes se manifesta inteiramente no tempo de resposta, não na confiabilidade binária das requisições.

## Estrutura do projeto
Trabalho-HTTP3/
├── scripts/
│   ├── http1_bench.py       # cliente HTTP/1.1
│   └── http3_bench.py       # cliente HTTP/3
├── plot_results.py          # geração dos gráficos comparativos
├── resultados/               # CSVs e gráficos gerados pelos experimentos
└── Docker/
├── docker-compose.yml
├── Caddyfile
├── Dockerfile.server     # imagem do Caddy + tc (iproute2)
├── Dockerfile.client     # imagem Python + requests + aioquic + pandas/matplotlib
├── run_experiment.sh     # automatiza os 3 cenários
└── livros/               # arquivos servidos pelo Caddy

## Como executar

```bash
cd Docker
docker-compose up -d --build

# roda os 3 cenários (0%, 3%, 5% de perda, 100ms de latência, 10 repetições)
bash run_experiment.sh

# gera os gráficos comparativos
docker exec -it cliente-http python3 /app/plot_results.py --dir /app/resultados
```

## Autor

Brayan Jone B. Jaques — 1901580327

## Links

- Relatório completo: https://docs.google.com/document/d/1Osy52BX9crNQW1EfWQt2YfBqsRDn9RI_DxpvgpAc2L8/edit?tab=t.0
- Repositório: https://github.com/BrayanJone/Avaliacao-de-comparacao-entre-HTTP-3-e-HTTP-1.1
