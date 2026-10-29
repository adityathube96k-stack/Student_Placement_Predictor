# Route reference

Generated with `python manage.py routes`. Access is enforced by decorators in `utils/decorators.py`; every `POST` requires a CSRF token.


## Public

| Method | URL | Endpoint |
|---|---|---|
| GET | `/` | `main.index` |
| GET | `/about` | `main.about` |
| GET,POST | `/auth/forgot-password` | `auth.forgot_password` |
| GET,POST | `/auth/login` | `auth.login` |
| GET | `/auth/logout` | `auth.logout` |
| GET,POST | `/auth/register` | `auth.register` |
| GET,POST | `/auth/reset-password/<token>` | `auth.reset_password` |
| GET,POST | `/contact` | `main.contact` |
| GET | `/health` | `health` |

## Signed in

| Method | URL | Endpoint |
|---|---|---|
| GET | `/notifications` | `notifications.inbox` |
| POST | `/notifications/<int:notification_id>/delete` | `notifications.delete_item` |
| GET | `/notifications/<int:notification_id>/open` | `notifications.open_item` |
| POST | `/notifications/read-all` | `notifications.read_all` |
| GET | `/notifications/unread-count` | `notifications.unread_count` |

## Student

| Method | URL | Endpoint |
|---|---|---|
| GET | `/reports/student` | `report.student_reports` |
| GET | `/reports/student/history.xlsx` | `report.student_history_xlsx` |
| GET | `/reports/student/pdf` | `report.student_pdf` |
| GET | `/student/analytics` | `analytics.student_analytics` |
| GET | `/student/certifications` | `recommendation.certifications` |
| GET | `/student/company-eligibility` | `company.company_eligibility` |
| GET | `/student/company-eligibility-history` | `company.company_eligibility_history` |
| GET | `/student/dashboard` | `dashboard.dashboard` |
| GET | `/student/drives` | `company.drives` |
| POST | `/student/drives/<int:drive_id>/apply` | `company.apply_drive` |
| GET | `/student/mock-interview` | `interview.mock_interview` |
| GET | `/student/mock-interview-history` | `interview.interview_history` |
| GET | `/student/mock-interview/result/<int:interview_id>` | `interview.interview_result` |
| GET | `/student/mock-interview/start` | `interview.start_interview` |
| POST | `/student/mock-interview/submit` | `interview.submit_interview` |
| GET,POST | `/student/prediction` | `prediction.prediction` |
| GET | `/student/prediction-history` | `prediction.prediction_history` |
| POST | `/student/prediction/preview` | `prediction.preview` |
| GET,POST | `/student/profile` | `dashboard.profile` |
| GET | `/student/readiness-history` | `readiness.readiness_history` |
| GET,POST | `/student/readiness-score` | `readiness.readiness_score` |
| GET | `/student/recommendations` | `recommendation.recommendations` |
| GET,POST | `/student/resume` | `resume.resume_upload` |
| GET | `/student/resume-history` | `resume.resume_history` |
| GET | `/student/resume/<int:analysis_id>` | `resume.resume_result` |
| GET | `/student/resume/<int:analysis_id>/file` | `resume.resume_file` |
| POST | `/student/resume/<int:analysis_id>/sync-skills` | `resume.sync_skills` |
| GET | `/student/roadmap` | `recommendation.roadmap` |
| GET,POST | `/student/skill-gap` | `skill_gap.skill_gap` |
| GET | `/student/skill-gap-history` | `skill_gap.skill_gap_history` |

## TPO

| Method | URL | Endpoint |
|---|---|---|
| POST | `/tpo/applications/<int:application_id>/status` | `tpo.application_status` |
| GET | `/tpo/company-drives` | `tpo.company_drives` |
| GET | `/tpo/dashboard` | `tpo.dashboard` |
| GET | `/tpo/drives/<int:drive_id>/applicants` | `tpo.drive_applicants` |
| POST | `/tpo/drives/<int:drive_id>/delete` | `tpo.drive_delete` |
| GET,POST | `/tpo/drives/<int:drive_id>/edit` | `tpo.drive_edit` |
| GET,POST | `/tpo/drives/new` | `tpo.drive_new` |
| GET | `/tpo/eligible-students` | `tpo.eligible_students` |
| GET | `/tpo/placement-statistics` | `tpo.placement_statistics` |
| GET | `/tpo/reports` | `tpo.reports` |

## Admin

| Method | URL | Endpoint |
|---|---|---|
| GET | `/admin/analytics` | `admin.analytics` |
| GET | `/admin/companies` | `admin.manage_companies` |
| POST | `/admin/companies/<int:company_id>/delete` | `admin.company_delete` |
| GET,POST | `/admin/companies/<int:company_id>/edit` | `admin.company_edit` |
| POST | `/admin/companies/<int:company_id>/toggle` | `admin.company_toggle` |
| GET,POST | `/admin/companies/new` | `admin.company_new` |
| GET | `/admin/dashboard` | `admin.dashboard` |
| POST | `/admin/datasets/<int:dataset_id>/delete` | `admin.dataset_delete` |
| POST | `/admin/datasets/<int:dataset_id>/toggle` | `admin.dataset_toggle` |
| GET,POST | `/admin/model-training` | `admin.model_training` |
| GET | `/admin/reports` | `admin.reports` |
| GET | `/admin/students` | `admin.manage_students` |
| POST | `/admin/students/<int:uid>/delete` | `admin.student_delete` |
| GET,POST | `/admin/students/<int:uid>/edit` | `admin.student_edit` |
| POST | `/admin/students/<int:uid>/toggle` | `admin.student_toggle` |
| GET,POST | `/admin/students/new` | `admin.student_new` |
| GET,POST | `/admin/upload-dataset` | `admin.upload_dataset` |

## Admin or TPO

| Method | URL | Endpoint |
|---|---|---|
| GET | `/reports/staff/companies.xlsx` | `report.companies_xlsx` |
| GET | `/reports/staff/placements.xlsx` | `report.placements_xlsx` |
| GET | `/reports/staff/predictions.xlsx` | `report.predictions_xlsx` |
| GET | `/reports/staff/students.csv` | `report.students_csv` |
| GET | `/reports/staff/students.xlsx` | `report.students_xlsx` |
