import requests
import time
import csv
import urllib3
import statistics

urllib3.disable_warnings()

URL = "https://localhost/arquivo.txt"

perda = input("Informe a porcentagem de perda (0, 1, 5): ")

arquivo = f"../results/http3_{perda}.csv"

tempos = []

with open(arquivo, "w", newline="") as file:

    writer = csv.writer(file)

    writer.writerow(["teste", "tempo_ms"])

    for i in range(100):

        inicio = time.time()

        r = requests.get(URL, verify=False)

        fim = time.time()

        tempo_ms = (fim - inicio) * 1000

        tempos.append(tempo_ms)

        writer.writerow([i + 1, tempo_ms])

        print(f"Teste {i+1}: {tempo_ms:.2f} ms")

media = sum(tempos) / len(tempos)

desvio = statistics.stdev(tempos)

print(f"\nMédia: {media:.2f} ms")

print(f"Desvio padrão: {desvio:.2f} ms")

print(f"\nResultados salvos em: {arquivo}")
