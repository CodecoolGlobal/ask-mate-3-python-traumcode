from flask import Flask, render_template, redirect, request, url_for, abort, flash
import database_manager
from datetime import datetime
from werkzeug.utils import secure_filename
import os
from uuid import uuid4 as uuid

app = Flask(__name__)

app.secret_key = 'alleluia'

app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.config['UPLOAD_EXTENSIONS'] = ['.jpg', '.png', '.gif']
app.config['UPLOAD_PATH'] = 'static/images'


def upload_image():
    uploaded_file = request.files.get('file')
    filename = ''
    if uploaded_file:
        unique_name = uuid()
        filename = str(unique_name) + secure_filename(uploaded_file.filename)
        file_ext = os.path.splitext(filename)[1]
        if file_ext not in app.config['UPLOAD_EXTENSIONS']:
            abort(400)
        uploaded_file.save(os.path.join(app.config['UPLOAD_PATH'], filename))

    return filename


@app.route("/")
def main_page():
    questions = database_manager.get_latest_five_questions()
    return render_template('main-page.html', questions=questions)


@app.route("/list")
def list_page():
    questions = database_manager.get_all_questions()

    order_by = request.args.get('order_by', 'submission_time')
    order_direction = request.args.get('order_direction', 'desc')
    reverse = True if order_direction == 'desc' else False

    questions = sorted(questions, key=lambda row: row[order_by], reverse=reverse)

    return render_template("list.html", questions=questions)


@app.route("/question/<int:question_id>")
def display_question(question_id):
    show_question = database_manager.display_question(question_id)
    show_answers = database_manager.display_answers(question_id)
    question_tags_by_q_id = database_manager.get_tags_for_question_by_question_id(question_id)

    len_answers = len(show_answers)
    comments_for_question = database_manager.get_comments_for_question(question_id)

    for answer in show_answers:
        answer['comments'] = database_manager.get_comments_for_answer(answer['id'])

    return render_template('question.html', show_question=show_question,
                           show_answers=show_answers,
                           question_id=question_id, len_answers=len_answers,
                           question_tags_by_q_id=question_tags_by_q_id, comments_for_question=comments_for_question)


@app.route('/add-question', methods=['GET', 'POST'])
def add_question():
    if request.method == "POST":
        new_question = dict(request.form)
        # todo dict comprehension for capitalize
        filename = upload_image()
        submission_time = datetime.now()

        new_question['submission_time'] = submission_time.strftime('%Y-%m-%d %H:%M:%S')
        new_question['image'] = filename
        new_question['message'] = new_question['message'].capitalize()
        new_question['title'] = new_question['title'].capitalize()

        question_id = database_manager.add_question(new_question)
        question_id = question_id['id']

        return redirect(url_for("display_question", question_id=question_id))
    return render_template('add-question.html')


@app.route('/question/<int:question_id>/edit', methods=['GET', 'POST'])
def edit_question(question_id):
    if request.method == "POST":
        edited_question = dict(request.form)
        # todo dict comprehension for capitalize()
        edited_question['title'] = edited_question['title'].capitalize()
        edited_question['message'] = edited_question['message'].capitalize()

        database_manager.edit_question(question_id, edited_question)
        return redirect(url_for("display_question", question_id=question_id))

    elif request.method == 'GET':
        question_details = database_manager.display_question(question_id)
        if not question_details:
            abort(404)
        return render_template("edit-question.html", question_details=question_details, question_id=question_id)


@app.route('/question/<int:question_id>/delete', methods=['POST'])
def delete_question(question_id):
    questions = database_manager.get_all_questions()
    answers = database_manager.display_answers(question_id)
    if request.method == 'POST':
        for question in questions:
            if question['id'] == question_id:
                q_image_name = question['image']

                if q_image_name:
                    os.remove('static/images/' + q_image_name)
                else:
                    pass

        for answer in answers:
            if answer['question_id'] == question_id:
                a_image_name = answer['image']
                if a_image_name:
                    os.remove('static/images/' + a_image_name)
                else:
                    pass

        database_manager.delete_question(question_id)
        return redirect("/list")


@app.route('/question/<question_id>/new-answer', methods=['GET', 'POST'])
def add_answer(question_id):
    if request.method == "POST":
        new_answer = dict(request.form)

        filename = upload_image()
        submission_time = datetime.now()

        new_answer['submission_time'] = submission_time.strftime('%Y-%m-%d %H:%M:%S')
        new_answer['image'] = filename
        new_answer['message'] = new_answer['message'].capitalize()

        database_manager.add_answer(question_id, new_answer)

        return redirect(url_for('display_question', question_id=question_id))
    return render_template('add-answer.html', question_id=question_id)


@app.route('/answer/<int:answer_id>/delete', methods=['GET', 'POST'])
def delete_answer(answer_id):
    if request.method == 'POST':
        question_id = database_manager.get_question_id_for_answer(answer_id)
        question_id = question_id['question_id']

        answers = database_manager.display_answers(question_id)
        image_name = answers[0]['image']

        if image_name:
            os.remove('static/images/' + image_name)
        else:
            pass

        database_manager.delete_answer(answer_id)

        return redirect(url_for('display_question', question_id=question_id, answer_id=answer_id))


@app.route('/question/<int:question_id>/vote_up', methods=['POST'])
def vote_up_question(question_id):
    database_manager.vote_up_down_question(question_id, "up")
    return redirect(request.referrer)


@app.route('/question/<int:question_id>/vote_down', methods=['POST'])
def vote_down_question(question_id):
    database_manager.vote_up_down_question(question_id, "down")
    return redirect(request.referrer)


@app.route('/answer/<int:answer_id>/vote_up', methods=['POST'])
def vote_up_answer(answer_id):
    question_obj = database_manager.get_question_id_for_answer(answer_id)

    question_id = question_obj['question_id']

    database_manager.vote_up_down_answer(answer_id, "up")

    return redirect(url_for('display_question', question_id=question_id))


@app.route('/answer/<int:answer_id>/vote_down', methods=['POST'])
def vote_down_answer(answer_id):
    question_obj = database_manager.get_question_id_for_answer(answer_id)

    question_id = question_obj['question_id']

    database_manager.vote_up_down_answer(answer_id, "down")

    return redirect(url_for('display_question', question_id=question_id))


@app.route('/question/<int:question_id>/new-tag', methods=['GET', 'POST'])
def add_tag_to_questions(question_id):
    all_tags = database_manager.get_all_tags()
    list_of_tags = [tag['name'] for tag in all_tags]

    if request.method == 'POST':
        chosen_tag = request.form.get('choose-tag')
        inserted_tag = request.form.get('insert-tag')
        inserted_tag = inserted_tag.lower()

        if "insert-tag" in request.form:
            if inserted_tag == "" or inserted_tag.isspace():
                pass
            elif inserted_tag in list_of_tags:
                print("elif")
                database_manager.ad_tag_in_question_tag(inserted_tag, question_id)
            else:
                print('else')
                database_manager.add_tag(inserted_tag)
                database_manager.ad_tag_in_question_tag(inserted_tag, question_id)

        if "choose-tag" in request.form:
            if chosen_tag in list_of_tags:
                database_manager.ad_tag_in_question_tag(chosen_tag, question_id)
            else:
                database_manager.add_tag(chosen_tag)
                database_manager.ad_tag_in_question_tag(chosen_tag, question_id)

        return redirect(url_for('display_question', question_id=question_id))
    return render_template('add-tag.html', question_id=question_id, list_of_tags=list_of_tags)


@app.route('/question/<question_id>/tag/<tag_id>/delete', methods=['GET', 'POST'])
def delete_tag(question_id, tag_id):
    if request.method == 'POST':
        database_manager.delete_tag(question_id, tag_id)
        return redirect(url_for('display_question', question_id=question_id, tag_id=tag_id))


@app.route('/question/<int:question_id>/new-comment', methods=['GET', 'POST'])
def add_comment_to_question(question_id):
    if request.method == 'GET':
        return render_template('add-comment-to-question.html', question_id=question_id)
    elif request.method == 'POST':
        dt = datetime.now()
        new_comment_for_q = dict(request.form)
        new_comment_for_q['question_id'] = question_id
        new_comment_for_q['submission_time'] = dt.strftime('%Y-%m-%d %H:%M:%S')
        new_comment_for_q['new-comment'] = new_comment_for_q['new-comment'].capitalize()
        database_manager.add_comment_to_question(new_comment_for_q)
        return redirect(url_for('display_question', question_id=question_id))


@app.route('/answer/<int:answer_id>/new-comment', methods=['GET', 'POST'])
def add_comments_to_answer(answer_id):
    answer_obj = database_manager.get_answer_by_answer_id(answer_id)
    question_id = answer_obj['question_id']
    if request.method == 'GET':
        return render_template("add-comment-to-answer.html", answer_id=answer_id, question_id=question_id)
    elif request.method == 'POST':
        dt = datetime.now()
        new_comment_for_a = dict(request.form)
        new_comment_for_a['answer_id'] = answer_id
        new_comment_for_a['submission_time'] = dt.strftime('%Y-%m-%d %H:%M:%S')
        # todo check the key in html, db, server
        new_comment_for_a['new-comment'] = new_comment_for_a['new-comment'].capitalize()
        database_manager.add_comment_for_answer(new_comment_for_a)

        return redirect(url_for('display_question', question_id=question_id))


@app.route('/comment/<int:comment_id>/edit', methods=['GET', 'POST'])
def edit_comment(comment_id):
    comment = database_manager.get_comment(comment_id)
    if request.method == 'GET':
        return render_template('edit-comment.html', comment_id=comment_id, comment=comment)
    elif request.method == 'POST':
        question_id = comment[0]['question_id']
        if not question_id:
            question_id = database_manager.get_ques_id_for_comments(comment_id)[0]['question_id']

        dt = datetime.now()
        edited_comment = dict(request.form)
        edited_comment['submission_time'] = dt.strftime('%Y-%m-%d %H:%M:%S')
        edited_comment['edited_count'] = database_manager.edited_count(comment_id)
        database_manager.edit_comment(comment_id, edited_comment)
        return redirect(url_for('display_question', question_id=question_id))


@app.route('/answer/<int:answer_id>/edit', methods=['GET', 'POST'])
def edit_answer(answer_id):
    answer_details = database_manager.get_answer_by_answer_id(answer_id)
    if request.method == 'GET':
        return render_template('edit-answer.html', answer_id=answer_id, answer_details=answer_details)
    elif request.method == 'POST':
        edited_answer = dict(request.form)
        filename = upload_image()
        edited_answer['image'] = filename
        edited_answer['message'] = edited_answer['message'].capitalize()
        database_manager.edit_answer(answer_id, edited_answer)
        return redirect(url_for('display_question', question_id=answer_details['question_id']))


@app.route('/comments/<int:comment_id>/delete', methods=['POST'])
def delete_comment(comment_id):
    if request.method == 'POST':
        database_manager.delete_comment(comment_id)
        return redirect(request.referrer)


@app.route('/search')
def search_question():
    phrase = request.args.get('search')
    phrase = phrase.lower()
    search_results = database_manager.search_questions(phrase)
    question_ids = [data['id'] for data in search_results]
    message = database_manager.search_message_from_answers(phrase)
    answer_ids = [data['question_id'] for data in message]
    answer_question_id = [value for value in question_ids if value in answer_ids]

    return render_template('search-results.html', search_results=search_results,
                           answer_question_id=answer_question_id,
                           message=message, phrase=phrase)


@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404


if __name__ == "__main__":
    app.run(debug=True)
