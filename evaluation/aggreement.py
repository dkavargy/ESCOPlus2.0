# escoplus/evaluation/agreement.py

import numpy as np
from sklearn.metrics import cohen_kappa_score
from statsmodels.stats.inter_rater import fleiss_kappa
from statsmodels.stats.inter_rater import aggregate_raters


def pairwise_cohen_kappa(ratings):
    """
    ratings: dict with rater names as keys and list of binary decisions (0/1)
    Returns pairwise Cohen's kappa scores.
    """
    raters = list(ratings.keys())
    results = {}

    for i in range(len(raters)):
        for j in range(i + 1, len(raters)):
            r1 = ratings[raters[i]]
            r2 = ratings[raters[j]]
            score = cohen_kappa_score(r1, r2)
            results[f"{raters[i]} vs {raters[j]}"] = score

    return results


def compute_fleiss_kappa(ratings_matrix):
    """
    ratings_matrix: list of lists
    Each row = [votes_for_0, votes_for_1]
    """
    return fleiss_kappa(np.array(ratings_matrix))


def agreement_summary(ratings):
    """
    High-level summary
    """
    pairwise = pairwise_cohen_kappa(ratings)

    print("Pairwise Cohen's Kappa:")
    for k, v in pairwise.items():
        print(f"{k}: {round(v, 3)}")

    return pairwise
