# Datasheet for the BBO Capstone Project Data Set

## Motivation: why did you create this data set? What task does it support?

I created this data set to document the full query history and observed function evaluations from my black box Bayesian optimisation capstone. Its purpose is to support analysis of how the optimisation process behaved across ten rounds and eight hidden objective functions. It gives a transparent record of what was tried, what was returned, and how later decisions were shaped by earlier observations.

The data set supports two main tasks. First, it supports reproducibility, because it preserves the inputs and outputs used to guide each round. Second, it supports reflection, because it makes it possible to examine how the optimisation strategy evolved over time rather than just focusing on final scores.

## Composition: what does it contain? What is the size and format and are there any gaps?

The data set contains submitted query points and the corresponding function evaluations returned by the capstone system. In practical terms, it is a historical record of optimisation inputs and outputs across all rounds of the exercise. It covers eight functions over ten rounds, so the data set is relatively small, structured, and tabular rather than large scale.

The main formats are text and repository files generated during the capstone workflow. These include submission records, processed outputs, logs, and supporting scripts or notebooks. One limitation is that the data only captures evaluated points, not the true hidden surfaces of the objective functions. That means the data is informative but incomplete. It shows what I observed, not the full landscape.

## Collection process: how were the queries generated? What strategy did you use? Over what time frame?

The queries were generated iteratively using a Bayesian optimisation approach. I used earlier observations to fit or update a surrogate view of each function and then selected new candidate points through acquisition-based search. Early rounds were more exploratory because uncertainty was higher. Later rounds became more selective because the growing query history gave a better basis for function-specific judgement.

The strategy did not remain fixed. In the earlier weeks I changed relatively little, mainly adjusting exploration settings such as xi. Later, I tuned more by function, including acquisition choice, kernel behaviour, restart settings, candidate search size, and related parameters. The collection period ran across the ten submission rounds of the capstone.

## Preprocessing and uses: have you applied any transformations? What are the intended and inappropriate uses?

The data was lightly preprocessed for organisation, comparison, and resubmission. That included structuring inputs and outputs by week, maintaining processed submission folders, and using scripts to review results across functions and rounds. The preprocessing did not alter the meaning of the observed function values. It mainly improved traceability and workflow consistency.

The intended use is to document optimisation behaviour, compare strategies, support reproducibility, and explain how decisions were made during the capstone. Inappropriate uses would include claiming that the data reveals the full underlying objective functions, or treating the observed history as proof that one strategy is universally best. It is a course project data set with narrow scope and limited sample size.

## Distribution and maintenance: where is the data set available? What are the terms of use? Who maintains it?

The data set is available through my public GitHub repository for the BBO capstone project, alongside the code, notebooks, and project documentation. It is maintained by me as the project owner. That makes version control and change history visible.

The main practical term of use is academic and portfolio review. Others can inspect the material to understand the project, but they should not treat it as a benchmark data set for general optimisation claims. Any reuse should keep the project context clear.
