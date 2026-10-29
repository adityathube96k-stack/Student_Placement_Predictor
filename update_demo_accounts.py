"""One-time local account updater for the Student Placement Predictor.
Run with: python update_demo_accounts.py
Delete this script after successful use because it contains demo credentials.
"""
from app import create_app
from database.db import execute, query_one
from utils.security import hash_password


import os

ACCOUNTS = [
    {
        "role": "admin",
        "name": "Aditya Thube",
        "email": "adityathube96k@gmail.com",
        "password": os.getenv("DEMO_ADMIN_PASSWORD", ""),
        "old_email": "admin@placement.com",
    },
    {
        "role": "tpo",
        "name": "Ganesh Marathe",
        "email": "ganeshmarathe8232@gmail.com",
        "password": os.getenv("DEMO_TPO_PASSWORD", ""),
        "old_email": "tpo@placement.com",
    },
    {
        "role": "student",
        "name": "Satish Dhangar",
        "email": "sdhangar811@gmail.com",
        "password": os.getenv("DEMO_STUDENT_PASSWORD", ""),
        "old_email": "student@placement.com",
    },
]

app = create_app()


app = create_app()
with app.app_context():
    for account in ACCOUNTS:
        # Prefer the target email if it already exists; otherwise preserve the
        # existing demo account (including its linked student profile).
        user = query_one("SELECT id FROM users WHERE email = %s", (account["email"],))
        if not user:
            user = query_one("SELECT id FROM users WHERE email = %s", (account["old_email"],))
        if not user:
            print(
                f'SKIPPED {account["role"]}: neither the existing demo account '
                f'({account["old_email"]}) nor the target email '
                f'({account["email"]}) exists. No account was created.'
            )
            continue
        execute(
            "UPDATE users SET full_name = %s, email = %s, password_hash = %s, role = %s, is_active = %s WHERE id = %s",
            (account["name"], account["email"], hash_password(account["password"]),
             account["role"], 1, user["id"]),
        )
        print(f'Updated {account["role"]}: {account["email"]}')

print("Account update complete. Remove update_demo_accounts.py after verifying sign-in.")
