### Executive summary (model and pipeline)

This solution is a weekly Bayesian Optimisation pipeline for eight black-box functions under strict evaluation limits (one new evaluation per function per week). Each function is modelled with a Gaussian Process (GP) regression surrogate that is refit after every new portal return. The GP’s uncertainty is used by acquisition functions (EI, PI, UCB, plus a MaxVar exploration option) to select the next input point. Candidate points are generated in the normalised domain ([0,1]^d) and converted into the portal’s required submission format. The pipeline produces audit artefacts (logs, progress plots, and week-by-week submission files) so each recommendation can be traced to the dataset state and model configuration at the time of decision.

### Model: GP regression surrogate

* **Surrogate model**: `GaussianProcessRegressor` (scikit-learn).
* **Role in the pipeline**: approximate the unknown black-box function (f(x)) using observed pairs ((X, y)), and provide:

  * predictive mean (\mu(x)) to guide exploitation, and
  * predictive standard deviation (\sigma(x)) to quantify uncertainty for exploration.
* **Per-function modelling**: a separate GP is fit for each of the 8 functions, using that function’s accumulated evaluation history.

### Kernel (Matérn / RBF) and why

* **Kernel used**: Matérn with (\nu = 2.5), wrapped in a scale term and combined with a noise term:

  [
  k(x,x') = C \cdot \text{Matérn}(\nu=2.5, \ell) ;+; \text{WhiteKernel}(\sigma_n^2)
  ]

  Implemented as:

  * `ConstantKernel(1.0, (1e-3, 1e3)) * Matern(length_scale=1s, length_scale_bounds=(1e-3, 1e2), nu=2.5) + WhiteKernel(...)`
* **Why Matérn (\nu=2.5)**: it is a practical default for unknown smooth functions because it is less “over-smooth” than RBF while still modelling smooth structure. It tends to behave well with small datasets and avoids the RBF tendency to impose too much smoothness when the function has sharper curvature.
* **RBF note**: RBF is a valid alternative kernel in the same setting, but the notebook’s implemented default is Matérn (\nu=2.5) for robustness.

### Acquisition function: EI / PI / UCB (and parameters)

The pipeline supports multiple acquisition rules to balance exploration and exploitation. All work off GP predictions (\mu(x)) and (\sigma(x)).

* **EI (Expected Improvement)** for maximisation
  [
  \text{EI}(x) = \mathbb{E}\left[\max(0, f(x) - f^* - \xi)\right]
  ]
  Parameter:

  * `xi = 0.01` (`EI_XI = 0.01`) to enforce a small improvement margin (encourages exploration when progress stalls).

* **PI (Probability of Improvement)** for maximisation
  [
  \text{PI}(x) = \mathbb{P}\left(f(x) > f^* + \xi\right)
  ]
  Parameter:

  * uses the same `xi = 0.01`.

* **UCB (Upper Confidence Bound)** for maximisation
  [
  \text{UCB}(x) = \mu(x) + \kappa \sigma(x)
  ]
  Parameter:

  * `kappa = 2.0` (`UCB_KAPPA = 2.0`) controls optimism under uncertainty (higher means more exploration).

* **Candidate evaluation strategy (important pipeline detail)**

  * Candidates are sampled randomly in ([0,1]^d): `N_CANDIDATES = 200_000`.
  * The acquisition score is computed for every candidate.
  * The best candidate becomes the proposed next point.
  * Defensive behaviour: if GP fitting fails, the pipeline falls back to a random valid point (to avoid breaking the weekly submission cycle).

### Intended use and not intended use

**Intended use**

* Sample-efficient optimisation where evaluations are expensive/slow/limited.
* Weekly iterative optimisation where you need:

  * a repeatable decision loop,
  * traceability of each proposed point,
  * safe defaults and fallbacks.
* Optimising within a **fixed bounded domain** ([0,1]^d).

**Not intended use**

* High-throughput scenarios where you can evaluate thousands or millions of points cheaply (use simpler global search or direct optimisation).
* Claims of unbiased global function learning (the data is adaptively sampled, so any “global accuracy” inference is risky).
* Highly discontinuous objectives or hard constraint surfaces unless you extend the modelling approach (constraints, non-stationary kernels, robust noise models).

### Evaluation (best-so-far curve, iterations/evals, comparisons)

**Primary evaluation artefact**

* **Best-so-far (BSF) curve** per function:

  * ( \text{BSF}_t = \max(y_1,\dots,y_t) )
  * Plotted across evaluation count to show convergence and week-by-week improvements.

**Iterations / evaluations**

* Each function starts from the provided initial dataset, then adds **one new evaluation per week**.
* Initial sizes in this project:

  * F1: 10, F2: 10, F3: 15, F4: 30, F5: 20, F6: 20, F7: 30, F8: 40
* Total evaluations per function = initial size + number of completed weeks for that function.

**Comparisons**

* The notebook does not present a full benchmark suite (e.g., random search vs EI vs UCB across repeated runs).
* It does include operational safeguards:

  * random fallback if the GP fails, and
  * a consistent progress plot for tracking improvement over time.
    If you want formal comparisons, the correct approach is to replay the same weekly budget under different acquisition strategies (EI vs UCB vs PI) and compare BSF curves, but that is not currently implemented as a controlled experiment in the workflow.

### Limitations (scaling, kernel sensitivity, noise, bound effects)

* **Computational scaling**: GP training is (O(n^3)) in the number of observations (n). As weeks accumulate, fitting can become slow, especially for higher dimensions (functions 7 and 8).
* **Kernel sensitivity**: performance depends on how well the kernel matches the true function’s smoothness and length-scales. A poor kernel choice can cause:

  * underfitting (too smooth), or
  * overconfident predictions in the wrong regions.
* **Noise issues**: if portal outputs are noisy:

  * the GP can chase noise,
  * best-so-far curves can show “improvement” that is just randomness,
  * WhiteKernel helps, but with very small (n) the noise estimation can still be fragile.
* **Bound-limited behaviour**: all search is constrained to ([0,1]^d). If the true optimum is near a boundary, the optimiser can over-sample edges, and candidate generation plus clamping can create repeated or near-repeated points near 0 or 1.
* **Candidate sampling approximation**: selecting the best point from a random candidate set (200k samples) is an approximation. It can miss narrow optima, particularly in higher dimensions, unless candidate coverage is very strong.
