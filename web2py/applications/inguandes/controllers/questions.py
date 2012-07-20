# -*- coding: utf-8 -*-

def view():
    if len(request.args) == 0:
        redirect(URL('default', 'index'))
    courseId = int(request.args[0])
    course = db.course[courseId]
    
    questions, cats = get_questions(db, courseId)
    
    category = request.vars.category
    questions = questions[category] if category is not None else [x for a in [v for (k,v) in questions.iteritems()] for x in a]
    
    selected_q = None
    alternatives = None
    if len(request.args) > 1:
        selected_q = int(request.args[1])
        alternatives = db(db.question_alternative.question == selected_q).select(db.question_alternative.ALL)
    
    return dict(co=course, cats=cats, questions=questions, category=category, selected_q=selected_q, alternatives=alternatives)
    
def add_question():
    courseId = int(request.vars.courseid)
    q_id = None
    href_vars = {'category':request.vars.category} if request.vars.category is not None else {}
    if request.vars.text is not None and len(request.vars.text.strip()) > 0:
        q_id = db.question.insert(  text=request.vars.text,
                                    category=request.vars.category,
                                    course=courseId)
    if q_id is None:
        redirect(URL('view', args=[courseId], vars=href_vars))
    else:
        redirect(URL('view', args=[courseId, q_id], vars=href_vars))
    
def add_alternative():
    courseId = int(request.vars.courseid)
    questionId = int(request.vars.questionid)
    href_vars = {'category':request.vars.category} if request.vars.category is not None else {}
    if request.vars.text is not None and len(request.vars.text.strip()) > 0:        
        db.question_alternative.insert( text=request.vars.text,
                                        is_correct=request.vars.iscorrect,
                                        question=questionId)
    
    redirect(URL('view', args=[courseId, questionId], vars=href_vars))
    