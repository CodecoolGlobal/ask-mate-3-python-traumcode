from psycopg2.extras import RealDictCursor

import database_common


@database_common.connection_handler
def get_all_questions(cursor: RealDictCursor) -> list:
    query = """
    SELECT * FROM question"""

    cursor.execute(query)
    return cursor.fetchall()


@database_common.connection_handler
def get_question_id(cursor: RealDictCursor):
    query = """
    SELECT id FROM question WHERE id = (SELECT max(id) FROM question)"""

    cursor.execute(query)
    return cursor.fetchone()


@database_common.connection_handler
def display_question(cursor: RealDictCursor, question_id: str) -> list:
    query = f"""
    SELECT * FROM question
    WHERE CAST (id AS text) LIKE '{question_id}'"""

    cursor.execute(query)
    return cursor.fetchall()


@database_common.connection_handler
def display_answers(cursor: RealDictCursor, question_id: str) -> list:
    query = f"""
    SELECT * FROM answer
    WHERE CAST (question_id AS text) LIKE '{question_id}'"""

    cursor.execute(query)
    return cursor.fetchall()


@database_common.connection_handler
def add_question(cursor: RealDictCursor, s_t, title, message, image):
    query = f"""
    INSERT INTO question (submission_time, view_number, vote_number, title, message, image) VALUES ('{s_t}','0' ,'0', '{title}', '{message}', '{image}') """

    cursor.execute(query)
