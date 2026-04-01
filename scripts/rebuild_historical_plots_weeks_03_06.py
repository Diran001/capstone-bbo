from __future__ import annotations

from pathlib import Path
import re

import matplotlib.pyplot as plt
import numpy as np


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_ROOT = PROJECT_ROOT / "data" / "initial_data"
PROCESSED_ROOT = PROJECT_ROOT / "data" / "processed"
PLOTS_ROOT = PROJECT_ROOT / "data" / "plots" / "historical"

INITIAL_SIZES = {
    1: (10, 2),
    2: (10, 2),
    3: (15, 3),
    4: (30, 4),
    5: (20, 4),
    6: (20, 5),
    7: (30, 6),
    8: (40, 8),
}

FUNCTION_DESCRIPTIONS = {
    1: "2D black-box function",
    2: "2D black-box function",
    3: "3D black-box function",
    4: "4D black-box function",
    5: "4D black-box function",
    6: "5D black-box function",
    7: "6D black-box function",
    8: "8D black-box function",
}


def parse_processed_outputs(week_num: int) -> list[list[float]]:
    path = PROCESSED_ROOT / f"Capstone_Project_Week{week_num:02d}SubmissionProcessed" / "outputs.txt"
    text = path.read_text(encoding="utf-8").strip()
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]

    parsed: list[list[float]] = []
    for ln in lines:
        clean = re.sub(r"np\.float64\(([^)]+)\)", r"\1", ln)
        values = eval(clean, {"__builtins__": {}}, {})
        parsed.append([float(v) for v in values])

    return parsed


def parse_processed_inputs(week_num: int) -> list[list[np.ndarray]]:
    """
    Parse cumulative weekly input lines such as:
    [array([...]), array([...]), ...]

    We use a restricted eval with a fake array() constructor so wrapped lines
    and numpy-style formatting do not break parsing.
    """
    path = PROCESSED_ROOT / f"Capstone_Project_Week{week_num:02d}SubmissionProcessed" / "inputs.txt"
    text = path.read_text(encoding="utf-8").strip()

    # Each top-level line is one cumulative weekly state
    raw_lines = [ln for ln in text.splitlines() if ln.strip()]

    # Reassemble records because some array representations span multiple lines.
    records: list[str] = []
    current = ""

    for ln in raw_lines:
        if current:
            current += "\n" + ln
        else:
            current = ln

        # A complete weekly record ends with ]]
        if current.strip().endswith("])]"):
            records.append(current.strip())
            current = ""

    if current.strip():
        records.append(current.strip())

    weekly_states: list[list[np.ndarray]] = []

    def array(x):
        return np.array(x, dtype=float)

    for rec in records:
        parsed = eval(rec, {"__builtins__": {}}, {"array": array})
        if len(parsed) != 8:
            raise ValueError(
                f"Week {week_num}: expected 8 function input arrays, got {len(parsed)}\nRecord:\n{rec}"
            )

        parsed_arrays = [np.asarray(a, dtype=float) for a in parsed]
        weekly_states.append(parsed_arrays)

    return weekly_states


def load_initial_prefix(func_id: int) -> tuple[np.ndarray, np.ndarray]:
    fdir = DATA_ROOT / f"function_{func_id}"
    X_full = np.load(fdir / "initial_inputs.npy")
    y_full = np.load(fdir / "initial_outputs.npy")

    initial_n, dim = INITIAL_SIZES[func_id]
    X0 = X_full[:initial_n].copy()
    y0 = y_full[:initial_n].copy()

    if X0.shape != (initial_n, dim):
        raise ValueError(
            f"Function {func_id}: expected initial shape {(initial_n, dim)}, got {X0.shape}"
        )
    if len(y0) != initial_n:
        raise ValueError(
            f"Function {func_id}: expected initial output length {initial_n}, got {len(y0)}"
        )

    return X0, y0


def reconstruct_state_after_week(target_week: int, func_id: int) -> tuple[np.ndarray, np.ndarray]:
    X, y = load_initial_prefix(func_id)

    for wk in range(1, target_week + 1):
        inputs_states = parse_processed_inputs(wk)
        outputs_states = parse_processed_outputs(wk)

        x_new = np.asarray(inputs_states[-1][func_id - 1], dtype=float)
        y_new = float(outputs_states[-1][func_id - 1])

        expected_dim = INITIAL_SIZES[func_id][1]
        if x_new.shape != (expected_dim,):
            raise ValueError(
                f"Week {wk}, function {func_id}: expected input shape {(expected_dim,)}, got {x_new.shape}"
            )

        X = np.vstack([X, x_new])
        y = np.append(y, y_new)

    return X, y


def create_progress_plot_from_state(func_id: int, y: np.ndarray, week_num: int) -> Path:
    bsf = np.maximum.accumulate(y)
    initial_size = INITIAL_SIZES[func_id][0]
    weeks_added = len(y) - initial_size

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(
        range(1, len(bsf) + 1),
        bsf,
        linewidth=2.5,
        label="Best so far",
        zorder=2,
    )

    ax.axvline(
        x=initial_size,
        color="gray",
        linestyle="--",
        label="Initial data",
        alpha=0.6,
        linewidth=1.5,
        zorder=1,
    )

    colours = ["red", "green", "orange", "purple", "brown", "pink", "cyan"]
    for w in range(1, min(weeks_added + 1, 13)):
        idx = initial_size + w
        colour = colours[(w - 1) % len(colours)]
        ax.plot(idx, bsf[idx - 1], "o", color=colour, markersize=10, label=f"Week {w}", zorder=3)
        ax.axvline(x=idx, color=colour, linestyle=":", alpha=0.2, zorder=1)

    ax.set_xlabel("Evaluation Count", fontsize=13, fontweight="bold")
    ax.set_ylabel("Best-so-far Output", fontsize=13, fontweight="bold")

    title = f"Function {func_id}: {FUNCTION_DESCRIPTIONS[func_id]}\n"
    title += f"Best: {bsf[-1]:+.6f} ({weeks_added} week{'s' if weeks_added != 1 else ''})"
    ax.set_title(title, fontsize=14, fontweight="bold")

    ax.grid(True, alpha=0.3, linestyle="--")
    ax.legend(fontsize=9, loc="best", ncol=2)
    plt.tight_layout()

    save_dir = PLOTS_ROOT / f"week_{week_num:02d}"
    save_dir.mkdir(parents=True, exist_ok=True)
    save_path = save_dir / f"function_{func_id}_week{week_num:02d}.png"

    plt.savefig(save_path, dpi=150, bbox_inches="tight")
    plt.close(fig)

    return save_path


def main() -> None:
    target_weeks = [3, 4, 5, 6]

    print(f"Project root: {PROJECT_ROOT}")
    print(f"Rebuilding historical plots for weeks: {target_weeks}\n")

    for week_num in target_weeks:
        print(f"Week {week_num:02d}")
        for func_id in range(1, 9):
            _, y = reconstruct_state_after_week(week_num, func_id)
            out = create_progress_plot_from_state(func_id, y, week_num)
            print(f"  Function {func_id}: {out}")
        print()

    print("Done.")


if __name__ == "__main__":
    main()