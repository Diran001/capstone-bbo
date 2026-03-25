# Black-Box Bayesian Optimisation (BBO) Capstone

## Overview

This repository contains my Black-Box Bayesian Optimisation capstone work. The task is to optimise eight unknown black-box functions where I cannot see the function equations. I only learn by submitting an input vector and receiving a score back from the course portal. The practical constraint is that I can submit one new query per function per week, so each query has to be chosen carefully.

The workflow is built to be repeatable, traceable, and easy to defend. The notebook handles the modelling logic. The folder structure and helper scripts keep the weekly process organised.

## Live repository structure

```text
CapStone_BBO/
├── .gitignore
├── LICENSE
├── README.md
├── requirements.txt
├── notebooks/
│   └── CapStone_BBO_Workflow.ipynb
├── scripts/
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
│   └── README_export.md
└── data/
    ├── initial_data/
    ├── processed/
    ├── submissions/
    ├── plots/
    └── logs/
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

## Weekly workflow

1. Start from the current cumulative data in `data/initial_data/`.
2. Run `notebooks/CapStone_BBO_Workflow.ipynb`.
3. Generate the next portal-ready `inputs.txt`.
4. Submit one new query per function to the portal.
5. When the returned results arrive, place the processed folder under `data/processed/`.
6. Copy or register the returned `outputs.txt` into `data/submissions/week_XX/outputs.txt`.
7. Run the notebook again for the next cycle.

## Technical approach

The current workflow uses a Gaussian Process surrogate per function with acquisition-based candidate selection. In practical terms, the notebook uses:

- scikit-learn Gaussian Process regression
- a Matérn kernel with explicit noise handling
- acquisition rules such as Expected Improvement, Probability of Improvement, and Upper Confidence Bound
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
