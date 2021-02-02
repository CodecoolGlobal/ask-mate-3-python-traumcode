import csv
import time
from datetime import datetime


ANSWERS_HEADER = ['id', 'submission_time', 'vote_number', 'question_id', 'message', 'image']
QUESTIONS_HEADER = ['id', 'submission_time', 'view_number', 'vote_number', 'title', 'message', 'image']
ANSWERS = '/home/flori/data/Documents/projects-web/ask-mate-2-python-FloareDeMai/sample_data/answer.csv'
QUESTIONS = '/home/flori/data/Documents/projects-web/ask-mate-2-python-FloareDeMai/sample_data/question.csv'


def read_file(filename):
    mylist = []

    with open(filename, 'r', newline='') as csv_file:

        reader = csv.DictReader(csv_file)

        for row in reader:
            mylist.append(row)
        return mylist


def create_question_id():
    return create_id(QUESTIONS)


def create_answer_id():
    return create_id(ANSWERS)


def create_id(filename):
    id_count = 0
    for row in read_file(filename):
        if row['id']:
            if id_count < int(row['id']):
                id_count = int(row['id'])
    id_count += 1
    return id_count


def question_csv2obj(csv_dict):

    question_obj = {}
    question_obj['id'] = int(csv_dict['id'])
    question_obj['submission_time'] = datetime.fromtimestamp(int(float(csv_dict['submission_time'])))
    # orice str care contine int devine pe bune un int
    return question_obj


def question_obj2csv(obj_dict):
    csv_obj = {}
    # csv_obj['id'] = str(obj_dict['id'])
    csv_obj['submission_time'] = int(obj_dict['submission_time'].timestamp())
    return csv_obj


def _read_questions(question_id=None):
    all_questions = read_file(QUESTIONS)
    questions = []
    if question_id is not None:
        for question in all_questions:
            if int(question['id']) == question_id:
                questions.append(question)
    else:
        questions = all_questions

    for question in questions:
        question['submission_time'] = datetime.utcfromtimestamp(int(float(question['submission_time'])))
        question['vote_number'] = int(question['vote_number'])
        question['view_number'] = int(question['view_number'])
    return questions
    # return [ question_csv2obj(q) for q in all_questions ]


def read_answers(question_id):
    pass


def read_questions():
    return _read_questions()


def read_question(question_id):
    questions = _read_questions(question_id)
    if questions:
        return questions[0]
    else:
        return None


def write_question(result):
    result['submission_time'] = int(datetime.now().timestamp())
    result['submission_time'] = int(result['submission_time'])

    if not result.get('id'):
        result['id'] = create_question_id()
        with open(QUESTIONS, "a", newline='') as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=QUESTIONS_HEADER)
            writer.writerow(result)
    else:
        questions = read_file(QUESTIONS)
        for item in questions:
            if int(item['id']) == int(result['id']):
                item.update(result)
        with open(QUESTIONS, "w", newline='') as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=QUESTIONS_HEADER)
            writer.writeheader()

            for item in questions:
                writer.writerow(item)


def write_answer(result, question_id):
    timestamp = int(time.time())
    result['id'] = create_id(ANSWERS)
    result['submission_time'] = timestamp
    result['vote_number'] = 0
    result['question_id'] = question_id
    result['message'] = result['message'].capitalize()
    

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


def delete_answer(answer_id):
    myanswers = []
    with open(ANSWERS, newline='') as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            if int(row['id']) != answer_id:
                myanswers.append(row)
    print(myanswers)
    
    with open(ANSWERS, "w", newline='') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=ANSWERS_HEADER)
        writer.writeheader()

        for item in myanswers:
            writer.writerow(item)


def edit_question(edited_question, question_id):
    pass

def vote_up_down(question_id, action):
    questions = read_file(QUESTIONS)
    if action == "up":
        for item in questions:
            if int(item['id']) == question_id:
                item['vote_number'] = str(int(item['vote_number']) + 1) 
    elif action == "down":
        for item in questions:
            if int(item['id']) == question_id:
                item['vote_number'] = str(int(item['vote_number']) - 1)
    with open(QUESTIONS, "w", newline='') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=QUESTIONS_HEADER)
        writer.writeheader()

        for item in questions:
            writer.writerow(item)
            

def vote_up_down_answer(answer_id, action):
    answers = read_file(ANSWERS)
    if action == "up":
        for item in answers:
            if int(item['id']) == answer_id:
                item['vote_number'] = str(int(item['vote_number']) + 1)
    elif action == "down":
        for item in answers:
            if int(item['id']) == answer_id:
                item['vote_number'] = str(int(item['vote_number']) - 1)
    with open(ANSWERS, "w", newline='') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=ANSWERS_HEADER)
        writer.writeheader()

        for item in answers:
            writer.writerow(item)



# def get_time_submission():
    
#     list_of_questions = read_file(QUESTIONS)
#     questions_with_transformed_submission_times = [int(submission['submission_time']) for submission in list_of_questions]
#     return submission_time


# def transform_time(list_time):
#     list_of_dates = []

#     for item in list_time:
#         item = datetime.utcfromtimestamp(int(float(item)))
#         list_of_dates.append(item)
#     return list_of_dates