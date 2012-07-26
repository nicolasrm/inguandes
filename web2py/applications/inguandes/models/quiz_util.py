# -*- coding: utf-8 -*-
import datetime
import random

def get_quizzes(db, instanceId, userId):
    qzs = db(db.quiz.instance==instanceId).select(db.quiz.ALL)
    
    qzs_dict = {}
    qzs_dict['pending'] = []
    qzs_dict['actived'] = []
    qzs_dict['ready'] = []
    qzs_dict['closed'] = []
    now = datetime.datetime.now()
    for q in qzs:
        u_quiz = get_user_quiz(db, q.id, userId)
        q['type'] = 'quiz'
        q['icon'] = 'icon-th-list'
        if q.starting > now:
            qzs_dict['pending'].append(q)
        elif q.ending >= now:
            if u_quiz is None or u_quiz['questions_pending'] > 0:
                qzs_dict['actived'].append(q)
            else:
                qzs_dict['ready'].append(q)
        else:
            qzs_dict['closed'].append(q)
    
    return qzs_dict
    
def get_quiz(db, quizId):
    cQuiz = db.quiz[quizId]
    q_cats = db(db.quiz_category.quiz == quizId).select()
    q_cats_table = {}
    q_count = 0
    qc_text = ""
    for qc in q_cats:
        q_count = q_count + qc.count
        q_cats_table[qc.category] = qc.count
        qc_text = qc_text + qc.category + ", "
    qc_text = qc_text[0:-2]
    
    quiz_course = db((db.section.instance == cQuiz.instance) & (db.section.course == db.course.id)).select(db.course.ALL).first()
    
    quiz_info = {}
    quiz_info['id'] = cQuiz.id
    quiz_info['name'] = cQuiz.name
    quiz_info['starting'] = cQuiz.starting
    quiz_info['ending'] = cQuiz.ending
    quiz_info['q_count'] = q_count
    quiz_info['categories'] = q_cats_table
    quiz_info['categories_text'] = qc_text
    quiz_info['instance'] = cQuiz.instance.title
    quiz_info['instance_id'] = cQuiz.instance
    quiz_info['course'] = quiz_course.name
    quiz_info['course_id'] = quiz_course.id
    
    return quiz_info
    
def get_user_quiz(db, quizId, user_id):
    u_quiz = db((db.user_quiz.the_user == user_id) & (db.user_quiz.quiz == quizId)).select().first()
    if u_quiz is None:
        return None
    else:
        quiz = get_quiz(db, quizId)
        available_qs = available_questions(db, u_quiz.id)
        uq_info = {}
        uq_info['id'] = u_quiz.id
        uq_info['started_on'] = u_quiz.started_on
        uq_info['questions_ready'] = quiz['q_count'] - len(available_qs)
        uq_info['questions_pending'] = len(available_qs)
        uq_info['questions_list'] = db(db.user_quiz_question.user_quiz == u_quiz.id).select()
        
        return uq_info
    
def get_or_create_user_quiz(db, quizId, user_id):
    quiz = db((db.user_quiz.the_user == user_id) & (db.user_quiz.quiz == quizId)).select().first()
    if quiz is None:
        quiz = create_quiz(db, quizId, user_id)
    else:
        quiz = quiz.id
    
    return quiz
    
def create_quiz(db, quizId, user_id):
    quiz_info = get_quiz(db, quizId)
    course_questions, course_cat = get_questions(db, quiz_info['course_id'])
    quiz_questions = []
    for (cat, total) in quiz_info['categories'].iteritems():
        count = 0
        if total <= len(course_questions[cat]):
            while count < total:
                q_idx = random.randint(0, len(course_questions[cat])-1)
                if course_questions[cat][q_idx].id not in quiz_questions:
                    quiz_questions.append(course_questions[cat][q_idx])
                    count = count + 1
        else:
            raise ValueError('Las preguntas de la categoria "{0}" ({1}) son menos de las requeridas ({2}).'.format(cat, len(course_questions[cat]), total))
    user_quiz_id = db.user_quiz.insert( the_user=user_id,
                                        quiz=quizId)
    for q in quiz_questions:
        db.user_quiz_question.insert(   user_quiz=user_quiz_id,
                                        question=q.id)
    return user_quiz_id
    
def available_questions(db, user_quiz_id):
    return db((db.user_quiz_question.user_quiz == user_quiz_id) & (db.user_quiz_question.started_on == None) & (db.user_quiz_question.answer_on == None)).select()    
    
def next_question(db, user_quiz_id):
    available_qs = available_questions(db, user_quiz_id)
    next_q = available_qs.first()
    if next_q is None:
        return None, -1
    else:        
        next_q.update_record(started_on=datetime.datetime.now())
        q = get_question(db, next_q.question)
        q['uq_id'] = next_q.id
        return q, len(available_qs)
        
def quiz_user_result(db, quiz_info, uq_info):
    if uq_info is None:
        return None
    else:
        q_results = []
        for uq in uq_info['questions_list']:
            qr = {}
            qr['question'] = uq.question.text
            qr['alternative'] = db(db.question_alternative.id == uq.alternative).select().first() if uq.alternative is not None else None
            qr['correct'] = db((db.question_alternative.question == uq.question) & (db.question_alternative.is_correct == True)).select().first()
            qr['is_correct'] = qr['alternative'].id == qr['correct'].id if qr['alternative'] is not None else None
            
            q_results.append(qr)
        
        return q_results