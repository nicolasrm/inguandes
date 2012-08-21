# -*- coding: utf-8 -*-
import datetime
import random

def get_instance_quizzes(db, instanceId):
    qzs = db(db.quiz.instance==instanceId).select(db.quiz.ALL, orderby=db.quiz.id)
    
    qzs_info = [get_quiz(db, q.id) for q in qzs]
    
    return qzs_info

def get_quizzes(db, instanceId, userId, section_info=None, user_role=None):
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
    quiz_info['discount_val'] = cQuiz.discount_val
    quiz_info['discount'] = cQuiz.discount_val is not None and cQuiz.discount_val != 0
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
        user = db.auth_user[user_id]        
        uq_info = {}
        uq_info['id'] = u_quiz.id
        uq_info['quiz'] = quiz
        uq_info['user_id'] = user_id
        uq_info['user_name'] = user.last_name + ', ' + user.first_name
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
                if course_questions[cat][q_idx] not in quiz_questions:
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
            qr['question_resume'] = quiz_question_resume(db, quiz_info, uq.question)
            
            q_results.append(qr)
        
        return q_results
        
def quiz_user_result_resume(db, uq_info):
    if uq_info is None:
        return None
    else:
        user = db.auth_user[uq_info['user_id']]
        q_results = {}
        q_results['quiz'] = uq_info['quiz']
        q_results['user_id'] = user.id
        q_results['name'] = user.last_name + ', ' + user.first_name
        q_results['started_on'] = uq_info['started_on']
        q_results['last'] = None
        q_results['questions_ready'] = uq_info['questions_ready']
        q_results['questions_pending'] = uq_info['questions_pending']
        q_results['correct'] = 0
        q_results['incorrect'] = 0
        q_results['omitted'] = 0
        for uq in uq_info['questions_list']:
            is_correct = quiz_is_correct(db, uq)
            if is_correct == True:
                q_results['correct'] = q_results['correct'] + 1
            elif is_correct == False:
                q_results['incorrect'] = q_results['incorrect'] + 1
            elif uq.started_on is not None:
                q_results['omitted'] = q_results['omitted'] + 1
            if uq.started_on is not None and (q_results['last'] is None or q_results['last'] < uq.started_on):
                q_results['last'] = uq.started_on
                
        q_results['score'] = q_results['correct'] - (q_results['incorrect']/float(q_results['quiz']['discount_val']) if q_results['quiz']['discount'] else 0)
        q_results['grade'] = round(1.0 + 6.0*q_results['score']/q_results['quiz']['q_count'] if q_results['score'] > 0 else 1.0, 1)
        
        return q_results
        
def quizzes_user_results(db, user_id, instanceId):
    qzs = db(db.quiz.instance==instanceId).select(db.quiz.ALL, orderby=db.quiz.id)
    results = {}
    for q in qzs:
        uq_info = get_user_quiz(db, q['id'], user_id)
        results[q['id']] = quiz_user_result_resume(db, uq_info)
        
    return results    
    
def quizzes_all_user_results(db, instanceId):
    stds = get_instance_users_by_role(db, instanceId, 0)
    qs_results = {}
    for s in stds:
        qs_results[s['id']] = quizzes_user_results(db, s['id'], instanceId)
        
    return qs_results
        
def quiz_is_correct(db, uqq):
    if uqq.alternative is None:
        return None
    is_correct = db(db.question_alternative.id == uqq.alternative).select().first().is_correct
    return is_correct if is_correct is not None else False
        
def quiz_results(db, quiz_info):
    stds = get_instance_users_by_role(db, quiz_info['instance_id'], 0)
    q_results = []
    for s in stds:
        ur = quiz_user_result_resume(db, get_user_quiz(db, quiz_info['id'], s.id))
        if ur is not None:
            q_results.append(ur)
    
    return q_results
    
def quiz_result_resume(db, quiz_info, q_results):
    q_resume = {}
    q_resume['syudents_ready'] = len(q_results)
    q_resume['students_count'] = get_instance_users_by_role_count(db, quiz_info['instance_id'], 0)
    q_resume['average'] = 0
    q_resume['max'] = -1
    q_resume['min'] = -1
    
    for ur in q_results:
        q_resume['average'] = q_resume['average'] + ur['correct']
        if ur['correct'] > q_resume['max']:
            q_resume['max'] = ur['correct']
        if q_resume['min'] == -1 or ur['correct'] < q_resume['min']:
            q_resume['min'] = ur['correct']
    
    q_resume['average'] = q_resume['average']/q_resume['syudents_ready'] if q_resume['syudents_ready'] > 0 else '-'
    
    return q_resume
    
def quiz_question_resume(db, quiz_info, q_id):
    question_info = {}
    question_info['total'] = db(db.user_quiz_question.question == q_id).count()
    question_info['correct'] = db((db.user_quiz_question.question == q_id) & (db.user_quiz_question.alternative == db.question_alternative.id) & (db.question_alternative.is_correct == True)).count()
    question_info['omitted'] = db((db.user_quiz_question.question == q_id) & (db.user_quiz_question.alternative == None)).count()
    question_info['wrong'] = question_info['total'] - (question_info['correct'] + question_info['omitted'])
        
    return question_info