#!/usr/bin/env bash
# run_experiment.sh — roda os 3 cenários (0%, 3%, 5% de perda, 100ms de
# latência) automaticamente: aplica o netem no servidor, roda os dois
# clientes (HTTP/1.1 e HTTP/3), salva cada resultado com nome único
# (nada de sobrepor CSV), remove o netem, e passa pro próximo cenário.
#
# Rode este script a partir da pasta Docker/, no HOST (não dentro de
# nenhum container):
#   bash run_experiment.sh

set -e

REPEATS=10
DELAY=100ms
LOSSES=(0 3 5)

RESULTS_DIR_HOST="../resultados"
RESULTS_DIR_CONTAINER="/app/resultados"

mkdir -p "$RESULTS_DIR_HOST"

for LOSS in "${LOSSES[@]}"; do
    echo ""
    echo "=================================================="
    echo " Cenário: perda ${LOSS}%  |  delay ${DELAY}"
    echo "=================================================="

    # limpa qualquer regra anterior (não falha se não existir nenhuma)
    docker exec servidor-http tc qdisc del dev eth0 root 2>/dev/null || true

    if [ "$LOSS" = "0" ]; then
        docker exec servidor-http tc qdisc add dev eth0 root netem delay "${DELAY}"
    else
        docker exec servidor-http tc qdisc add dev eth0 root netem delay "${DELAY}" loss "${LOSS}%"
    fi

    echo "--- netem aplicado ---"
    docker exec servidor-http tc qdisc show dev eth0

    echo ""
    echo ">> Rodando HTTP/1.1 (perda ${LOSS}%)..."
    docker exec cliente-http python3 /app/scripts/http1_bench.py \
        --repeats "${REPEATS}" \
        --output "${RESULTS_DIR_CONTAINER}/http1_loss${LOSS}.csv"

    echo ""
    echo ">> Rodando HTTP/3 (perda ${LOSS}%)..."
    docker exec cliente-http python3 /app/scripts/http3_bench.py \
        --repeats "${REPEATS}" \
        --output "${RESULTS_DIR_CONTAINER}/http3_loss${LOSS}.csv"

    # limpa a regra antes do próximo cenário
    docker exec servidor-http tc qdisc del dev eth0 root
done

echo ""
echo "=================================================="
echo " Experimento concluído."
echo " CSVs em: ${RESULTS_DIR_HOST}/"
echo "=================================================="
ls -la "$RESULTS_DIR_HOST"
