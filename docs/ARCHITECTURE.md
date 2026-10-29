# Architecture

```
Browser ── Flask app (app.py: create_app)
            ├─ routes/         one blueprint per feature, thin controllers
            ├─ models/         data access (User, Student, Company, Drive, Notification, ...)
            ├─ analytics/      aggregate queries for dashboards and charts
            ├─ ml/             dataset cleaning, training, registry, prediction + explanations
            ├─ recommendation_engine/ · company_eligibility/ · interview_engine/ · resume_analyzer/
            ├─ reports/        PDF (ReportLab) and Excel/CSV (openpyxl) generation
            ├─ notifications/  in-app, SMTP email, SMS webhook
            ├─ database/       dual-engine connection layer, schema, seed data
            └─ templates/ + static/   server-rendered UI, no build step
```

## Request lifecycle

1. `before_request` starts a permanent session and verifies the CSRF token on every non-GET request.
2. A decorator (`student_required`, `admin_required`, `tpo_required`) checks the session role.
3. The route validates input, calls models/engines, and renders a template or returns a download.
4. `after_request` adds security headers, including a Content-Security-Policy that forbids inline scripts (all JavaScript lives in `static/js`).

## Prediction pipeline

* **Training** (`ml/train_model.py`): cleans the dataset, splits 80/20, compares logistic regression, random forest and gradient boosting with 5-fold cross-validation, prefers the simpler model when scores are within 0.5 F1 points, then reports hold-out accuracy, precision, recall, F1, ROC AUC, a confusion matrix and permutation importance. The deployed model is refit on all rows.
* **Registry**: each run is written to `model_versions`; the active artifact is `ml/models/placement_pipeline.joblib` with `model_metadata.json`.
* **Serving** (`ml/predict.py`): one batched call returns the probability and, for each input, how far it moves the probability compared with the median student. `model_loader` retrains automatically if the artifact is missing or was saved by an incompatible scikit-learn version.
* **Optional features**: projects, internships and certifications are used when the dataset contains them. Datasets with only the six core columns still train; missing values are median-imputed.

## Security measures

* Passwords hashed with scrypt (Werkzeug); minimum 8 characters with a letter and a number.
* CSRF tokens on every state-changing request; session cookie `HttpOnly`, `SameSite=Lax`, `Secure` in production.
* Login throttling per email and IP; password reset links are signed, expire, and stop working after use.
* Resumes are stored in `instance/resumes` under random names and served only to their owner.
* Uploads are validated (PDF signature, CSV schema and ranges) and size-limited.
* All SQL is parameterised; only whitelisted column names are interpolated.
* Same-site redirect checking, no user enumeration on password reset, `no-store` caching for signed-in pages.

## Deployment

`gunicorn --preload run:app` (see `Dockerfile`, `docker-compose.yml`, `render.yaml`, `Procfile`). `--preload` creates the app, and therefore the database, once before workers start. Set `APP_ENV=production`, a real `SECRET_KEY`, and `ADMIN_EMAIL`/`ADMIN_PASSWORD` for the first admin; demo data is off by default in production.
