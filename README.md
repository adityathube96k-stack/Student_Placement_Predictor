# 🎓 Student_Placement_Predictor

## 📌 Overview

**Student_Placement_Predictor** is an industry-level AI and Machine Learning based web application designed to predict student placement opportunities and improve career readiness.

The system analyzes academic performance, technical skills, communication abilities, aptitude scores, internships, projects, certifications, and other employability factors to predict placement outcomes and generate personalized recommendations.

The platform helps students, Training & Placement Officers (TPOs), and educational institutions monitor placement readiness through advanced analytics and intelligent recommendations.

---

# 🚀 Features

## 👨‍🎓 Student Features

### Authentication System

* Student Registration
* Secure Login
* Forgot Password
* Profile Management
* Role-Based Access

### Placement Prediction

* Placement Prediction (Placed / Not Placed)
* Placement Probability Score
* Prediction History
* Performance Tracking

### Placement Readiness Score

* Readiness Score (0–100)
* Employability Assessment
* Progress Monitoring

### Resume Analyzer

* Resume Upload (PDF)
* Resume Parsing
* Resume Scoring
* Resume Improvement Suggestions

### Skill Gap Analysis

* Identify Missing Skills
* Industry Skill Comparison
* Personalized Recommendations

### Career Roadmap Generator

* Monthly Learning Plan
* Career Growth Roadmap
* Personalized Development Path

### Company Eligibility Checker

* Company-wise Eligibility Check
* CGPA Validation
* Skills Matching
* Backlog Verification

### AI Interview Preparation

* Technical Questions
* HR Questions
* Aptitude Questions
* Mock Interviews
* Interview Evaluation

### Learning Recommendations

* Recommended Courses
* Certification Suggestions
* Learning Resources

### Reports

* Placement Report
* Resume Report
* Skill Gap Report
* Download PDF Reports

---

## 👨‍💼 Admin Features

### Student Management

* Add Student
* Update Student
* Delete Student
* Manage Records

### Company Management

* Add Company
* Edit Eligibility Criteria
* Manage Recruitment Rules

### Analytics Dashboard

* Placement Statistics
* Department Analysis
* Student Performance Analysis

### Machine Learning Management

* Dataset Upload
* Model Retraining
* Model Evaluation

---

## 🏢 TPO Features

### Placement Monitoring

* Eligible Students List
* Placement Statistics
* Company-wise Reports
* Department-wise Reports

---

# 🏗 System Architecture

```text
Frontend (HTML/CSS/JavaScript)
            │
            ▼
       Flask Backend
            │
 ┌──────────┴──────────┐
 ▼                     ▼
MySQL Database   Machine Learning Engine
                         │
                         ▼
                 Prediction Model
                         │
                         ▼
             Recommendation Engine
```

---

# 🧠 Machine Learning Workflow

```text
Dataset
   │
   ▼
Data Cleaning
   │
   ▼
Feature Engineering
   │
   ▼
Train/Test Split
   │
   ▼
Random Forest / XGBoost
   │
   ▼
Model Evaluation
   │
   ▼
Model Deployment
   │
   ▼
Real-Time Prediction
```

---

# 🛠 Technology Stack

## Frontend

* HTML5
* CSS3
* JavaScript
* Bootstrap 5
* Chart.js

## Backend

* Python
* Flask

## Database

* MySQL

## Machine Learning

* Scikit-Learn
* Pandas
* NumPy
* Joblib

## Resume Processing

* PyPDF2
* pdfplumber
* NLTK
* spaCy

## Reporting

* ReportLab
* OpenPyXL

## Notifications

* Flask-Mail

## Deployment

* GitHub
* Render
* AWS
* Docker

---

# 📂 Project Structure

```text
Student_Placement_Predictor/
│
├── app.py
├── config.py
├── requirements.txt
├── .env
├── README.md
│
├── static/
│   ├── css/
│   ├── js/
│   ├── images/
│   └── uploads/
│
├── templates/
│   ├── auth/
│   ├── student/
│   ├── admin/
│   └── tpo/
│
├── routes/
├── models/
├── database/
├── dataset/
├── ml/
├── resume_analyzer/
├── recommendation_engine/
├── interview_engine/
├── company_eligibility/
├── analytics/
├── reports/
├── notifications/
├── utils/
├── tests/
└── docs/
```

---

# 🗄 Database Tables

### users

* id
* name
* email
* password
* role

### students

* id
* user_id
* cgpa
* attendance
* aptitude
* coding
* communication
* technical
* projects
* internships
* certifications

### predictions

* id
* user_id
* prediction
* probability
* readiness_score

### companies

* id
* company_name
* min_cgpa
* required_skills

### resume_analysis

* id
* user_id
* resume_score

### interviews

* id
* user_id
* interview_score

### notifications

* id
* user_id
* message
* status

---

# ⚙ Installation

## Clone Repository

```bash
git clone https://github.com/your-username/Student_Placement_Predictor.git
cd Student_Placement_Predictor
```

---

## Create Virtual Environment

### Windows

```bash
python -m venv venv
venv\Scripts\activate
```

### Linux / macOS

```bash
python3 -m venv venv
source venv/bin/activate
```

---

## Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Configure Database

Create MySQL Database:

```sql
CREATE DATABASE placement_predictor;
```

Update database credentials inside:

```python
config.py
```

---

## Train Machine Learning Model

```bash
python ml/train_model.py
```

---

## Run Application

```bash
python app.py
```

Open Browser:

```text
http://127.0.0.1:5000
```

---

# 📊 Prediction Inputs

The model uses the following parameters:

* CGPA
* Attendance Percentage
* Aptitude Score
* Coding Skill Score
* Communication Skill Score
* Technical Skill Score
* Projects Completed
* Internship Experience
* Certifications

---

# 🎯 Prediction Outputs

### Placement Prediction

* Placed
* Not Placed

### Placement Probability

Example:

```text
89%
```

### Placement Readiness Score

Example:

```text
84/100
```

### Recommendations

* Improve Coding Skills
* Complete More Projects
* Improve Communication Skills
* Obtain Industry Certifications
* Practice Aptitude Questions

---

# 🔒 Security Features

* Password Hashing
* Session Management
* Role-Based Access Control
* Input Validation
* SQL Injection Prevention
* Secure Authentication
* Protected Admin Routes

---

# 📈 Future Enhancements

* AI Career Assistant Chatbot
* LinkedIn Profile Analysis
* ATS Resume Scoring
* Real-Time Job Recommendations
* Voice-Based Mock Interviews
* AI Career Guidance System
* Multi-College Placement Analytics
* Mobile Application

---

# 📊 Expected Benefits

### Students

* Understand placement readiness
* Improve weak skills
* Receive personalized recommendations
* Prepare effectively for interviews

### Colleges

* Monitor student placement performance
* Improve placement statistics
* Generate analytical reports

### TPO

* Track eligible students
* Manage company requirements
* Analyze placement trends

---


---

# 📄 License

This project is developed for academic, educational, and research purposes.

© 2026 Student_Placement_Predictor. All Rights Reserved.
