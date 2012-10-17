# -*- coding: utf-8 -*-
@auth.requires_login()
def view():
    p_info = None
    if len(request.args) > 0:
        p_info = get_practice(db, int(request.args[0]))
    practices = get_user_practices(db, auth.user.id)
    return dict(practices=practices, p_info=p_info)   

@auth.requires_login()
def add_practice():
    p_id = None
    if request.vars.category is not None:
        p_id = db.practice.insert(  the_user=auth.user.id,
                                    category=request.vars.category)
    
    redirect(URL('view', args=[p_id]))

@auth.requires_login()    
def update_company():
    p_id = request.vars.practiceid
    practice = db.practice[p_id]
    
    if practice.company is None:
        com_id = db.company.insert( rut=request.vars.rut,
                                    name=request.vars.name,
                                    businessLine=request.vars.businessLine,
                                    address=request.vars.address,
                                    city=request.vars.city,
                                    country=request.vars.country)
        practice.update_record(company=com_id)
    else:
        com = db.company[practice.company]
        com.update_record(  rut=request.vars.rut,
                            name=request.vars.name,
                            businessLine=request.vars.businessLine,
                            address=request.vars.address,
                            city=request.vars.city,
                            country=request.vars.country)
        
    session.flash = 'Datos guardados con éxito.'
    session.flash_level = 'success'
    redirect(URL('view', args=[p_id]))

@auth.requires_login()    
def update_validator():
    p_id = request.vars.practiceid
    practice = db.practice[p_id]
    if practice.validator is None:
        emp_id = db.company_employee.insert(company=practice.company,
                                            first_name=request.vars.first_name,
                                            last_name=request.vars.last_name,
                                            position=request.vars.position,
                                            department=request.vars.department,
                                            phone=request.vars.phone,
                                            email=request.vars.email)
        practice.update_record(validator=emp_id)
    else:
        emp = db.company_employee[practice.validator]
        emp.update_record(  company=practice.company,
                            first_name=request.vars.first_name,
                            last_name=request.vars.last_name,
                            position=request.vars.position,
                            department=request.vars.department,
                            phone=request.vars.phone,
                            email=request.vars.email)
    
    session.flash = 'Datos guardados con éxito.'
    session.flash_level = 'success'
    redirect(URL('view', args=[p_id]))

@auth.requires_login()
def update_practice():
    p_id = request.vars.practiceid
    practice = db.practice[p_id]
    practice.update_record( description=request.vars.description,
                            starting=request.vars.starting,
                            ending=request.vars.ending)
    
    session.flash = 'Datos guardados con éxito.'
    session.flash_level = 'success'
    redirect(URL('view', args=[p_id]))

@auth.requires_login()    
def start_validation():
    if len(request.args) == 0:
        redirect(URL('view'))
    p_id = int(request.args[0])
    p_key = generate_key(p_id)
    practice = db.practice[p_id]
    practice.update_record(p_key=p_key)
    
    send_validation_email(db, p_id)
    
    practice.update_record(validation_sent=request.now)
    
    session.flash = 'Correo electrónico enviado correctamente.'
    session.flash_level = 'success'
    
    redirect(URL('view', args=[p_id]))
    
def validate_practice():
    if len(request.args) == 0:
        redirect(URL(''))
    p_key = request.args[0]
    practice = db(db.practice.p_key == p_key).select().first()
    
    if practice is not None:
        practice.update_record(validation_ready=request.now)
    else:
        redirect(URL(''))
    
    return dict()
