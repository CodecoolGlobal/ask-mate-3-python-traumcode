from psycopg2.extras import RealDictCursor
import database_common


@database_common.connection_handler
def add_user(cursor: RealDictCursor, user_obj):
    query = """
    INSERT INTO users (username, email, password, image, registration_date) 
    VALUES (%s, %s, %s, %s, now()) RETURNING id;"""

    cursor.execute(query, (user_obj['username'],
                           user_obj['email'],
                           user_obj['password'],
                           user_obj['image']))
    user_id = cursor.fetchone()
    return user_id


@database_common.connection_handler
def get_user_details(cursor: RealDictCursor, email):
    query = """
    SELECT * FROM users
    WHERE email = %(email)s"""

    cursor.execute(query, {'email': email})
    return cursor.fetchall()


@database_common.connection_handler
def get_all_users_details(cursor: RealDictCursor) -> list:
    query = """
    SELECT * FROM users"""

    cursor.execute(query)
    return cursor.fetchall()


@database_common.connection_handler
def count_question_for_all_users(cursor: RealDictCursor) -> list:
    query = """
    SELECT users.username, users.email, users.image, users.registration_date,
       count(q.user_id) as asked_question
    FROM users
    LEFT JOIN question q on users.id = q.user_id
    GROUP BY users.username, users.email, users.image, users.registration_date """

    cursor.execute(query)
    return cursor.fetchall()