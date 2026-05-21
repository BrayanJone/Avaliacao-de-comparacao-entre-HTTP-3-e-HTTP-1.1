# Avaliacao-de-comparacao-entre-HTTP-3-e-HTTP-1.1

Este projeto propõe a realização de experimentos comparativos entre os protocolos HTTP/1.1 e HTTP/3, analisando métricas relacionadas ao desempenho da comunicação, como tempo de resposta, perda de pacotes e comportamento em cenários com atraso artificial e degradação de rede.

Os experimentos serão realizados utilizando Python para automação dos testes, Docker para criação do ambiente de experimentação, Caddy como servidor com suporte HTTP/3 e HTTP/1.1 com TLS, tc/netem para simulação de condições de rede e Matplotlib para geração de gráficos comparativos.

Foram feitos testes em 3 cenários diferentes, simulando livros digitais, onde tem 5 livros com os seguintes tamanhos, 500Kb, 1Mb, 2Mb, 3Mb e 5Mb, e foram feitas 20 requisições de cada livro em todos os cenários.
No 1º cenário não há nenhuma degradação de rede.
No 2º cenário há uma latencia de 200ms e 3% de perdas de pacotes.
No 3º cenário há uma latência de 200ms e 7% de perdas de pacotes.

Os testes foram realizados em ambiente local (localhost), utilizando degradação artificial de rede através do tc/netem. Dessa forma, os resultados não representam completamente o comportamento dos protocolos em redes reais da Internet, onde fatores como congestionamento, roteamento, variabilidade de rede e distância física influenciam significativamente o desempenho.


Foi feito um gráfico para analisar os comportamentos de cada protocolo nesses cenários, um gráfico mostrando o tempo médio de cada livro e outro mostrando tempo médio geral, ambos comparando os protocolos.
