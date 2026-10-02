import os

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash
)
from werkzeug.utils import secure_filename

from resume_analyzer.parser import analyze_resume


resume_bp = Blueprint(
    "resume",
    __name__,
    url_prefix="/student"
)


BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

UPLOAD_FOLDER = os.path.join(
    BASE_DIR,
    "static",
    "uploads",
    "resumes"
)

ALLOWED_EXTENSIONS = {
    "pdf"
}


def allowed_file(filename):
    """
    Check whether uploaded file is a PDF.
    """

    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower()
        in ALLOWED_EXTENSIONS
    )


@resume_bp.route(
    "/resume",
    methods=["GET", "POST"]
)
def resume_upload():

    # -------------------------------------------------
    # Authentication check
    # -------------------------------------------------

    if "user_id" not in session:
        return redirect(
            url_for("auth.login")
        )

    if session.get("role") != "student":
        flash(
            "Access denied.",
            "danger"
        )

        return redirect(
            url_for("auth.login")
        )

    # -------------------------------------------------
    # GET request
    # -------------------------------------------------

    if request.method == "GET":

        return render_template(
            "student/resume_upload.html"
        )

    # -------------------------------------------------
    # Check uploaded file
    # -------------------------------------------------

    if "resume" not in request.files:

        flash(
            "Please select a resume PDF.",
            "danger"
        )

        return redirect(
            url_for("resume.resume_upload")
        )

    file = request.files["resume"]

    if not file or file.filename == "":

        flash(
            "Please select a resume PDF.",
            "danger"
        )

        return redirect(
            url_for("resume.resume_upload")
        )

    # -------------------------------------------------
    # Validate file type
    # -------------------------------------------------

    if not allowed_file(file.filename):

        flash(
            "Only PDF resume files are allowed.",
            "danger"
        )

        return redirect(
            url_for("resume.resume_upload")
        )

    # -------------------------------------------------
    # Create upload directory
    # -------------------------------------------------

    os.makedirs(
        UPLOAD_FOLDER,
        exist_ok=True
    )

    # -------------------------------------------------
    # Create secure filename
    # -------------------------------------------------

    original_filename = secure_filename(
        file.filename
    )

    user_id = session["user_id"]

    filename = (
        f"user_{user_id}_"
        f"{original_filename}"
    )

    file_path = os.path.join(
        UPLOAD_FOLDER,
        filename
    )

    # -------------------------------------------------
    # Save PDF
    # -------------------------------------------------

    try:

        file.save(file_path)

    except Exception as error:

        print(
            "Resume Upload Error:",
            error
        )

        flash(
            "Unable to upload resume.",
            "danger"
        )

        return redirect(
            url_for("resume.resume_upload")
        )

    # -------------------------------------------------
    # Analyze resume
    # -------------------------------------------------

    try:

        result = analyze_resume(
            file_path
        )

        # Do not expose the complete PDF path
        # to the browser.

        result["filename"] = filename

        return render_template(
            "student/resume_result.html",
            result=result
        )

    except Exception as error:

        print(
            "Resume Analysis Error:",
            error
        )

        flash(
            "Resume uploaded, but analysis failed. "
            "Please upload a readable PDF resume.",
            "danger"
        )

        return redirect(
            url_for("resume.resume_upload")
        )