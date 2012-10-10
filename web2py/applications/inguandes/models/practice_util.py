# -*- coding: utf-8 -*-

def get_user_practices(db, userId):
    ps = db(db.practice.the_user==userId).select(db.practice.ALL)
    
    ps_info = [get_practice(db, p.id) for p in ps]    
    return ps_info 
    
def get_practice(db, pId):
    p = db(db.practice.id==pId).select(db.practice.ALL).first()
        
    p_info = {}
    p_info['id'] = p.id
    p_info['user'] = p.the_user
    p_info['category'] = p.category
    p_info['category_name'] = practice_category[p.category]
    p_info['state'] = 'pending'
    
    return p_info 