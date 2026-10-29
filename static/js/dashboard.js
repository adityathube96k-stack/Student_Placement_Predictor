
document.addEventListener("DOMContentLoaded", () => {
    loadDashboardData();
});


// =========================================================
// Dashboard State
// =========================================================

const dashboardData = {
    cgpa: null,
    attendance: null,
    skills: {
        technical: null,
        coding: null,
        aptitude: null,
        communication: null
    },
    prediction: null,
    skillGaps: []
};


// =========================================================
// Safe API Helper
// =========================================================

async function fetchJSON(url) {
    const response = await fetch(url);

    if (!response.ok) {
        throw new Error(`Request failed: ${url} (${response.status})`);
    }

    return response.json();
}


// =========================================================
// Load Dashboard Data
// =========================================================

async function loadDashboardData() {
    try {
        // Load student profile
        try {
            const data = await fetchJSON("/api/student/profile");

            if (data.success && data.profile) {
                const nameElement = document.getElementById("studentName");

                if (nameElement) {
                    nameElement.textContent =
                        data.profile.full_name || "Student";
                }
            }
        } catch (error) {
            console.error("Profile loading error:", error);
        }

        // Load academic records
        try {
            const data = await fetchJSON("/api/student/academic");

            if (
                data.success &&
                Array.isArray(data.academic_records) &&
                data.academic_records.length > 0
            ) {
                const academic = data.academic_records[0];

                dashboardData.cgpa = toNumber(academic.cgpa);
                dashboardData.attendance = toNumber(academic.attendance);

                setValue(
                    "cgpaValue",
                    dashboardData.cgpa === null
                        ? "--"
                        : dashboardData.cgpa.toFixed(2)
                );

                setValue(
                    "attendanceValue",
                    dashboardData.attendance === null
                        ? "--"
                        : `${dashboardData.attendance.toFixed(0)}%`
                );
            }
        } catch (error) {
            console.error("Academic records loading error:", error);
        }

        // Load student skill records
        try {
            const data = await fetchJSON("/api/student/skills");

            if (data.success && data.skills) {
                const skills = data.skills;

                dashboardData.skills.technical =
                    toNumber(skills.technical_score);

                dashboardData.skills.coding =
                    toNumber(skills.coding_score);

                dashboardData.skills.aptitude =
                    toNumber(skills.aptitude_score);

                dashboardData.skills.communication =
                    toNumber(skills.communication_score);

                renderAllSkills();
            }
        } catch (error) {
            console.error("Student skills loading error:", error);
        }

        // Load latest prediction history
        try {
            const data = await fetchJSON("/api/prediction/history");

            if (
                data.success &&
                Array.isArray(data.history) &&
                data.history.length > 0
            ) {
                dashboardData.prediction = data.history[0];
                updatePrediction(dashboardData.prediction);
            } else {
                showNoPredictionState();
            }
        } catch (error) {
            console.error("Prediction history loading error:", error);
            showNoPredictionState();
        }

        // Load latest skill-gap records
        try {
            const data = await fetchJSON("/api/student/skill-gaps");

            if (data.success && Array.isArray(data.skill_gaps)) {
                dashboardData.skillGaps = data.skill_gaps;
            }
        } catch (error) {
            console.error("Skill gaps loading error:", error);
        }

        updatePreparationOverview();

    } catch (error) {
        console.error("Dashboard loading error:", error);
    }
}


// =========================================================
// General Helpers
// =========================================================

function toNumber(value) {
    if (
        value === null ||
        value === undefined ||
        value === ""
    ) {
        return null;
    }

    const number = Number(value);

    return Number.isFinite(number) ? number : null;
}


function setValue(elementId, value) {
    const element = document.getElementById(elementId);

    if (element) {
        element.textContent = value;
    }
}


// =========================================================
// Render Skill Scores
// =========================================================

function renderAllSkills() {
    const skillConfig = [
        {
            key: "technical",
            scoreId: "technicalScore",
            progressId: "technicalProgress",
            statusId: "technicalStatus"
        },
        {
            key: "coding",
            scoreId: "codingScore",
            progressId: "codingProgress",
            statusId: "codingStatus"
        },
        {
            key: "aptitude",
            scoreId: "aptitudeScore",
            progressId: "aptitudeProgress",
            statusId: "aptitudeStatus"
        },
        {
            key: "communication",
            scoreId: "communicationScore",
            progressId: "communicationProgress",
            statusId: "communicationStatus"
        }
    ];

    skillConfig.forEach(skill => {
        const score = dashboardData.skills[skill.key];

        updateSkill(
            skill.scoreId,
            skill.progressId,
            score
        );

        updateSkillStatus(score, skill.statusId);
    });
}


function updateSkill(scoreElementId, progressElementId, value) {
    const score = toNumber(value);

    const scoreElement = document.getElementById(scoreElementId);
    const progressElement = document.getElementById(progressElementId);

    if (scoreElement) {
        scoreElement.textContent =
            score === null ? "--" : `${score.toFixed(0)}%`;
    }

    if (progressElement) {
        progressElement.style.width =
            score === null
                ? "0%"
                : `${Math.min(100, Math.max(0, score))}%`;

        progressElement.setAttribute(
            "aria-valuenow",
            score === null ? "0" : String(score)
        );
    }
}


// =========================================================
// Skill Status
// =========================================================

function updateSkillStatus(score, statusElementId) {
    const element = document.getElementById(statusElementId);

    if (!element) {
        return;
    }

    const value = toNumber(score);

    if (value === null) {
        element.textContent = "Data Required";
    } else if (value >= 80) {
        element.textContent = "Target Achieved";
    } else if (value >= 70) {
        element.textContent = "Nearly There";
    } else if (value >= 50) {
        element.textContent = "Developing";
    } else {
        element.textContent = "Needs Focus";
    }
}


// =========================================================
// Update Prediction
// =========================================================

function updatePrediction(prediction) {
    const probability = toNumber(prediction.placement_probability);
    const employability = toNumber(prediction.employability_score);

    setValue(
        "placementValue",
        probability === null ? "--" : `${probability.toFixed(2)}%`
    );

    setValue(
        "placementProbability",
        probability === null ? "--" : `${probability.toFixed(2)}%`
    );

    setValue(
        "employabilityValue",
        employability === null ? "--" : `${employability.toFixed(2)}%`
    );

    const label =
        prediction.prediction_label || "Not available";

    setValue("predictionLabel", label);
    setValue("predictionStatus", label);

    const insightElement =
        document.getElementById("predictionInsight");

    if (insightElement) {
        insightElement.textContent =
            getPredictionInsight(probability, employability);
    }
}


function getPredictionInsight(probability, employability) {
    if (probability === null || employability === null) {
        return "Generate a prediction to receive placement insights.";
    }

    if (probability >= 80 && employability >= 75) {
        return "Strong placement outlook. Continue practicing and maintain your performance.";
    }

    if (probability >= 80) {
        return "High predicted placement probability. Keep improving your employability and weaker skills.";
    }

    if (probability >= 60) {
        return "Moderate placement outlook. Work consistently on your skill gaps and interview preparation.";
    }

    return "Focus on improving your skills and academic preparation before your next prediction.";
}


// =========================================================
// Preparation Overview
// =========================================================

function updatePreparationOverview() {
    updatePlacementReadiness();
    updateSkillDevelopment();
    updateAcademicStatus();
    updateNextAction();
}


function updatePlacementReadiness() {
    const element = document.getElementById("readinessText");

    if (!element) {
        return;
    }

    if (!dashboardData.prediction) {
        element.textContent = "Generate a prediction";
        return;
    }

    const probability = toNumber(
        dashboardData.prediction.placement_probability
    );

    if (probability === null) {
        element.textContent = "Data Required";
    } else if (probability >= 80) {
        element.textContent = "High";
    } else if (probability >= 60) {
        element.textContent = "Moderate";
    } else {
        element.textContent = "Needs Improvement";
    }
}


// =========================================================
// Skill Development
// =========================================================

function updateSkillDevelopment() {
    const element = document.getElementById("skillDevelopmentText");

    if (!element) {
        return;
    }

    const scores = Object.values(dashboardData.skills)
        .map(toNumber)
        .filter(score => score !== null);

    if (scores.length === 0) {
        element.textContent = "Data Required";
        return;
    }

    const belowTarget = scores.filter(score => score < 80).length;

    if (belowTarget === 0) {
        element.textContent = "Target Achieved";
    } else if (belowTarget <= 2) {
        element.textContent = "Good Progress";
    } else {
        element.textContent = "Needs Focus";
    }
}


// =========================================================
// Academic Status
// =========================================================

function updateAcademicStatus() {
    const element = document.getElementById("academicStatusText");

    if (!element) {
        return;
    }

    const cgpa = toNumber(dashboardData.cgpa);
    const attendance = toNumber(dashboardData.attendance);

    if (cgpa === null || attendance === null) {
        element.textContent = "Data Required";
    } else if (cgpa >= 8 && attendance >= 75) {
        element.textContent = "Strong";
    } else if (cgpa >= 7 && attendance >= 70) {
        element.textContent = "Good";
    } else {
        element.textContent = "Needs Attention";
    }
}


// =========================================================
// Recommended Next Action
// =========================================================

function updateNextAction() {
    const element = document.getElementById("nextActionText");

    if (!element) {
        return;
    }

    const scores = [
        {
            name: "Technical Skills",
            score: dashboardData.skills.technical
        },
        {
            name: "Coding",
            score: dashboardData.skills.coding
        },
        {
            name: "Aptitude",
            score: dashboardData.skills.aptitude
        },
        {
            name: "Communication",
            score: dashboardData.skills.communication
        }
    ].filter(skill => toNumber(skill.score) !== null);

    if (scores.length === 0) {
        element.textContent = "Update your skill profile";
        return;
    }

    scores.sort((a, b) => Number(a.score) - Number(b.score));

    const lowestSkill = scores[0];

    if (Number(lowestSkill.score) >= 80) {
        element.textContent = "Maintain your performance";
    } else {
        element.textContent = `Improve ${lowestSkill.name}`;
    }
}


// =========================================================
// No Prediction State
// =========================================================

function showNoPredictionState() {
    setValue("placementValue", "--");
    setValue("employabilityValue", "--");
    setValue("placementProbability", "--");
    setValue("predictionLabel", "Not available");
    setValue("predictionStatus", "No Prediction");
    setValue(
        "predictionInsight",
        "Generate a prediction to receive AI-powered placement insights."
    );
}


// =========================================================
// Legacy Animation Helper
// Kept available if other scripts use it.
// =========================================================

function animateNumber(elementId, targetValue, decimals = 0, suffix = "") {
    const element = document.getElementById(elementId);

    if (!element) {
        return;
    }

    const target = toNumber(targetValue);

    element.textContent =
        target === null ? "--" : `${target.toFixed(decimals)}${suffix}`;
}


function typeText(element, text) {
    if (element) {
        element.textContent = text == null ? "" : String(text);
    }
}