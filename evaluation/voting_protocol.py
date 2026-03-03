# escoplus/evaluation/voting_protocol.py

from collections import Counter


def majority_vote(votes):
    """
    votes: list of 0/1 decisions from 3 raters
    Returns final decision and agreement level
    """
    count = Counter(votes)

    decision = count.most_common(1)[0][0]
    agreement_ratio = count[decision] / len(votes)

    return decision, agreement_ratio


def consensus_required(votes):
    """
    Returns True only if unanimous
    """
    return len(set(votes)) == 1


def resolve_disagreement(votes, discussion_round_votes=None):
    """
    First apply majority.
    If no consensus, require second discussion round.
    """
    if consensus_required(votes):
        return votes[0], "unanimous"

    if discussion_round_votes:
        if consensus_required(discussion_round_votes):
            return discussion_round_votes[0], "resolved_after_discussion"

    return None, "no_consensus"
