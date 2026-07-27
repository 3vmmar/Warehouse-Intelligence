"""Report-ready visualizations for the integrated AI system.

The React application provides interactive animation; this module creates
static PNG evidence suitable for the submitted report and presentation.
"""

from __future__ import annotations

from pathlib import Path

from environment import WarehouseEnvironment
from q_learning import QLearningResult

PALETTE = {
    "background": "#070A12",
    "panel": "#101625",
    "text": "#E7ECF7",
    "muted": "#8792A8",
    "cyan": "#51E6FF",
    "violet": "#8C6CFF",
    "green": "#50E3A4",
    "amber": "#FFBF69",
}


def save_search_comparison(summary: list[dict], output_path: str | Path) -> Path:
    plt = _plt()
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    labels = [row["display_name"] for row in summary]
    costs = [row.get("mean_path_cost") or 0 for row in summary]
    runtimes = [row.get("mean_runtime_ms") or 0 for row in summary]
    work = [row.get("mean_work_units") or 0 for row in summary]
    memory = [row.get("mean_memory_units") or 0 for row in summary]

    fig, axes_grid = plt.subplots(2, 2, figsize=(15, 10), facecolor=PALETTE["background"])
    axes = axes_grid.flatten()
    for axis in axes:
        axis.set_facecolor(PALETTE["panel"])
        axis.tick_params(colors=PALETTE["muted"], labelsize=8)
        for spine in axis.spines.values():
            spine.set_visible(False)
        axis.grid(axis="x", color="#273148", alpha=0.55, linewidth=0.7)

    colors = [PALETTE["cyan"], PALETTE["violet"], PALETTE["green"], PALETTE["amber"]]
    for axis, values, title, color in zip(
        axes,
        (costs, runtimes, work, memory),
        (
            "Mean solution cost",
            "Mean runtime (ms)",
            "Mean search work",
            "Mean memory units",
        ),
        colors,
        strict=True,
    ):
        positions = list(range(len(labels)))
        axis.barh(positions, values, color=color, alpha=0.88)
        axis.set_yticks(
            positions,
            labels if axis in (axes[0], axes[2]) else ["" for _ in labels],
        )
        axis.invert_yaxis()
        axis.set_title(title, color=PALETTE["text"], fontsize=12, fontweight="bold", pad=14)
    fig.suptitle(
        "Search and Optimization Comparison",
        color=PALETTE["text"],
        fontsize=18,
        fontweight="bold",
        y=0.98,
    )
    fig.tight_layout(rect=(0, 0, 1, 0.94))
    fig.savefig(output_path, dpi=180, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)
    return output_path


def save_q_learning_curve(result: QLearningResult, output_path: str | Path) -> Path:
    plt = _plt()
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    episodes = [row["episode"] for row in result.training_curve]
    rewards = [row["average_reward"] for row in result.training_curve]
    success = [row["success_rate"] * 100 for row in result.training_curve]
    epsilon = [row["epsilon"] for row in result.training_curve]

    fig, axes = plt.subplots(2, 1, figsize=(12, 8), sharex=True, facecolor=PALETTE["background"])
    for axis in axes:
        axis.set_facecolor(PALETTE["panel"])
        axis.tick_params(colors=PALETTE["muted"])
        axis.grid(color="#273148", alpha=0.55, linewidth=0.7)
        for spine in axis.spines.values():
            spine.set_visible(False)

    axes[0].plot(episodes, rewards, color=PALETTE["cyan"], linewidth=2.2, label="Average reward")
    axes[0].set_ylabel("Reward", color=PALETTE["muted"])
    axes[0].legend(frameon=False, labelcolor=PALETTE["text"])
    axes[1].plot(episodes, success, color=PALETTE["green"], linewidth=2.2, label="Success rate %")
    epsilon_axis = axes[1].twinx()
    epsilon_axis.plot(
        episodes, epsilon, color=PALETTE["amber"], linewidth=1.5, alpha=0.8, label="Epsilon"
    )
    epsilon_axis.tick_params(colors=PALETTE["amber"])
    epsilon_axis.set_ylabel("Epsilon", color=PALETTE["amber"])
    axes[1].set_ylabel("Success %", color=PALETTE["muted"])
    axes[1].set_xlabel("Episode", color=PALETTE["muted"])
    axes[1].legend(frameon=False, labelcolor=PALETTE["text"], loc="upper left")
    fig.suptitle("Q-Learning Convergence", color=PALETTE["text"], fontsize=18, fontweight="bold")
    fig.tight_layout(rect=(0, 0, 1, 0.95))
    fig.savefig(output_path, dpi=180, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)
    return output_path


def save_policy_map(
    environment: WarehouseEnvironment,
    result: QLearningResult,
    output_path: str | Path,
) -> Path:
    plt = _plt()
    import numpy as np

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    base = np.zeros((environment.rows, environment.cols), dtype=float)
    for row in range(environment.rows):
        for col in range(environment.cols):
            base[row, col] = (
                -1 if environment.grid[row][col] else environment.terrain_costs[row][col]
            )

    fig, axis = plt.subplots(figsize=(10, 10), facecolor=PALETTE["background"])
    axis.set_facecolor(PALETTE["panel"])
    axis.imshow(base, cmap="magma", interpolation="nearest", alpha=0.72)
    arrow = {"UP": "↑", "DOWN": "↓", "LEFT": "←", "RIGHT": "→"}
    for index, state in enumerate(result.state_lookup):
        row, col, carrying = state
        if carrying or environment.grid[row][col] or result.policy[index] is None:
            continue
        if environment.rows <= 36:
            axis.text(
                col,
                row,
                arrow[result.policy[index]],
                ha="center",
                va="center",
                color="#E7ECF7",
                fontsize=5,
            )
    if result.policy_path:
        xs = [state[1] for state in result.policy_path]
        ys = [state[0] for state in result.policy_path]
        axis.plot(xs, ys, color=PALETTE["cyan"], linewidth=2.4, alpha=0.95)
    for label, position, color in (
        ("S", environment.start, PALETTE["cyan"]),
        ("P", environment.pickup, PALETTE["amber"]),
        ("D", environment.delivery, PALETTE["green"]),
    ):
        axis.scatter(
            position[1], position[0], s=140, color=color, edgecolors="white", linewidths=0.8
        )
        axis.text(
            position[1],
            position[0],
            label,
            ha="center",
            va="center",
            color="#070A12",
            fontweight="bold",
        )
    axis.set_xticks([])
    axis.set_yticks([])
    axis.set_title(
        "Learned policy and greedy rollout",
        color=PALETTE["text"],
        fontsize=16,
        fontweight="bold",
        pad=14,
    )
    fig.tight_layout()
    fig.savefig(output_path, dpi=180, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)
    return output_path


def _plt():
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    return plt
