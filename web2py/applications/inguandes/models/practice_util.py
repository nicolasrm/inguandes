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
    p_info['state'] = 'pending'
    p_info['description'] = p.description
    p_info['starting'] = p.starting
    p_info['ending'] = p.ending
    
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
        
        return emp_info
    else:
        return None
