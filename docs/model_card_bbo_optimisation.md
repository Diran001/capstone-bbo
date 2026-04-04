# Model Card for the BBO Optimisation Approach

## Overview: name of your approach, type and version

**Model name:** BBO Capstone Bayesian Optimisation Workflow  
**Type:** Surrogate-based black box optimisation workflow  
**Version:** Capstone ten-round submission version

This is not a predictive model in the usual classification or regression sense. It is an optimisation approach built around sequential decision-making under uncertainty. That matters, because the point is not to label examples but to choose promising new query points.

## Intended use: what tasks is it suitable for? What use cases should be avoided?

This approach is suitable for small-sample black box optimisation where function evaluations are limited and expensive, and where the aim is to improve results over repeated rounds. It is useful when you need a structured balance between exploration and exploitation.

It should be avoided where the objective surface is fully known already, where very large-scale brute force search is feasible, or where users expect guaranteed convergence from a small number of evaluations. It is also a bad fit if someone wants to treat the surrogate as the real function rather than as a temporary guide.

## Details: explain your strategy across the ten rounds, including the techniques you used and how your approach evolved

Across the ten rounds, my strategy moved from broad experimentation to more function-specific judgement. In the earlier rounds, I relied more on general settings and limited tuning. At that stage, the main goal was to build enough history to see how the functions were behaving. I did not know the response surfaces, so a wider search made sense.

As the rounds progressed, I became more selective. I started tuning by function rather than assuming one setting worked well for all eight cases. That included adjusting acquisition behaviour, kernel-related choices, restart levels, and candidate search size. The logic was simple. Different functions appeared to respond differently, so a uniform strategy became less convincing over time.

## Performance: summarise your results across the eight functions. What metrics did you use?

Performance was assessed mainly through observed objective values across rounds, historical best values by function, and comparison of week-on-week outcomes. I focused on whether later rounds improved on earlier bests, whether gains were stable, and whether certain functions appeared easier or harder for the surrogate-guided strategy to learn.

The results were mixed rather than uniformly improving. Some functions appeared more learnable and responded better to iterative refinement. Others remained unstable or resistant, even after more data had been collected. That pattern suggests the optimisation workflow had strengths, but also clear limits.

## Assumptions and limitations: what assumptions underlie your strategy? What are its constraints or failure modes?

The core assumption is that past observations contain enough local structure for a surrogate-guided method to make useful next-step decisions. A second assumption is that the acquisition mechanism can manage the tension between exploring unknown areas and exploiting promising ones already found.

The main limitation is that the optimiser only sees sparse samples of hidden functions. If a function is highly irregular, sharp, noisy, or poorly captured by the surrogate assumptions, the search can become unreliable. Another limitation is path dependence. What happens later depends heavily on what was sampled earlier. A weak early trajectory can shape the rest of the search.

## Ethical considerations: how does transparency support reproducibility and real-world adaptation?

Transparency matters here because it makes the optimisation process inspectable. A reader can see not only the final scores, but also the query history, the logic of the strategy, and the points where the approach changed. That makes the work easier to critique, reproduce, and improve.

In a real-world setting, this matters even more. Transparent documentation helps others judge whether the method is suitable, where it may fail, and how much confidence they should place in the results.

## Would adding more detail to your model card improve its clarity or usefulness?

Up to a point, yes. More detail helps when it explains how choices were made, what changed over time, and where the method struggled. That is useful because a simple final summary can hide the fact that performance varied sharply by function.

That said, there is a limit. Too much technical detail can make the card harder to read and less useful for a general audience. So the best structure is one that stays concise but still documents the key strategy changes, assumptions, performance pattern, and known limitations.
