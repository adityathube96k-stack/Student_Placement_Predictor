document.addEventListener("DOMContentLoaded", () => {
    loadProfileData();
});


// =========================================================
// Load All Profile Data
// =========================================================

async function loadProfileData() {

    try {

        await loadProfile();

        await loadAcademic();

        await loadSkills();

        await loadCertifications();

        await loadProjects();

        await loadInternships();

    } catch (error) {

        console.error(
            "Profile loading error:",
            error
        );
    }
}


// =========================================================
// Load Student Profile
// =========================================================

async function loadProfile() {

    const response =
        await fetch("/api/student/profile");

    if (!response.ok) {
        console.error("Failed to load profile.");
        return;
    }

    const data =
        await response.json();

    if (!data.success || !data.profile) {
        return;
    }

    const profile =
        data.profile;


    // Header
    setText(
        "profileName",
        profile.full_name
    );

    setText(
        "profileEmail",
        profile.email
    );


    // Personal Information
    setText(
        "studentId",
        profile.student_id
    );

    setText(
        "fullName",
        profile.full_name
    );

    setText(
        "email",
        profile.email
    );

    setText(
        "phone",
        profile.phone
    );

    setText(
        "gender",
        profile.gender
    );

    setText(
        "dateOfBirth",
        formatDate(profile.date_of_birth)
    );


    // Academic Information
    setText(
        "department",
        profile.department
    );

    setText(
        "yearOfStudy",
        profile.year_of_study
    );

    setText(
        "semester",
        profile.semester
    );
}


// =========================================================
// Load Academic Records
// =========================================================

async function loadAcademic() {

    const response =
        await fetch("/api/student/academic");

    if (!response.ok) {
        console.error(
            "Failed to load academic records."
        );
        return;
    }

    const data =
        await response.json();

    if (
        !data.success ||
        !data.academic_records ||
        data.academic_records.length === 0
    ) {
        return;
    }

    const academic =
        data.academic_records[0];


    setText(
        "cgpa",
        academic.cgpa
    );

    setText(
        "attendance",
        academic.attendance + "%"
    );

    setText(
        "semesterMarks",
        academic.semester_marks + "%"
    );

    setText(
        "backlogs",
        academic.backlogs
    );
}


// =========================================================
// Load Skills
// =========================================================

async function loadSkills() {

    const response =
        await fetch("/api/student/skills");

    if (!response.ok) {
        console.error(
            "Failed to load skills."
        );
        return;
    }

    const data =
        await response.json();

    if (
        !data.success ||
        !data.skills
    ) {
        return;
    }

    const skills =
        data.skills;


    renderTags(
        "programmingLanguages",
        skills.programming_languages
    );

    renderTags(
        "technicalSkills",
        skills.technical_skills
    );

    renderTags(
        "softSkills",
        skills.soft_skills
    );
}


// =========================================================
// Load Certifications
// =========================================================

async function loadCertifications() {

    const response =
        await fetch(
            "/api/student/certifications"
        );

    if (!response.ok) {
        console.error(
            "Failed to load certifications."
        );
        return;
    }

    const data =
        await response.json();

    const container =
        document.getElementById(
            "certificationsList"
        );

    if (!container) {
        return;
    }


    if (
        !data.success ||
        !data.certifications ||
        data.certifications.length === 0
    ) {

        container.innerHTML =
            `<div class="empty-state">
                No certifications added yet.
            </div>`;

        return;
    }


    container.innerHTML = "";


    data.certifications.forEach(
        certification => {

            const item =
                document.createElement("div");

            item.className =
                "profile-list-item";


            item.innerHTML = `
                <h4>
                    ${escapeHtml(
                        certification.certification_name
                    )}
                </h4>

                <p>
                    Issued by:
                    ${escapeHtml(
                        certification.issuing_organization || ""
                    )}
                </p>

                <div class="item-meta">
                    ${formatDate(
                        certification.issue_date
                    )}
                </div>
            `;

            container.appendChild(item);
        }
    );
}


// =========================================================
// Load Projects
// =========================================================

async function loadProjects() {

    const response =
        await fetch(
            "/api/student/projects"
        );

    if (!response.ok) {
        console.error(
            "Failed to load projects."
        );
        return;
    }

    const data =
        await response.json();

    const container =
        document.getElementById(
            "projectsList"
        );

    if (!container) {
        return;
    }


    if (
        !data.success ||
        !data.projects ||
        data.projects.length === 0
    ) {

        container.innerHTML =
            `<div class="empty-state">
                No projects added yet.
            </div>`;

        return;
    }


    container.innerHTML = "";


    data.projects.forEach(
        project => {

            const item =
                document.createElement("div");

            item.className =
                "profile-list-item";


            item.innerHTML = `
                <h4>
                    ${escapeHtml(
                        project.project_title
                    )}
                </h4>

                <p>
                    ${escapeHtml(
                        project.description || ""
                    )}
                </p>

                <div class="item-meta">
                    ${escapeHtml(
                        project.technologies || ""
                    )}
                </div>
            `;

            container.appendChild(item);
        }
    );
}


// =========================================================
// Load Internships
// =========================================================

async function loadInternships() {

    const response =
        await fetch(
            "/api/student/internships"
        );

    if (!response.ok) {
        console.error(
            "Failed to load internships."
        );
        return;
    }

    const data =
        await response.json();

    const container =
        document.getElementById(
            "internshipsList"
        );

    if (!container) {
        return;
    }


    if (
        !data.success ||
        !data.internships ||
        data.internships.length === 0
    ) {

        container.innerHTML =
            `<div class="empty-state">
                No internships added yet.
            </div>`;

        return;
    }


    container.innerHTML = "";


    data.internships.forEach(
        internship => {

            const item =
                document.createElement("div");

            item.className =
                "profile-list-item";


            const duration =
                internship.duration_months !== null &&
                internship.duration_months !== undefined
                    ? `${internship.duration_months} months`
                    : "";


            item.innerHTML = `
                <h4>
                    ${escapeHtml(
                        internship.company_name
                    )}
                </h4>

                <p>
                    Role:
                    ${escapeHtml(
                        internship.role || ""
                    )}
                </p>

                <div class="item-meta">
                    ${escapeHtml(duration)}
                </div>
            `;

            container.appendChild(item);
        }
    );
}


// =========================================================
// Helper: Set Text
// =========================================================

function setText(
    elementId,
    value
) {

    const element =
        document.getElementById(
            elementId
        );

    if (!element) {
        return;
    }

    if (
        value === undefined ||
        value === null ||
        value === ""
    ) {

        element.textContent = "--";

        return;
    }

    element.textContent = value;
}


// =========================================================
// Helper: Render Skill Tags
// =========================================================

function renderTags(
    elementId,
    value
) {

    const container =
        document.getElementById(
            elementId
        );

    if (!container) {
        return;
    }


    if (
        value === undefined ||
        value === null ||
        value === ""
    ) {

        container.innerHTML =
            `<span class="skill-tag">
                Not added
            </span>`;

        return;
    }


    let values = [];


    if (Array.isArray(value)) {

        values = value;

    } else {

        values =
            String(value)
                .split(",")
                .map(
                    item => item.trim()
                )
                .filter(
                    item => item.length > 0
                );
    }


    if (values.length === 0) {

        container.innerHTML =
            `<span class="skill-tag">
                Not added
            </span>`;

        return;
    }


    container.innerHTML = "";


    values.forEach(
        skill => {

            const tag =
                document.createElement("span");

            tag.className =
                "skill-tag";

            tag.textContent = skill;

            container.appendChild(tag);
        }
    );
}


// =========================================================
// Helper: Format Date
// =========================================================

function formatDate(value) {

    if (
        !value ||
        value === "--"
    ) {
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


// =========================================================
// Helper: Escape HTML
// =========================================================

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