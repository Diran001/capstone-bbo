### Executive summary (data)

This dataset is the full history of evaluated inputs and returned scores for eight separate black-box functions. Each record is one completed evaluation: an input vector **x** submitted to the portal and a scalar score **y** returned by the portal. Inputs are constrained to a normalised cube and stored per-function as NumPy arrays (`initial_inputs.npy`, `initial_outputs.npy`). The starter pack provides the initial design points; subsequent points are generated sequentially by Bayesian Optimisation (one new point per function per week). The dataset is not a random sample of the space because later points are chosen adaptively to improve the objective. This makes the data highly informative for optimisation, but biased for any “global modelling” claims.

### The problem (what this data represents)

You cannot see the true functions. The only way to learn is to submit an **x** and observe the resulting **y**. So the dataset is the only evidence we have about each function. The purpose of collecting it is not “statistics for its own sake”. It exists to support decision-making: where to probe next to improve the best score under strict query limits.

### What one row/record means

One row is one evaluation event:

* **Input**: `x = [x1, x2, …, xd]` (a single candidate point in d dimensions)
* **Output**: `y` (the portal-returned scalar score for that function at that x)

In plain terms: **submit x → receive y → store (x, y)**.

### Dimensions and bounds (from the notebook)

This capstone has **8 functions**, each with its own input dimension and initial dataset size:

* Function 1: **d = 2**, initial X shape **(10, 2)**
* Function 2: **d = 2**, initial X shape **(10, 2)**
* Function 3: **d = 3**, initial X shape **(15, 3)**
* Function 4: **d = 4**, initial X shape **(30, 4)**
* Function 5: **d = 4**, initial X shape **(20, 4)**
* Function 6: **d = 5**, initial X shape **(20, 5)**
* Function 7: **d = 6**, initial X shape **(30, 6)**
* Function 8: **d = 8**, initial X shape **(40, 8)**

**Bounds / constraints** (enforced in code):

* Each coordinate is clamped to the portal-valid range **[0.000000, 0.999999]**.
* Candidate generation is done in **[0, 1]^d** (random candidates), then clamped to the valid range.

### How you collected it (initial design + sequential BO)

Collection happens in two phases:

1. **Initial design (starter pack)**
   The initial `(X, y)` points are provided by the course starter dataset. These are treated as a space-filling “initial design” (random or low-discrepancy style sampling provided externally).

2. **Sequential Bayesian Optimisation (weekly loop)**
   After week 1, each new record is generated as follows:

   * Fit a surrogate model to all past data for that function.
   * Score candidate x points using an acquisition function (explore vs exploit).
   * Submit the chosen x to the portal.
   * Receive y and append it to the dataset.

Operationally: **one new (x, y) per function per week**.

### Preprocessing (scaling/normalisation, duplicates)

Inputs:

* **No scaling needed** because inputs are already normalised to **[0, 1]^d** by design and enforced by clamping.

Outputs:

* For GP fitting stability, the notebook **standardises y** internally:

  * `y_scaled = (y - mean(y)) / std(y)`
  * The stored “ground truth” outputs remain the raw portal `y`; scaling is for modelling only.

Duplicates:

* The notebook explicitly checks whether the proposed `x_next` is an exact duplicate (within tight tolerance) of an existing row in `X`.
* If a duplicate is detected, it perturbs the point slightly with small Gaussian noise and clamps it back into **[0, 1]**. This is purely to avoid wasting a weekly query on the same point.

### Bias and limitations (selection bias from adaptive sampling)

This dataset is **not** a random sample of the input space.

* Later points are chosen deliberately where the optimiser believes improvement is likely (or uncertainty is high).
* That means the dataset becomes concentrated in “promising” regions and under-represents other regions.
* Consequence: you should not treat the data as suitable for unbiased global inference (for example, “learning the full surface accurately everywhere”). It is optimisation data, not a survey sample.
* Noise is also possible in the portal returns. If noise is material, the dataset can contain apparent improvements that are just randomness, and the model may chase that unless the noise model and exploration are handled carefully.
