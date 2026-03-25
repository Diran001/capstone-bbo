# Black-Box Bayesian Optimisation (BBO) Capstone

## Section 1: Project overview

### What this is

This repository contains my Black-Box Bayesian Optimisation capstone work. The task is to optimise eight unknown black-box functions where I cannot see the function equations and I only learn by submitting an input vector and receiving a score back from the course portal. The hard constraint is that I can submit one new query per function per week, so every query has to count.

### Overall goal and why it matters

The overall goal is to find high-scoring inputs under a strict evaluation budget. This is directly relevant to real-world ML and engineering because many objectives are expensive, slow, or risky to evaluate. In these settings, sample-efficient decision-making matters more than brute-force search.

## Section 2: Live working layout

The live repository uses the following working structure:

- `notebooks/CapStone_BBO_Workflow.ipynb`
- `data/initial_data/` for cumulative datasets
- `data/processed/Capstone_Project_WeekXXSubmissionProcessed/` for returned portal files
- `data/submissions/week_XX/` for canonical weekly inputs and outputs
- `data/plots/` for progress charts
- `data/logs/` for execution records

## Section 3: Method

The modelling workflow uses a Gaussian Process surrogate and acquisition-based candidate selection. This is suitable for the capstone because the evaluation budget is tiny and the objective functions are black-box.

## Section 4: Weekly operation

1. Update cumulative data if a returned week is ready
2. Fit or refit the surrogate models
3. Generate next candidate points
4. Save portal-ready `inputs.txt`
5. Save placeholder `outputs.txt` where required by workflow
6. Place returned files into the matching processed week folder
7. Register and validate with the helper scripts

## Section 5: Repository notes

This file is a supporting technical write-up. The main entry point for GitHub users should remain `README.md`.
