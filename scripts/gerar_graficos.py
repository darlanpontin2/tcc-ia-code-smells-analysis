#!/usr/bin/env python3
"""Gera gráficos comparativos a partir dos dados individuais de code smells."""

import argparse
import csv
from collections import defaultdict
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator


ROOT = Path(__file__).resolve().parents[1]
DATA_FILE = ROOT / "data" / "code_smells.csv"
COLORS = {"Gratuita": "#3977b8", "Paga": "#e07a32", "Base": "#777777"}
plt.rcParams.update(
    {
        "axes.spines.top": False,
        "axes.spines.right": False,
        "figure.facecolor": "white",
        "axes.facecolor": "white",
        "font.size": 10,
        "axes.titleweight": "bold",
    }
)


def load_data(path=DATA_FILE):
    with path.open(encoding="utf-8", newline="") as file:
        rows = list(csv.DictReader(file))
    for row in rows:
        row["individual_smells"] = int(row["individual_smells"])
        row["lines"] = int(row["lines"]) if row["lines"] else None
    return rows


def generated_samples(rows):
    return [row for row in rows if row["provider"] in ("Gratuita", "Paga")]


def totals_by_provider(rows):
    totals = defaultdict(int)
    for row in generated_samples(rows):
        totals[row["provider"]] += row["individual_smells"]
    return totals


def smells_per_thousand_lines(row):
    if not row["lines"]:
        return None
    return row["individual_smells"] * 1000 / row["lines"]


def save_figure(fig, output_dir, filename):
    fig.savefig(output_dir / filename, dpi=300, bbox_inches="tight")
    plt.close(fig)


def plot_overall(rows, output_dir):
    totals = totals_by_provider(rows)
    providers = ["Gratuita", "Paga"]
    values = [totals[provider] for provider in providers]
    fig, ax = plt.subplots(figsize=(7, 4.5))
    bars = ax.bar(providers, values, color=[COLORS[p] for p in providers], width=0.58)
    ax.bar_label(bars, padding=4, fontsize=11, fontweight="bold")
    ax.set(title="Total de code smells individuais por modalidade de IA", ylabel="Smells individuais")
    ax.text(
        0.5,
        -0.19,
        "Soma dos exemplos informados (4 por modalidade); não inclui os 43 smells do projeto base.",
        transform=ax.transAxes,
        ha="center",
        color="#555555",
        fontsize=9,
    )
    ax.set_ylim(0, max(values) * 1.2)
    save_figure(fig, output_dir, "01_comparacao_geral.png")


def plot_modules(rows, output_dir):
    samples = generated_samples(rows)
    modules = ["Carrinho", "Login", "Checkout"]
    fig, axes = plt.subplots(1, 3, figsize=(13, 4.8), sharey=True)
    for ax, module in zip(axes, modules):
        subset = [row for row in samples if row["module"] == module]
        positions = list(range(len(subset)))
        bars = ax.bar(
            positions,
            [row["individual_smells"] for row in subset],
            color=[COLORS[row["provider"]] for row in subset],
            width=0.68,
        )
        ax.set_xticks(positions, [row["label"].replace(module + " ", "") for row in subset], rotation=25, ha="right")
        ax.set_title(module)
        ax.bar_label(bars, padding=3, fontsize=9)
        ax.grid(axis="y", alpha=0.2)
    axes[0].set_ylabel("Smells individuais")
    axes[-1].legend(
        handles=[
            plt.Rectangle((0, 0), 1, 1, color=COLORS["Gratuita"], label="Gratuita"),
            plt.Rectangle((0, 0), 1, 1, color=COLORS["Paga"], label="Paga"),
        ],
        frameon=False,
        loc="upper left",
    )
    fig.suptitle("Comparação por funcionalidade e variante", fontweight="bold")
    fig.text(
        0.5,
        0.01,
        "As variantes são mantidas separadas; nem todos os módulos têm o mesmo número de versões.",
        ha="center",
        color="#555555",
        fontsize=9,
    )
    fig.tight_layout(rect=(0, 0.07, 1, 0.93))
    save_figure(fig, output_dir, "02_analise_por_modulo.png")


def plot_login_minification(rows, output_dir):
    subset = [
        row
        for row in rows
        if row["provider"] == "Gratuita" and row["module"] == "Login"
    ]
    fig, ax = plt.subplots(figsize=(7, 4.5))
    bars = ax.bar(
        [row["variation"] for row in subset],
        [row["individual_smells"] for row in subset],
        color=[COLORS["Gratuita"]] * len(subset),
        width=0.58,
    )
    ax.bar_label(bars, padding=4, fontweight="bold")
    ax.set(title="Login gratuito: impacto da minificação", ylabel="Smells individuais")
    ax.set_ylim(0, max(row["individual_smells"] for row in subset) * 1.25)
    save_figure(fig, output_dir, "03_impacto_minificacao.png")


def plot_checkout_fragmentation(rows, output_dir):
    subset = [
        row
        for row in rows
        if row["provider"] == "Paga"
        and row["module"] == "Checkout"
        and row["variation"] in ("Único", "Fracionado")
    ]
    fig, ax = plt.subplots(figsize=(7, 4.5))
    bars = ax.bar(
        [row["variation"] for row in subset],
        [row["individual_smells"] for row in subset],
        color=[COLORS["Paga"]] * len(subset),
        width=0.58,
    )
    ax.bar_label(bars, padding=4, fontweight="bold")
    ax.set(title="Checkout pago: impacto da fragmentação", ylabel="Smells individuais")
    ax.set_ylim(0, max(row["individual_smells"] for row in subset) * 1.2)
    save_figure(fig, output_dir, "04_impacto_fragmentacao.png")


def plot_density(rows, output_dir):
    samples = generated_samples(rows)
    fig, ax = plt.subplots(figsize=(10, 5.5))
    positions = list(range(len(samples)))
    bars = ax.bar(
        positions,
        [smells_per_thousand_lines(row) for row in samples],
        color=[COLORS[row["provider"]] for row in samples],
    )
    ax.set_xticks(positions, [row["label"] for row in samples], rotation=35, ha="right")
    ax.set(title="Densidade de code smells", ylabel="Smells individuais por 1.000 linhas")
    ax.bar_label(bars, labels=[f"{smells_per_thousand_lines(row):.1f}" for row in samples], padding=3, fontsize=8)
    ax.grid(axis="y", alpha=0.2)
    fig.tight_layout()
    save_figure(fig, output_dir, "05_densidade.png")


def plot_lines_vs_smells(rows, output_dir):
    fig, ax = plt.subplots(figsize=(8, 5.5))
    for row in generated_samples(rows):
        ax.scatter(
            row["lines"],
            row["individual_smells"],
            s=75,
            color=COLORS[row["provider"]],
            edgecolor="white",
            linewidth=0.8,
            zorder=3,
        )
        ax.annotate(
            row["label"],
            (row["lines"], row["individual_smells"]),
            xytext=(5, 5),
            textcoords="offset points",
            fontsize=8,
        )
    ax.set(title="Linhas de código versus code smells", xlabel="Linhas de código", ylabel="Smells individuais")
    ax.xaxis.set_major_locator(MaxNLocator(integer=True, nbins=6))
    ax.grid(alpha=0.2)
    ax.legend(
        handles=[
            plt.Line2D([], [], marker="o", linestyle="", color=COLORS["Gratuita"], label="Gratuita"),
            plt.Line2D([], [], marker="o", linestyle="", color=COLORS["Paga"], label="Paga"),
        ],
        frameon=False,
    )
    fig.tight_layout()
    save_figure(fig, output_dir, "06_linhas_vs_smells.png")


def plot_diversity(output_dir):
    fig, ax = plt.subplots(figsize=(9, 4.5))
    ax.axis("off")
    ax.set_title("Taxa de diversidade de tipos de smells", pad=18)
    ax.text(
        0.5,
        0.59,
        "Não calculável com os dados fornecidos",
        ha="center",
        va="center",
        fontsize=16,
        fontweight="bold",
        color="#555555",
        transform=ax.transAxes,
    )
    ax.text(
        0.5,
        0.37,
        "Há contagens totais de smells individuais, mas não a quantidade por tipo.\n"
        "Para comparar diversidade, informe os tipos distintos detectados em cada código.",
        ha="center",
        va="center",
        fontsize=11,
        color="#555555",
        transform=ax.transAxes,
    )
    save_figure(fig, output_dir, "07_diversidade_indisponivel.png")


def plot_comparison_table(rows, output_dir):
    columns = ["Código", "IA", "Funcionalidade", "Variante", "Smells individuais", "Linhas", "Smells / 1.000 linhas"]
    table_rows = []
    for row in rows:
        density = smells_per_thousand_lines(row)
        table_rows.append(
            [
                row["label"],
                row["provider"],
                row["module"],
                row["variation"],
                str(row["individual_smells"]),
                str(row["lines"]) if row["lines"] is not None else "—",
                f"{density:.2f}" if density is not None else "—",
            ]
        )
    fig, ax = plt.subplots(figsize=(14, 4.8))
    ax.axis("off")
    ax.set_title("Tabela comparativa dos dados informados", pad=16)
    table = ax.table(cellText=table_rows, colLabels=columns, cellLoc="center", loc="center")
    table.auto_set_font_size(False)
    table.set_fontsize(8.5)
    table.scale(1, 1.55)
    for col in range(len(columns)):
        table[(0, col)].set_facecolor("#29475f")
        table[(0, col)].set_text_props(color="white", weight="bold")
    for row_index in range(1, len(table_rows) + 1):
        table[(row_index, 0)].set_text_props(ha="left")
        if row_index % 2 == 0:
            for col in range(len(columns)):
                table[(row_index, col)].set_facecolor("#f0f4f7")
    fig.text(
        0.5,
        0.04,
        "Projeto base: 43 smells; valores por IA consideram somente a coluna “Code Smells Individuais”.",
        ha="center",
        fontsize=9,
        color="#555555",
    )
    save_figure(fig, output_dir, "08_tabela_comparativa.png")


def generate(rows, output_dir):
    output_dir.mkdir(parents=True, exist_ok=True)
    plot_overall(rows, output_dir)
    plot_modules(rows, output_dir)
    plot_login_minification(rows, output_dir)
    plot_checkout_fragmentation(rows, output_dir)
    plot_density(rows, output_dir)
    plot_lines_vs_smells(rows, output_dir)
    plot_diversity(output_dir)
    plot_comparison_table(rows, output_dir)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=ROOT / "figures",
        help="Diretório de saída das imagens (padrão: figures/).",
    )
    args = parser.parse_args()
    rows = load_data()
    generate(rows, args.output_dir)
    totals = totals_by_provider(rows)
    print(f"Gráficos salvos em: {args.output_dir.resolve()}")
    print(f"Total gratuito: {totals['Gratuita']} smells individuais")
    print(f"Total pago: {totals['Paga']} smells individuais")
    print("Diversidade: indisponível sem contagens por tipo de smell")


if __name__ == "__main__":
    main()
