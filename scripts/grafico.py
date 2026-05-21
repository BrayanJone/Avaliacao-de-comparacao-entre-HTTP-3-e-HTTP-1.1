import pandas as pd
import matplotlib.pyplot as plt

# =========================
# Leitura dos arquivos
# =========================

http1_0 = pd.read_csv("../results/http1_0.csv")
http1_3 = pd.read_csv("../results/http1_3.csv")
http1_7 = pd.read_csv("../results/http1_7.csv")

http3_0 = pd.read_csv("../results/http3_0.csv")
http3_3 = pd.read_csv("../results/http3_3.csv")
http3_7 = pd.read_csv("../results/http3_7.csv")

# =========================
# Médias gerais
# =========================

medias_http1 = [
    http1_0["tempo_ms"].mean(),
    http1_3["tempo_ms"].mean(),
    http1_7["tempo_ms"].mean()
]

medias_http3 = [
    http3_0["tempo_ms"].mean(),
    http3_3["tempo_ms"].mean(),
    http3_7["tempo_ms"].mean()
]

cenarios = ["0%", "3%", "7%"]

# =========================
# Gráfico 1
# =========================

plt.figure(figsize=(8,5))

plt.plot(cenarios, medias_http1, marker='o', label="HTTP/1.1")
plt.plot(cenarios, medias_http3, marker='o', label="HTTP/3")

plt.title("Comparação entre HTTP/1.1 e HTTP/3")
plt.xlabel("Perda de Pacotes")
plt.ylabel("Tempo Médio (ms)")
plt.legend()

plt.grid(True)

plt.savefig("../results/grafico_geral.png")

# =========================
# Médias por livro
# =========================

livros_http1 = http1_3.groupby("livro")["tempo_ms"].mean()
livros_http3 = http3_3.groupby("livro")["tempo_ms"].mean()

# =========================
# Gráfico 2
# =========================

plt.figure(figsize=(10,5))

plt.plot(livros_http1.index, livros_http1.values,
         marker='o', label="HTTP/1.1")

plt.plot(livros_http3.index, livros_http3.values,
         marker='o', label="HTTP/3")

plt.title("Tempo médio por livro (3% perda)")
plt.xlabel("Livros")
plt.ylabel("Tempo Médio (ms)")
plt.legend()

plt.grid(True)

plt.savefig("../results/grafico_livros.png")

print("Gráficos salvos em results/")
