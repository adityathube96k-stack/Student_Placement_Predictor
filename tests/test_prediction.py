from ml.predict import predict_placement


def test_prediction_output():
    result = predict_placement(
        cgpa=8.0,
        attendance=90.0,
        aptitude_score=80.0,
        coding_score=85.0,
        communication_score=75.0,
        technical_score=82.0
    )

    assert result is not None
    assert "prediction" in result
    assert "placement_probability" in result
    assert "not_placed_probability" in result


def test_prediction_probabilities():
    result = predict_placement(
        cgpa=8.0,
        attendance=90.0,
        aptitude_score=80.0,
        coding_score=85.0,
        communication_score=75.0,
        technical_score=82.0
    )

    placement_probability = result["placement_probability"]
    not_placed_probability = result["not_placed_probability"]

    assert 0 <= placement_probability <= 100
    assert 0 <= not_placed_probability <= 100

    assert round(
        placement_probability + not_placed_probability,
        2
    ) == 100.00