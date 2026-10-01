from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash
)

from ml.predict import predict_placement


prediction_bp = Blueprint(
    "prediction",
    __name__,
    url_prefix="/student"
)


# =====================================================
# PLACEMENT PREDICTION
# =====================================================

@prediction_bp.route(
    "/prediction",
    methods=["GET", "POST"]
)
def prediction():

    # Check login
    if "user_id" not in session:
        return redirect(
            url_for("auth.login")
        )

    # Only students
    if session.get("role") != "student":

        flash(
            "Access denied.",
            "danger"
        )

        return redirect(
            url_for("auth.login")
        )


    # =================================================
    # GET REQUEST
    # =================================================

    if request.method == "GET":

        return render_template(
            "student/prediction.html"
        )


    # =================================================
    # POST REQUEST
    # =================================================

    try:

        cgpa = float(
            request.form.get(
                "cgpa",
                0
            )
        )

        attendance = float(
            request.form.get(
                "attendance",
                0
            )
        )

        aptitude_score = float(
            request.form.get(
                "aptitude_score",
                0
            )
        )

        coding_score = float(
            request.form.get(
                "coding_score",
                0
            )
        )

        communication_score = float(
            request.form.get(
                "communication_score",
                0
            )
        )

        technical_score = float(
            request.form.get(
                "technical_score",
                0
            )
        )


        # =============================================
        # ML PREDICTION
        # =============================================

        result = predict_placement(

            cgpa=cgpa,

            attendance=attendance,

            aptitude_score=aptitude_score,

            coding_score=coding_score,

            communication_score=communication_score,

            technical_score=technical_score
        )


        # =============================================
        # RESULT PAGE
        # =============================================

        return render_template(

            "student/result.html",

            result=result,

            inputs={
                "cgpa": cgpa,
                "attendance": attendance,
                "aptitude_score": aptitude_score,
                "coding_score": coding_score,
                "communication_score": communication_score,
                "technical_score": technical_score
            }
        )


    except ValueError as error:

        flash(
            str(error),
            "danger"
        )

        return redirect(
            url_for(
                "prediction.prediction"
            )
        )


    except Exception as error:

        print(
            "Prediction Route Error:",
            error
        )

        flash(
            "Unable to generate placement prediction.",
            "danger"
        )

        return redirect(
            url_for(
                "prediction.prediction"
            )
        )