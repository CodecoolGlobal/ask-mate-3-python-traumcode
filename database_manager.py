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
    query = """
    SELECT * FROM question
    ORDER BY %(order_by)s %(order_direction)s"""

    cursor.execute(query, {"order_by": order_by,
                           'order_direction': order_direction})
    return cursor.fetchall()


@database_common.connection_handler
def display_question(cursor: RealDictCursor, question_id) -> list:
    query = """
    SELECT * FROM question
    WHERE id = %(question_id)s;"""

    cursor.execute(query, {'question_id': question_id})
    return cursor.fetchall()


@database_common.connection_handler
def display_answers(cursor: RealDictCursor, question_id) -> list:
    query = """
    SELECT * FROM answer
    WHERE question_id =  %(question_id)s ORDER BY submission_time DESC"""

    cursor.execute(query, {'question_id': question_id})
    return cursor.fetchall()


@database_common.connection_handler
def add_question(cursor: RealDictCursor, new_question) -> list:
    query = """ 
    INSERT INTO question (submission_time, view_number, vote_number, title, message, image) 
    VALUES (%s,0 ,0, %s, %s, %s) returning id;"""

    cursor.execute(query, (new_question['submission_time'],
                           new_question['title'],
                           new_question['message'],
                           new_question['image']))
    question_id = cursor.fetchone()
    return question_id


@database_common.connection_handler
def edit_question(cursor: RealDictCursor, question_id, edited_question):
    query = """
            UPDATE question SET title = %s, message = %s
            WHERE id = %s """

    cursor.execute(query, (edited_question['title'],
                           edited_question['message'],
                           question_id))


@database_common.connection_handler
def delete_question(cursor: RealDictCursor, question_id):
    query = """
    DELETE FROM comment WHERE question_id = %(question_id)s;
    DELETE FROM answer WHERE question_id = %(question_id)s;
    DELETE FROM question_tag WHERE question_id = %(question_id)s AND tag_id = %(question_id)s;
    DELETE FROM question WHERE id = %(question_id)s;  """

    cursor.execute(query, {'question_id': question_id})


@database_common.connection_handler
def add_answer(cursor: RealDictCursor, question_id, new_answer) -> list:
    query = """
    INSERT INTO answer (submission_time, vote_number, question_id, message, image) 
    VALUES (%s, 0, %s, %s, %s) """

    cursor.execute(query, (new_answer['submission_time'],
                   question_id,
                   new_answer['message'],
                   new_answer['image']))


@database_common.connection_handler
def delete_answer(cursor: RealDictCursor, answer_id):
    query = """
    DELETE FROM comment WHERE answer_id = %(answer_id)s;
    DELETE FROM answer WHERE id = %(answer_id)s;"""

    cursor.execute(query, {'answer_id': answer_id})


@database_common.connection_handler
def get_question_id_for_answer(cursor: RealDictCursor, answer_id):
    query = """
    SELECT question_id FROM answer WHERE id = %(answer_id)s"""

    cursor.execute(query, {'answer_id': answer_id})
    return cursor.fetchone()


@database_common.connection_handler
def vote_up_down_question(cursor: RealDictCursor, question_id, action):
    if action == "up":
        query = """
        UPDATE question SET vote_number = vote_number + 1 
        WHERE id = %(question_id)s """
    else:
        query = """
        UPDATE question SET vote_number = vote_number - 1 
        WHERE id = %(question_id)s"""

    cursor.execute(query, {'question_id': question_id})


@database_common.connection_handler
def vote_up_down_answer(cursor: RealDictCursor, answer_id, action):
    if action == "up":
        query = """
        UPDATE answer SET vote_number = vote_number + 1 
        WHERE id =  %(answer_id)s """
    else:
        query = """
        UPDATE answer SET vote_number = vote_number - 1 
        WHERE id = %(answer_id)s"""

    cursor.execute(query, {'answer_id': answer_id})


@database_common.connection_handler
def get_all_tags(cursor: RealDictCursor) -> list:
    query = """
        SELECT * FROM tag"""

    cursor.execute(query)
    return cursor.fetchall()


@database_common.connection_handler
def get_tags_for_question_by_question_id(cursor: RealDictCursor, question_id):
    query = """
    SELECT tag.id, name from tag 
    INNER JOIN question_tag on
    tag.id = question_tag.tag_id 
    INNER JOIN question on
    question.id = question_tag.question_id
    WHERE question.id = %(question_id)s;
    """
    cursor.execute(query, {'question_id': question_id})
    return cursor.fetchall()


@database_common.connection_handler
def add_tag(cursor: RealDictCursor, name):
    query = """
            INSERT INTO tag (name)
            VALUES (%(name)s);"""

    cursor.execute(query, {'name': name})


@database_common.connection_handler
def ad_tag_in_question_tag(cursor: RealDictCursor, tag, question_id):
    query = """
            INSERT INTO question_tag (tag_id, question_id) 
            VALUES ((SELECT id FROM tag WHERE name = %(tag)s), %(question_id)s)
            ON CONFLICT ON CONSTRAINT pk_question_tag_id
            DO NOTHING"""

    cursor.execute(query, {'tag': tag,
                           'question_id': question_id})


@database_common.connection_handler
def delete_tag(cursor: RealDictCursor, question_id, tag_id):
    query = """
                DELETE FROM question_tag WHERE question_id = %(question_id)s AND 
                tag_id = %(tag_id)s;"""

    cursor.execute(query, {'question_id': question_id,
                           'tag_id': tag_id})


@database_common.connection_handler
def get_latest_five_questions(cursor: RealDictCursor) -> list:
    query = """
                SELECT * FROM question ORDER BY submission_time DESC LIMIT 5"""

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
    query = """
    SELECT * FROM answer 
    WHERE id = %(answer_id)s
    ORDER BY submission_time DESC;
    """
    cursor.execute(query, {'answer_id': answer_id})
    return cursor.fetchone()


@database_common.connection_handler
def get_comments_for_answer(cursor: RealDictCursor, answer_id):
    query = """
            SELECT * FROM comment WHERE answer_id = %(answer_id)s
            AND question_id is NULL ORDER BY submission_time DESC;"""
    cursor.execute(query, {'answer_id': answer_id})
    return cursor.fetchall()


@database_common.connection_handler
def edit_answer(cursor: RealDictCursor, answer_id, edited_answer):
    query = """
            UPDATE answer SET (message, image) = (%s , %s)
            WHERE id = %s;
            """
    cursor.execute(query, (edited_answer['message'],
                           edited_answer['image'],
                           answer_id))
