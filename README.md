# capstone-bbo
Capstone project: Black-Box Bayesian Optimisation

# Capstone: Bayesian Black-Box Optimisation (BBO)

## Overview
This capstone tackles eight synthetic black-box optimisation problems where the function forms are unknown and evaluations are limited (one new query per function per week). I use Bayesian Optimisation with Gaussian Process surrogate models to propose the next input points, balancing exploration and exploitation via standard acquisition functions. The main deliverable is a reproducible weekly loop that ingests portal results, refits models, generates the next submissions in the required format, and logs plots and artefacts for auditability.

Problem: “Optimise unknown black-box functions under a strict evaluation budget.”

Approach: “Gaussian Process surrogate + acquisition function (EI/UCB/PI).”

Result: “Best score achieved and any headline behaviour.”


## What is in this repository
- `notebooks/` – main workflow notebook: `CapStone_BBO_Complete_Workflow2.ipynb`
- `docs/non_technical_writeup.md` – non-technical explanation of approach and results
- `docs/data_sheet_capstone_bbo.md` – dataset datasheet (limitations and bias)
- `docs/model_card_capstone_bbo.md` – model card (intended use, evaluation, limits)
- `data/README.md` – data description and how to reproduce
- `src/` / `scripts/` – reusable code and helper scripts (if used)
- `outputs/` – logs/reports (not committed by default)

## Quickstart (run locally)

### Setup
1. Install Python 3.10+.
2. Create and activate a virtual environment:
   - Windows (PowerShell):
     - `python -m venv .venv`
     - `.venv\Scripts\Activate.ps1`
   - macOS/Linux:
     - `python3 -m venv .venv`
     - `source .venv/bin/activate`
3. Install dependencies:
   - `pip install -r requirements.txt`

### Run
- Open and run the main notebook:
  - `notebooks/CapStone_BBO_Complete_Workflow2.ipynb`

## Data
Large datasets are not stored in GitHub. See `data/README.md` for:
- what data exists,
- **What data exists**
  - `initial_data/` (starter pack from the course):
    - `initial_data/function_k/initial_inputs.npy`
    - `initial_data/function_k/initial_outputs.npy`
  - `submissions/week_XX/` (weekly artefacts):
    - `inputs.txt` (proposed portal submissions)
    - `outputs.txt` (returned portal values)
    - `Week*.txt` (portal confirmation downloads, if saved)
  - `plots/` and `logs/` (derived artefacts):
    - progress plots, historical plots, and JSON run logs

- where it comes from,
- **Where it comes from**
  - Initial `.npy` files come from the course starter zip (`Initial_data_points_starter.zip`).
  - Weekly outputs come from the capstone submission portal.

- how to reproduce it.
- **How to reproduce it**
  - Start by placing the starter pack into `initial_data/` with the expected per-function subfolders.
  - Each week:
    1) Run the notebook for Week N  
    2) Submit Week N+1 points (from `submissions/week_{N+1:02d}/inputs.txt`)  
    3) Save returned values into `submissions/week_{N+1:02d}/outputs.txt`  
    4) Repeat  
  - Because the notebook writes backups before every append, you can always roll back if needed.

## Key documents
- Non-technical write-up: `docs/non_technical_writeup.md`
- Data sheet: `docs/data_sheet_capstone_bbo.md`
- Model card: `docs/model_card_capstone_bbo.md`

## Key documents
- Non-technical write-up: `docs/non_technical_writeup.md`  
  Plain-English narrative of the problem, the BO loop, and what changed week to week.

- Data sheet: `docs/data_sheet_capstone_bbo.md`  
  What the data is, how it was collected (portal loop), limitations, and bias/coverage notes.

- Model card: `docs/model_card_capstone_bbo.md`  
  Intended use, evaluation approach, key assumptions (black-box, limited evaluations), and known failure modes.
