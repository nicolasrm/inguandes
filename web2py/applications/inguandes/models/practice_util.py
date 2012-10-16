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
    p_info['company'] = get_company(db, p.company)
    p_info['validator'] = get_employee(db, p.validator)    
    p_info['description'] = p.description
    p_info['starting'] = p.starting
    p_info['ending'] = p.ending
    p_info['state'] = 'pending'
    if (p_info['company'] is not None and p_info['company']['is_complete'] and p_info['validator'] is not None and p_info['validator']['is_complete'] and p_info['description'] is not None 
            and len(p_info['description']) > 0 and p_info['starting'] is not None and p_info['ending'] is not None):
        p_info['state'] = 'ready_to_validate'
    
    return p_info 

def get_company(db, comId):
    com = db(db.company.id == comId).select(db.company.ALL).first()
    
    if com is not None:
        com_info = {}
        com_info['id'] = com.id
        com_info['rut'] = com.rut
        com_info['name'] = com.name
        com_info['businessLine'] = com.businessLine
        com_info['address'] = com.address
        com_info['city'] = com.city
        com_info['country'] = com.country
        com_info['is_complete'] = False if com_info['rut'] is None or com_info['name'] is None or com_info['businessLine'] is None or com_info['address'] is None or com_info['city'] is None or com_info['country'] is None else True
        
        return com_info
    else:
        return None
        
def get_employee(db, empId):
    emp = db(db.company_employee.id == empId).select(db.company_employee.ALL).first()
    
    if emp is not None:
        emp_info = {}
        emp_info['id'] = emp.id
        emp_info['company'] = get_company(db, emp.company)
        emp_info['first_name'] = emp.first_name
        emp_info['last_name'] = emp.last_name
        emp_info['position'] = emp.position
        emp_info['department'] = emp.department
        emp_info['phone'] = emp.phone
        emp_info['email'] = emp.email
        emp_info['is_complete'] = False if emp_info['first_name'] is None or emp_info['last_name'] is None or emp_info['position'] is None or emp_info['department'] is None or emp_info['phone'] is None or emp_info['email'] is None else True
        
        return emp_info
    else:
        return None
