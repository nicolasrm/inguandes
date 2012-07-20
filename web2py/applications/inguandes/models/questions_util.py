# -*- coding: utf-8 -*-

def get_questions(db, courseId):
    qs = db(db.question.course==courseId).select(db.question.ALL)
    
    categories = []
    questions = {}
    for q in qs:
        if q.category not in categories:
            categories.append(q.category)
            questions[q.category] = []
        questions[q.category].append(q)
    
    return questions, categories
    
def get_categories(db, courseId):
    categories = db(db.question.course==courseId).select(db.question.category, orderby=db.question.category, distinct=True)
    cat_list = [cat.category for cat in categories]
    
    return cat_list
    
def get_question(db, qId):
    q = db.question[qId]
    alts = db(db.question_alternative.question == qId).select()
    
    alts_dict = {}
    for alt in alts:
        alts_dict[alt.id] = alt.text
    
    q_obj = {}
    q_obj['id'] = q.id
    q_obj['text'] = q.text
    q_obj['category'] = q.id
    q_obj['alternatives'] = alts_dict
    
    return q_obj
    