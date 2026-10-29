"""Notification and email text templates."""

TEMPLATES = {
    "welcome": ("Welcome to Student Placement Predictor",
                "Hi {name}, your account is ready. Complete your profile to unlock predictions, "
                "skill-gap analysis and company eligibility."),
    "new_drive": ("New placement drive: {company}",
                  "{company} is hiring for {role} on {date}. Check your eligibility and apply."),
    "application_status": ("Application update: {company}",
                           "Your application for {role} at {company} is now: {status}."),
    "selected": ("Congratulations! You were selected by {company}",
                 "You have been selected for {role} at {company}. The placement cell will contact you."),
    "model_trained": ("Prediction model retrained",
                      "{algorithm} ({version}) is now active. Accuracy {accuracy}% on {rows} rows."),
    "contact": ("New contact message from {name}", "{subject}: {message}"),
    "reset": ("Reset your password",
              "Hi {name},\n\nUse the link below to choose a new password. It expires in {minutes} minutes "
              "and works once.\n\n{link}\n\nIf you did not request this, ignore this email."),
}


def render(key, **values):
    title, body = TEMPLATES[key]
    return title.format(**values), body.format(**values)
