from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle
)


# =====================================================
# PDF REPORT GENERATOR
# =====================================================

def generate_student_report(student, report_data=None):
    """
    Generate a professional PDF placement report
    for a student.

    Parameters
    ----------
    student : dict
        Student profile information.

    report_data : dict, optional
        Placement prediction, readiness, skill gap,
        resume and recommendation information.

    Returns
    -------
    BytesIO
        PDF file stored in memory.
    """

    if report_data is None:
        report_data = {}

    buffer = BytesIO()

    document = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=18 * mm,
        leftMargin=18 * mm,
        topMargin=18 * mm,
        bottomMargin=18 * mm
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "ReportTitle",
        parent=styles["Title"],
        alignment=TA_CENTER,
        fontSize=20,
        leading=24,
        spaceAfter=8
    )

    subtitle_style = ParagraphStyle(
        "ReportSubtitle",
        parent=styles["Normal"],
        alignment=TA_CENTER,
        fontSize=10,
        leading=14,
        spaceAfter=18
    )

    heading_style = ParagraphStyle(
        "SectionHeading",
        parent=styles["Heading2"],
        fontSize=13,
        leading=17,
        spaceBefore=10,
        spaceAfter=8
    )

    normal_style = ParagraphStyle(
        "ReportNormal",
        parent=styles["Normal"],
        fontSize=9.5,
        leading=14
    )

    story = []

    # =================================================
    # HEADER
    # =================================================

    story.append(
        Paragraph(
            "Student Placement Predictor",
            title_style
        )
    )

    story.append(
        Paragraph(
            "Student Placement & Career Intelligence Report",
            subtitle_style
        )
    )

    # =================================================
    # STUDENT INFORMATION
    # =================================================

    story.append(
        Paragraph(
            "1. Student Information",
            heading_style
        )
    )

    student_data = [
        [
            "Name",
            _safe_value(student.get("full_name"))
        ],
        [
            "Email",
            _safe_value(student.get("email"))
        ],
        [
            "Enrollment No.",
            _safe_value(student.get("enrollment_no"))
        ],
        [
            "Branch",
            _safe_value(student.get("branch"))
        ],
        [
            "Year",
            _safe_value(student.get("year"))
        ],
        [
            "Phone",
            _safe_value(student.get("phone"))
        ]
    ]

    student_table = Table(
        student_data,
        colWidths=[45 * mm, 125 * mm]
    )

    student_table.setStyle(
        TableStyle([
            (
                "BACKGROUND",
                (0, 0),
                (0, -1),
                colors.HexColor("#EAF2F8")
            ),
            (
                "GRID",
                (0, 0),
                (-1, -1),
                0.5,
                colors.grey
            ),
            (
                "FONTNAME",
                (0, 0),
                (-1, -1),
                "Helvetica"
            ),
            (
                "FONTNAME",
                (0, 0),
                (0, -1),
                "Helvetica-Bold"
            ),
            (
                "FONTSIZE",
                (0, 0),
                (-1, -1),
                9
            ),
            (
                "VALIGN",
                (0, 0),
                (-1, -1),
                "MIDDLE"
            ),
            (
                "TOPPADDING",
                (0, 0),
                (-1, -1),
                7
            ),
            (
                "BOTTOMPADDING",
                (0, 0),
                (-1, -1),
                7
            )
        ])
    )

    story.append(student_table)

    # =================================================
    # ACADEMIC & SKILL PROFILE
    # =================================================

    story.append(
        Paragraph(
            "2. Academic & Skill Profile",
            heading_style
        )
    )

    profile_data = [
        ["Metric", "Score"],
        [
            "CGPA",
            _format_value(student.get("cgpa"))
        ],
        [
            "Attendance",
            _percentage(student.get("attendance"))
        ],
        [
            "Aptitude",
            _percentage(student.get("aptitude_score"))
        ],
        [
            "Coding",
            _percentage(student.get("coding_score"))
        ],
        [
            "Communication",
            _percentage(student.get("communication_score"))
        ],
        [
            "Technical",
            _percentage(student.get("technical_score"))
        ]
    ]

    profile_table = Table(
        profile_data,
        colWidths=[100 * mm, 70 * mm]
    )

    profile_table.setStyle(
        TableStyle([
            (
                "BACKGROUND",
                (0, 0),
                (-1, 0),
                colors.HexColor("#1F4E78")
            ),
            (
                "TEXTCOLOR",
                (0, 0),
                (-1, 0),
                colors.white
            ),
            (
                "FONTNAME",
                (0, 0),
                (-1, 0),
                "Helvetica-Bold"
            ),
            (
                "GRID",
                (0, 0),
                (-1, -1),
                0.5,
                colors.grey
            ),
            (
                "FONTSIZE",
                (0, 0),
                (-1, -1),
                9
            ),
            (
                "ALIGN",
                (1, 1),
                (1, -1),
                "CENTER"
            ),
            (
                "TOPPADDING",
                (0, 0),
                (-1, -1),
                6
            ),
            (
                "BOTTOMPADDING",
                (0, 0),
                (-1, -1),
                6
            )
        ])
    )

    story.append(profile_table)

    # =================================================
    # PLACEMENT PREDICTION
    # =================================================

    story.append(
        Paragraph(
            "3. Placement Prediction",
            heading_style
        )
    )

    prediction = report_data.get(
        "prediction",
        "Not Available"
    )

    probability = report_data.get(
        "probability",
        "Not Available"
    )

    prediction_data = [
        ["Prediction", _safe_value(prediction)],
        ["Placement Probability", _format_percentage(probability)]
    ]

    prediction_table = Table(
        prediction_data,
        colWidths=[70 * mm, 100 * mm]
    )

    prediction_table.setStyle(
        TableStyle([
            (
                "BACKGROUND",
                (0, 0),
                (0, -1),
                colors.HexColor("#EAF2F8")
            ),
            (
                "FONTNAME",
                (0, 0),
                (0, -1),
                "Helvetica-Bold"
            ),
            (
                "GRID",
                (0, 0),
                (-1, -1),
                0.5,
                colors.grey
            ),
            (
                "FONTSIZE",
                (0, 0),
                (-1, -1),
                9
            ),
            (
                "TOPPADDING",
                (0, 0),
                (-1, -1),
                7
            ),
            (
                "BOTTOMPADDING",
                (0, 0),
                (-1, -1),
                7
            )
        ])
    )

    story.append(prediction_table)

    # =================================================
    # READINESS
    # =================================================

    story.append(
        Paragraph(
            "4. Placement Readiness",
            heading_style
        )
    )

    readiness_score = report_data.get(
        "readiness_score",
        "Not Available"
    )

    readiness_level = report_data.get(
        "readiness_level",
        "Not Available"
    )

    readiness_data = [
        ["Readiness Score", _format_percentage(readiness_score)],
        ["Readiness Level", _safe_value(readiness_level)]
    ]

    readiness_table = Table(
        readiness_data,
        colWidths=[70 * mm, 100 * mm]
    )

    readiness_table.setStyle(
        TableStyle([
            (
                "BACKGROUND",
                (0, 0),
                (0, -1),
                colors.HexColor("#EAF2F8")
            ),
            (
                "FONTNAME",
                (0, 0),
                (0, -1),
                "Helvetica-Bold"
            ),
            (
                "GRID",
                (0, 0),
                (-1, -1),
                0.5,
                colors.grey
            ),
            (
                "FONTSIZE",
                (0, 0),
                (-1, -1),
                9
            ),
            (
                "TOPPADDING",
                (0, 0),
                (-1, -1),
                7
            ),
            (
                "BOTTOMPADDING",
                (0, 0),
                (-1, -1),
                7
            )
        ])
    )

    story.append(readiness_table)

    # =================================================
    # SKILL GAP
    # =================================================

    story.append(
        Paragraph(
            "5. Skill Gap Analysis",
            heading_style
        )
    )

    skill_gap = report_data.get(
        "skill_gap",
        "Not Available"
    )

    skill_status = report_data.get(
        "skill_status",
        "Not Available"
    )

    skill_data = [
        ["Total Skill Gap", _format_value(skill_gap)],
        ["Overall Status", _safe_value(skill_status)]
    ]

    skill_table = Table(
        skill_data,
        colWidths=[70 * mm, 100 * mm]
    )

    skill_table.setStyle(
        TableStyle([
            (
                "BACKGROUND",
                (0, 0),
                (0, -1),
                colors.HexColor("#EAF2F8")
            ),
            (
                "FONTNAME",
                (0, 0),
                (0, -1),
                "Helvetica-Bold"
            ),
            (
                "GRID",
                (0, 0),
                (-1, -1),
                0.5,
                colors.grey
            ),
            (
                "FONTSIZE",
                (0, 0),
                (-1, -1),
                9
            ),
            (
                "TOPPADDING",
                (0, 0),
                (-1, -1),
                7
            ),
            (
                "BOTTOMPADDING",
                (0, 0),
                (-1, -1),
                7
            )
        ])
    )

    story.append(skill_table)

    # =================================================
    # RESUME ANALYSIS
    # =================================================

    story.append(
        Paragraph(
            "6. Resume Analysis",
            heading_style
        )
    )

    resume_score = report_data.get(
        "resume_score",
        "Not Available"
    )

    resume_status = report_data.get(
        "resume_status",
        "Not Available"
    )

    resume_data = [
        ["Resume Score", _format_percentage(resume_score)],
        ["Resume Status", _safe_value(resume_status)]
    ]

    resume_table = Table(
        resume_data,
        colWidths=[70 * mm, 100 * mm]
    )

    resume_table.setStyle(
        TableStyle([
            (
                "BACKGROUND",
                (0, 0),
                (0, -1),
                colors.HexColor("#EAF2F8")
            ),
            (
                "FONTNAME",
                (0, 0),
                (0, -1),
                "Helvetica-Bold"
            ),
            (
                "GRID",
                (0, 0),
                (-1, -1),
                0.5,
                colors.grey
            ),
            (
                "FONTSIZE",
                (0, 0),
                (-1, -1),
                9
            ),
            (
                "TOPPADDING",
                (0, 0),
                (-1, -1),
                7
            ),
            (
                "BOTTOMPADDING",
                (0, 0),
                (-1, -1),
                7
            )
        ])
    )

    story.append(resume_table)

    # =================================================
    # RECOMMENDATIONS
    # =================================================

    story.append(
        Paragraph(
            "7. Career Recommendations",
            heading_style
        )
    )

    recommendations = report_data.get(
        "recommendations",
        []
    )

    if recommendations:

        for index, recommendation in enumerate(
            recommendations,
            start=1
        ):

            story.append(
                Paragraph(
                    f"{index}. {_safe_value(recommendation)}",
                    normal_style
                )
            )

            story.append(
                Spacer(1, 3)
            )

    else:

        story.append(
            Paragraph(
                "No recommendations available.",
                normal_style
            )
        )

    # =================================================
    # DISCLAIMER
    # =================================================

    story.append(
        Spacer(1, 12)
    )

    story.append(
        Paragraph(
            "<b>Disclaimer:</b> Placement predictions are "
            "analytical outputs generated by the Student "
            "Placement Predictor system. They should be "
            "used as decision-support information and not "
            "as a final guarantee of placement.",
            normal_style
        )
    )

    # =================================================
    # FOOTER
    # =================================================

    story.append(
        Spacer(1, 12)
    )

    story.append(
        Paragraph(
            "Student Placement Predictor • "
            "Placement & Career Intelligence System",
            subtitle_style
        )
    )

    document.build(story)

    buffer.seek(0)

    return buffer


# =====================================================
# HELPER FUNCTIONS
# =====================================================

def _safe_value(value):
    """
    Convert None or empty values into readable text.
    """

    if value is None:
        return "Not Available"

    value = str(value).strip()

    if not value:
        return "Not Available"

    return value


def _format_value(value):
    """
    Format numeric values safely.
    """

    if value is None:
        return "Not Available"

    try:
        return f"{float(value):.2f}"
    except (TypeError, ValueError):
        return _safe_value(value)


def _percentage(value):
    """
    Format a numeric value as a percentage.
    """

    if value is None:
        return "Not Available"

    try:
        return f"{float(value):.2f}%"
    except (TypeError, ValueError):
        return _safe_value(value)


def _format_percentage(value):
    """
    Format percentage-like values.

    Supports:
    - 85.5 -> 85.50%
    - '85.5%' -> 85.5%
    """

    if value is None:
        return "Not Available"

    if isinstance(value, str):

        value = value.strip()

        if value.endswith("%"):
            return value

    try:
        return f"{float(value):.2f}%"
    except (TypeError, ValueError):
        return _safe_value(value)