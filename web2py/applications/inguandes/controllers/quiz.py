# -*- coding: utf-8 -*-
import datetime

@auth.requires_login()
def call():
    return service()

@auth.requires_login()
def start():
    if len(request.args) == 0:
        redirect(URL('default', 'index'))
    quizId = int(request.args[0])
    quiz_info = get_quiz(db, quizId)
        
    user_quiz = get_user_quiz(db, quizId, auth.user.id)
            
    return dict(quiz_info=quiz_info, user_quiz=user_quiz)

@auth.requires_login()
def answer():
    if len(request.args) == 0:
        redirect(URL('default', 'index'))
        
    quizId = int(request.args[0])
    quiz_info = get_quiz(db, quizId)
        
    user_quiz_id = get_or_create_user_quiz(db, quizId, auth.user.id)
    c_question, qs_availables = next_question(db, user_quiz_id)
    
    return dict(quiz_info=quiz_info, c_question=c_question, total_q=quiz_info['q_count'], q_idx=(quiz_info['q_count']-qs_availables+1))

@service.json
def receive_answer(uq_id, alt_id):
    user_qq = db.user_quiz_question[uq_id]
    user_qq.update_record(  alternative=alt_id,
                            answer_on=datetime.datetime.now)
                            
    response.headers['Content-Type'] = 'application/json'
    return response.json({'message': 'Respuesta guardada'})

@auth.requires_login()
def result():
    if len(request.args) == 0:
        redirect(URL('default', 'index'))
    quizId = int(request.args[0])
    quiz_info = get_quiz(db, quizId)
        
    user_quiz = get_user_quiz(db, quizId, auth.user.id)
    user_resullt = quiz_user_result(db, quiz_info, user_quiz)
    
    return dict(quiz_info=quiz_info, user_quiz=user_quiz, user_resullt=user_resullt)