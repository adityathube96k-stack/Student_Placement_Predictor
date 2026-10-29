#!/usr/bin/env python
"""Command line helper.

    python manage.py init-db            create/upgrade tables (and demo data outside production)
    python manage.py seed [--force]     insert demo data
    python manage.py create-user        create an admin / tpo / student account
    python manage.py train              retrain the placement model
    python manage.py export-schema      write database/schema.sql (MySQL)
    python manage.py routes             list all URLs
    python manage.py test               run the test suite
"""
import argparse
import getpass
import sys


def cmd_init_db(args):
    from config import Config
    from database.init_db import init_database
    info = init_database(seed=args.seed or None)
    print(f"Database ready ({info['engine']}). Added columns: {info['columns_added'] or 'none'}. "
          f"Demo data: {'created' if info['seeded'] else 'skipped'}.")


def cmd_seed(args):
    from database.schema import create_schema
    from database.seed import seed_demo
    create_schema()
    print("Demo data created." if seed_demo(force=args.force) else "Users already exist; use --force to add anyway.")


def cmd_create_user(args):
    from database.schema import create_schema
    from models.student import Student
    from models.user import User
    from utils.validators import password_problem, validate_email
    create_schema()
    email = args.email or input("Email: ").strip().lower()
    name = args.name or input("Full name: ").strip()
    password = args.password or getpass.getpass("Password: ")
    if not validate_email(email) or password_problem(password) or len(name) < 2:
        sys.exit(password_problem(password) or "Invalid name or email.")
    if User.find_by_email(email):
        sys.exit("That email already exists.")
    user_id = User.create(name, email, password, args.role)
    if args.role == "student":
        Student.create_profile(user_id)
    print(f"Created {args.role} {email}.")


def cmd_train(args):
    from ml.train_model import train_model
    info = train_model()
    print(f"Trained {info['algorithm']} ({info['version']}) on {info['rows']} rows")
    for key, value in info["metrics"].items():
        print(f"  {key:<10}{value}%")


def cmd_export_schema(args):
    from database.schema import export_mysql_sql
    with open("database/schema.sql", "w", encoding="utf-8") as handle:
        handle.write(export_mysql_sql())
    print("Wrote database/schema.sql")


def cmd_routes(args):
    from app import create_app
    app = create_app()
    for rule in sorted(app.url_map.iter_rules(), key=lambda r: str(r)):
        print(f"{','.join(sorted(rule.methods - {'HEAD', 'OPTIONS'})):<10} {rule}")


def cmd_test(args):
    import unittest
    suite = unittest.defaultTestLoader.discover("tests", top_level_dir=".")
    sys.exit(0 if unittest.TextTestRunner(verbosity=1).run(suite).wasSuccessful() else 1)


def main():
    parser = argparse.ArgumentParser(description="Student Placement Predictor management")
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("init-db"); p.add_argument("--seed", action="store_true"); p.set_defaults(fn=cmd_init_db)
    p = sub.add_parser("seed"); p.add_argument("--force", action="store_true"); p.set_defaults(fn=cmd_seed)
    p = sub.add_parser("create-user")
    p.add_argument("--role", choices=["admin", "tpo", "student"], default="admin")
    p.add_argument("--email"); p.add_argument("--name"); p.add_argument("--password"); p.set_defaults(fn=cmd_create_user)
    sub.add_parser("train").set_defaults(fn=cmd_train)
    sub.add_parser("export-schema").set_defaults(fn=cmd_export_schema)
    sub.add_parser("routes").set_defaults(fn=cmd_routes)
    sub.add_parser("test").set_defaults(fn=cmd_test)
    args = parser.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()
