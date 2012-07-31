# -*- coding: utf-8 -*-

@auth.requires_login()
def call():
    return service()

@auth.requires_login()
def view():        
    if len(request.args) == 0:
        redirect(URL('default', 'index'))
    instanceId = int(request.args[0])
    inst = db.instance[instanceId]
           
    c_groups = db(db.content_group.instance==instanceId).select()
    contents = get_instance_content(db, instanceId)

    courseId = db(db.section.instance == instanceId).select().first().course
    
    questions, cats = get_questions(db, courseId)
        
    u_tasks = get_user_tasks(db, instanceId, auth.user.id)
    
    user_role = get_user_role(db, instanceId, auth.user.id)
    if user_role is None:
        session.flash = 'No tienes permisos para acceder a la instancia <strong>' + inst.title + '</strong>'
        redirect(URL('default', 'index'))
        
    if user_role == 3 and len(request.args) > 1:
        user_role = int(request.args[1])
        
    inst_links = db(db.instance_link.instance == instanceId).select()
    
    news = get_instance_news(db, instanceId)
            
    return dict(inst=inst, c_groups=c_groups, contents=contents, cats=cats, u_tasks=u_tasks, user_role=user_role, inst_links=inst_links, news=news)
    
@auth.requires_login()
def add_contentgroup():
    instanceId = int(request.vars.instanceid)
    if request.vars.title is not None:
        db.content_group.insert(title=request.vars.title,
                                instance=instanceId)
    redirect(URL('view', args=[instanceId]))
    
@auth.requires_login()
def add_content():
    instanceId = int(request.vars.instanceid)
    if request.vars.contenttype is not None and request.vars.name is not None:
        cgId = int(request.vars.cgid)
        cType = request.vars.contenttype
        if cType == "file":
            db.content_file.insert( name=request.vars.name,
                                    file=db.content_file.file.store(request.vars.file.file, request.vars.file.filename),
                                    is_required=request.vars.isrequired,
                                    content_group=cgId,
                                    description=request.vars.description)
        elif cType == "video":
            db.content_video.insert(name=request.vars.name,
                                    url=request.vars.url,
                                    is_required=request.vars.isrequired,
                                    content_group=cgId,
                                    description=request.vars.description)
        elif cType == "link":
            db.content_link.insert( name=request.vars.name,
                                    url=request.vars.url,
                                    is_required=request.vars.isrequired,
                                    content_group=cgId,
                                    description=request.vars.description)
        else:
            session.flash = "Tipo de contenido no conocido: {0}".format(cType)
    else:
        session.flash = "No fue posible agregar el contenido"
    redirect(URL('view', args=[instanceId]))

@auth.requires_login()    
def remove_content():
    if len(request.args) > 1:
        contentId = int(request.args[0])
        cType = request.args[1]
        result = True
        if cType == "file":
            del db.content_file[contentId]
        elif cType == "video":
            del db.content_video[contentId]
        elif cType == "link":
            del db.content_link[contentId]
        else:
            result = False
        
        response.headers['Content-Type'] = 'application/json'
        if result:
            response.status = 200
            return response.json({'message': 'Contenido ' + str(contentId) + ' eliminado'})
        else:
            response.status = 400
            return response.json({'message': 'No fue posible eliminar el contenido ' + str(contentId)})
    else:
        response.headers['Content-Type'] = 'application/json'
        response.status = 400
        return response.json({'message': 'Faltan parametros'})
            
@auth.requires_login()
def edit_content():
    if len(request.args) > 1:
        contentId = int(request.args[0])
        cType = request.args[1]
        obj = None
        if cType == "file":
            obj = db.content_file[contentId]
        elif cType == "video":
            obj = db.content_video[contentId]
        elif cType == "link":
            obj = db.content_link[contentId]
            
        response.headers['Content-Type'] = 'application/json'
        if obj is not None:
            obj.update_record(  name=request.vars.name,
                                is_required=request.vars.isrequired,
                                description=request.vars.description)
            response.status = 200
            return response.json({  'message': 'Contenido ' + str(contentId) + ' eliminado',
                                    'content': obj.as_dict()})
        else:
            response.status = 400
            return response.json({'message': 'No fue posible eliminar el contenido ' + str(contentId)})
    
@auth.requires_login()
def download_content_file():
    return response.download(request, db)
    
@service.json
def log_content(content_type, content_id):
    log_user_content(db, auth.user.id, content_type, content_id)

@auth.requires_login()
def ticket_categories():
    if len(request.args) == 0:
        redirect(URL('default', 'index'))
    instanceId = int(request.args[0])
    inst = db.instance[instanceId]

    cats, categories = get_ticket_categories(db, instanceId)

    selected_c = None
    subcategories = None
    moderators = None
    sections = None
    if len(request.args) > 1:
        selected_c = int(request.args[1])
        subcategories = db(db.ticket_subcategory.index==selected_c).select(db.ticket_subcategory.id ,db.ticket_subcategory.name).as_list()
        moderators = get_instance_moderators(db, instanceId)
        sections = get_instance_sections(db, instanceId)

    selected_sc = None
    sc_config = None
    if len(request.args) > 2:
        selected_sc = int(request.args[2])
        sc_config = db(db.ticket_subcategory.id==selected_sc).select().first().as_dict()

    return dict(inst=inst, cats=cats, categories=categories, subcategories=subcategories, selected_c=selected_c, selected_sc=selected_sc, sc_config=sc_config, moderators=moderators, sections=sections)

@auth.requires_login()
def add_ticket_category():
    instanceId = int(request.vars.instanceid)
    if request.vars.category:
        db.ticket_category_index.insert(name=request.vars.category,
                                    instance=instanceId)
        redirect(URL('ticket_categories', args=[instanceId]))

@auth.requires_login()
def add_ticket_subcategory():
    from datetime import datetime
    isToAll = request.vars.is_to_all == '1'
    instanceId = int(request.vars.instanceid)
    categoryId = int(request.vars.categoryid)
    print request.vars
    print isToAll
    if isToAll:
        if request.vars.subcategory:
            try:
                if request.vars.moderator:
                    moderatorId = int(request.vars.moderator)
                else:
                    session.flash = 'Debe elegir un moderador'
                    redirect(URL('ticket_categories', args=[instanceId, categoryId]))
                multiple=bool(request.vars.multiple),
                is_appealable=bool(request.vars.is_appealable)
                opening = datetime.strptime(request.vars.opening, '%Y-%m-%d %H:%M:%S')
                closing = datetime.strptime(request.vars.closing, '%Y-%m-%d %H:%M:%S')
                if opening >= closing:
                    session.flash = 'La fecha de apertura debe ser mayor a la de cierre'
                    redirect(URL('ticket_categories', args=[instanceId, categoryId]))
            except ValueError:
                session.flash = 'Fecha de apertura o cierre inválida'
                redirect(URL('ticket_categories', args=[instanceId, categoryId]))
            configs = []
            for s in get_instance_sections(db, instanceId):
                configs.append(db.section_ticket_subcategory.insert(the_section=s.id,
                                                                    opening=opening,
                                                                    closing=closing,
                                                                    moderator=moderatorId))
            db.ticket_subcategory.insert(   name=request.vars.subcategory,
                                            index=categoryId,
                                            multiple=multiple,
                                            is_appealable=is_appealable,
                                            sections_config=configs)
            session.flash = 'Subcategoría creada con éxito'
            redirect(URL('ticket_categories', args=[instanceId, categoryId]))
        else:
            session.flash = 'Debe ingresar el nombre de la subcategoría'
            redirect(URL('ticket_categories', args=[instanceId, categoryId]))
    else:
        if request.vars.subcategory:
            openings, closings, moderators = [], [], []
            sections = get_instance_sections(db, instanceId)
            try:
                multiple=bool(request.vars.multiple),
                is_appealable=bool(request.vars.is_appealable)
                for s in sections:
                    nrc = str(s.nrc)
                    moderators.append(int(request.vars['moderator-' + nrc]))
                    openings.append(datetime.strptime(request.vars['opening-' + nrc], '%Y-%m-%d %H:%M:%S'))
                    closings.append(datetime.strptime(request.vars['closing-' + nrc], '%Y-%m-%d %H:%M:%S'))
                    if openings[-1] >= closings[-1]:
                        session.flash = 'La fecha de apertura debe ser mayor a la de cierre'
                        redirect(URL('ticket_categories', args=[instanceId, categoryId]))
            except ValueError:
                session.flash = 'Existe una fecha inválida o falta elegir al menos un moderador'
                redirect(URL('ticket_categories', args=[instanceId, categoryId]))
            idx = 0
            configs = []
            for s in sections:
                configs.append(db.section_ticket_subcategory.insert(the_section=s.id,
                                                                    opening=openings[idx],
                                                                    closing=closings[idx],
                                                                    moderator=moderators[idx]))
                idx += 1
                
            db.ticket_subcategory.insert(   name=request.vars.subcategory,
                                            index=categoryId,
                                            multiple=multiple,
                                            is_appealable=is_appealable,
                                            sections_config=configs)
            session.flash = 'Subcategoría creada con éxito'
            redirect(URL('ticket_categories', args=[instanceId, categoryId]))
        else:
            session.flash = 'Debe ingresar el nombre de la subcategoría'
            redirect(URL('ticket_categories', args=[instanceId, categoryId]))

@auth.requires_login()
def submit_ticket():
    instances = get_user_student_instances(db, auth.user.id)
    selected_i = None
    categories = None
    if len(request.args) > 0:
        instanceId = int(request.args[0])
        inst = db.instance[instanceId]
        selected_i = instanceId
        categories = get_ticket_categories_with_sub_for_user(db, instanceId, auth.user.id)
        
    selected_sc = None
    if len(request.args) > 1:
        subcategoryId = int(request.args[1])
        selected_sc = subcategoryId
        
    return dict(instances=instances, selected_i=selected_i, categories=categories, selected_sc=selected_sc)

@request.restful()
def quiz():
    @auth.requires_login()
    def GET(quizId):
        redirect(URL('quiz', 'start', args=[quizId]))
    
    @auth.requires_login()
    def POST(**fields):  
        if len(fields['name'].strip()) > 0 and len(fields['starting'].strip()) > 0:
            courseId = db(db.section.instance == fields['instance']).select().first().course
            categories = get_categories(db, courseId)
            
            quiz_id = db.quiz.insert(   name=fields['name'],
                                        starting=fields['starting'],
                                        ending=fields['ending'],
                                        instance=fields['instance'])   
                                        
            for cat in categories:
                if cat in fields:
                    db.quiz_category.insert(category=cat,
                                            count=fields[cat],
                                            quiz=quiz_id)
            
            response.headers['Content-Type'] = 'application/json'        
            return response.json({'message': 'ok'})
        else:
            response.headers['Content-Type'] = 'application/json'        
            return response.json({'message': 'error'})
        
    return locals()
    
@request.restful()
def assignment():
    @auth.requires_login()
    def GET(assignmentId):
        redirect(URL('assignment', 'view', args=[assignmentId]))
    
    @auth.requires_login()
    def POST(**fields):  
        if len(fields['name'].strip()) > 0 and len(fields['starting'].strip()) > 0:
            assignmentId = db.assignment.insert(name=fields['name'],
                                                starting=fields['starting'],
                                                ending=fields['ending'],
                                                instance=fields['instance'],
                                                file_types=fields['file_types'] if len(fields['file_types'].strip()) > 0 else None,
                                                multiple=fields['multiple'],
                                                max_size=fields['max_size'])
            
            session.flash = "Trabajo agregado con éxito"
            redirect(URL('view', args=[fields['instance']]))
        else:
            session.flash = "No fue posible agregar el trabajo solicitado"        
        
    return locals()

@auth.requires_login()
def add_permanent_link():
    instanceId = int(request.vars.instanceid)
    if request.vars.icon is not None and request.vars.url is not None:
        db.instance_link.insert(icon=request.vars.icon,
                                url=request.vars.url,
                                instance=instanceId,
                                description=request.vars.description)
    redirect(URL('view', args=[instanceId]))
    
@auth.requires_login()
def groups():
    if len(request.args) == 0:
        redirect(URL('default', 'index'))
    instanceId = int(request.args[0])
    inst = db.instance[instanceId]
    
    gls = get_group_lists(db, instanceId)
    gl_info = None
    g_info = None
    if len(request.args) > 1:
        gl_id = int(request.args[1])
        gl_info = get_grouplist_info(db, gl_id)     
        if len(request.args) > 2:
            g_id = int(request.args[2])
            g_info = get_group_info(db, gl_id, g_id)     
            print g_info
    
    return dict(inst=inst, gls=gls, gl_info=gl_info, g_info=g_info)
    
@auth.requires_login()
def add_grouplist():
    instanceId = int(request.vars.instanceid)
    if request.vars.name is not None:
        db.group_list.insert(   name=request.vars.name,
                                instance=instanceId)
    redirect(URL('groups', args=[instanceId]))
    
@auth.requires_login()
def add_group():    
    stds = request.vars['students[]']
    response.headers['Content-Type'] = 'application/json'        
    if stds is not None and len(stds) > 0:
        number = max_group_number(db, request.vars.grouplist) + 1
        for std in stds:
            db.student_group.insert(student=std,
                                    group_id=number,
                                    group_list=request.vars.grouplist)
        
        return response.json({  'message': 'Nuevo grupo '.format(str(number)),
                                'group_id': number})
    else:
        return response.json({'message': 'No hay alumnos que agregar.'})

@auth.requires_login()
def del_group_student():
    if len(request.args) > 2:
        gl_id = int(request.args[0])
        gl_info = get_grouplist_info(db, gl_id)     
        g_id = int(request.args[1])
        std_id = int(request.args[2])
        
        db((db.student_group.student == std_id) & (db.student_group.group_id == g_id) & (db.student_group.group_list == gl_id)).delete()        
        redirect(URL('groups', args=[gl_info['instance'], gl_info['id'], g_id]))
    else:
        redirect(URL('default', 'index'))
        
@auth.requires_login()
def add_group_student():
    if len(request.args) > 2:
        gl_id = int(request.args[0])
        gl_info = get_grouplist_info(db, gl_id)     
        g_id = int(request.args[1])
        std_id = int(request.args[2])
        
        db.student_group.insert(student=std_id,
                                group_id=g_id,
                                group_list=gl_id)
        
        redirect(URL('groups', args=[gl_info['instance'], gl_info['id'], g_id]))
    else:
        redirect(URL('default', 'index'))

@auth.requires_login()        
def add_new():
    instanceId = int(request.vars.instanceid)
    if request.vars.title is not None and request.vars.content is not None:
        db.instance_new.insert( title=request.vars.title,
                                content=request.vars.content,
                                instance=instanceId,
                                creator=auth.user.id)
        session.flash = 'Noticia agregada correctamente'
    else:
        session.flash = 'No fue posible agregar la noticia'
    redirect(URL('view', args=[instanceId]))
