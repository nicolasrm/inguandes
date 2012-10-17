# -*- coding: utf-8 -*-
import random
import string

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
        
def generate_key(pId):
    p_key = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(6))
    p_key = p_key + str(pId)
    return p_key
        
def send_validation_email(db, pId):
    practice = db.practice[pId]
    validator = db.company_employee[practice.validator]
    the_user = db.auth_user[practice.the_user]
    company = db.company[practice.company]
    tos = [validator.email]
        
    message = 'Estimado,\r\nel alumno {} {} ha inscrito su práctica indicando la siguiente información:\r\n'.format(the_user.first_name, the_user.last_name)
    message = message + 'Rut empresa: {}\r\n'.format(company.rut)
    message = message + 'Nombre empresa: {}\r\n'.format(company.name)
    message = message + 'Dirección empresa: {}\r\n\r\n'.format(company.address)
    message = message + 'Descripción práctica: {}\r\n'.format(practice.description)
    message = message + 'Fecha estimada de inicio: {}\r\n'.format(practice.starting)
    message = message + 'Fecha estimada de fin: {}\r\n\r\n'.format(practice.ending)
    message = message + 'Si la información es correcta, le pedimos que presione en el link a continuación como validación de la inscripción de la práctica del alumno. Si no conoce al alumno, o no tiene la información para validar esta inscripción, por favor eliminar este correo.\r\n'
    message = message + URL('practice', 'validate_practice', args=[practice.p_key], scheme=True, host=True)
    message = message + '\r\n--\r\nFacultad de Ingeniería y Ciencias Aplicadas\r\nUniversidad de los Andes'
    subject = '[iuandes] Validación Inscripción Práctica'
    
    mail.send(  to=tos,
                subject=subject,
                message=message)
