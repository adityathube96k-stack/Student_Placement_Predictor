from database.db import get_connection
from utils.security import hash_password


class User:

    @staticmethod
    def find_by_email(email):

        connection = None

        try:

            connection = get_connection()

            with connection.cursor() as cursor:

                cursor.execute(
                    """
                    SELECT *
                    FROM users
                    WHERE email = %s
                    """,
                    (email,)
                )

                return cursor.fetchone()

        finally:

            if connection:
                connection.close()


    @staticmethod
    def find_by_id(user_id):

        connection = None

        try:

            connection = get_connection()

            with connection.cursor() as cursor:

                cursor.execute(
                    """
                    SELECT *
                    FROM users
                    WHERE id = %s
                    """,
                    (user_id,)
                )

                return cursor.fetchone()

        finally:

            if connection:
                connection.close()


    @staticmethod
    def create(full_name, email, password):

        connection = None

        try:

            connection = get_connection()

            password_hash = hash_password(password)

            with connection.cursor() as cursor:

                cursor.execute(
                    """
                    INSERT INTO users
                    (
                        full_name,
                        email,
                        password_hash,
                        role
                    )
                    VALUES
                    (
                        %s,
                        %s,
                        %s,
                        'student'
                    )
                    """,
                    (
                        full_name,
                        email,
                        password_hash
                    )
                )

                return cursor.lastrowid

        finally:

            if connection:
                connection.close()