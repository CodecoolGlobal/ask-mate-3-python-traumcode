from flask import Flask, render_template, redirect, request, url_for, abort
import data_handler
import time
from datetime import datetime
from werkzeug.utils import secure_filename
import os
from uuid import uuid4 as uuid


app = Flask(__name__)

app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.config['UPLOAD_EXTENSIONS'] = ['.jpg', '.png', '.gif']
app.config['UPLOAD_PATH'] = 'static/images'


@app.route("/")
@app.route("/list")
def main_page():
    params_of_get = dict(request.args)
    order_by = params_of_get.get("order_by", 'submission_time')
    order_direction = params_of_get.get('order_direction', 'desc') 
    rev = True if order_direction == 'desc' else False

    questions = data_handler.read_questions()
    questions = sorted(questions, key=lambda q: q[order_by], reverse=rev)

    return render_template("list.html", questions=questions)


@app.route("/question/<int:question_id>")
def display_question(question_id):
    questions = data_handler.read_file(data_handler.QUESTIONS)
    answers = data_handler.read_file(data_handler.ANSWERS)

    show_question = data_handler.read_question(question_id)
    show_answers = []
    
    for line in questions:
        count = int(line['view_number'])
        if int(line['id']) == question_id:
            count += 1
            data_handler.write_count(count, question_id)

    for line in answers:
        if int(line['question_id']) == question_id:
            show_answers.append(line)

    return render_template('question.html', show_question=show_question, show_answers=show_answers, question_id=question_id)


@app.route('/add-question', methods=['GET', 'POST'])
def add_question():
    if request.method == "POST":
        result = dict(request.form)
        uploaded_file = request.files.get("file")
        print(uploaded_file)
        filename = ''
        if uploaded_file:
            unique_name = uuid()
            filename = str(unique_name) + secure_filename(uploaded_file.filename)
            file_ext = os.path.splitext(filename)[1]
            if file_ext not in app.config['UPLOAD_EXTENSIONS']:
                abort(400)
            uploaded_file.save(os.path.join(app.config['UPLOAD_PATH'], filename))
        
        result['view_number'] = 0
        result['vote_number'] = 0
        result['title'] = result['title'].capitalize()
        result['message'] = result['message'].capitalize()
        result['image'] = filename

        print(filename)
        data_handler.write_question(result)
        question_id = data_handler.create_id(data_handler.QUESTIONS)-1
    
        return redirect(url_for("display_question", question_id=question_id))
    return render_template('add-question.html')


@app.route('/question/<int:question_id>/edit', methods=['GET', 'POST'])
def edit_question(question_id):
        if request.method == "POST":
            edited_question = dict(request.form)
            edited_question["id"] = str(question_id)
            print(edited_question)
            data_handler.write_question(edited_question)
            return redirect(url_for("display_question", question_id=question_id))
            
        elif request.method == 'GET':  # OPTIONS, HEAD, PUT, PATCH, DELETE (HTTP methods...)
            item = data_handler.read_question(question_id)
            if not item:
                abort(404)
            return render_template("edit-question.html", question=item)


@app.route('/question/<int:question_id>/new-answer', methods=['GET', 'POST'])
def add_answer(question_id):
    if request.method == "POST":
        result = dict(request.form)
        uploaded_file = request.files.get("file")
        print(uploaded_file)
        filename = ''
        if uploaded_file:
            unique_name = uuid()
            filename = str(unique_name) + secure_filename(uploaded_file.filename)
            file_ext = os.path.splitext(filename)[1]
            if file_ext not in app.config['UPLOAD_EXTENSIONS']:
                abort(400)
            uploaded_file.save(os.path.join(app.config['UPLOAD_PATH'], filename))
        result['image'] = filename
        data_handler.write_answer(result, question_id)
        return redirect(url_for("display_question", question_id=question_id))

    return render_template('add-answer.html', question_id=question_id)


@app.route('/question/<int:question_id>/delete', methods=['POST'])
def delete_question(question_id):
    all_answers = data_handler.read_file(data_handler.ANSWERS)
    all_question = data_handler.read_file(data_handler.QUESTIONS)
    if request.method == "POST":
        for row in all_question:
            if int(row['id']) == question_id:
                try:
                    os.remove("static/images/" + row['image'])
                except:
                    pass


        for row in all_answers:
            if int(row['question_id']) == question_id:
                os.remove("static/images/" + row['image'])
        
        data_handler.delete_question(question_id)
        return redirect("/list")

    return redirect("/list")


@app.route('/answer/<int:answer_id>/delete', methods=['GET', 'POST'])
def delete_answer(answer_id):
    all_answers = data_handler.read_file(data_handler.ANSWERS)
    if request.method == "POST":
        for row in all_answers:
            if int(row['id']) == answer_id:
                question_id = int(row['question_id'])
                try:
                    os.remove("static/images/" + row['image'])
                except:
                    pass
        
        data_handler.delete_answer(answer_id)
        question_url = url_for('display_question', question_id=question_id)
        
        return redirect(question_url)
    

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


if __name__ == "__main__":
    app.run(debug=True)