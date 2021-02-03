from psycopg2.extras import RealDictCursor
import database_common


@database_common.connection_handler
def add_user(cursor: RealDictCursor, user_obj):
    query = """
    INSERT INTO users (username, email, password, image, registration_date, reputation) 
    VALUES (%s, %s, %s, %s, now(),0) RETURNING id;"""

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
def get_user_details_by_user_id(cursor: RealDictCursor, user_id):
    query = f"""
    SELECT u.id, u.username, u.registration_date, u.reputation, u.image,
    count(distinct q.id) as asked_question,
    count(distinct a.id) as answers,
    count(distinct c.id) as comments
    FROM users u
    LEFT JOIN question q on u.id = q.user_id
    LEFT JOIN answer a on u.id = a.user_id
    LEFT JOIN comment c on u.id = c.user_id
    WHERE u.id = {user_id}
    GROUP BY u.id"""

    cursor.execute(query)
    return cursor.fetchall()


@database_common.connection_handler
def get_all_users_details(cursor: RealDictCursor) -> list:
    query = """
    SELECT u.id, u.username, u.email, u.image, u.registration_date, u.reputation,
    count (distinct q.id) as question_asked, count(distinct a.id) as answers, count(distinct c.id) as comments
    FROM users u
    LEFT JOIN question q on u.id = q.user_id
    LEFT JOIN answer a on u.id = a.user_id
    LEFT JOIN comment c on u.id = c.user_id
    GROUP BY u.id"""

    cursor.execute(query)
    return cursor.fetchall()


@database_common.connection_handler
def get_all_user_questions(cursor: RealDictCursor, user_id) -> list:
    query = f"""
    SELECT title, message, submission_time, view_number, vote_number FROM question
    WHERE user_id = {user_id}"""

    cursor.execute(query)
    return cursor.fetchall()


@database_common.connection_handler
def get_all_user_answers(cursor: RealDictCursor, user_id) -> list:
    query = f"""
    SELECT message, submission_time, vote_number FROM answer
    WHERE user_id = {user_id}"""

    cursor.execute(query)
    return cursor.fetchall()


@database_common.connection_handler
def get_all_user_comments(cursor: RealDictCursor, user_id) -> list:
    query = f"""
    SELECT message, submission_time FROM comment
    WHERE user_id = {user_id}"""

    cursor.execute(query)
    return cursor.fetchall()


@database_common.connection_handler
def get_user_id_by_question_id(cursor: RealDictCursor, question_id):
    query = f"""
    SELECT user_id FROM question
    WHERE id = {question_id}"""

    cursor.execute(query)
    id = cursor.fetchone()
    return id['user_id']


@database_common.connection_handler
def get_user_id_by_answer_id(cursor: RealDictCursor, answer_id):
    query = f"""
    SELECT user_id FROM answer
    WHERE id = {answer_id}"""

    cursor.execute(query)
    id = cursor.fetchone()
    return id['user_id']


@database_common.connection_handler
def gain_lose_reputation_on_question(cursor: RealDictCursor, user_id, action):
    if action == "up":
        query = f"""
        UPDATE users SET reputation = reputation + 5
        WHERE id = '{user_id}'"""
    else:
        query = f"""
        UPDATE users SET reputation = reputation - 2
        WHERE id = '{user_id}'"""

    cursor.execute(query)


@database_common.connection_handler
def gain_lose_reputation_on_answer(cursor: RealDictCursor, user_id, action):
    if action == 'up':
        query = f"""
        UPDATE users SET reputation = reputation + 10
        WHERE id = '{user_id}'"""
    else:
        query = f"""
        UPDATE users SET reputation = reputation - 2
        WHERE id = '{user_id}'"""

    cursor.execute(query)


@database_common.connection_handler
def gain_reputation_on_accepted_answer(cursor: RealDictCursor, user_id):
    query = f"""
    UPDATE users SET reputation = reputation + 15
    WHERE id = '{user_id}'"""

    cursor.execute(query)


@database_common.connection_handler
def valid_invalid_answer(cursor: RealDictCursor, answer_id, validation):
    query = f"""
    UPDATE answer SET accepted = {validation}
    WHERE id = {answer_id}"""

    cursor.execute(query)


@database_common.connection_handler
def get_all_tags_and_count_of_tags(cursor: RealDictCursor):
    query = """
    SELECT name, count(question_tag.question_id) as number_ques from tag
    INNER JOIN question_tag on
    tag.id = question_tag.tag_id
    group by name;"""

    cursor.execute(query)
    return cursor.fetchall()


