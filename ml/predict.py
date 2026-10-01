# ==========================================================
# STUDENT PLACEMENT PREDICTOR
# ML PREDICTION ENGINE
# ==========================================================

import os
import joblib
import pandas as pd


# ==========================================================
# PATH CONFIGURATION
# ==========================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

MODEL_PATH = os.path.join(
    BASE_DIR,
    "ml",
    "models",
    "placement_model.pkl"
)

SCALER_PATH = os.path.join(
    BASE_DIR,
    "ml",
    "models",
    "scaler.pkl"
)


# ==========================================================
# LOAD MODEL
# ==========================================================

def load_model():

    if not os.path.exists(MODEL_PATH):

        raise FileNotFoundError(
            "Placement model not found. "
            "Please train the model first."
        )

    return joblib.load(
        MODEL_PATH
    )


# ==========================================================
# LOAD SCALER
# ==========================================================

def load_scaler():

    if not os.path.exists(SCALER_PATH):

        raise FileNotFoundError(
            "Scaler not found. "
            "Please run preprocessing first."
        )

    return joblib.load(
        SCALER_PATH
    )


# ==========================================================
# VALIDATE INPUT
# ==========================================================

def validate_input(
    cgpa,
    attendance,
    aptitude_score,
    coding_score,
    communication_score,
    technical_score
):

    values = [
        cgpa,
        attendance,
        aptitude_score,
        coding_score,
        communication_score,
        technical_score
    ]

    # Check numeric values
    try:

        values = [
            float(value)
            for value in values
        ]

    except (TypeError, ValueError):

        raise ValueError(
            "All prediction inputs must be numeric."
        )


    # Validate CGPA
    if not 0 <= values[0] <= 10:

        raise ValueError(
            "CGPA must be between 0 and 10."
        )


    # Validate remaining scores
    for value in values[1:]:

        if not 0 <= value <= 100:

            raise ValueError(
                "Attendance and skill scores "
                "must be between 0 and 100."
            )


    return values


# ==========================================================
# MAKE PREDICTION
# ==========================================================

def predict_placement(
    cgpa,
    attendance,
    aptitude_score,
    coding_score,
    communication_score,
    technical_score
):

    # Validate input
    values = validate_input(
        cgpa,
        attendance,
        aptitude_score,
        coding_score,
        communication_score,
        technical_score
    )


    # Load model and scaler
    model = load_model()
    scaler = load_scaler()


    # Convert input into NumPy array
    input_data = pd.DataFrame(
    [values],
    columns=[
        "cgpa",
        "attendance",
        "aptitude_score",
        "coding_score",
        "communication_score",
        "technical_score"
    ]
)


    # Scale input
    input_scaled = scaler.transform(
        input_data
    )


    # Predict class
    prediction = model.predict(
        input_scaled
    )[0]


    # Get probability
    probabilities = model.predict_proba(
        input_scaled
    )[0]


    # Probability of placement
    placement_probability = (
        probabilities[1] * 100
    )


    # Probability of not being placed
    not_placed_probability = (
        probabilities[0] * 100
    )


    # Convert prediction to readable result
    if prediction == 1:

        result = "Placed"

    else:

        result = "Not Placed"


    return {
        "prediction": int(prediction),
        "result": result,
        "placement_probability": round(
            placement_probability,
            2
        ),
        "not_placed_probability": round(
            not_placed_probability,
            2
        )
    }


# ==========================================================
# TEST PREDICTION
# ==========================================================

if __name__ == "__main__":

    try:

        result = predict_placement(
            cgpa=8.5,
            attendance=88,
            aptitude_score=82,
            coding_score=85,
            communication_score=80,
            technical_score=87
        )


        print(
            "=========================================="
        )

        print(
            "PLACEMENT PREDICTION"
        )

        print(
            "=========================================="
        )

        print(
            f"Prediction          : "
            f"{result['result']}"
        )

        print(
            f"Placement Probability: "
            f"{result['placement_probability']}%"
        )

        print(
            f"Not Placed Probability: "
            f"{result['not_placed_probability']}%"
        )

        print(
            "=========================================="
        )


    except Exception as error:

        print(
            "Prediction Error:",
            error
        )