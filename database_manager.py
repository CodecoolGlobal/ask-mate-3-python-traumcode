from psycopg2.extras import RealDictCursor

import database_common


@database_common.connection_handler
def get_all_questions(cursor: RealDictCursor) -> list:
    query = """
    SELECT * FROM question"""

    cursor.execute(query)
    return cursor.fetchall()


@database_common.connection_handler
def sort_all_question(cursor: RealDictCursor, order_by, order_direction) -> list:
    query = f"""
    SELECT * FROM question
    ORDER BY {order_by} {order_direction}"""

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
def display_answers(cursor: RealDictCursor, question_id) -> list:
    query = f"""
    SELECT * FROM answer
    WHERE CAST (question_id AS text) LIKE '{question_id}'"""

    cursor.execute(query)
    return cursor.fetchall()


@database_common.connection_handler
def add_question(cursor: RealDictCursor, s_t, title, message, image) -> list:
    query = f"""
    INSERT INTO question (submission_time, view_number, vote_number, title, message, image) VALUES ('{s_t}','0' ,'0', '{title}', '{message}', '{image}') """

    cursor.execute(query)


@database_common.connection_handler
def edit_question(cursor: RealDictCursor, question_id, title, message):
    query = f"""
    UPDATE question SET title = '{title}', message = '{message}'
    WHERE CAST (id AS text) LIKE '{question_id}' """

    cursor.execute(query)


@database_common.connection_handler
def delete_question(cursor: RealDictCursor, question_id):
    query = f"""
    DELETE FROM answer WHERE CAST(question_id AS text) LIKE '{question_id}';
    DELETE FROM question_tag WHERE CAST(question_id AS text) LIKE '{question_id}';
    DELETE FROM question WHERE CAST(id AS text) LIKE '{question_id}';"""

    cursor.execute(query)


@database_common.connection_handler
def add_answer(cursor: RealDictCursor, s_t, question_id, message, image) -> list:
    query = f"""
    INSERT INTO answer (submission_time, vote_number, question_id, message, image) VALUES ('{s_t}','0', '{question_id}', '{message}', '{image}') """

    cursor.execute(query)


@database_common.connection_handler
def delete_answer(cursor: RealDictCursor, answer_id):
    query = f"""
    DELETE FROM comment WHERE CAST(answer_id AS text) LIKE '{answer_id}';
    DELETE FROM answer WHERE CAST (id AS text) LIKE '{answer_id}'"""

    cursor.execute(query)


@database_common.connection_handler
def get_question_id_for_answer(cursor: RealDictCursor, answer_id):
    query = f"""
    SELECT question_id FROM answer WHERE CAST(id AS text) LIKE '{answer_id}'"""

    cursor.execute(query)
    return cursor.fetchone()