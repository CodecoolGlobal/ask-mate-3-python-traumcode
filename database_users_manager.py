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
def get_all_users_stories(cursor: RealDictCursor):
    query = """ 
    select  u.id, u.username, u.registration_date,count (distinct q.id) as count_questions, count (distinct a.id) as count_answers, count (distinct c.id) as count_comments
    from users u
    left join question q on u.id = q.user_id
    left join answer a on u.id = a.user_id
    left join comment c on u.id = c.user_id
    group by  u.id
            """
    cursor.execute(query)
    return cursor.fetchall()
