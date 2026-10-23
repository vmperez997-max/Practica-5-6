import numpy as np
import pandas as pd
import pytest

from inf8239_u03.data import validate_movielens
from inf8239_u03.evaluation import RankingEngine, evaluate, pareto_mask
from inf8239_u03.metrics import hit_rate_at_k
from inf8239_u03.recommenders import MatrixFactorization, temporal_leave_one_out


def test_missing_recommendation_is_a_miss():
    truth = pd.DataFrame({"userId": [1, 2], "movieId": [3, 4], "rating": [5, 2]})
    assert hit_rate_at_k({1: [3]}, truth) == 0.5
    metrics = evaluate({1: [3], 2: [5]}, truth, 5)
    assert metrics["precision_at_10"] == 0.05
    assert metrics["positive_hit_rate_at_10"] == 1


def test_single_event_user_and_ties(sample_ratings):
    data = pd.concat(
        [
            sample_ratings,
            pd.DataFrame(
                {"userId": [9], "movieId": [5], "rating": [4], "timestamp": [1]}
            ),
        ],
        ignore_index=True,
    )
    data.loc[data.userId.eq(1), "timestamp"] = 7
    train, test = temporal_leave_one_out(data.sample(frac=1, random_state=1))
    assert 9 in set(train.userId) and 9 not in set(test.userId)
    assert test.loc[test.userId.eq(1), "movieId"].item() == 3
    assert len(train) + len(test) == len(data)


@pytest.mark.parametrize("failure", ["duplicate", "null", "timestamp", "rating_step"])
def test_audit_rejects_invalid_data(sample_ratings, sample_movies, failure):
    data = sample_ratings.copy()
    if failure == "duplicate":
        data = pd.concat([data, data.iloc[:1]])
    elif failure == "null":
        data.loc[0, "userId"] = np.nan
    elif failure == "timestamp":
        data.loc[0, "timestamp"] = -1
    else:
        data.loc[0, "rating"] = 3.7
    with pytest.raises(ValueError):
        validate_movielens(data, sample_movies)


def test_rankings_exclude_seen_and_cold_fallback(sample_ratings, sample_movies):
    model = MatrixFactorization(factors=3).fit(sample_ratings, epochs=2)
    engine = RankingEngine(sample_ratings, sample_movies, model)
    seen = set(sample_ratings.loc[sample_ratings.userId.eq(1), "movieId"])
    for method in ["popularity", "content", "collaborative", "hybrid"]:
        assert not set(engine.recommend(1, method)) & seen
    assert engine.recommend(999, "hybrid") == engine.recommend(888, "popularity")
    assert engine.recommend(1, "hybrid", alpha=0) == engine.recommend(1, "content")
    assert engine.recommend(1, "hybrid", alpha=1) == engine.recommend(
        1, "collaborative"
    )


def test_pareto_uses_coverage_and_cost():
    frame = pd.DataFrame(
        {
            "hit_rate_at_10": [0.2, 0.1, 0.3],
            "coverage": [0.2, 0.1, 0.1],
            "total_seconds": [1, 2, 1],
            "model_bytes": [1, 2, 1],
        }
    )
    assert pareto_mask(frame) == [True, False, True]
