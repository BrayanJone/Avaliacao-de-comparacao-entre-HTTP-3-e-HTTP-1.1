import pandas as pd

arquivos = {
    "HTTP/1.1 - 0%": "../results/http1_0.csv",
    "HTTP/1.1 - 3%": "../results/http1_3.csv",
    "HTTP/1.1 - 7%": "../results/http1_7.csv",

    "HTTP/3 - 0%": "../results/http3_0.csv",
    "HTTP/3 - 3%": "../results/http3_3.csv",
    "HTTP/3 - 7%": "../results/http3_7.csv",
}

for nome, caminho in arquivos.items():

    df = pd.read_csv(caminho)

    print(f"\n{nome}")
    print("-" * 40)

    medias = df.groupby("livro")["tempo_ms"].mean()

    for livro, media in medias.items():
        print(f"{livro}: {media:.2f} ms")

    media_geral = df["tempo_ms"].mean()

    desvio_geral = df["tempo_ms"].std()

    print("\nResumo Geral")
    print(f"Média geral: {media_geral:.2f} ms")
    print(f"Desvio padrão geral: {desvio_geral:.2f} ms")
