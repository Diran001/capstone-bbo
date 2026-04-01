"""
Enhanced plotting patch for CapStone_BBO_Workflow.ipynb
Tailored to the repo structure in CapStone_BBO_git.

Usage in notebook:
    # after your existing imports / GP functions are defined
    from bbo_plotting_patch import *

    # then call
    generate_enhanced_plots(week_num=week_num, show_inline=True)

This module expects these notebook globals to exist:
    DATA_ROOT, PLOTS_DIR, INITIAL_SIZES, FUNCTION_DESCRIPTIONS,
    fit_gp_surrogate, get_bbo_tuning
"""

from __future__ import annotations

import math
from pathlib import Path
from typing import Iterable, Optional, Sequence, Tuple

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize
from matplotlib.cm import ScalarMappable
from pandas import DataFrame

try:
    import pandas as pd
except Exception:  # pragma: no cover
    pd = None

from sklearn.decomposition import PCA


# -----------------------------------------------------------------------------
# Data helpers
# -----------------------------------------------------------------------------

def _load_function_data(DATA_ROOT: Path, func_id: int) -> tuple[np.ndarray, np.ndarray]:
    fdir = Path(DATA_ROOT) / f"function_{func_id}"
    X = np.load(fdir / "initial_inputs.npy")
    y = np.load(fdir / "initial_outputs.npy")
    return np.asarray(X, dtype=float), np.asarray(y, dtype=float).ravel()


def _best_idx(y: np.ndarray) -> int:
    return int(np.nanargmax(y))


def _week_indices(initial_size: int, n_total: int) -> np.ndarray:
    return np.arange(1, n_total - initial_size + 1)


def _save_figure(fig, PLOTS_DIR: Path, func_id: int, name: str, week_num: Optional[int] = None, dpi: int = 160):
    if week_num is not None:
        save_dir = Path(PLOTS_DIR) / "historical" / f"week_{week_num:02d}"
    else:
        save_dir = Path(PLOTS_DIR) / "current"
    save_dir.mkdir(parents=True, exist_ok=True)

    base = save_dir / f"function_{func_id}_{name}.png"
    out = base
    version = 2
    while out.exists():
        out = save_dir / f"function_{func_id}_{name}_v{version}.png"
        version += 1

    fig.savefig(out, dpi=dpi, bbox_inches="tight")
    return out


# -----------------------------------------------------------------------------
# GP grid prediction helpers
# -----------------------------------------------------------------------------

def _fit_plot_gp(fit_gp_surrogate, X: np.ndarray, y: np.ndarray, func_id: int):
    gp, y_mean, y_std = fit_gp_surrogate(X, y, func_id=func_id, random_state=42)
    return gp, float(y_mean), float(y_std)


def _predict_unscaled(gp, pts: np.ndarray, y_mean: float, y_std: float):
    mu, sigma = gp.predict(pts, return_std=True)
    mu = y_mean + y_std * np.asarray(mu)
    sigma = y_std * np.asarray(sigma)
    return mu, sigma


def _grid2d(x_range=(0.0, 1.0), y_range=(0.0, 1.0), n: int = 80):
    xs = np.linspace(*x_range, n)
    ys = np.linspace(*y_range, n)
    XX, YY = np.meshgrid(xs, ys)
    return xs, ys, XX, YY


def _slice_grid_predict(
    gp,
    y_mean: float,
    y_std: float,
    d: int,
    axis_pair: tuple[int, int],
    fixed_values: np.ndarray,
    n_grid: int = 70,
):
    i, j = axis_pair
    xs, ys, XX, YY = _grid2d(n=n_grid)
    pts = np.tile(np.asarray(fixed_values, dtype=float), (XX.size, 1))
    pts[:, i] = XX.ravel()
    pts[:, j] = YY.ravel()
    mu, sigma = _predict_unscaled(gp, pts, y_mean, y_std)
    return XX, YY, mu.reshape(XX.shape), sigma.reshape(XX.shape)


# -----------------------------------------------------------------------------
# Plot primitives
# -----------------------------------------------------------------------------

def plot_progress_with_observations(
    DATA_ROOT,
    PLOTS_DIR,
    INITIAL_SIZES,
    FUNCTION_DESCRIPTIONS,
    func_id: int,
    week_num: Optional[int] = None,
    show_inline: bool = True,
):
    X, y = _load_function_data(DATA_ROOT, func_id)
    bsf = np.maximum.accumulate(y)
    initial_size = INITIAL_SIZES[func_id][0]
    weeks_added = len(y) - initial_size

    fig, ax = plt.subplots(figsize=(10, 5.5))
    ax.plot(np.arange(1, len(y) + 1), y, marker="o", linewidth=1.2, alpha=0.7, label="Observed y")
    ax.plot(np.arange(1, len(y) + 1), bsf, linewidth=2.5, label="Best so far")
    ax.axvline(initial_size, linestyle="--", alpha=0.7, label="Initial data")

    bi = _best_idx(y)
    ax.scatter(bi + 1, y[bi], s=120, marker="*", zorder=5, label=f"Best = {y[bi]:+.6f}")

    ax.set_xlabel("Evaluation count")
    ax.set_ylabel("Objective value")
    ax.set_title(
        f"Function {func_id}: {FUNCTION_DESCRIPTIONS[func_id]}\n"
        f"Observed values and best-so-far ({weeks_added} week{'s' if weeks_added != 1 else ''})"
    )
    ax.grid(True, alpha=0.25, linestyle="--")
    ax.legend(loc="best")
    fig.tight_layout()

    out = _save_figure(fig, PLOTS_DIR, func_id, "progress_enhanced", week_num)
    if show_inline:
        plt.show()
    else:
        plt.close(fig)
    return out


def plot_2d_surface_and_contour(
    DATA_ROOT,
    PLOTS_DIR,
    FUNCTION_DESCRIPTIONS,
    fit_gp_surrogate,
    func_id: int,
    week_num: Optional[int] = None,
    show_inline: bool = True,
    n_grid: int = 80,
):
    X, y = _load_function_data(DATA_ROOT, func_id)
    if X.shape[1] != 2:
        raise ValueError(f"Function {func_id} is not 2D")

    gp, y_mean, y_std = _fit_plot_gp(fit_gp_surrogate, X, y, func_id)
    XX, YY, MU, SIG = _slice_grid_predict(gp, y_mean, y_std, 2, (0, 1), np.array([0.5, 0.5]), n_grid=n_grid)

    best = _best_idx(y)

    fig = plt.figure(figsize=(15, 5.5))

    ax1 = fig.add_subplot(1, 2, 1)
    cf = ax1.contourf(XX, YY, MU, levels=20)
    ax1.contour(XX, YY, MU, levels=10, linewidths=0.6, alpha=0.6)
    ax1.scatter(X[:, 0], X[:, 1], c=y, edgecolor="black", s=50)
    ax1.scatter(X[best, 0], X[best, 1], marker="*", s=200, edgecolor="black")
    ax1.set_xlabel("x1")
    ax1.set_ylabel("x2")
    ax1.set_title("GP mean contour + sampled points")
    fig.colorbar(cf, ax=ax1, shrink=0.9, label="Predicted objective")

    ax2 = fig.add_subplot(1, 2, 2, projection="3d")
    surf = ax2.plot_surface(XX, YY, MU, linewidth=0, antialiased=True, alpha=0.85)
    ax2.scatter(X[:, 0], X[:, 1], y, s=28, depthshade=True)
    ax2.scatter(X[best, 0], X[best, 1], y[best], marker="*", s=220, depthshade=True)
    ax2.set_xlabel("x1")
    ax2.set_ylabel("x2")
    ax2.set_zlabel("Objective")
    ax2.set_title("GP mean surface")
    fig.colorbar(surf, ax=ax2, shrink=0.75, pad=0.1, label="Predicted objective")

    fig.suptitle(f"Function {func_id}: {FUNCTION_DESCRIPTIONS[func_id]}", fontsize=14)
    fig.tight_layout()
    out = _save_figure(fig, PLOTS_DIR, func_id, "surface_contour", week_num)
    if show_inline:
        plt.show()
    else:
        plt.close(fig)
    return out


def plot_3d_scatter_coloured(
    DATA_ROOT,
    PLOTS_DIR,
    FUNCTION_DESCRIPTIONS,
    func_id: int,
    week_num: Optional[int] = None,
    show_inline: bool = True,
):
    X, y = _load_function_data(DATA_ROOT, func_id)
    d = X.shape[1]
    if d < 3:
        raise ValueError(f"Function {func_id} has only {d} dimensions")

    best = _best_idx(y)
    fig = plt.figure(figsize=(8.5, 6.5))
    ax = fig.add_subplot(111, projection="3d")
    sc = ax.scatter(X[:, 0], X[:, 1], X[:, 2], c=y, s=55, depthshade=True)
    ax.scatter(X[best, 0], X[best, 1], X[best, 2], marker="*", s=220, edgecolor="black")
    ax.set_xlabel("x1")
    ax.set_ylabel("x2")
    ax.set_zlabel("x3")
    ax.set_title(f"Function {func_id}: 3D input scatter coloured by objective")
    fig.colorbar(sc, ax=ax, shrink=0.8, pad=0.08, label="Observed objective")
    fig.tight_layout()

    out = _save_figure(fig, PLOTS_DIR, func_id, "scatter3d_objective", week_num)
    if show_inline:
        plt.show()
    else:
        plt.close(fig)
    return out


def plot_4d_encoded_scatter(
    DATA_ROOT,
    PLOTS_DIR,
    FUNCTION_DESCRIPTIONS,
    func_id: int,
    week_num: Optional[int] = None,
    show_inline: bool = True,
):
    X, y = _load_function_data(DATA_ROOT, func_id)
    if X.shape[1] < 4:
        raise ValueError(f"Function {func_id} has fewer than 4 dimensions")

    best = _best_idx(y)
    fig = plt.figure(figsize=(8.8, 6.6))
    ax = fig.add_subplot(111, projection="3d")
    sc = ax.scatter(X[:, 0], X[:, 1], X[:, 2], c=X[:, 3], s=45 + 80 * (y - y.min()) / max(1e-12, (y.max() - y.min())), alpha=0.9)
    ax.scatter(X[best, 0], X[best, 1], X[best, 2], marker="*", s=240, edgecolor="black")
    ax.set_xlabel("x1")
    ax.set_ylabel("x2")
    ax.set_zlabel("x3")
    ax.set_title(f"Function {func_id}: x1-x2-x3 with colour=x4 and size=objective")
    fig.colorbar(sc, ax=ax, shrink=0.8, pad=0.08, label="x4")
    fig.tight_layout()

    out = _save_figure(fig, PLOTS_DIR, func_id, "scatter4d_encoded", week_num)
    if show_inline:
        plt.show()
    else:
        plt.close(fig)
    return out


def plot_3var_slice_panels(
    DATA_ROOT,
    PLOTS_DIR,
    FUNCTION_DESCRIPTIONS,
    fit_gp_surrogate,
    func_id: int,
    week_num: Optional[int] = None,
    show_inline: bool = True,
    axis_pair: tuple[int, int] = (0, 1),
    sliced_dim: int = 2,
    slice_values: Sequence[float] = (0.1, 0.5, 0.9),
    n_grid: int = 70,
):
    X, y = _load_function_data(DATA_ROOT, func_id)
    if X.shape[1] != 3:
        raise ValueError(f"Function {func_id} is not 3D")

    gp, y_mean, y_std = _fit_plot_gp(fit_gp_surrogate, X, y, func_id)
    base = X[_best_idx(y)].copy()

    fig, axes = plt.subplots(1, len(slice_values), figsize=(5.4 * len(slice_values), 4.8), sharex=True, sharey=True)
    if len(slice_values) == 1:
        axes = [axes]

    for ax, sval in zip(axes, slice_values):
        fixed = base.copy()
        fixed[sliced_dim] = float(sval)
        XX, YY, MU, _ = _slice_grid_predict(gp, y_mean, y_std, 3, axis_pair, fixed, n_grid=n_grid)
        cf = ax.contourf(XX, YY, MU, levels=20)

        mask = np.abs(X[:, sliced_dim] - sval) <= 0.18
        ax.scatter(X[mask, axis_pair[0]], X[mask, axis_pair[1]], c=y[mask], edgecolor="black", s=40)
        ax.set_title(f"x{sliced_dim+1} = {sval:.2f}")
        ax.set_xlabel(f"x{axis_pair[0]+1}")
        ax.set_ylabel(f"x{axis_pair[1]+1}")

    fig.colorbar(cf, ax=axes, shrink=0.85, label="Predicted objective")
    fig.suptitle(f"Function {func_id}: conditional slice panels for 3D input", fontsize=14)
    fig.tight_layout()

    out = _save_figure(fig, PLOTS_DIR, func_id, "slice_panels_3d", week_num)
    if show_inline:
        plt.show()
    else:
        plt.close(fig)
    return out


def plot_4d_slice_panels(
    DATA_ROOT,
    PLOTS_DIR,
    FUNCTION_DESCRIPTIONS,
    fit_gp_surrogate,
    func_id: int,
    week_num: Optional[int] = None,
    show_inline: bool = True,
    axis_pair: tuple[int, int] = (0, 1),
    slice_dims: tuple[int, int] = (2, 3),
    slice_values: Sequence[float] = (0.1, 0.9),
    n_grid: int = 70,
):
    X, y = _load_function_data(DATA_ROOT, func_id)
    if X.shape[1] < 4:
        raise ValueError(f"Function {func_id} has fewer than 4 dimensions")

    gp, y_mean, y_std = _fit_plot_gp(fit_gp_surrogate, X, y, func_id)
    base = X[_best_idx(y)].copy()
    v1, v2 = slice_values

    fig, axes = plt.subplots(2, 2, figsize=(12, 10), sharex=True, sharey=True)
    panel_values = [(v1, v1), (v1, v2), (v2, v1), (v2, v2)]

    for ax, (s1, s2) in zip(axes.ravel(), panel_values):
        fixed = base.copy()
        fixed[slice_dims[0]] = float(s1)
        fixed[slice_dims[1]] = float(s2)
        XX, YY, MU, _ = _slice_grid_predict(gp, y_mean, y_std, X.shape[1], axis_pair, fixed, n_grid=n_grid)
        cf = ax.contourf(XX, YY, MU, levels=20)

        mask = (np.abs(X[:, slice_dims[0]] - s1) <= 0.20) & (np.abs(X[:, slice_dims[1]] - s2) <= 0.20)
        if np.any(mask):
            ax.scatter(X[mask, axis_pair[0]], X[mask, axis_pair[1]], c=y[mask], edgecolor="black", s=36)

        ax.set_title(
            f"x{slice_dims[0]+1} = {s1:.2f}, x{slice_dims[1]+1} = {s2:.2f}"
        )
        ax.set_xlabel(f"x{axis_pair[0]+1}")
        ax.set_ylabel(f"x{axis_pair[1]+1}")

    fig.colorbar(cf, ax=axes.ravel().tolist(), shrink=0.86, label="Predicted objective")
    fig.suptitle(
        f"Function {func_id}: 4D conditional slice comparison over x{axis_pair[0]+1}-x{axis_pair[1]+1}",
        fontsize=14,
    )
    fig.tight_layout()

    axis_name = f"axes_x{axis_pair[0]+1}x{axis_pair[1]+1}_slice_x{slice_dims[0]+1}x{slice_dims[1]+1}"
    out = _save_figure(fig, PLOTS_DIR, func_id, f"slice_panels_4d_{axis_name}", week_num)
    if show_inline:
        plt.show()
    else:
        plt.close(fig)
    return out


def plot_parallel_coordinates_topn(
    DATA_ROOT,
    PLOTS_DIR,
    FUNCTION_DESCRIPTIONS,
    func_id: int,
    week_num: Optional[int] = None,
    show_inline: bool = True,
    top_n: int = 20,
):
    X, y = _load_function_data(DATA_ROOT, func_id)
    d = X.shape[1]

    order = np.argsort(y)[-min(top_n, len(y)):]
    X_top = X[order]
    y_top = y[order]

    fig, ax = plt.subplots(figsize=(max(10, d * 1.2), 5.8))
    norm = Normalize(vmin=float(y_top.min()), vmax=float(y_top.max()))
    cmap = plt.cm.viridis
    xs = np.arange(d)

    for row, yi in zip(X_top, y_top):
        ax.plot(xs, row, alpha=0.75, linewidth=1.5, color=cmap(norm(float(yi))))

    ax.set_xticks(xs)
    ax.set_xticklabels([f"x{i+1}" for i in range(d)])
    ax.set_ylim(0.0, 1.0)
    ax.set_ylabel("Input value")
    ax.set_title(f"Function {func_id}: parallel coordinates for top {len(order)} points")
    ax.grid(True, axis="y", alpha=0.25, linestyle="--")

    sm = ScalarMappable(norm=norm, cmap=cmap)
    sm.set_array([])
    fig.colorbar(sm, ax=ax, label="Observed objective")
    fig.tight_layout()

    out = _save_figure(fig, PLOTS_DIR, func_id, "parallel_topn", week_num)
    if show_inline:
        plt.show()
    else:
        plt.close(fig)
    return out


def plot_pca_projection(
    DATA_ROOT,
    PLOTS_DIR,
    FUNCTION_DESCRIPTIONS,
    func_id: int,
    week_num: Optional[int] = None,
    show_inline: bool = True,
):
    X, y = _load_function_data(DATA_ROOT, func_id)
    if X.shape[1] < 3:
        raise ValueError(f"Function {func_id} has too few dimensions for a meaningful PCA view")

    pca = PCA(n_components=2, random_state=42)
    Z = pca.fit_transform(X)
    best = _best_idx(y)

    fig, ax = plt.subplots(figsize=(7.2, 5.8))
    sc = ax.scatter(Z[:, 0], Z[:, 1], c=y, s=55)
    ax.scatter(Z[best, 0], Z[best, 1], marker="*", s=240, edgecolor="black")
    ax.set_xlabel(f"PC1 ({100*pca.explained_variance_ratio_[0]:.1f}% var)")
    ax.set_ylabel(f"PC2 ({100*pca.explained_variance_ratio_[1]:.1f}% var)")
    ax.set_title(f"Function {func_id}: PCA projection of sampled input space")
    ax.grid(True, alpha=0.25, linestyle="--")
    fig.colorbar(sc, ax=ax, label="Observed objective")
    fig.tight_layout()

    out = _save_figure(fig, PLOTS_DIR, func_id, "pca_projection", week_num)
    if show_inline:
        plt.show()
    else:
        plt.close(fig)
    return out


def plot_topn_coordinate_heatmap(
    DATA_ROOT,
    PLOTS_DIR,
    FUNCTION_DESCRIPTIONS,
    func_id: int,
    week_num: Optional[int] = None,
    show_inline: bool = True,
    top_n: int = 20,
):
    X, y = _load_function_data(DATA_ROOT, func_id)
    d = X.shape[1]
    order = np.argsort(y)[-min(top_n, len(y)):][::-1]
    X_top = X[order]
    y_top = y[order]

    fig, ax = plt.subplots(figsize=(max(8, d * 1.1), max(5, len(order) * 0.28)))
    im = ax.imshow(X_top, aspect="auto", interpolation="nearest")
    ax.set_xticks(np.arange(d))
    ax.set_xticklabels([f"x{i+1}" for i in range(d)])
    ax.set_yticks(np.arange(len(order)))
    ax.set_yticklabels([f"#{r+1} | y={y_top[r]:+.3f}" for r in range(len(order))])
    ax.set_title(f"Function {func_id}: coordinate heatmap for top {len(order)} points")
    ax.set_xlabel("Input dimension")
    ax.set_ylabel("Ranked sampled points")
    fig.colorbar(im, ax=ax, label="Input value")
    fig.tight_layout()

    out = _save_figure(fig, PLOTS_DIR, func_id, "topn_heatmap", week_num)
    if show_inline:
        plt.show()
    else:
        plt.close(fig)
    return out


# -----------------------------------------------------------------------------
# Orchestration
# -----------------------------------------------------------------------------

def generate_enhanced_plots(
    DATA_ROOT,
    PLOTS_DIR,
    INITIAL_SIZES,
    FUNCTION_DESCRIPTIONS,
    fit_gp_surrogate,
    week_num: Optional[int] = None,
    show_inline: bool = True,
):
    """
    Generate a dimension-appropriate plot set for all functions.

    Returns a dict of function_id -> list[path].
    """
    outputs = {}

    for func_id in range(1, 9):
        X, y = _load_function_data(DATA_ROOT, func_id)
        d = X.shape[1]
        paths = []

        paths.append(plot_progress_with_observations(
            DATA_ROOT, PLOTS_DIR, INITIAL_SIZES, FUNCTION_DESCRIPTIONS, func_id, week_num, show_inline
        ))

        if d == 2:
            paths.append(plot_2d_surface_and_contour(
                DATA_ROOT, PLOTS_DIR, FUNCTION_DESCRIPTIONS, fit_gp_surrogate, func_id, week_num, show_inline
            ))

        elif d == 3:
            paths.append(plot_3d_scatter_coloured(
                DATA_ROOT, PLOTS_DIR, FUNCTION_DESCRIPTIONS, func_id, week_num, show_inline
            ))
            paths.append(plot_3var_slice_panels(
                DATA_ROOT, PLOTS_DIR, FUNCTION_DESCRIPTIONS, fit_gp_surrogate, func_id, week_num, show_inline
            ))

        elif d == 4:
            paths.append(plot_4d_encoded_scatter(
                DATA_ROOT, PLOTS_DIR, FUNCTION_DESCRIPTIONS, func_id, week_num, show_inline
            ))
            paths.append(plot_4d_slice_panels(
                DATA_ROOT, PLOTS_DIR, FUNCTION_DESCRIPTIONS, fit_gp_surrogate, func_id, week_num, show_inline
            ))
            # complementary view across the other pair
            paths.append(plot_4d_slice_panels(
                DATA_ROOT, PLOTS_DIR, FUNCTION_DESCRIPTIONS, fit_gp_surrogate, func_id, week_num, show_inline,
                axis_pair=(2, 3), slice_dims=(0, 1)
            ))

        else:
            # selective high-dimensional views
            paths.append(plot_parallel_coordinates_topn(
                DATA_ROOT, PLOTS_DIR, FUNCTION_DESCRIPTIONS, func_id, week_num, show_inline
            ))
            paths.append(plot_pca_projection(
                DATA_ROOT, PLOTS_DIR, FUNCTION_DESCRIPTIONS, func_id, week_num, show_inline
            ))
            paths.append(plot_topn_coordinate_heatmap(
                DATA_ROOT, PLOTS_DIR, FUNCTION_DESCRIPTIONS, func_id, week_num, show_inline
            ))
            if d >= 5:
                # conditional 4D-style panel using first four dimensions, others fixed at best point
                paths.append(plot_4d_slice_panels(
                    DATA_ROOT, PLOTS_DIR, FUNCTION_DESCRIPTIONS, fit_gp_surrogate, func_id, week_num, show_inline,
                    axis_pair=(0, 1), slice_dims=(2, 3)
                ))

        outputs[func_id] = paths

    return outputs
