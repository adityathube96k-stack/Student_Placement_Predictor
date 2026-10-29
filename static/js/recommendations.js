document.addEventListener("DOMContentLoaded", () => {
    loadRecommendations();
});

async function loadRecommendations() {

    const container =
        document.getElementById("recommendationsContainer");

    const highCount =
        document.getElementById("highRecommendationCount");

    const mediumCount =
        document.getElementById("mediumRecommendationCount");

    const totalCount =
        document.getElementById("totalRecommendationCount");

    try {

        const response =
            await fetch("/api/student/recommendations");

        if (!response.ok) {
            throw new Error("Failed to load recommendations.");
        }

        const data =
            await response.json();

        if (
            !data.success ||
            !data.recommendations ||
            data.recommendations.length === 0
        ) {

            showEmptyState(
                container,
                "No recommendations available. Generate a prediction first."
            );

            return;
        }

        const recommendations =
            data.recommendations;

        renderRecommendations(
            container,
            recommendations
        );

        updateRecommendationCounts(
            highCount,
            mediumCount,
            totalCount,
            recommendations
        );

    } catch (error) {

        console.error(
            "Recommendation loading error:",
            error
        );

        showEmptyState(
            container,
            "Unable to load recommendations."
        );
    }
}


/* =========================================================
   Render Recommendations
   ========================================================= */

function renderRecommendations(
    container,
    recommendations
) {

    if (!container) {
        return;
    }

    container.innerHTML = "";

    recommendations.forEach(
        (recommendation, index) => {

            const item =
                document.createElement("div");

            item.className =
                "profile-list-item recommendation-item";

            const priority =
                String(
                    recommendation.priority || "Medium"
                );

            const priorityClass =
                priority.toLowerCase();

            item.innerHTML = `

                <div class="recommendation-header">

                    <div class="recommendation-number">
                        ${index + 1}
                    </div>

                    <div class="recommendation-title">

                        <h4>
                            ${escapeHtml(
                                recommendation.category
                            )}
                        </h4>

                        <span class="recommendation-priority ${priorityClass}">
                            ${escapeHtml(priority)}
                        </span>

                    </div>

                </div>

                <div class="recommendation-content">

                    <p>
                        ${escapeHtml(
                            recommendation.recommendation
                        )}
                    </p>

                </div>

            `;

            container.appendChild(item);
        }
    );
}


/* =========================================================
   Update Summary Counts
   ========================================================= */

function updateRecommendationCounts(
    highElement,
    mediumElement,
    totalElement,
    recommendations
) {

    let high = 0;
    let medium = 0;

    recommendations.forEach(
        recommendation => {

            const priority =
                String(
                    recommendation.priority || ""
                ).toLowerCase();

            if (priority === "high") {
                high++;
            }

            if (priority === "medium") {
                medium++;
            }
        }
    );

    if (highElement) {
        highElement.textContent = high;
    }

    if (mediumElement) {
        mediumElement.textContent = medium;
    }

    if (totalElement) {
        totalElement.textContent =
            recommendations.length;
    }
}


/* =========================================================
   Empty State
   ========================================================= */

function showEmptyState(
    container,
    message
) {

    if (!container) {
        return;
    }

    container.innerHTML = `

        <div class="empty-state">

            ${escapeHtml(message)}

        </div>

    `;
}


/* =========================================================
   HTML Escape
   ========================================================= */

function escapeHtml(value) {

    if (
        value === undefined ||
        value === null
    ) {
        return "";
    }

    return String(value)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}