
document.addEventListener("DOMContentLoaded", loadSkillGaps);

async function loadSkillGaps() {
    const container = document.getElementById("skillGapsContainer");
    const highCount = document.getElementById("highPriorityCount");
    const mediumCount = document.getElementById("mediumPriorityCount");

    if (!container) return;

    container.innerHTML = '<div class="empty-state">Loading skill gaps...</div>';

    try {
        const response = await fetch("/api/student/skill-gaps", {
            method: "GET",
            credentials: "same-origin",
            headers: {
                "Accept": "application/json"
            }
        });

        if (!response.ok) {
            throw new Error(`Failed to load skill gaps (HTTP ${response.status})`);
        }

        const data = await response.json();

        if (!data.success) {
            throw new Error(data.message || "Unable to load skill gaps.");
        }

        const skillGaps = data.skill_gaps || [];

        if (skillGaps.length === 0) {
            showEmptyState(
                container,
                "No skill gap data available. Generate a prediction first."
            );
            updateCounts(highCount, mediumCount, []);
            return;
        }

        renderSkillGaps(container, skillGaps);
        updateCounts(highCount, mediumCount, skillGaps);

    } catch (error) {
        console.error("Skill gap loading error:", error);

        showEmptyState(
            container,
            "Unable to load skill gaps. Please refresh the page or log in again."
        );
    }
}

function renderSkillGaps(container, skillGaps) {
    container.innerHTML = "";

    skillGaps.forEach(gap => {
        const current = Number(gap.current_score) || 0;
        const target = Number(gap.target_score) || 80;
        const priority = String(gap.priority || "Medium");
        const item = document.createElement("div");

        item.className = "profile-list-item";

        const header = document.createElement("div");
        header.className = "skill-gap-header";

        const details = document.createElement("div");
        const title = document.createElement("h4");
        title.textContent = gap.skill_name || "Unnamed skill";

        const score = document.createElement("p");
        score.append("Current Score: ");

        const scoreValue = document.createElement("strong");
        scoreValue.textContent = current.toFixed(0);
        score.appendChild(scoreValue);

        details.append(title, score);

        const badge = document.createElement("span");
        badge.className = `skill-priority ${priority.toLowerCase()}`;
        badge.textContent = priority;

        header.append(details, badge);

        const progressSection = document.createElement("div");
        progressSection.className = "skill-gap-progress";

        const progressBar = document.createElement("div");
        progressBar.className = "skill-gap-progress-bar";

        const progressFill = document.createElement("div");
        progressFill.className = "skill-gap-progress-fill";
        progressFill.style.width =
            `${Math.min(Math.max(current, 0), 100)}%`;

        progressBar.appendChild(progressFill);
        progressSection.appendChild(progressBar);

        const meta = document.createElement("div");
        meta.className = "item-meta";
        meta.textContent =
            `Target: ${target.toFixed(0)} | Gap: ${Math.max(target - current, 0).toFixed(0)} points`;

        item.append(header, progressSection, meta);
        container.appendChild(item);
    });
}

function updateCounts(highElement, mediumElement, skillGaps) {
    if (!highElement || !mediumElement) return;

    highElement.textContent = skillGaps.filter(
        gap => String(gap.priority).toLowerCase() === "high"
    ).length;

    mediumElement.textContent = skillGaps.filter(
        gap => String(gap.priority).toLowerCase() === "medium"
    ).length;
}

function showEmptyState(container, message) {
    if (!container) return;

    const state = document.createElement("div");
    state.className = "empty-state";
    state.textContent = message;

    container.replaceChildren(state);
}