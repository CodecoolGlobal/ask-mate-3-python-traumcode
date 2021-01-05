import os
import csv
import time
import datetime


ANSWERS_HEADER = ['id', 'submission_time', 'vote_number', 'question_id', 'message', 'image']
QUESTIONS_HEADER = ['id', 'submission_time', 'view_number', 'vote_number', 'title', 'message', 'image']
ANSWERS = 'sample_data/answer.csv'
QUESTIONS = 'sample_data/question.csv'


def read_file(filename):
    mylist = []

    with open(filename, 'r', newline='') as csv_file:

        reader = csv.DictReader(csv_file)

        for row in reader:
            mylist.append(row)

        # for line in mylist:
        #     if line['submission_time']:
        #         line['submission_time'] = time.strftime("%d/%m/%Y %H:%M", time.localtime(int(line['submission_time'])))

        return mylist


def create_id(filename):
    id_count = 0
    for row in read_file(filename):
        if row['id']:
            if id_count < int(row['id']):
                id_count = int(row['id'])
    id_count += 1
    return id_count


def write_question(result):
    # timestamp = int(time.time())
    result['id'] = create_id(QUESTIONS)
    result['submission_time'] = timestamp
    result['view_number'] = 0
    result['vote_number'] = 0
    result['image'] = ""
    result['title'] = result['title'].capitalize()
    result['message'] = result['message'].capitalize()

    with open(QUESTIONS, "a", newline='') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=QUESTIONS_HEADER)
        writer.writerow(result)


def write_answer(result, question_id):
    # timestamp = int(time.time())
    result['id'] = create_id(ANSWERS)
    result['submission_time'] = timestamp
    result['vote_number'] = 0
    result['question_id'] = question_id
    result['message'] = result['message'].capitalize()
    result['image'] = ''

    with open(ANSWERS, "a", newline='') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=ANSWERS_HEADER)
        writer.writerow(result)


def write_count(count, question_id):
    dict_list = read_file(QUESTIONS)

    with open(QUESTIONS, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=QUESTIONS_HEADER)
        writer.writeheader()

        for line in dict_list:
            if int(line['id']) == question_id:
                line['view_number'] = str(count)
            # if line['submission_time']:
            #     line['submission_time'] = int(time.mktime(datetime.datetime.strptime(line['submission_time'],
            #                                                                          "%d/%m/%Y %H:%M").timetuple()))

            writer.writerow(line)


def delete_question(question_id):
    myquestion = []
    with open(QUESTIONS, newline='') as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            if int(row['id'])!= question_id:
                myquestion.append(row)

    with open(QUESTIONS, "w", newline='') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=QUESTIONS_HEADER)
        writer.writeheader()

        for item in myquestion:
            writer.writerow(item)

    delete_question_answers(question_id)


def delete_question_answers(question_id):
    myanswers = []
    with open(ANSWERS, newline='') as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            if int(row['question_id']) != question_id:
                myanswers.append(row)

    with open(ANSWERS, "w", newline='') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=ANSWERS_HEADER)
        writer.writeheader()

        for item in myanswers:
            writer.writerow(item)