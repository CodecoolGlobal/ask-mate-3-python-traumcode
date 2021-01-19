from flask import Flask, render_template, redirect, request, url_for, abort
import data_handler
import database_manager
from datetime import datetime
from werkzeug.utils import secure_filename
import os


app = Flask(__name__)

app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.config['UPLOAD_EXTENSIONS'] = ['.jpg', '.png', '.gif']
app.config['UPLOAD_PATH'] = 'static/images'


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


@app.route("/question/<int:question_id>")
def display_question(question_id):

    show_question = database_manager.display_question(question_id)
    show_answers = database_manager.display_answers(question_id)

    return render_template('question.html', show_question=show_question, show_answers=show_answers, question_id=question_id)


@app.route('/add-question', methods=['GET', 'POST'])
def add_question():
    if request.method == "POST":
        new_question = request.form
        max_id = database_manager.get_question_id()

        question_id = max_id['id'] + 1
        submission_time = datetime.now()
        title = new_question['title']
        message = new_question['message']
        image = ""

        database_manager.add_question(submission_time, title, message, image)

        return redirect(url_for("display_question", question_id=question_id))
    return render_template('add-question.html')


@app.route('/question/<int:question_id>/edit', methods=['GET', 'POST'])
def edit_question(question_id):
    if request.method == "POST":
        edited_question = dict(request.form)

        title = edited_question['title']
        message = edited_question['message']

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
    if request.method == 'POST':
        database_manager.delete_question(question_id)
        return redirect("/list")


@app.route('/question/<question_id>/new-answer', methods=['GET', 'POST'])
def add_answer(question_id):
    if request.method == "POST":
        new_answer = request.form
        submission_time = datetime.now()
        message = new_answer['message']
        image = ''
        database_manager.add_answer(submission_time, question_id, message, image)

        return redirect(url_for('display_question', question_id=question_id))
    return render_template('add-answer.html', question_id=question_id)


@app.route('/answer/<answer_id>/delete', methods=['GET', 'POST'])
def delete_answer(answer_id):
    if request.method == 'POST':
        question_id = database_manager.get_question_id_for_answer(answer_id)
        database_manager.delete_answer(answer_id)
        # return render_template('display_question', question_id=question_id, answer_id=answer_id)
        # return redirect(url_for('display_question', question_id=question_id, answer_id=answer_id))


@app.route('/question/<int:question_id>/vote_up')
def vote_up_question(question_id):
    data_handler.vote_up_down(question_id, "up")

    return redirect('/list')


@app.route('/question/<int:question_id>/vote_down')
def vote_down_question(question_id):
    data_handler.vote_up_down(question_id, "down")

    return redirect('/list')


@app.route('/answer/<int:answer_id>/vote_up')
def vote_up_answer(answer_id):
    all_answers = data_handler.read_file(data_handler.ANSWERS)
    for row in all_answers:
        if int(row['id']) == answer_id:
            question_id = int(row['question_id'])

    data_handler.vote_up_down_answer(answer_id, "up")

    return redirect(url_for('display_question', question_id=question_id))


@app.route('/answer/<int:answer_id>/vote_down')
def vote_down_answer(answer_id):
    all_answers = data_handler.read_file(data_handler.ANSWERS)
    for row in all_answers:
        if int(row['id']) == answer_id:
            question_id = int(row['question_id'])

    data_handler.vote_up_down_answer(answer_id, "down")

    return redirect(url_for('display_question', question_id=question_id))


@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404


if __name__ == "__main__":
    app.run(debug=True)
