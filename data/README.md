### Executive summary (data handling in this repo)

This repo separates data into raw portal artefacts, interim working files, and processed artefacts produced by the notebook. The true “raw” source of new labels is the course evaluator (portal), not this repository. Large datasets are not stored in GitHub by design. Instead, the notebook reconstructs the working dataset by combining the starter pack (`.npy` files) with weekly portal returns saved under `submissions/week_XX/`. After a run, you will have the next-week submission files, updated `.npy` datasets (with backups), plus logs and plots that document what changed and why.

---

## What “raw / interim / processed” mean in your repo

### Raw

Raw means “as close as possible to the original source, unchanged”.

In this project, raw data is:

* The **starter pack** provided by the course (initial evaluated points and scores).
* The **portal return artefacts** for each week (the confirmation file you download and the numeric outputs returned by the evaluator).

Typical raw files:

* `initial_data/function_k/initial_inputs.npy`
* `initial_data/function_k/initial_outputs.npy`
* `submissions/week_XX/Week*.txt` (portal confirmation download, if you save it)
* `submissions/week_XX/outputs.txt` (the portal-returned y values, copied in)

Raw data is not “pretty”. It is retained for traceability and to allow rebuilds.

### Interim

Interim means “working artefacts created during the run to help the pipeline operate”.

In this repo, interim data includes:

* Week-level staging files used to bridge portal format ↔ modelling format.
* Temporary candidate sets and model objects held in memory.
* Any intermediate logs/JSON emitted during a run.

Interim files you may see:

* `submissions/week_XX/SUBMISSION_GUIDE.md` (copy/paste guide)
* `logs/` run logs (timestamps, settings, parsing outcomes, point chosen)

Interim data exists to reduce manual steps and support debugging.

### Processed

Processed means “derived outputs created by the pipeline for analysis, audit, or re-use”.

In this repo, processed data includes:

* Updated `.npy` arrays after appending the latest week’s results.
* Plots showing convergence and progress.
* Historical tracking artefacts.

Typical processed outputs:

* `plots/current/` (latest week plots)
* `plots/historical/` (dated plots across weeks)
* `logs/` (structured run logs)
* `initial_data/function_k/backups/` (snapshots before updates)

Processed artefacts are reproducible from raw inputs plus the notebook.

---

## Whether actual datasets are stored

Partially.

* The **starter pack datasets** (`initial_inputs.npy`, `initial_outputs.npy`) are small and are typically kept locally.
* The **full working dataset** grows week by week. It is usually **not committed to GitHub** because it is generated from the course portal and can be reproduced locally from:

  * starter pack + weekly portal returns.

So in Git terms: the repo is designed to carry **code + structure + documentation**, while the evolving data stays local.

---

## If not stored, explain why and how it’s produced

### Why it is not stored

* **Practicality**: week-by-week datasets, plots, and logs create churn and noise in version control.
* **Restrictions**: course platforms often expect you to treat evaluator outputs as submission artefacts rather than public datasets.
* **Reproducibility**: the correct source of truth is “starter pack + portal returns”; the repo can be rebuilt from that without committing derived files.

### How data is produced

* Initial data comes from the **course starter pack** (pre-evaluated points and scores).
* New data points come from the **course evaluator / platform**:

  1. Notebook proposes a new input vector `x` for each function.
  2. You submit these `x` values to the portal.
  3. The evaluator returns the corresponding scalar outputs `y`.
  4. The notebook appends these `(x, y)` pairs into the per-function `.npy` files.

---

## What files the user will see after running the notebook

Assuming you run Week N and generate Week N+1 submissions, you will typically see:

### Under `submissions/week_{N+1:02d}/`

* `inputs.txt`
  8 lines, one per function, hyphen-separated values with 6 decimals, portal-ready.
* `outputs.txt`
  Initially blank or placeholder. You populate this after the portal returns results.
* `SUBMISSION_GUIDE.md`
  Human-readable instructions: which line maps to which function and what to paste where.

### Under `initial_data/function_k/`

* `initial_inputs.npy`
  Updated to include the newly processed Week N evaluation point.
* `initial_outputs.npy`
  Updated to include the newly processed Week N output score.
* `backups/`
  Timestamped copies of `.npy` files taken before any append, so you can roll back.

### Under `plots/`

* `plots/current/`
  Latest best-so-far / progress plots per function.
* `plots/historical/`
  Archived plots tagged by week/run timestamp.

### Under `logs/`

* Run logs capturing:

  * week number processed,
  * parsed file checks,
  * model settings (kernel/acquisition),
  * chosen point per function,
  * any fallbacks or exceptions.

If the portal files are missing or misformatted, the notebook logs that explicitly and will either stop safely or fall back to defaults depending on the failure mode.
