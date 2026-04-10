# Black-Box Bayesian Optimisation (BBO) Capstone

## Overview

This repository contains my capstone work on Black-Box Bayesian Optimisation. The task is to optimise eight unknown black-box functions whose analytical forms are not observable. Information about each function is obtained only through interaction with the course portal: an input vector is submitted and a corresponding score is returned.

<p align="left">
  <img src="./docs/images/bbo-optimisation-loop.png" width="15%" alt="Black-Box Bayesian Optimisation Process Diagram">
  <br>
  <i><b>Figure 1:</b> The iterative Bayesian Optimisation loop: candidate inputs are evaluated, a Gaussian Process surrogate is updated, and an acquisition function selects the next query.</i>
</p>

A key practical constraint of the capstone is that only one new query per function may be submitted each week. As a result, each candidate point must be selected carefully. The workflow in this repository is therefore designed to support reproducibility, traceability, and transparent justification of optimisation choices across successive rounds.

## Research objective

The objective of this repository is to document and support a repeatable optimisation workflow for sparse, sequential black-box evaluation under a strict submission budget. The repository provides an organised environment for:

- maintaining cumulative observations for each function
- generating weekly portal-ready candidate inputs
- registering returned outputs
- tracking progress across rounds
- supporting transparent explanation of modelling and selection logic

This repository is intended as a research-focused capstone environment rather than as a general-purpose optimisation library.

## Repository structure

```text
capstone-bbo/
├── .gitignore
├── .vscode/
├── LICENSE
├── README.md
├── requirements.txt
├── notebooks/
│   └── bbo_workflow.ipynb
├── scripts/
│   ├── backfill_historical_enhanced_plots.py
│   ├── bbo_plotting_patch.py
│   ├── build_powerbi_dataset.py
│   ├── cap_scr_v010_week.cmd
│   ├── cap_scr_v010_run_week.cmd
│   ├── cap_scr_v010_prepare_week.cmd
│   ├── cap_scr_v010_register_week.cmd
│   ├── cap_scr_v010_check_week.cmd
│   ├── cap_scr_v010_status.cmd
│   ├── cap_scr_v010_copy_processed_outputs.cmd
│   └── cap_scr_v010_archive_zips.cmd
├── docs/
│   ├── CapStone_BBO_Setup_Guide.md
│   ├── README_bbo_export.md
│   ├── README_export.md
│   ├── datasheet_bbo_dataset.md
│   ├── model_card_bbo_optimisation.md
│   └── images/
│       └── bbo-optimisation-loop.png
└── data/
    ├── initial_data/
    ├── processed/
    ├── submissions/
    ├── plots/
    ├── logs/
    └── powerbi/
```

## What the notebook uses

The live notebook is `notebooks/CapStone_BBO_Workflow.ipynb`.

It works from the repository root and uses these main folders:

- `data/initial_data/` for cumulative function datasets
- `data/submissions/` for weekly portal-ready inputs and returned outputs
- `data/processed/` for manually downloaded portal return folders
- `data/plots/` for progress charts
- `data/logs/` for execution logs

Processed week folders follow this convention:

- `data/processed/Capstone_Project_WeekXXSubmissionProcessed/`

## Development environment

This repository is maintained primarily in Visual Studio Code with a Conda-managed Python environment. The project is designed to run from the repository root so that notebooks, scripts, data folders, and documentation remain consistent across weekly optimisation cycles.

Environment conventions used in this repository include:

- Visual Studio Code for development and notebook execution
- Conda for Python environment and package management
- repository-root execution for workflow consistency
- structured local folders for data, logs, plots, submissions, and documentation

Editor-specific workspace settings are generally treated as local convenience files rather than core project artefacts.

## Weekly workflow

1. Start from the current cumulative data in `data/initial_data/`.
2. Run `notebooks/CapStone_BBO_Workflow.ipynb`.
3. Generate the next portal-ready `inputs.txt`.
4. Submit one new query per function to the portal.
5. When the returned results arrive, place the processed folder under `data/processed/`.
6. Copy or register the returned `outputs.txt` into `data/submissions/week_XX/outputs.txt`.
7. Run the notebook again for the next cycle.

## Technical approach

The current workflow uses a Gaussian Process surrogate per function with acquisition-based candidate selection. 

In practical terms, the notebook uses:
- **scikit-learn Gaussian Process regression**
- **A Matérn kernel** with explicit noise handling:
  $k(x, x') = \sigma^2 \frac{2^{1-\nu}}{\Gamma(\nu)} \left( \sqrt{2\nu} \frac{d}{\rho} \right)^\nu K_\nu \left( \sqrt{2\nu} \frac{d}{\rho} \right)$
- **Acquisition rules** such as Expected Improvement (EI), Probability of Improvement (PI), and Upper Confidence Bound (UCB).
- large random candidate sampling to approximate the best next point in the bounded search space

This is a good fit for the capstone because the data is sparse and the evaluation budget is tight.

## Helper scripts

Run scripts from the repository root, for example:

```cmd
.\scripts\cap_scr_v010_week.cmd check 8
.\scripts\cap_scr_v010_status.cmd
.\scripts\cap_scr_v010_copy_processed_outputs.cmd 8
```

`cap_scr_v010_archive_zips.cmd` is an optional maintenance utility, not part of the normal weekly flow.

## Notes

This is the main public entry point for the repository. Supporting write-ups are kept in `docs/`.

## Project documentation

- [Datasheet for the BBO data set](docs/datasheet_bbo_dataset.md)
- [Model card for the BBO optimisation approach](docs/model_card_bbo_optimisation.md)

## Research context

This repository is maintained as a research-focused capstone environment for Black-Box Bayesian Optimisation. It emphasises reproducibility, function-specific tuning, historical comparison across rounds, and transparent experimental workflow design.

### *Author: Diran Afolabi*

> [!IMPORTANT]
> **Disclaimer :**
> This repository contains experimental Bayesian optimisation research prototypes developed for academic and educational purposes. It is not intended for production deployment or operational decision-making. Any results, outputs, or observations should be treated as illustrative only.
