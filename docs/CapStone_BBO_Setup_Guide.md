# CapStone_BBO - Project Structure and Setup Guide

## Overview

This guide describes the live structure for the Black-Box Bayesian Optimisation capstone repository.

The working assumptions are simple:

- the main workflow notebook sits in `notebooks/`
- cumulative data lives in `data/initial_data/`
- weekly submissions live in `data/submissions/`
- processed portal-return folders live in `data/processed/`
- plots and logs are generated into `data/plots/` and `data/logs/`

The aim is a structure that is clean enough for GitHub, but still practical for weekly execution.

## Project structure

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
    │   ├── function_1/
    │   ├── function_2/
    │   ├── ...
    │   └── function_8/
    ├── submissions/
    │   ├── week_01/
    │   ├── week_02/
    │   └── ...
    ├── processed/
    │   ├── Capstone_Project_Week01SubmissionProcessed/
    │   ├── ...
    │   └── Capstone_Project_Week08SubmissionProcessed/
    ├── plots/
    │   ├── current/
    │   └── historical/
    └── logs/
```

## Initial setup

### Step 1: Open the repo root

Use the repository root as the working folder:

```text
C:\Users\Diran\Coursework\CapStone_BBO\
```

### Step 2: Open the notebook from the repo root

Open VS Code or Jupyter at the repository root, then open:

```text
notebooks\CapStone_BBO_Workflow.ipynb
```

### Step 3: Ensure the runtime folders exist

The notebook and scripts expect:

- `data/initial_data/`
- `data/submissions/`
- `data/processed/`
- `data/plots/`
- `data/logs/`

### Step 4: Populate `data/initial_data/`

The notebook expects the cumulative function data under:

```text
data\initial_data\function_1\
...
data\initial_data\function_8\
```

Each function folder should contain the current NumPy input and output arrays used by the workflow.

## What the live notebook expects

The main notebook works from the repository root and expects the `data/` layout above.

## Weekly operating sequence

### A. Generate the next submission

1. Open the repository root.
2. Open `notebooks/CapStone_BBO_Workflow.ipynb`.
3. Set the correct week number in the notebook.
4. Run the workflow to generate the next portal-ready `inputs.txt`.
5. The generated proposal file should be written under `data\submissions\week_XX\inputs.txt`.

### B. Submit to the portal

Submit the eight lines from `data\submissions\week_XX\inputs.txt` to the course portal.

### C. Store the returned portal results

When the portal return arrives, place the returned processed folder under:

```text
data\processed\Capstone_Project_WeekXXSubmissionProcessed\
```

Use the underscore convention consistently.

### D. Copy or register the returned outputs

If needed, use the helper script to validate and copy the returned outputs into the canonical weekly location:

```cmd
.\scripts\cap_scr_v010_copy_processed_outputs.cmd 8
```

This updates `data\submissions\week_08\outputs.txt`.

### E. Continue the cycle

Once `data\submissions\week_XX\outputs.txt` is in place, rerun the notebook to update cumulative data and generate the next week's proposal.

## Script usage

Run scripts from the repository root.

### Main wrapper

```cmd
.\scripts\cap_scr_v010_week.cmd prepare 8
.\scripts\cap_scr_v010_week.cmd register 8
.\scripts\cap_scr_v010_week.cmd check 8
.\scripts\cap_scr_v010_week.cmd status
.\scripts\cap_scr_v010_week.cmd run 8
```

### Convenience wrappers

```cmd
.\scripts\cap_scr_v010_prepare_week.cmd 8
.\scripts\cap_scr_v010_register_week.cmd 8
.\scripts\cap_scr_v010_check_week.cmd 8
.\scripts\cap_scr_v010_status.cmd
.\scripts\cap_scr_v010_run_week.cmd 8
```

### Archive utility

`cap_scr_v010_archive_zips.cmd` is an optional maintenance script for tidying root-level zip clutter. It is not part of the normal weekly run flow.
