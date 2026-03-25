# Black-Box Bayesian Optimisation (BBO) Capstone

## Project overview

This repository contains my Black-Box Bayesian Optimisation capstone work. The challenge is to optimise eight unknown black-box functions under a strict weekly evaluation budget. I can submit one new query per function per week, so the workflow has to be sample-efficient and operationally disciplined.

## Live repository structure

The live repository is organised around the actual working flow:

- `notebooks/CapStone_BBO_Workflow.ipynb` as the main workflow notebook
- `data/initial_data/` for cumulative function datasets
- `data/submissions/` for weekly portal-ready inputs and returned outputs
- `data/processed/` for manually downloaded portal-return folders
- `data/plots/` for progress visualisations
- `data/logs/` for execution records

Processed week folders follow the convention:

- `data/processed/Capstone_Project_WeekXXSubmissionProcessed/`

## Modelling approach

The project uses a Gaussian Process surrogate with acquisition-driven candidate search. This is a better fit for the capstone than a large deep learning stack because the data is sparse and each weekly submission is expensive.

## Practical workflow

1. Load cumulative data from `data/initial_data/`
2. Process prior weekly results if available
3. Fit/update the surrogate models
4. Generate the next week of candidate points
5. Save portal-ready files under `data/submissions/week_XX/`
6. After the portal return is received, place the files under `data/processed/Capstone_Project_WeekXXSubmissionProcessed/`
7. Use the helper scripts to register and check the weekly state

## Notes

This file is a supporting project summary. The main repository entry point should remain `README.md`.
