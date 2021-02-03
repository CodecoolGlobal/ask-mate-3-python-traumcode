from flask import Flask, render_template, redirect, request, url_for, abort, session, flash
import database_manager
from datetime import datetime
from werkzeug.utils import secure_filename
import os
from uuid import uuid4 as uuid
import util_password
import database_users_manager
from functools import wraps

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


def login_required(func):
    @wraps(func)
    def wrap(*args, **kwargs):
        if 'id' in session:
            return func(*args, **kwargs)
        else:
            flash("You need to login first")
            return redirect(url_for('login_page'))
    return wrap


def login_forbidden(func):
    @wraps(func)
    def wrap(*args, **kwargs):
        if 'id' not in session:
            return func(*args, **kwargs)
        else:
            flash(f"You are already logged with {session['username']}")
            return redirect(url_for('main_page'))
    return wrap


@app.route("/users-list")
@login_required
def show_users():
    all_users = database_users_manager.get_all_users_details()
    return render_template('users-list.html', all_users=all_users)


@app.route("/user/<int:user_id>")
@login_required
def show_profile(user_id):
    show_details = database_users_manager.get_user_details_by_user_id(user_id)
    questions = database_users_manager.get_all_user_questions(user_id)
    answers = database_users_manager.get_all_user_answers(user_id)
    comments = database_users_manager.get_all_user_comments(user_id)
    return render_template('show-profile.html', user_id=user_id,
                           show_details=show_details,
                           questions=questions,
                           answers=answers,
                           comments=comments)


@app.route("/registration")
def registration_page():
    return render_template('registration.html')


@app.route("/registration", methods=['POST'])
@login_forbidden
def registration_page_post():
    new_user_obj = dict(request.form)
    filename = upload_image()
    hashed_password = util_password.generate_hash_password(request.form.get('password'))
    new_user_obj['password'] = hashed_password
    new_user_obj['image'] = filename
    database_users_manager.add_user(new_user_obj)
    user_details = database_users_manager.get_user_details(new_user_obj['email'])
    session['id'] = user_details[0]['id']
    session['username'] = user_details[0]['username']
    return redirect(url_for('main_page'))


@app.route("/login")
@login_forbidden
def login_page():
    return render_template('login.html')


@app.route("/login", methods=['POST'])
def login_page_post():
    email = request.form.get('email')
    plain_text_password = request.form.get('password')
    user_details = database_users_manager.get_user_details(email)

    if not user_details:
        flash("Invalid username/password combination")
        return redirect(url_for('login_page'))
    else:
        verified_password = util_password.check_hash_password(user_details[0]['password'], plain_text_password)

    if not verified_password:
        flash("Invalid username/password combination")
        return redirect(url_for('login_page'))
    else:
        session['id'] = user_details[0]['id']
        session['username'] = user_details[0]['username']
        return redirect(url_for('main_page'))


@app.route("/logout")
def logout():
    session.pop('id', None)
    return redirect(url_for('login_page'))


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
    if not show_question:
        abort(404)
    show_answers = database_manager.display_answers(question_id)
    question_tags_by_q_id = database_manager.get_tags_for_question_by_question_id(question_id)

    len_answers = len(show_answers)
    comments_for_question = database_manager.get_comments_for_question(question_id)

    for answer in show_answers:
        answer['comments'] = database_manager.get_comments_for_answer(answer['id'])

    print(show_answers)

    return render_template('question.html', show_question=show_question,
                           show_answers=show_answers,
                           question_id=question_id, len_answers=len_answers,
                           question_tags_by_q_id=question_tags_by_q_id, comments_for_question=comments_for_question)


@app.route('/add-question', methods=['GET', 'POST'])
@login_required
def add_question():
    if request.method == "POST":
        new_question = dict(request.form)
        filename = upload_image()
        submission_time = datetime.now()

        new_question['submission_time'] = submission_time.strftime('%Y-%m-%d %H:%M:%S')
        new_question['image'] = filename
        new_question['message'] = new_question['message'].capitalize()
        new_question['title'] = new_question['title'].capitalize()
        new_question['user_id'] = session['id']

        question_obj = dict(database_manager.add_question(new_question))
        question_id = question_obj['id']

        return redirect(url_for("display_question", question_id=question_id))
    return render_template('add-question.html')


@app.route('/question/<int:question_id>/edit', methods=['GET', 'POST'])
@login_required
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
@login_required
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
@login_required
def add_answer(question_id):
    if request.method == "POST":
        new_answer = dict(request.form)

        filename = upload_image()
        submission_time = datetime.now()

        new_answer['user_id'] = session['id']
        new_answer['submission_time'] = submission_time.strftime('%Y-%m-%d %H:%M:%S')
        new_answer['image'] = filename
        new_answer['message'] = new_answer['message'].capitalize()

        database_manager.add_answer(question_id, new_answer)

        return redirect(url_for('display_question', question_id=question_id))
    return render_template('add-answer.html', question_id=question_id)


@app.route('/answer/<int:answer_id>/delete', methods=['GET', 'POST'])
@login_required
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


@app.route('/answer/<int:answer_id>', methods=['POST'])
@login_required
def valid_invalid_answer(answer_id):
    user_id_by_answer = database_users_manager.get_user_id_by_answer_id(answer_id)
    question_id = database_manager.get_question_id_for_answer(answer_id)['question_id']
    user_id_by_question = database_users_manager.get_user_id_by_question_id(question_id)
    if user_id_by_answer != session['id'] and user_id_by_question == session['id']:
        validation = request.form['validation']
        database_users_manager.valid_invalid_answer(answer_id, validation)
        if validation == 'true':
            database_users_manager.gain_reputation_on_accepted_answer(user_id_by_answer)
        return redirect(url_for('display_question', question_id=question_id))
    else:
        if user_id_by_answer == session['id']:
            flash("You cannot accept your own answer")
        else:
            flash("You cannot accept answer on others questions")
        return redirect(url_for('display_question', question_id=question_id))


@app.route('/question/<int:question_id>/vote_up', methods=['POST'])
@login_required
def vote_up_question(question_id):
    database_manager.vote_up_down_question(question_id, "up")
    database_users_manager.gain_lose_reputation_on_question(database_users_manager.get_user_id_by_question_id(question_id), 'up')
    return redirect(request.referrer)


@app.route('/question/<int:question_id>/vote_down', methods=['POST'])
@login_required
def vote_down_question(question_id):
    database_manager.vote_up_down_question(question_id, "down")
    database_users_manager.gain_lose_reputation_on_question(database_users_manager.get_user_id_by_question_id(question_id), 'down')
    return redirect(request.referrer)


@app.route('/answer/<int:answer_id>/vote_up', methods=['POST'])
@login_required
def vote_up_answer(answer_id):
    question_obj = database_manager.get_question_id_for_answer(answer_id)

    question_id = question_obj['question_id']

    database_manager.vote_up_down_answer(answer_id, "up")
    database_users_manager.gain_lose_reputation_on_answer(database_users_manager.get_user_id_by_answer_id(answer_id), 'up')

    return redirect(url_for('display_question', question_id=question_id))


@app.route('/answer/<int:answer_id>/vote_down', methods=['POST'])
@login_required
def vote_down_answer(answer_id):
    question_obj = database_manager.get_question_id_for_answer(answer_id)

    question_id = question_obj['question_id']

    database_manager.vote_up_down_answer(answer_id, "down")
    database_users_manager.gain_lose_reputation_on_answer(database_users_manager.get_user_id_by_answer_id(answer_id), 'down')

    return redirect(url_for('display_question', question_id=question_id))


@app.route('/question/<int:question_id>/new-tag', methods=['GET', 'POST'])
@login_required
def add_tag_to_questions(question_id):
    all_tags = database_manager.get_all_tags()
    list_of_tags_from_database = [tag['name'] for tag in all_tags]

    if request.method == 'POST':
        chosen_tag = request.form.get('choose-tag')
        list_of_tags_from_question = database_manager.get_tags_by_qs_id(question_id)
        verified_tags = [tag['name'] for tag in list_of_tags_from_question]
        if chosen_tag not in verified_tags:
            if "choose-tag" in request.form:
                if chosen_tag in list_of_tags_from_database:
                    database_manager.ad_tag_in_question_tag(chosen_tag, question_id)
                else:
                    database_manager.add_tag(chosen_tag)
                    database_manager.ad_tag_in_question_tag(chosen_tag, question_id)
        else:
            flash("Tag already exists")
        return redirect(url_for('display_question', question_id=question_id))
    return render_template('add-tag.html', question_id=question_id, list_of_tags=list_of_tags_from_database)


@app.route('/question/<question_id>/tag/<tag_id>/delete', methods=['GET', 'POST'])
@login_required
def delete_tag(question_id, tag_id):
    if request.method == 'POST':
        database_manager.delete_tag(question_id, tag_id)
        return redirect(url_for('display_question', question_id=question_id, tag_id=tag_id))


@app.route('/question/<int:question_id>/new-comment', methods=['GET', 'POST'])
@login_required
def add_comment_to_question(question_id):
    if request.method == 'GET':
        return render_template('add-comment-to-question.html', question_id=question_id)
    elif request.method == 'POST':
        dt = datetime.now()
        new_comment_for_q = dict(request.form)
        new_comment_for_q['user_id'] = session['id']
        new_comment_for_q['question_id'] = question_id
        new_comment_for_q['submission_time'] = dt.strftime('%Y-%m-%d %H:%M:%S')
        new_comment_for_q['new-comment'] = new_comment_for_q['new-comment'].capitalize()
        database_manager.add_comment_to_question(new_comment_for_q)
        return redirect(url_for('display_question', question_id=question_id))


@app.route('/answer/<int:answer_id>/new-comment', methods=['GET', 'POST'])
@login_required
def add_comments_to_answer(answer_id):
    answer_obj = database_manager.get_answer_by_answer_id(answer_id)
    if not answer_obj:
        abort(404)
    question_id = answer_obj['question_id']
    if request.method == 'GET':
        return render_template("add-comment-to-answer.html", answer_id=answer_id, question_id=question_id)
    elif request.method == 'POST':
        dt = datetime.now()
        new_comment_for_a = dict(request.form)
        new_comment_for_a['answer_id'] = answer_id
        new_comment_for_a['submission_time'] = dt.strftime('%Y-%m-%d %H:%M:%S')
        new_comment_for_a['new-comment'] = new_comment_for_a['new-comment'].capitalize()
        database_manager.add_comment_for_answer(new_comment_for_a)

        return redirect(url_for('display_question', question_id=question_id))


@app.route('/comment/<int:comment_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_comment(comment_id):
    comment = database_manager.get_comment(comment_id)
    if request.method == 'GET':
        if not comment:
            abort(404)
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
@login_required
def edit_answer(answer_id):
    answer_details = database_manager.get_answer_by_answer_id(answer_id)
    if request.method == 'GET':
        if not answer_details:
            abort(404)
        return render_template('edit-answer.html', answer_id=answer_id, answer_details=answer_details)
    elif request.method == 'POST':
        edited_answer = dict(request.form)
        filename = upload_image()
        edited_answer['image'] = filename
        edited_answer['message'] = edited_answer['message'].capitalize()
        database_manager.edit_answer(answer_id, edited_answer)
        return redirect(url_for('display_question', question_id=answer_details['question_id']))


@app.route('/comments/<int:comment_id>/delete', methods=['POST'])
@login_required
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


@app.route('/tags')
def list_tags():
    tag_details_obj = database_users_manager.get_all_tags_and_count_of_tags()
    return render_template('list-tags.html', tag_details_obj=tag_details_obj)


@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404


if __name__ == "__main__":
    app.run(debug=True)
