document.addEventListener("DOMContentLoaded", () => {
    loadPredictionHistory();
});

async function loadPredictionHistory() {

    const container =
        document.getElementById("historyContainer");

    const totalPredictions =
        document.getElementById("totalPredictions");

    const bestPlacement =
        document.getElementById("bestPlacement");

    const bestEmployability =
        document.getElementById("bestEmployability");

    try {

        const response =
            await fetch("/api/prediction/history");

        if (!response.ok) {
            throw new Error("Failed to load prediction history.");
        }

        const data =
            await response.json();

        if (
            !data.success ||
            !data.history ||
            data.history.length === 0
        ) {

            showEmptyState(
                container,
                "No prediction history available. Generate your first prediction."
            );

            return;
        }

        const history =
            data.history;

        renderHistory(
            container,
            history
        );

        updateSummary(
            totalPredictions,
            bestPlacement,
            bestEmployability,
            history
        );

    } catch (error) {

        console.error(
            "Prediction history error:",
            error
        );

        showEmptyState(
            container,
            "Unable to load prediction history."
        );
    }
}


/* =========================================================
   Render History
   ========================================================= */

function renderHistory(
    container,
    history
) {

    if (!container) {
        return;
    }

    container.innerHTML = "";

    history.forEach(
        (prediction, index) => {

            const item =
                document.createElement("div");

            item.className =
                "profile-list-item history-item";

            const probability =
                Number(
                    prediction.placement_probability
                );

            const employability =
                Number(
                    prediction.employability_score
                );

            const predictionLabel =
                prediction.prediction_label ||
                "Prediction";

            const date =
                formatDate(
                    prediction.created_at
                );

            const statusClass =
                prediction.performance_prediction == 1
                    ? "positive"
                    : "needs-improvement";

            item.innerHTML = `

                <div class="history-header">

                    <div>

                        <h4>
                            Prediction #${history.length - index}
                        </h4>

                        <p>
                            ${escapeHtml(date)}
                        </p>

                    </div>

                    <span class="history-status ${statusClass}">
                        ${escapeHtml(predictionLabel)}
                    </span>

                </div>


                <div class="history-metrics">

                    <div class="history-metric">

                        <span>
                            Placement Probability
                        </span>

                        <strong>
                            ${probability.toFixed(2)}%
                        </strong>

                    </div>


                    <div class="history-metric">

                        <span>
                            Employability Score
                        </span>

                        <strong>
                            ${employability.toFixed(2)}%
                        </strong>

                    </div>


                    <div class="history-metric">

                        <span>
                            AI Model
                        </span>

                        <strong>
                            ${escapeHtml(
                                prediction.model_name || "ML Model"
                            )}
                        </strong>

                    </div>

                </div>

            `;

            container.appendChild(item);
        }
    );
}


/* =========================================================
   Summary
   ========================================================= */

function updateSummary(
    totalElement,
    bestPlacementElement,
    bestEmployabilityElement,
    history
) {

    if (totalElement) {
        totalElement.textContent =
            history.length;
    }

    let highestPlacement = 0;
    let highestEmployability = 0;

    history.forEach(
        prediction => {

            const placement =
                Number(
                    prediction.placement_probability
                );

            const employability =
                Number(
                    prediction.employability_score
                );

            if (placement > highestPlacement) {
                highestPlacement = placement;
            }

            if (employability > highestEmployability) {
                highestEmployability = employability;
            }
        }
    );

    if (bestPlacementElement) {
        bestPlacementElement.textContent =
            highestPlacement.toFixed(2) + "%";
    }

    if (bestEmployabilityElement) {
        bestEmployabilityElement.textContent =
            highestEmployability.toFixed(2) + "%";
    }
}


/* =========================================================
   Date Formatting
   ========================================================= */

function formatDate(value) {

    if (!value) {
        return "--";
    }

    const date =
        new Date(value);

    if (isNaN(date.getTime())) {
        return value;
    }

    return date.toLocaleDateString(
        "en-IN",
        {
            day: "2-digit",
            month: "short",
            year: "numeric"
        }
    );
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