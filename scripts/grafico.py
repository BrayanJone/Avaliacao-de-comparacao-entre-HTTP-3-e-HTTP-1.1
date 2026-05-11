import pandas as pd
import matplotlib.pyplot as plt

http1_0 = pd.read_csv("../results/http1_0.csv")
http1_1 = pd.read_csv("../results/http1_1.csv")
http1_5 = pd.read_csv("../results/http1_5.csv")

http3_0 = pd.read_csv("../results/http3_0.csv")
http3_1 = pd.read_csv("../results/http3_1.csv")
http3_5 = pd.read_csv("../results/http3_5.csv")

medias_http1 = [
    http1_0["tempo_ms"].mean(),
    http1_1["tempo_ms"].mean(),
    http1_5["tempo_ms"].mean()
]

medias_http3 = [
    http3_0["tempo_ms"].mean(),
    http3_1["tempo_ms"].mean(),
    http3_5["tempo_ms"].mean()
]

cenarios = ["0%", "1%", "5%"]

plt.figure(figsize=(8,5))

plt.plot(cenarios, medias_http1, marker='o', label="HTTP/1.1")

plt.plot(cenarios, medias_http3, marker='o', label="HTTP/3")

plt.xlabel("Perda de Pacotes")

plt.ylabel("Tempo Médio (ms)")

plt.title("HTTP/1.1 vs HTTP/3")

plt.legend()

plt.grid(True)

plt.savefig("../results/comparacao.png")

plt.show()
