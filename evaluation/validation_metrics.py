# escoplus/evaluation/validation_metrics.py

import numpy as np


def decision_stability(scores, threshold):
    """
    scores: list of SI_sj values
    threshold: Q90 or other percentile
    Returns proportion above threshold
    """
    scores = np.array(scores)
    above = np.sum(scores >= threshold)
    return above / len(scores)


def sensitivity_analysis(scores, percentiles=[80, 85, 90, 95]):
    """
    Tests robustness across percentile thresholds.
    """
    results = {}

    for p in percentiles:
        threshold = np.percentile(scores, p)
        kept = decision_stability(scores, threshold)
        results[f"Q{p}"] = {
            "threshold": threshold,
            "retained_ratio": kept
        }

    return results


def entropy_of_decisions(decisions):
    """
    decisions: list of 0/1 inclusion decisions
    Measures structural complexity.
    """
    from scipy.stats import entropy

    counts = np.bincount(decisions)
    probs = counts / np.sum(counts)
    return entropy(probs)
