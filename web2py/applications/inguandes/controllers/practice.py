# -*- coding: utf-8 -*-
@auth.requires_login()
def view():
    p_info = None
    if len(request.args) > 0:
        p_info = get_practice(db, int(request.args[0]))
    practices = get_user_practices(db, auth.user.id)
    p_period = get_current_next_period(db, 0)
    return dict(practices=practices, p_info=p_info, p_period=p_period)   

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
                                    business_line=request.vars.businessLine,
                                    address=request.vars.address,
                                    city=request.vars.city,
                                    country=request.vars.country)
        practice.update_record(company=com_id)
    else:
        com = db.company[practice.company]
        com.update_record(  rut=request.vars.rut,
                            name=request.vars.name,
                            business_line=request.vars.businessLine,
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
    
    result = send_validation_email(db, p_id)
    
    if result:    
        practice.update_record(validation_sent=request.now)
        session.flash = 'Correo electrónico enviado correctamente a {}.'.format(practice.validator.email)
        session.flash_level = 'success'
    else:
        session.flash = 'No se pudo enviar el correo electrónico a {}.'.format(practice.validator.email)
        session.flash_level = 'error'
    
    redirect(URL('view', args=[p_id]))

# Not require authorization
def validate_practice():
    if len(request.args) == 0:
        redirect(URL(''))
    p_key = request.args[0]
    practice = db(db.practice.p_key == p_key).select().first()
    validation_result = True if int(request.args[1]) == 1 else False
    
    if practice is not None:
        practice.update_record(validation_ready=request.now, validation_result=validation_result)
    else:
        redirect(URL(''))
    
    return dict(validation_result=validation_result)
 
@auth.requires_membership(role='ing-admin')   
def view_all():
    selected_state = request.vars.state
    if selected_state is None:
        selected_state = 'validation_ready'
        
    pid = None
    if len(request.args) > 0:
        pid = int(request.args[0])
        
    practices = None
    p_info = None
    if pid is None:
        practices = get_practice_by_state(db, selected_state)
    else:
        p_info = get_practice(db, pid)
        
    st_counts = get_practices_state_counts(db)
        
    return dict(selected_state=selected_state, practices=practices, p_info=p_info, st_counts=st_counts)

@auth.requires_membership(role='ing-admin')       
def practice_register_evaluation():    
    p_id = int(request.vars.practiceid)
    practice = db.practice[p_id]
    approve_result = True if int(request.vars.approveresult) == 1 else False    
    practice.update_record( approved=approve_result,
                            approved_comment=request.vars.comments if len(request.vars.comments) > 0 else None,
                            approved_date=request.now)
    redirect(URL('view_all', vars={'state':'validation_ready'}))
