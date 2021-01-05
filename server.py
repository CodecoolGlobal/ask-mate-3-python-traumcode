from flask import Flask, render_template, redirect, request, url_for
import data_handler
import time
import datetime

app = Flask(__name__)


@app.route("/")
@app.route("/list")
def main_page():
    questions = data_handler.read_file(data_handler.QUESTIONS)
    values = dict(request.args)
    order_by = values.get("order_by")
    # for question in questions:
    #         question['submission_time'] = time.strftime("%d/%m/%Y %H:%M", time.localtime(int(question['submission_time'])))
    if "order_by" in values.keys():
        order_by = values["order_by"]
        if values["order_by"] in data_handler.QUESTIONS_HEADER:
            if order_by in values.values() and "asc" in values.values():
                questions = sorted(questions, key=lambda row: row.get(order_by))
            else:
                questions = sorted(questions, key=lambda row: row.get(order_by), reverse=True)
            return render_template("list.html", questions=questions)
        else:
            return render_template("list.html", questions=questions)
    else:
        questions = sorted(questions, key=lambda row: row.get("submission_time"), reverse=True)

        return render_template("list.html", questions=questions)


@app.route("/question/<int:question_id>")
def display_question(question_id):
    questions = data_handler.read_file(data_handler.QUESTIONS)
    answers = data_handler.read_file(data_handler.ANSWERS)

    show_questions = []
    show_answers = []

    for line in questions:
        count = int(line['view_number'])
        if int(line['id']) == question_id:
            show_questions.append(line['title'])
            show_questions.append(line['message'])
            count += 1
            data_handler.write_count(count, question_id)

    for line in answers:
        if int(line['question_id']) == question_id:
            show_answers.append(line['message'])

    return render_template('question.html', questions=questions, question_id=question_id, show_questions=show_questions, show_answers=show_answers)


@app.route('/add-question', methods=['GET', 'POST'])
def add_question():
    if request.method == "POST":
        result = dict(request.form)
        data_handler.write_question(result)
        question_id = data_handler.create_id(data_handler.QUESTIONS)-1
        return redirect(url_for("display_question", question_id=question_id))
    return render_template('add-question.html')


@app.route('/question/<int:question_id>/new-answer', methods=['GET', 'POST'])
def add_answer(question_id):
    if request.method == "POST":
        result = dict(request.form)
        data_handler.write_answer(result, question_id)
        return redirect(url_for("display_question", question_id=question_id))
    return render_template('add-answer.html', question_id=question_id)


@app.route('/question/<int:question_id>/delete', methods=['POST'])
def delete_question(question_id):
    if request.method == "POST":
        data_handler.delete_question(question_id)
        return redirect("/list")
    return redirect("/list")


if __name__ == "__main__":
    app.run(debug=True)
