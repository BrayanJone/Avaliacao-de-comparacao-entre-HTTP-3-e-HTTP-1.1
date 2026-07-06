"""
plot_results.py — gera gráficos comparativos entre HTTP/1.1 e HTTP/3 a
partir dos CSVs gerados pelo run_experiment.sh.

Espera encontrar arquivos no padrão:
  resultados/http1_loss0.csv, http1_loss3.csv, http1_loss5.csv
  resultados/http3_loss0.csv, http3_loss3.csv, http3_loss5.csv

Gera 4 gráficos em resultados/graficos/:
  - tempo_medio.png    (tempo médio de download, com desvio padrão)
  - vazao_media.png    (vazão média, com desvio padrão)
  - taxa_sucesso.png   (% de requisições concluídas com sucesso)
  - boxplot_tempo.png  (distribuição do tempo, um painel por cenário)

Uso:
  python3 plot_results.py --dir /app/resultados
"""

import argparse
import glob
import os
import re

import matplotlib.pyplot as plt
import pandas as pd

PADRAO_ARQUIVO = re.compile(r"(http[13])_loss(\d+)\.csv")


def carregar_tudo(results_dir):
    partes = []
    for path in glob.glob(os.path.join(results_dir, "*.csv")):
        nome = os.path.basename(path)
        m = PADRAO_ARQUIVO.match(nome)
        if not m:
            continue
        protocolo_raw, perda = m.group(1), m.group(2)
        df = pd.read_csv(path)
        df["protocolo"] = "HTTP/1.1" if protocolo_raw == "http1" else "HTTP/3"
        df["cenario_perda"] = f"{perda}%"
        partes.append(df)

    if not partes:
        raise SystemExit(
            f"Nenhum CSV encontrado em {results_dir} no padrão httpN_lossX.csv "
            "(gerado pelo run_experiment.sh)"
        )
    return pd.concat(partes, ignore_index=True)


def ordem_cenarios(df):
    return sorted(df["cenario_perda"].unique(), key=lambda x: int(x.replace("%", "")))


def grafico_barras_com_erro(df, coluna_valor, coluna_erro, ylabel, titulo, arquivo_saida, escala=1.0, log=False, fmt="%.1f"):
    cenarios = ordem_cenarios(df)
    protocolos = ["HTTP/1.1", "HTTP/3"]
    x = range(len(cenarios))
    largura = 0.35

    fig, ax = plt.subplots(figsize=(8, 5))
    for i, proto in enumerate(protocolos):
        sub = (
            df[df["protocolo"] == proto]
            .set_index("cenario_perda")
            .reindex(cenarios)
        )
        offset = (i - 0.5) * largura
        barras = ax.bar(
            [xi + offset for xi in x],
            sub[coluna_valor] * escala,
            width=largura,
            yerr=(sub[coluna_erro] * escala if coluna_erro else None),
            capsize=4,
            label=proto,
        )
        ax.bar_label(barras, fmt=fmt, padding=8, fontsize=9)

    ax.set_xticks(list(x))
    ax.set_xticklabels(cenarios)
    ax.set_xlabel("Cenário de perda de pacotes")
    ax.set_ylabel(ylabel)
    ax.set_title(titulo)
    if log:
        ax.set_yscale("log")
    ax.legend()
    fig.tight_layout()
    fig.savefig(arquivo_saida, dpi=150)
    plt.close(fig)


def plot_tempo_medio(df, out_dir):
    ok = df[df["sucesso"] == True]
    agg = ok.groupby(["cenario_perda", "protocolo"])["tempo_s"].agg(["mean", "std"]).reset_index()
    grafico_barras_com_erro(
        agg, "mean", "std",
        ylabel="Tempo médio de download (s)",
        titulo="Tempo médio de download — HTTP/1.1 vs HTTP/3",
        arquivo_saida=os.path.join(out_dir, "tempo_medio.png"),
    )


def plot_vazao_media(df, out_dir):
    ok = df[df["sucesso"] == True]
    agg = ok.groupby(["cenario_perda", "protocolo"])["vazao_Bps"].agg(["mean", "std"]).reset_index()
    grafico_barras_com_erro(
        agg, "mean", "std",
        ylabel="Vazão média (KB/s) — escala log",
        titulo="Vazão média — HTTP/1.1 vs HTTP/3",
        arquivo_saida=os.path.join(out_dir, "vazao_media.png"),
        escala=1 / 1024,
        log=True,
        fmt="%.0f",
    )


def plot_taxa_sucesso(df, out_dir):
    agg = df.groupby(["cenario_perda", "protocolo"])["sucesso"].mean().reset_index()
    grafico_barras_com_erro(
        agg, "sucesso", None,
        ylabel="Taxa de sucesso (%)",
        titulo="Taxa de sucesso das requisições — HTTP/1.1 vs HTTP/3",
        arquivo_saida=os.path.join(out_dir, "taxa_sucesso.png"),
        escala=100,
    )


def plot_boxplot_tempo(df, out_dir):
    ok = df[df["sucesso"] == True].copy()
    cenarios = ordem_cenarios(ok)

    fig, axes = plt.subplots(1, len(cenarios), figsize=(5 * len(cenarios), 5), sharey=True)
    if len(cenarios) == 1:
        axes = [axes]

    for ax, cenario in zip(axes, cenarios):
        sub = ok[ok["cenario_perda"] == cenario]
        dados = [sub[sub["protocolo"] == p]["tempo_s"] for p in ["HTTP/1.1", "HTTP/3"]]
        ax.boxplot(dados)
        ax.set_xticks([1, 2])
        ax.set_xticklabels(["HTTP/1.1", "HTTP/3"])
        ax.set_title(f"Perda {cenario}")
        ax.set_ylabel("Tempo (s)")

    fig.suptitle("Distribuição do tempo de download por cenário")
    fig.tight_layout()
    fig.savefig(os.path.join(out_dir, "boxplot_tempo.png"), dpi=150)
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dir", default="/app/resultados")
    args = parser.parse_args()

    df = carregar_tudo(args.dir)

    out_dir = os.path.join(args.dir, "graficos")
    os.makedirs(out_dir, exist_ok=True)

    plot_tempo_medio(df, out_dir)
    plot_vazao_media(df, out_dir)
    # plot_boxplot_tempo(df, out_dir)  # desativado a pedido: mais difícil
    # de explicar (quartis, mediana, outliers). Reative se quiser voltar
    # a usá-lo mais pra frente.
    # plot_taxa_sucesso(df, out_dir)  # desativado: ficou 100% em todos os
    # cenários porque os clientes não têm timeout curto — nenhuma
    # requisição falha de fato, só fica mais lenta. Reative se algum dia
    # adicionar timeout aos scripts e quiser medir falhas de verdade.

    print(f"Gráficos salvos em: {out_dir}")
    for f in sorted(os.listdir(out_dir)):
        print(f"  - {f}")


if __name__ == "__main__":
    main()
