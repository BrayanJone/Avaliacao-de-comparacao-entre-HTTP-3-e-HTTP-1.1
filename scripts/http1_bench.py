"""
http1_bench.py — Cliente HTTP/1.1 para benchmarking, no MESMO formato de
saída do http3_bench.py (pra facilitar comparar/plotar os dois depois).

Correções em relação ao test_http1.py original:
  - reaproveita UMA única conexão TCP/TLS (requests.Session) para toda a
    rodada (20 repetições x 5 livros), igual o http3_bench.py faz com a
    conexão QUIC — sem isso a comparação fica injusta, porque o HTTP/1.1
    pagaria handshake TLS 100x e o HTTP/3 só 1x.
  - usa o tamanho REAL do conteúdo baixado (len(r.content)) em vez de uma
    tabela de tamanhos fixa.
  - tem timeout e trata falhas de requisição sem derrubar o experimento
    inteiro (essencial nos cenários de 3%/7% de perda).
  - usa statistics.pstdev (igual o http3_bench.py) para manter os dois
    scripts consistentes entre si.

Uso:
  python http1_bench.py --host servidor --port 8443 \
      --books livro1.txt livro2.txt livro3.txt livro4.txt livro5.txt \
      --repeats 20 --output resultados_http1.csv
"""

import argparse
import csv
import statistics
import time

import requests
import urllib3

urllib3.disable_warnings()


def run_benchmark(host, port, books, repeats, timeout, output_csv):
    results = []
    session = requests.Session()

    for i in range(1, repeats + 1):
        for book in books:
            url = f"https://{host}:{port}/livros/{book}"
            start = time.perf_counter()
            try:
                r = session.get(url, verify=False, timeout=timeout)
                r.raise_for_status()
                elapsed = time.perf_counter() - start
                size_bytes = len(r.content)
                throughput = size_bytes / elapsed if elapsed > 0 else 0
                results.append(
                    {
                        "repeticao": i,
                        "livro": book,
                        "sucesso": True,
                        "tempo_s": elapsed,
                        "tamanho_bytes": size_bytes,
                        "vazao_Bps": throughput,
                    }
                )
                print(
                    f"[{i:02d}] {book}: {elapsed:.4f}s  "
                    f"{size_bytes/1024:.1f}KB  {throughput/1024:.1f}KB/s"
                )
            except requests.exceptions.RequestException as exc:
                elapsed = time.perf_counter() - start
                print(f"[{i:02d}] {book}: FALHOU ({exc})")
                results.append(
                    {
                        "repeticao": i,
                        "livro": book,
                        "sucesso": False,
                        "tempo_s": elapsed,
                        "tamanho_bytes": 0,
                        "vazao_Bps": 0,
                    }
                )

    session.close()

    with open(output_csv, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=results[0].keys())
        writer.writeheader()
        writer.writerows(results)

    sucesso = [r for r in results if r["sucesso"]]
    if sucesso:
        tempos = [r["tempo_s"] for r in sucesso]
        vazoes = [r["vazao_Bps"] for r in sucesso]
        print("\n--- Estatísticas gerais (HTTP/1.1) ---")
        print(f"Requisições com sucesso: {len(sucesso)}/{len(results)}")
        print(f"Tempo médio: {statistics.mean(tempos):.4f}s")
        print(f"Desvio padrão do tempo: {statistics.pstdev(tempos):.4f}s")
        print(f"Vazão média: {statistics.mean(vazoes)/1024:.2f} KB/s")
    else:
        print("\nNenhuma requisição teve sucesso.")


def main():
    parser = argparse.ArgumentParser(description="Benchmark de cliente HTTP/1.1")
    parser.add_argument("--host", default="servidor")
    parser.add_argument("--port", type=int, default=8443)
    parser.add_argument(
        "--books",
        nargs="+",
        default=["livro1.txt", "livro2.txt", "livro3.txt", "livro4.txt", "livro5.txt"],
    )
    parser.add_argument("--repeats", type=int, default=20)
    parser.add_argument("--timeout", type=float, default=15.0, help="timeout por requisição, em segundos")
    parser.add_argument("--output", default="resultados_http1.csv")
    args = parser.parse_args()

    run_benchmark(args.host, args.port, args.books, args.repeats, args.timeout, args.output)


if __name__ == "__main__":
    main()
