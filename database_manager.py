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
    WHERE CAST (question_id AS text) LIKE '{question_id}' ORDER BY submission_time"""

    cursor.execute(query)
    return cursor.fetchall()


@database_common.connection_handler
def add_question(cursor: RealDictCursor, s_t, title, message, image) -> list:
    query = f""" 
    INSERT INTO question (submission_time, view_number, vote_number, title, message, image) VALUES ('{s_t}','0' ,'0', '{title}', '{message}', '{image}');"""

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
    DELETE FROM comment WHERE CAST(question_id AS text) LIKE '{question_id}';
    DELETE FROM answer WHERE CAST(question_id AS text) LIKE '{question_id}';
    DELETE FROM question_tag WHERE CAST(question_id AS text) LIKE '{question_id}' AND CAST(tag_id AS text) LIKE  '{question_id}';
    DELETE FROM question WHERE CAST(id AS text) LIKE '{question_id}';  """

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
    SELECT question_id FROM answer WHERE id = %s"""

    cursor.execute(query, {'answer_id': answer_id})
    return cursor.fetchone()


@database_common.connection_handler
def vote_up_down_question(cursor: RealDictCursor, question_id, action):
    if action == "up":
        query = f"""
        UPDATE question SET vote_number = vote_number + 1 WHERE CAST(id AS text) LIKE '{question_id}' """
    else:
        query = f"""
        UPDATE question SET vote_number = vote_number - 1 WHERE CAST(id AS text) LIKE '{question_id}'"""

    cursor.execute(query)


@database_common.connection_handler
def vote_up_down_answer(cursor: RealDictCursor, answer_id, action):
    if action == "up":
        query = f"""
        UPDATE answer SET vote_number = vote_number + 1 WHERE CAST(id AS text) LIKE '{answer_id}' """
    else:
        query = f"""
        UPDATE answer SET vote_number = vote_number - 1 WHERE CAST(id as text) LIKE '{answer_id}'"""

    cursor.execute(query)


@database_common.connection_handler
def get_all_tags(cursor: RealDictCursor) -> list:
    query = """
        SELECT * FROM tag"""

    cursor.execute(query)
    return cursor.fetchall()


@database_common.connection_handler
def get_all_question_tag(cursor: RealDictCursor) -> list:
    query = """
            SELECT * FROM question_tag"""

    cursor.execute(query)
    return cursor.fetchall()


@database_common.connection_handler
def get_tag_id(cursor: RealDictCursor, name) -> list:
    query = f"""
            SELECT id FROM tag WHERE name LIKE '{name}'"""

    cursor.execute(query)
    return cursor.fetchone()


@database_common.connection_handler
def add_tag(cursor: RealDictCursor, name):
    query = f"""
            INSERT INTO tag (name) SELECT lower('{name}') WHERE NOT EXISTS (SELECT id FROM tag WHERE name LIKE lower('{name}')) 
            RETURNING id"""

    cursor.execute(query)
    return "tag added"


@database_common.connection_handler
def ad_tag_in_question_tag(cursor: RealDictCursor, question_id, tag_id):
    query = f"""
            INSERT INTO question_tag (question_id, tag_id) VALUES ('{question_id}', '{tag_id}')"""

    cursor.execute(query)


@database_common.connection_handler
def delete_tag(cursor: RealDictCursor, question_id, tag_id):
    query = f"""
                DELETE FROM question_tag WHERE CAST(question_id AS text) LIKE '{question_id}' AND 
                CAST(tag_id AS text) LIKE '{tag_id}'"""

    cursor.execute(query)


@database_common.connection_handler
def get_latest_five_questions(cursor: RealDictCursor) -> list:
    query = """
                SELECT * FROM question ORDER BY  submission_time DESC LIMIT 5"""

    cursor.execute(query)
    return cursor.fetchall()


@database_common.connection_handler
def add_comment_to_question(cursor: RealDictCursor, new_comment):

    query = """
            INSERT INTO comment (question_id, message, submission_time) VALUES (%s, %s, %s);
            """
    cursor.execute(query, (new_comment['question_id'],
                           new_comment['new-comment'],
                           new_comment['submission_time']))


@database_common.connection_handler
def get_comments_for_question(cursor: RealDictCursor, question_id):
    query = """
            SELECT * FROM comment WHERE question_id = %(question_id)s 
            AND answer_id is NULL ORDER BY submission_time DESC;"""
    cursor.execute(query, {'question_id': question_id})
    return cursor.fetchall()


@database_common.connection_handler
def add_comment_for_answer(cursor: RealDictCursor, new_comment):
    query = """
            INSERT INTO comment (answer_id, message, submission_time) VALUES (%s, %s, %s);"""
    cursor.execute(query, (new_comment['answer_id'],
                           new_comment['new-comment'],
                           new_comment['submission_time']))


@database_common.connection_handler
def get_answer_by_answer_id(cursor, answer_id):
    cursor.execute("""
    SELECT * FROM answer 
    WHERE id = %(answer_id)s
    ORDER BY submission_time DESC;
    """,
                   {'answer_id': answer_id})
    answers = cursor.fetchone()
    return answers


@database_common.connection_handler
def get_comments_for_answer(cursor: RealDictCursor, answer_id):
    query = """
            SELECT * FROM comment WHERE answer_id = %(answer_id)s
            AND question_id is NULL ORDER BY submission_time DESC;"""
    cursor.execute(query, {'answer_id': answer_id})
    return cursor.fetchall()

