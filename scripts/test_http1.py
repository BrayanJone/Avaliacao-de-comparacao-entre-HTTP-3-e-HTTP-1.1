import requests
import time
import csv
import statistics

URL = "http://localhost:8000/arquivo.txt"

perda = input("Informe a porcentagem de perda (0, 1, 5): ")

arquivo = f"../results/http1_{perda}.csv"

tempos = []

with open(arquivo, "w", newline="") as file:

    writer = csv.writer(file)

    writer.writerow(["teste", "tempo_ms"])

    for i in range (100):

        inicio = time.time()

        r = requests.get(URL)

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

