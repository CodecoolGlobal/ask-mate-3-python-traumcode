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
@app.route("/list")
def main_page():
    questions = database_manager.get_all_questions()

    header = request.args
    order_by = request.args.get('order_by')
    order_direction = request.args.get('order_direction')
    reverse = True if order_direction == 'desc' else False

    if order_by in header or order_direction:
        questions = sorted(questions, key=lambda row: row[order_by], reverse=reverse)
    else:
        questions = sorted(questions, key=lambda row: row['submission_time'], reverse=True)

    return render_template("list.html", questions=questions)


@app.route("/question/<question_id>")
def display_question(question_id):
    show_question = database_manager.display_question(question_id)
    show_answers = database_manager.display_answers(question_id)
    all_tags = database_manager.get_all_tags()
    question_tags = database_manager.get_all_question_tag()
    tag_name_list = []
    tag_id = None
    for q in question_tags:
        for tag in all_tags:
            if int(question_id) == q['question_id'] and q['tag_id'] == tag['id']:
                tag_name_list.append(tag['name'])
                tag_id = q['tag_id']
    len_answers = len(show_answers)
    return render_template('question.html', show_question=show_question,
                           show_answers=show_answers,
                           question_id=question_id, len_answers=len_answers, tag_name_list=tag_name_list, tag_id=tag_id)


@app.route('/add-question', methods=['GET', 'POST'])
def add_question():
    if request.method == "POST":
        new_question = request.form
        max_id = database_manager.get_question_id()
        filename = upload_image()

        question_id = max_id['id'] + 1
        submission_time = datetime.now()
        title = new_question['title'].capitalize()
        message = new_question['message'].capitalize()
        image = filename

        database_manager.add_question(submission_time, title, message, image)

        return redirect(url_for("display_question", question_id=question_id))
    return render_template('add-question.html')


@app.route('/question/<int:question_id>/edit', methods=['GET', 'POST'])
def edit_question(question_id):
    if request.method == "POST":
        edited_question = dict(request.form)

        title = edited_question['title'].capitalize()
        message = edited_question['message'].capitalize()

        database_manager.edit_question(question_id, title, message)

        return redirect(url_for("display_question", question_id=question_id))

    elif request.method == 'GET':
        details_question = database_manager.display_question(question_id)
        for i in details_question:
            details = {'message': i['message'],
                       'title': i['title']}
        if not details_question:
            abort(404)
        return render_template("edit-question.html", details=details, question_id=question_id)


@app.route('/question/<question_id>/delete', methods=['POST'])
def delete_question(question_id):
    questions = database_manager.get_all_questions()
    answers = database_manager.display_answers(question_id)
    if request.method == 'POST':
        for value in questions:
            if value['id'] == int(question_id):
                qimage_name = value['image']
                print(value['id'])
                print(qimage_name)
                try:
                    os.remove('static/images/' + qimage_name)
                except:
                    pass

        for value in answers:
            if value['question_id'] == int(question_id):
                aimage_name = value['image']
                try:
                    os.remove('static/images/' + aimage_name)
                except:
                    pass

        database_manager.delete_question(question_id)
        return redirect("/list")


@app.route('/question/<question_id>/new-answer', methods=['GET', 'POST'])
def add_answer(question_id):
    if request.method == "POST":
        filename = upload_image()
        new_answer = request.form
        submission_time = datetime.now()
        message = new_answer['message']
        image = filename

        database_manager.add_answer(submission_time, question_id, message, image)

        return redirect(url_for('display_question', question_id=question_id))
    return render_template('add-answer.html', question_id=question_id)


@app.route('/answer/<answer_id>/delete', methods=['GET', 'POST'])
def delete_answer(answer_id):
    if request.method == 'POST':
        data = database_manager.get_question_id_for_answer(answer_id)
        for value in data.values():
            question_id = value

        answers = database_manager.display_answers(question_id)
        for value in answers:
            image_name = value['image']

        try:
            os.remove('static/images/' + image_name)
        except:
            pass

        database_manager.delete_answer(answer_id)

        return redirect(url_for('display_question', question_id=question_id, answer_id=answer_id))


@app.route('/question/<int:question_id>/vote_up', methods=['POST'])
def vote_up_question(question_id):
    database_manager.vote_up_down_question(question_id, "up")

    return redirect('/list')


@app.route('/question/<int:question_id>/vote_down', methods=['POST'])
def vote_down_question(question_id):
    database_manager.vote_up_down_question(question_id, "down")

    return redirect('/list')


@app.route('/answer/<int:answer_id>/vote_up', methods=['POST'])
def vote_up_answer(answer_id):
    data = database_manager.get_question_id_for_answer(answer_id)

    for value in data.values():
        question_id = value

    database_manager.vote_up_down_answer(answer_id, "up")

    return redirect(url_for('display_question', question_id=question_id))


@app.route('/answer/<int:answer_id>/vote_down', methods=['POST'])
def vote_down_answer(answer_id):
    data = database_manager.get_question_id_for_answer(answer_id)

    for value in data.values():
        question_id = value

    database_manager.vote_up_down_answer(answer_id, "down")

    return redirect(url_for('display_question', question_id=question_id))


@app.route('/question/<question_id>/new-tag', methods=['GET', 'POST'])
def add_tag_to_questions(question_id):
    all_tags = database_manager.get_all_tags()
    list_of_tags = [tag['name'] for tag in all_tags]

    if request.method == 'POST':
        choose_tag = request.form.get('choose-tag')
        inserted_tag = request.form.get('insert-tag').lower()
        if 'choose' in request.form:
            try:
                tag_id = database_manager.get_tag_id(choose_tag)
                database_manager.ad_tag_in_question_tag(question_id, tag_id['id'])
            except:
                flash("Tag already exist!!")
        elif 'insert' in request.form:
            try:
                database_manager.add_tag(inserted_tag)
                tag_id = database_manager.get_tag_id(inserted_tag)
                database_manager.ad_tag_in_question_tag(question_id, tag_id['id'])
            except:
                flash("Tag already exist!!")
        return redirect(url_for('display_question', question_id=question_id))
    else:
        return render_template('add-tag.html', question_id=question_id, list_of_tags=list_of_tags)


@app.route('/question/<question_id>/tag/<tag_id>/delete', methods=['GET', 'POST'])
def delete_tag(question_id, tag_id):
    if request.method == 'POST':
        database_manager.delete_tag(question_id, tag_id)
        return redirect(url_for('display_question', question_id=question_id, tag_id=tag_id))


@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404


if __name__ == "__main__":
    app.run(debug=True)
