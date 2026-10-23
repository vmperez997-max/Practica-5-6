"""Plot only existing measurements; no retraining."""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd


def plot_results(summary, destination):
    fig, ax = plt.subplots(figsize=(10, 5))
    offsets = [(5, -12), (5, 5), (5, 5), (-15, 14), (5, -12), (5, 5), (5, -12), (5, 5)]
    for index, row in enumerate(summary.itertuples(), 1):
        name = {
            "popularity": "Popularidad",
            "content": "Contenido",
            "collaborative": "MF",
            "hybrid": "Híbrido",
        }[row.method]
        if row.factors:
            name += f" {row.factors}/{row.epochs}"
        if row.method == "hybrid":
            name += f" alpha={row.alpha}"
        ax.scatter(
            row.total_seconds,
            row.hit_rate_at_10 * 100,
            s=35 + row.coverage * 350,
            marker="o" if row.pareto else "x",
            label=f"{index}. {name}",
        )
        ax.annotate(
            str(index),
            (row.total_seconds, row.hit_rate_at_10 * 100),
            xytext=offsets[index - 1],
            textcoords="offset points",
            fontsize=9,
        )
    ax.set(
        xlabel="Segundos: entrenamiento MF + ranking",
        ylabel="HitRate@10 (%)",
        title="Costo y utilidad · medias por configuración",
    )
    ax.margins(x=0.12, y=0.12)
    ax.grid(alpha=0.15)
    ax.legend(loc="center left", bbox_to_anchor=(1.02, 0.5), fontsize=8, frameon=False)
    fig.text(
        0.12,
        0.015,
        "Área del marcador: cobertura. Círculo: Pareto; cruz: dominado.",
        fontsize=8,
    )
    fig.tight_layout(rect=[0, 0.035, 1, 1])
    fig.savefig(destination, dpi=160)
    plt.close(fig)


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    plot_results(pd.read_csv(root / "reports/pareto.csv"), root / "reports/pareto.png")
