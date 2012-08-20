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
    answer_on = datetime.datetime.now()
    diff = answer_on - user_qq.started_on
    
    response.headers['Content-Type'] = 'application/json'
    if diff.seconds <= user_qq.question.time + 5:    
        user_qq.update_record(  alternative=alt_id,
                                answer_on=answer_on)                                
        
        return response.json({'message': 'Respuesta guardada'})
    else:
        return response.json({'message': 'Respuesta no guardada, tiempo excedido.'})

@auth.requires_login()
def result():
    if len(request.args) == 0:
        redirect(URL('default', 'index'))
    quizId = int(request.args[0])
    quiz_info = get_quiz(db, quizId)
    
    user_role = get_user_role(db, quiz_info['instance_id'], auth.user.id)
    if len(request.args) == 1 and user_roles[user_role] == 'Profesor' or user_roles[user_role] == 'Ayudante Jefe':
        redirect(URL('quiz', 'all_result', args=[quizId]))
    
    if quiz_info['ending'] >= datetime.datetime.now() and user_roles[user_role] == 'Estudiante':
        redirect(URL('instance', 'view', args=[quiz_info['instance_id']]))
        
    user_id = auth.user.id
    if len(request.args) == 2 and user_roles[user_role] == 'Profesor' or user_roles[user_role] == 'Ayudante Jefe':
        user_id = int(request.args[1])
        
    user_quiz = get_user_quiz(db, quizId, user_id)
    user_result = quiz_user_result(db, quiz_info, user_quiz)
        
    q_resume = quiz_result_resume(db, quiz_info, quiz_results(db, quiz_info))
    u_resume = quiz_user_result_resume(db, user_quiz)
    
    return dict(quiz_info=quiz_info, user_quiz=user_quiz, user_result=user_result, q_resume=q_resume, u_resume=u_resume)
    
@auth.requires_login()
def user_results():
    if len(request.args) == 0:
        redirect(URL('default', 'index'))
        
    instanceId = int(request.args[0])
    inst_info = get_instance_info(db, instanceId)
    if inst_info is None:
        redirect(URL('default', 'index'))
        
    user_role = get_user_role(db, instanceId, auth.user.id)
        
    if len(request.args) == 1 and user_roles[user_role] == 'Profesor' or user_roles[user_role] == 'Ayudante Jefe':
        redirect(URL('quiz', 'all_user_results', args=[instanceId]))
    
    user_id = auth.user.id
    if len(request.args) == 2 and user_roles[user_role] == 'Profesor' or user_roles[user_role] == 'Ayudante Jefe':
        user_id = int(request.args[1])
        
    user = db.auth_user[user_id]        
    qzs = get_instance_quizzes(db, instanceId)
    user_results = quizzes_user_results(db, user_id, instanceId)    
        
    return dict(inst_info=inst_info, qzs=qzs, user_results=user_results, user=user)
    
@auth.requires_login()
def all_result():
    if len(request.args) == 0:
        redirect(URL('default', 'index'))
        
    quizId = int(request.args[0])
    quiz_info = get_quiz(db, quizId)
    
    user_role = get_user_role(db, quiz_info['instance_id'], auth.user.id)
    if user_roles[user_role] != 'Profesor' and user_roles[user_role] != 'Ayudante Jefe':
        redirect(URL('instance', 'view', args=[quiz_info['instance_id']]))
    
    q_results = quiz_results(db, quiz_info)
    q_resume = quiz_result_resume(db, quiz_info, q_results)
    
    return dict(quiz_info=quiz_info, q_results=q_results, q_resume=q_resume)

@auth.requires_login()    
def all_user_results():
    if len(request.args) == 0:
        redirect(URL('default', 'index'))
        
    instanceId = int(request.args[0])
    inst_info = get_instance_info(db, instanceId)
    if inst_info is None:
        redirect(URL('default', 'index'))
        
    user_role = get_user_role(db, instanceId, auth.user.id)
    if user_roles[user_role] != 'Profesor' and user_roles[user_role] != 'Ayudante Jefe':
        redirect(URL('instance', 'view', args=[instanceId]))
        
    stds = get_instance_users_by_role(db, instanceId, 0)
    qzs = get_instance_quizzes(db, instanceId)
    qs_results = quizzes_all_user_results(db, instanceId)
        
    return dict(inst_info=inst_info, stds=stds, qzs=qzs, qs_results=qs_results)