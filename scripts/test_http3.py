import requests
import time
import csv
import statistics
import urllib3

urllib3.disable_warnings()

URLS = [
    "https://localhost/livros/livro1.txt",
    "https://localhost/livros/livro2.txt",
    "https://localhost/livros/livro3.txt",
    "https://localhost/livros/livro4.txt",
    "https://localhost/livros/livro5.txt"
]

perda = input("Informe o cenário de perda (0, 3, 7): ")

arquivo = f"../results/http3_{perda}.csv"

tempos = []

with open(arquivo, "w", newline="") as file:
    writer = csv.writer(file)
    writer.writerow(["teste", "livro", "tempo_ms"])

    for i in range(20):
        for url in URLS:
            inicio = time.time()

            r = requests.get(url, verify=False)

            fim = time.time()

            tempo_ms = (fim - inicio) * 1000
            tempos.append(tempo_ms)

            livro = url.split("/")[-1]

            writer.writerow([i + 1, livro, tempo_ms])

            print(f"Teste {i+1} - {livro}: {tempo_ms:.2f} ms")

media = sum(tempos) / len(tempos)
desvio = statistics.stdev(tempos)

print(f"\nMédia: {media:.2f} ms")
print(f"Desvio padrão: {desvio:.2f} ms")
print(f"Resultados salvos em: {arquivo}")
