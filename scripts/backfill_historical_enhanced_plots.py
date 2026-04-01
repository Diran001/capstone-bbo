from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

import numpy as np
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import Matern, WhiteKernel, ConstantKernel as C

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
    1: "2D source localisation (contamination/radiation detection)",
    2: "2D noisy scoring system with local optima",
    3: "3D drug discovery mixture optimisation",
    4: "4D business configuration with costly evaluations",
    5: "4D chemical process yield maximisation",
    6: "5D recipe-style optimisation",
    7: "6D hyperparameter tuning",
    8: "8D high-dimensional hyperparameter optimisation",
}

DEFAULT_TUNING = {
    "n_restarts_optimizer": 10,
    "length_scale_bounds": (1e-2, 10.0),
    "noise_level": 1e-6,
}

# Match your current notebook block for week 10 so the plotting GP is aligned
TUNING_BY_WEEK = {
    10: {
        1: {"n_restarts_optimizer": 10, "length_scale_bounds": (1e-3, 8.0),  "noise_level": 1e-5},
        2: {"n_restarts_optimizer": 12, "length_scale_bounds": (1e-3, 10.0), "noise_level": 1e-6},
        3: {"n_restarts_optimizer": 14, "length_scale_bounds": (1e-3, 12.0), "noise_level": 1e-6},
        4: {"n_restarts_optimizer": 16, "length_scale_bounds": (1e-3, 12.0), "noise_level": 1e-5},
        5: {"n_restarts_optimizer": 14, "length_scale_bounds": (1e-3, 6.0),  "noise_level": 1e-6},
        6: {"n_restarts_optimizer": 16, "length_scale_bounds": (1e-3, 15.0), "noise_level": 1e-6},
        7: {"n_restarts_optimizer": 18, "length_scale_bounds": (1e-3, 20.0), "noise_level": 1e-5},
        8: {"n_restarts_optimizer": 20, "length_scale_bounds": (1e-3, 25.0), "noise_level": 1e-5},
    }
}

RUN_WEEK = 10

ENHANCED_SUFFIXES = [
    "progress_enhanced",
    "surface_contour",
    "scatter3d_objective",
    "slice_panels_3d",
    "scatter4d_encoded",
    "slice_panels_4d_axes_x1x2_slice_x3x4",
    "slice_panels_4d_axes_x3x4_slice_x1x2",
    "parallel_topn",
    "pca_projection",
    "topn_heatmap",
]


def get_bbo_tuning(func_id: int, week: int | None = None) -> dict:
    cfg = dict(DEFAULT_TUNING)
    active_week = RUN_WEEK if week is None else int(week)
    prior_weeks = sorted(w for w in TUNING_BY_WEEK if w <= active_week)
    if prior_weeks:
        cfg.update(TUNING_BY_WEEK[prior_weeks[-1]].get(int(func_id), {}))
    return cfg


def fit_gp_surrogate(X: np.ndarray, y: np.ndarray, func_id=None, random_state: int = 0):
    X = np.asarray(X, dtype=float)
    y = np.asarray(y, dtype=float).ravel()

    y_mean = float(y.mean())
    y_std = float(y.std()) if float(y.std()) > 0 else 1.0
    y_scaled = (y - y_mean) / y_std

    d = X.shape[1]
    cfg = get_bbo_tuning(int(func_id), week=RUN_WEEK)
    ls_lo, ls_hi = cfg["length_scale_bounds"]
    noise_level = cfg["noise_level"]

    kernel = (
        C(1.0, (1e-3, 1e3))
        * Matern(length_scale=np.ones(d), length_scale_bounds=(ls_lo, ls_hi), nu=2.5)
        + WhiteKernel(noise_level=noise_level, noise_level_bounds=(1e-10, 1e-1))
    )

    gp = GaussianProcessRegressor(
        kernel=kernel,
        n_restarts_optimizer=cfg["n_restarts_optimizer"],
        random_state=random_state,
    )

    try:
        gp.fit(X, y_scaled)
    except Exception:
        gp = GaussianProcessRegressor(kernel=kernel, n_restarts_optimizer=2, random_state=random_state)
        gp.fit(X, y_scaled)

    return gp, y_mean, y_std


def repo_root_from_arg(path_str: str) -> Path:
    root = Path(path_str).resolve()
    if (root / "data" / "initial_data").exists() and (root / "scripts" / "bbo_plotting_patch.py").exists():
        return root
    if (root / "CapStone_BBO_git" / "data" / "initial_data").exists():
        return root / "CapStone_BBO_git"
    raise FileNotFoundError("Could not locate repo root containing data/initial_data and scripts/bbo_plotting_patch.py")


def expected_size(func_id: int, week_num: int) -> int:
    return int(INITIAL_SIZES[func_id][0] + week_num)


def trim_data_for_week(repo_root: Path, temp_data_root: Path, week_num: int) -> None:
    source_root = repo_root / "data" / "initial_data"
    if temp_data_root.exists():
        shutil.rmtree(temp_data_root)
    temp_data_root.mkdir(parents=True, exist_ok=True)

    for func_id in range(1, 9):
        src_dir = source_root / f"function_{func_id}"
        dst_dir = temp_data_root / f"function_{func_id}"
        dst_dir.mkdir(parents=True, exist_ok=True)

        X = np.load(src_dir / "initial_inputs.npy")
        y = np.load(src_dir / "initial_outputs.npy")
        keep = expected_size(func_id, week_num)

        if len(X) < keep or len(y) < keep:
            raise ValueError(
                f"Function {func_id}: need {keep} rows for week {week_num:02d}, found X={len(X)}, y={len(y)}"
            )

        np.save(dst_dir / "initial_inputs.npy", X[:keep])
        np.save(dst_dir / "initial_outputs.npy", y[:keep])


def clean_enhanced_outputs(plot_week_dir: Path) -> None:
    if not plot_week_dir.exists():
        return
    for func_id in range(1, 9):
        for suffix in ENHANCED_SUFFIXES:
            for candidate in plot_week_dir.glob(f"function_{func_id}_{suffix}*.png"):
                candidate.unlink()


def run_week(repo_root: Path, week_num: int, overwrite: bool) -> list[Path]:
    scripts_dir = repo_root / "scripts"
    sys.path.insert(0, str(scripts_dir))
    import bbo_plotting_patch as plotting_patch

    temp_data_root = repo_root / "data" / "_temp_backfill_initial_data"
    trim_data_for_week(repo_root, temp_data_root, week_num)

    target_dir = repo_root / "data" / "plots" / "historical" / f"week_{week_num:02d}"
    if overwrite:
        clean_enhanced_outputs(target_dir)

    try:
        outputs = plotting_patch.generate_enhanced_plots(
            DATA_ROOT=temp_data_root,
            PLOTS_DIR=repo_root / "data" / "plots",
            INITIAL_SIZES=INITIAL_SIZES,
            FUNCTION_DESCRIPTIONS=FUNCTION_DESCRIPTIONS,
            fit_gp_surrogate=fit_gp_surrogate,
            week_num=week_num,
            show_inline=False,
        )
    finally:
        if temp_data_root.exists():
            shutil.rmtree(temp_data_root)

    flattened = []
    for _, paths in outputs.items():
        flattened.extend(Path(p) for p in paths)
    return flattened


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Backfill enhanced historical BBO plots using week-correct sliced data.")
    parser.add_argument("--repo-root", default=".", help="Path to CapStone_BBO_git repo root, or parent folder containing it.")
    parser.add_argument("--week", type=int, help="Single week number to rebuild.")
    parser.add_argument("--start-week", type=int, help="Start week for range rebuild.")
    parser.add_argument("--end-week", type=int, help="End week for range rebuild.")
    parser.add_argument("--overwrite", action="store_true", help="Delete existing enhanced PNGs for target week(s) before regenerating.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = repo_root_from_arg(args.repo_root)

    if args.week is not None:
        weeks = [args.week]
    else:
        start = 1 if args.start_week is None else args.start_week
        end = 8 if args.end_week is None else args.end_week
        if start > end:
            raise ValueError("start-week cannot be greater than end-week")
        weeks = list(range(start, end + 1))

    print(f"Repo root: {repo_root}")
    print(f"Weeks to rebuild: {weeks}")
    print(f"Overwrite enhanced plots: {args.overwrite}")

    total = 0
    for week_num in weeks:
        outputs = run_week(repo_root, week_num, overwrite=args.overwrite)
        total += len(outputs)
        print(f"Week {week_num:02d}: generated {len(outputs)} enhanced plot files")

    print(f"Done. Generated {total} enhanced plot files in total.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
