from database.db import get_connection


class Student:

    @staticmethod
    def create_profile(user_id):

        connection = None

        try:

            connection = get_connection()

            with connection.cursor() as cursor:

                cursor.execute(
                    """
                    INSERT INTO students
                    (user_id)
                    VALUES (%s)
                    """,
                    (user_id,)
                )

        finally:

            if connection:
                connection.close()


    @staticmethod
    def get_by_user_id(user_id):

        connection = None

        try:

            connection = get_connection()

            with connection.cursor() as cursor:

                cursor.execute(
                    """
                    SELECT
                        s.*,
                        u.full_name,
                        u.email
                    FROM students s
                    INNER JOIN users u
                        ON s.user_id = u.id
                    WHERE s.user_id = %s
                    """,
                    (user_id,)
                )

                return cursor.fetchone()

        finally:

            if connection:
                connection.close()