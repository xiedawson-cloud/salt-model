"""Create publication-style exploratory plots from Monte Carlo outputs."""
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt


def main():
    root = Path(__file__).resolve().parents[2]
    results = root / "results"
    figs = results / "figures"
    figs.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(results / "monte_carlo_outputs.csv")

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.hist(df["dissolved_cr_mg_L"], bins=35)
    ax.set_xlabel("Dissolved chromium (mg/L)")
    ax.set_ylabel("Number of sampled scenarios")
    ax.set_title("Scenario ensemble: dissolved chromium")
    fig.tight_layout()
    fig.savefig(figs / "dissolved_chromium_distribution.png", dpi=180)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(8, 5))
    sc = ax.scatter(df["temperature_C"], df["dissolved_cr_mg_L"],
                    c=df["redox_index"], s=15, alpha=0.65)
    ax.set_xlabel("Temperature (°C)")
    ax.set_ylabel("Dissolved chromium (mg/L)")
    ax.set_title("Temperature and chromium response across scenarios")
    cb = fig.colorbar(sc, ax=ax)
    cb.set_label("Dimensionless redox scenario index")
    fig.tight_layout()
    fig.savefig(figs / "temperature_vs_chromium.png", dpi=180)
    plt.close(fig)

    ranks = pd.read_csv(results / "rank_associations.csv")
    pivot = ranks.pivot(index="parameter", columns="output", values="spearman_rho")
    fig, ax = plt.subplots(figsize=(10, 5.5))
    im = ax.imshow(pivot.values, aspect="auto", vmin=-1, vmax=1)
    ax.set_yticks(range(len(pivot.index)), pivot.index)
    ax.set_xticks(range(len(pivot.columns)), [c.replace("_", "\n") for c in pivot.columns])
    ax.set_title("Spearman rank associations within selected scenario ranges")
    fig.colorbar(im, ax=ax, label="Spearman rho")
    fig.tight_layout()
    fig.savefig(figs / "rank_association_heatmap.png", dpi=180)
    plt.close(fig)

if __name__ == "__main__":
    main()
