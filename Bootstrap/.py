
"""
🌌 AQATRONIKS v24.0 – MASTER BOOTSTRAP

Single-file, publication-style bootstrap lab:

- Simulated "AQATRONIKS vs baseline" performance.
- Histograms + KDE + latency comparison.
- Interactive Plotly dashboard served with Flask.
- Minimal, self-contained code for easy copy/paste and publishing.

Dependencies:
    pip install numpy pandas matplotlib seaborn scipy plotly flask
"""

from __future__ import annotations

import os
import warnings
from typing import Dict, List

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from flask import Flask, render_template_string
from plotly.subplots import make_subplots
from scipy import stats
import seaborn as sns

warnings.filterwarnings("ignore")

# ==============================
# 1. GLOBAL STYLE CONFIG
# ==============================

# Color palette tuned for light/dark backgrounds and print
AQATRONIKS_PALETTE: Dict[str, str] = {
    "primary": "#2196F3",  # main blue
    "spin": "#F44336",     # baseline red
    "neuro": "#4CAF50",    # green accent
    "power": "#FF9800",    # orange accent
    "gold": "#FFEB3B",     # high-performance gold
    "dark": "#0D1117",     # dark background
    "card": "#161B22",     # card-like panels
}

# Matplotlib / seaborn publication style
plt.style.use("default")
sns.set_palette("husl")
plt.rcParams.update(
    {
        "font.family": "DejaVu Sans",
        "font.size": 12,
        "axes.linewidth": 1.2,
        "xtick.major.width": 1.2,
        "ytick.major.width": 1.2,
        "figure.dpi": 300,
        "savefig.dpi": 300,
        "figure.facecolor": "white",
        "axes.facecolor": "white",
    }
)

# ==============================
# 2. CORE VISUALIZER
# ==============================


class AqatroniksVisualizer:
    """
    🎨 Publication-quality bootstrap and latency visualizations.
    """

    def __init__(self) -> None:
        self.app = Flask(__name__)
        self._setup_routes()

    # ---------- Simulation ----------

    def bootstrap_simulation(
        self, n_samples: int = 10_000, n_bootstrap: int = 1_000
    ) -> Dict[str, np.ndarray]:
        """
        Generate synthetic bootstrap data for "AQATRONIKS vs baseline".

        Interpreted as:
        - aqatroniks: high-accuracy detector (e.g., 99.9%).
        - baseline: conventional method (e.g., ~92%).
        """
        rng = np.random.default_rng(42)

        # Ground truth distributions (beta distributions of accuracy)
        true_samples = rng.beta(1000, 1, n_samples)  # ~99.9%
        base_samples = rng.beta(80, 7, n_samples)    # ~92%

        # Bootstrap resampling
        true_bootstrap: List[float] = []
        base_bootstrap: List[float] = []

        for _ in range(n_bootstrap):
            true_bootstrap.append(float(rng.choice(true_samples, n_samples).mean()))
            base_bootstrap.append(float(rng.choice(base_samples, n_samples).mean()))

        true_bootstrap = np.array(true_bootstrap)
        base_bootstrap = np.array(base_bootstrap)

        ci_aq = np.percentile(true_bootstrap, [2.5, 97.5])
        ci_base = np.percentile(base_bootstrap, [2.5, 97.5])

        return {
            "aqatroniks": true_bootstrap,
            "baseline": base_bootstrap,
            "ci_aq": ci_aq,
            "ci_base": ci_base,
        }

    # ---------- Matplotlib/Seaborn static figure ----------

    def create_bootstrap_figure(self, data: Dict[str, np.ndarray]) -> str:
        """
        Create a Matplotlib figure (2x2 grid) and save to PNG.

        Returns:
            Path to the saved PNG file.
        """
        fig, axes = plt.subplots(2, 2, figsize=(12, 10))
        fig.suptitle(
            "AQATRONIKS v24.0 – Bootstrap Analysis\n"
            "High-accuracy detector vs baseline",
            fontsize=16,
            fontweight="bold",
        )

        aq = data["aqatroniks"]
        base = data["baseline"]
        ci_aq = data["ci_aq"]
        ci_base = data["ci_base"]

        # 1. Bootstrap distributions (histograms)
        ax1 = axes[0, 0]
        ax1.hist(
            aq,
            bins=50,
            alpha=0.7,
            color=AQATRONIKS_PALETTE["gold"],
            density=True,
            label="AQATRONIKS",
            edgecolor="white",
        )
        ax1.hist(
            base,
            bins=50,
            alpha=0.6,
            color=AQATRONIKS_PALETTE["spin"],
            density=True,
            label="Baseline",
            edgecolor="white",
        )
        ax1.axvline(ci_aq[0], color="gold", lw=3, label=f"AQATRONIKS 95% CI: {ci_aq[0]:.2%}")
        ax1.axvline(ci_aq[1], color="gold", lw=3)
        ax1.axvline(ci_base[0], color="red", lw=2, linestyle="--", label="Baseline 95% CI")
        ax1.axvline(ci_base[1], color="red", lw=2, linestyle="--")
        ax1.set_xlabel("Detection accuracy")
        ax1.set_ylabel("Density")
        ax1.legend(frameon=True, fancybox=True, shadow=True)
        ax1.grid(True, alpha=0.3)

        # 2. KDE overlay
        ax2 = axes[0, 1]
        sns.kdeplot(aq, ax=ax2, color=AQATRONIKS_PALETTE["gold"], linewidth=3, label="AQATRONIKS")
        sns.kdeplot(
            base,
            ax=ax2,
            color=AQATRONIKS_PALETTE["spin"],
            linewidth=3,
            label="Baseline",
        )
        ax2.axvline(np.mean(aq), color="gold", lw=3)
        ax2.axvline(np.mean(base), color="red", lw=3)
        ax2.set_title("Kernel density estimate")
        ax2.grid(True, alpha=0.3)
        ax2.legend()

        # 3. Latency comparison
        rng = np.random.default_rng(123)
        lat_aq = rng.normal(loc=15.0, scale=2.0, size=1000)   # ~15 ms
        lat_base = rng.normal(loc=7200.0, scale=600.0, size=1000)  # ~2 h in seconds

        ax3 = axes[1, 0]
        ax3.boxplot(
            [lat_aq, lat_base],
            labels=["AQATRONIKS (ms)", "Baseline (s)"],
            patch_artist=True,
        )
        for patch, color in zip(
            ax3.artists, [AQATRONIKS_PALETTE["primary"], AQATRONIKS_PALETTE["spin"]]
        ):
            patch.set_facecolor(color)
        ax3.set_title("Latency comparison")
        ax3.grid(True, alpha=0.3)

        # 4. QQ-plot (approximate normality check)
        ax4 = axes[1, 1]
        stats.probplot(aq, dist="norm", plot=ax4)
        ax4.set_title("AQATRONIKS bootstrap QQ-plot")

        fig.tight_layout(rect=[0, 0, 1, 0.93])

        output_path = os.path.abspath("aqatroniks_bootstrap.png")
        fig.savefig(output_path, bbox_inches="tight")
        plt.close(fig)
        return output_path

    # ---------- Plotly dashboard ----------

    def build_plotly_figure(self, data: Dict[str, np.ndarray]) -> go.Figure:
        """
        Create a Plotly figure with multiple views of the bootstrap results.
        """
        aq = data["aqatroniks"]
        base = data["baseline"]
        ci_aq = data["ci_aq"]
        ci_base = data["ci_base"]

        fig = make_subplots(
            rows=2,
            cols=2,
            subplot_titles=(
                "Bootstrap distributions",
                "Kernel density estimate",
                "Latency comparison",
                "CDF comparison",
            ),
        )

        # Row 1, Col 1: Histograms
        fig.add_trace(
            go.Histogram(
                x=aq,
                nbinsx=50,
                name="AQATRONIKS",
                marker_color=AQATRONIKS_PALETTE["gold"],
                opacity=0.7,
                histnorm="probability density",
            ),
            row=1,
            col=1,
        )
        fig.add_trace(
            go.Histogram(
                x=base,
                nbinsx=50,
                name="Baseline",
                marker_color=AQATRONIKS_PALETTE["spin"],
                opacity=0.6,
                histnorm="probability density",
            ),
            row=1,
            col=1,
        )

        # CI lines
        for v in ci_aq:
            fig.add_vline(
                x=v,
                line_width=2,
                line_color=AQATRONIKS_PALETTE["gold"],
                row=1,
                col=1,
            )
        for v in ci_base:
            fig.add_vline(
                x=v,
                line_width=2,
                line_color=AQATRONIKS_PALETTE["spin"],
                line_dash="dash",
                row=1,
                col=1,
            )

        # Row 1, Col 2: KDE curves (approximate using histogram-based density)
        aq_density_y, aq_density_x = np.histogram(aq, bins=80, density=True)
        base_density_y, base_density_x = np.histogram(base, bins=80, density=True)

        def centers(edges: np.ndarray) -> np.ndarray:
            return 0.5 * (edges[:-1] + edges[1:])

        fig.add_trace(
            go.Scatter(
                x=centers(aq_density_x),
                y=aq_density_y,
                mode="lines",
                name="AQATRONIKS KDE (approx)",
                line=dict(color=AQATRONIKS_PALETTE["gold"], width=3),
            ),
            row=1,
            col=2,
        )
        fig.add_trace(
            go.Scatter(
                x=centers(base_density_x),
                y=base_density_y,
                mode="lines",
                name="Baseline KDE (approx)",
                line=dict(color=AQATRONIKS_PALETTE["spin"], width=3),
            ),
            row=1,
            col=2,
        )

        # Row 2, Col 1: Latency boxplot (simple version)
        rng = np.random.default_rng(123)
        lat_aq = rng.normal(loc=15.0, scale=2.0, size=1000)
        lat_base = rng.normal(loc=7200.0, scale=600.0, size=1000)

        fig.add_trace(
            go.Box(
                y=lat_aq,
                name="AQATRONIKS latency (ms)",
                marker_color=AQATRONIKS_PALETTE["primary"],
            ),
            row=2,
            col=1,
        )
        fig.add_trace(
            go.Box(
                y=lat_base,
                name="Baseline latency (s)",
                marker_color=AQATRONIKS_PALETTE["spin"],
            ),
            row=2,
            col=1,
        )

        # Row 2, Col 2: Empirical CDFs
        def ecdf(x: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
            xs = np.sort(x)
            ys = np.linspace(0, 1, len(xs))
            return xs, ys

        x_aq_cdf, y_aq_cdf = ecdf(aq)
        x_base_cdf, y_base_cdf = ecdf(base)

        fig.add_trace(
            go.Scatter(
                x=x_aq_cdf,
                y=y_aq_cdf,
                mode="lines",
                name="AQATRONIKS CDF",
                line=dict(color=AQATRONIKS_PALETTE["gold"], width=3),
            ),
            row=2,
            col=2,
        )
        fig.add_trace(
            go.Scatter(
                x=x_base_cdf,
                y=y_base_cdf,
                mode="lines",
                name="Baseline CDF",
                line=dict(color=AQATRONIKS_PALETTE["spin"], width=3),
            ),
            row=2,
            col=2,
        )

        fig.update_layout(
            title="AQATRONIKS v24.0 – Bootstrap dashboard",
            template="plotly_dark",
            legend=dict(orientation="h", x=0, y=1.1),
            bargap=0.05,
        )

        return fig

    # ---------- Flask wiring ----------

    def _setup_routes(self) -> None:
        @self.app.route("/")
        def index():
            data = self.bootstrap_simulation()
            fig = self.build_plotly_figure(data)
            html = fig.to_html(full_html=False, include_plotlyjs="cdn")

            template = """
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="utf-8">
                <title>AQATRONIKS v24.0 – Bootstrap</title>
                <meta name="viewport" content="width=device-width, initial-scale=1">
                <style>
                    body {
                        margin: 0;
                        padding: 0;
                        background: #0D1117;
                        color: #E6EDF3;
                        font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
                    }
                    header {
                        padding: 1rem 1.25rem;
                        border-bottom: 1px solid #30363D;
                        background: #010409;
                    }
                    main {
                        padding: 1rem;
                    }
                    .subtitle {
                        font-size: 0.9rem;
                        opacity: 0.8;
                    }
                    .card {
                        background: #161B22;
                        border-radius: 8px;
                        padding: 1rem;
                        box-shadow: 0 0 0 1px #30363D;
                    }
                </style>
            </head>
            <body>
                <header>
                    <h1>AQATRONIKS v24.0 – Bootstrap Lab</h1>
                    <p class="subtitle">
                        Single-file bootstrap dashboard · simulated detector vs baseline
                    </p>
                </header>
                <main>
                    <div class="card">
                        {{ plot_html|safe }}
                    </div>
                </main>
            </body>
            </html>
            """
            return render_template_string(template, plot_html=html)

    # ---------- Runner ----------

    def run(self, host: str = "127.0.0.1", port: int = 5000) -> None:
        """
        Start the Flask development server.
        """
        print(
            f"\n[aqatroniks] running bootstrap dashboard at http://{host}:{port}\n"
            "Press Ctrl+C to stop.\n"
        )
        self.app.run(host=host, port=port, debug=False)


# ==============================
# 3. ENTRY POINT
# ==============================


def main() -> None:
    visualizer = AqatroniksVisualizer()
    # Also generate a static PNG for publications/papers
    data = visualizer.bootstrap_simulation()
    png_path = visualizer.create_bootstrap_figure(data)
    print(f"[aqatroniks] static figure saved to: {png_path}")
    visualizer.run()


if __name__ == "__main__":
    main()
```



