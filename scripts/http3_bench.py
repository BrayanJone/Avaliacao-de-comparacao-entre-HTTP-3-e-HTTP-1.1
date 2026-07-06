"""
http3_bench.py — Cliente HTTP/3 para benchmarking (baseado no exemplo oficial do aioquic:
https://github.com/aiortc/aioquic/blob/main/examples/http3_client.py)

Baixa uma lista de "livros" (arquivos) em sequência, N vezes, e registra:
  - tempo de download de cada arquivo
  - tamanho em bytes
  - vazão (throughput)
  - TTFB (time to first byte) - opcional, útil pra ver o impacto do handshake QUIC sob perda

Uso:
  python http3_bench.py --host caddy --port 443 \
      --books livro1.pdf livro2.pdf livro3.pdf livro4.pdf livro5.pdf \
      --repeats 20 --insecure --output resultados_http3.csv
"""

import argparse
import asyncio
import csv
import ssl
import statistics
import time
from collections import deque
from typing import Deque, Dict, List, cast
from urllib.parse import urlparse

from aioquic.asyncio.client import connect
from aioquic.asyncio.protocol import QuicConnectionProtocol
from aioquic.h3.connection import H3_ALPN, H3Connection
from aioquic.h3.events import DataReceived, H3Event, HeadersReceived
from aioquic.quic.configuration import QuicConfiguration


class HttpClient(QuicConnectionProtocol):
    """Cliente HTTP/3 mínimo em cima do QuicConnectionProtocol do aioquic."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._http = H3Connection(self._quic)
        self._request_events: Dict[int, Deque[H3Event]] = {}
        self._request_waiter: Dict[int, asyncio.Future] = {}
        self._ttfb: Dict[int, float] = {}
        self._start_time: Dict[int, float] = {}

    async def get(self, url: str):
        parsed = urlparse(url)
        stream_id = self._quic.get_next_available_stream_id()
        headers = [
            (b":method", b"GET"),
            (b":scheme", b"https"),
            (b":authority", parsed.netloc.encode()),
            (b":path", (parsed.path or "/").encode()),
        ]

        waiter = self._loop.create_future()
        self._request_events[stream_id] = deque()
        self._request_waiter[stream_id] = waiter
        self._start_time[stream_id] = time.perf_counter()

        self._http.send_headers(stream_id=stream_id, headers=headers, end_stream=True)
        self.transmit()

        body = await asyncio.shield(waiter)
        ttfb = self._ttfb.pop(stream_id, None)
        return body, ttfb

    def http_event_received(self, event: H3Event) -> None:
        if isinstance(event, (HeadersReceived, DataReceived)):
            stream_id = event.stream_id
            if stream_id not in self._request_events:
                return

            if isinstance(event, DataReceived) and stream_id not in self._ttfb:
                self._ttfb[stream_id] = time.perf_counter() - self._start_time[stream_id]

            self._request_events[stream_id].append(event)

            if event.stream_ended:
                body = b"".join(
                    e.data for e in self._request_events[stream_id]
                    if isinstance(e, DataReceived)
                )
                waiter = self._request_waiter.pop(stream_id)
                self._request_events.pop(stream_id)
                if not waiter.done():
                    waiter.set_result(body)

    def quic_event_received(self, event) -> None:
        for http_event in self._http.handle_event(event):
            self.http_event_received(http_event)


async def run_benchmark(
    host: str,
    port: int,
    books: List[str],
    repeats: int,
    insecure: bool,
    output_csv: str,
):
    configuration = QuicConfiguration(alpn_protocols=H3_ALPN, is_client=True)
    if insecure:
        configuration.verify_mode = ssl.CERT_NONE

    results = []

    async with connect(
        host,
        port,
        configuration=configuration,
        create_protocol=HttpClient,
    ) as client:
        client = cast(HttpClient, client)

        for i in range(1, repeats + 1):
            for book in books:
                url = f"https://{host}:{port}/livros/{book}"
                start = time.perf_counter()
                try:
                    body, ttfb = await client.get(url)
                except Exception as exc:  # captura timeouts/erros sob perda de pacote
                    elapsed = time.perf_counter() - start
                    print(f"[{i:02d}] {book}: FALHOU ({exc})")
                    results.append(
                        {
                            "repeticao": i,
                            "livro": book,
                            "sucesso": False,
                            "tempo_s": elapsed,
                            "ttfb_s": None,
                            "tamanho_bytes": 0,
                            "vazao_Bps": 0,
                        }
                    )
                    continue

                elapsed = time.perf_counter() - start
                size_bytes = len(body)
                throughput = size_bytes / elapsed if elapsed > 0 else 0
                results.append(
                    {
                        "repeticao": i,
                        "livro": book,
                        "sucesso": True,
                        "tempo_s": elapsed,
                        "ttfb_s": ttfb,
                        "tamanho_bytes": size_bytes,
                        "vazao_Bps": throughput,
                    }
                )
                print(
                    f"[{i:02d}] {book}: {elapsed:.4f}s  "
                    f"TTFB={ttfb:.4f}s  {size_bytes/1024:.1f}KB  "
                    f"{throughput/1024:.1f}KB/s"
                )

    with open(output_csv, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=results[0].keys())
        writer.writeheader()
        writer.writerows(results)

    sucesso = [r for r in results if r["sucesso"]]
    if sucesso:
        tempos = [r["tempo_s"] for r in sucesso]
        vazoes = [r["vazao_Bps"] for r in sucesso]
        print("\n--- Estatísticas gerais (HTTP/3) ---")
        print(f"Requisições com sucesso: {len(sucesso)}/{len(results)}")
        print(f"Tempo médio: {statistics.mean(tempos):.4f}s")
        print(f"Desvio padrão do tempo: {statistics.pstdev(tempos):.4f}s")
        print(f"Vazão média: {statistics.mean(vazoes)/1024:.2f} KB/s")
    else:
        print("\nNenhuma requisição teve sucesso.")


def main():
    parser = argparse.ArgumentParser(description="Benchmark de cliente HTTP/3 (aioquic)")
    parser.add_argument("--host", default="servidor", help="host/IP do servidor Caddy")
    parser.add_argument("--port", type=int, default=443)
    parser.add_argument(
        "--books",
        nargs="+",
        default=["livro1.txt", "livro2.txt", "livro3.txt", "livro4.txt", "livro5.txt"],
    )
    parser.add_argument("--repeats", type=int, default=20)
    parser.add_argument(
        "--insecure",
        action="store_true",
        default=True,
        help="não validar certificado TLS (necessário com 'tls internal' do Caddy)",
    )
    parser.add_argument("--output", default="resultados_http3.csv")
    args = parser.parse_args()

    asyncio.run(
        run_benchmark(
            host=args.host,
            port=args.port,
            books=args.books,
            repeats=args.repeats,
            insecure=args.insecure,
            output_csv=args.output,
        )
    )


if __name__ == "__main__":
    main()
