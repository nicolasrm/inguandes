# -*- coding: utf-8 -*-
import datetime
import os
import contenttype

@auth.requires_login()
def call():
    return service()

@auth.requires_login()
def view():
    if len(request.args) == 0:
        redirect(URL('default', 'index'))
    assignmentId = int(request.args[0])
    
    asgn_info = get_assignment(db, assignmentId)
    
    user_role = get_user_role(db, asgn_info['instance_id'], auth.user.id)
    
    user_id = auth.user.id
    if len(request.args) > 1 and user_role >= 2:
        user_id = int(request.args[1])
    
    
    section_info = get_user_section(db, asgn_info['instance_id'], user_id)
    asgn_info = get_assignment(db, assignmentId, section_info)    
        
    user_group = get_user_assignment_group(db, asgn_info, user_id)
    asgn_files = get_group_files(db, asgn_info, user_id)
    
    user_evals = get_user_assignment_evaluation(db, asgn_info, user_id)
            
    return dict(asgn_info=asgn_info, asgn_files=asgn_files, user_group=user_group, user_evals=user_evals, user_role=user_role)
    
@request.restful()
def assignment_files():

    @auth.requires_login()
    def POST(assignment_id, **fields):        
        asgn_info = get_assignment(db, assignment_id)
        uploaded_files = []
        error_msg = ''
                        
        if asgn_info['is_available']:
            array_files = fields['files[]']
            if not isinstance(fields['files[]'], (list, tuple)):
                array_files = [fields['files[]']]            
            if asgn_info['multiple'] or len(array_files) == 1:            
                for f in array_files:
                    o_filename, o_ext = os.path.splitext(f.filename)
                    
                    f.file.seek(0, os.SEEK_END)
                    file_size = f.file.tell()/1024
                    f.file.seek(0, os.SEEK_SET)
                    
                    if (asgn_info['file_types'] is None or len(asgn_info['file_types']) == 0 or o_ext[1:] in asgn_info['file_types']) and file_size <= asgn_info['max_size_kb']:            
                        # Discard previous file with the same name if this exists
                        old_file = db((db.user_assignment_file.original_filename == f.filename) & (db.user_assignment_file.available == True)).select().first()
                        if old_file is not None:
                            old_file.update_record(available=False)
                        
                        n_filename = f.filename if len(o_filename) < 30 else o_filename[:30] + o_ext
                        file_id = db.user_assignment_file.insert(   the_user=auth.user.id,
                                                                    assignment=assignment_id,
                                                                    original_filename=f.filename,
                                                                    file=db.user_assignment_file.file.store(f.file, n_filename))
                                    
                        uploaded_files.append(get_assignment_file_info(db, file_id))
                    elif file_size > asgn_info['max_size_kb']:
                        error_msg = 'Archivo mas grande que lo permitido ({0} vs {1})'.format(file_size, asgn_info['max_size_kb'])
                    elif len(asgn_info['file_types']) > 0 and o_ext[1:] not in asgn_info['file_types']:
                        error_msg = 'Extension no permitida ({0} vs {1})'.format(o_ext[1:], asgn_info['file_types'])
                    else:
                        error_msg = 'Error al guardar'
            else:
                error_msg = 'Este trabajo permite un solo archivo'
        else:
            error_msg = 'El trabajo ya no permite el envio de nuevos archivos'
        
        if request.ajax:
            if request.env.http_accept.find('application/json'):
                response.headers['Content-Type'] = 'application/json'
            else:
                response.headers['Content-Type'] = 'text/plain'
            
            if len(uploaded_files) > 0:
                return response.json(uploaded_files)
            else:                
                return response.json({
                    'code': 'Error',
                    'message': error_msg
                    })        
    
    @auth.requires_login()
    def DELETE(file_id):
        u_file = db.user_assignment_file[file_id]
        asgn_info = get_assignment(db, u_file.assignment)
        response.headers['Content-Type'] = 'application/json'
        response.status = 200
        
        if asgn_info['is_available']:
            db.user_assignment_file[file_id].update_record(available=False)
            log_action(db, auth.user.id, 'delete_file', 'user_assignment_file', file_id)
            return response.json({'mensaje': 'archivo ' + file_id + ' eliminado'})
        else:            
            return response.json({'mensaje': 'No esta permitido borrar archivos'})
    
    return locals()
    
@auth.requires_login()
def download_user_assignment_file():
    log_download(db, auth.user.id, request.args[0])
    return response.download(request, db)
    
@auth.requires_login()
def download_assignment_file():
    return response.download(request, db)

@auth.requires_login()
def result():
    if len(request.args) == 0:
        redirect(URL('default', 'index'))
    assignmentId = int(request.args[0])
    asgn_info = get_assignment(db, assignmentId)
    section_info = get_user_section(db, asgn_info['instance_id'], auth.user.id)
    asgn_info = get_assignment(db, assignmentId, section_info)
    
    user_role = get_user_role(db, asgn_info['instance_id'], auth.user.id)
    if len(request.args) == 1 and user_roles[user_role] == 'Profesor' or user_roles[user_role] == 'Ayudante Jefe':
        redirect(URL('all_result', args=[assignmentId]))
    else:
        redirect(URL('view', args=[assignmentId]))
    
@auth.requires_login()
def all_result():
    if len(request.args) == 0:
        redirect(URL('default', 'index'))
        
    assignmentId = int(request.args[0])
    asgn_info = get_assignment(db, assignmentId)
    
    user_role = get_user_role(db, asgn_info['instance_id'], auth.user.id)
    if user_roles[user_role] != 'Profesor' and user_roles[user_role] != 'Ayudante Jefe':
        redirect(URL('view', args=[assignmentId]))
    
    a_results = assignment_results(db, asgn_info)
    a_evals = get_assignment_group_evaluations(db, asgn_info)
    
    return dict(asgn_info=asgn_info, a_results=a_results, a_evals=a_evals)
    
@auth.requires_login()
def download_all():
    if len(request.args) == 0:
        redirect(URL('default', 'index'))
        
    assignmentId = int(request.args[0])
    asgn_info = get_assignment(db, assignmentId)
    
    tmpfilepath = zip_assignment(db, asgn_info)
    
    response.headers['Content-Type'] = contenttype.contenttype(tmpfilepath)
    response.headers['Content-Disposition'] = 'attachment; filename={0}.zip'.format(asgn_info['name'])
        
    return response.stream(open(tmpfilepath,'rb'),chunk_size=4096)

@auth.requires_login()    
def add_group_evaluation():
    if request.vars.ending is not None and request.vars.assignmentid is not None:
        assignmentId = int(request.vars.assignmentid)
        ge_id = db.group_evaluation.insert( ending=request.vars.ending,
                                            include_myself=request.vars.include_myself,
                                            distribute_all=request.vars.distribute_all,
                                            total_points=request.vars.total_points,
                                            max_individual_points=request.vars.max_individual_points)
                                            
        asgn = db.assignment[assignmentId]
        asgn.update_record(group_evaluation=ge_id)
    
    redirect(URL('all_result', args=[assignmentId]))
    
@auth.requires_login()    
def evaluate_group():
    if request.vars.assignmentid is not None:
        assignmentId = int(request.vars.assignmentid)
        asgn_info = get_assignment(db, assignmentId)
        user_group = get_user_assignment_group(db, asgn_info, auth.user.id)
        evals = {}
        total = 0
        error = None
        for std in user_group['students']:
            field = 'evaluation_' + str(std['id'])
            if request.vars[field] is not None:
                evals[std['id']] = int(request.vars[field]) if len(request.vars[field]) > 0 else 0
                total = total + evals[std['id']]
                if evals[std['id']] > asgn_info['group_evaluation']['max_individual_points']:
                    error = 'No puedes asignar más de {0} puntos a un integrante.'.format(asgn_info['group_evaluation']['max_individual_points'])
        
        if asgn_info['group_evaluation']['distribute_all'] and asgn_info['group_evaluation']['total_points'] != total:
            error = 'Debes distribuir exactamente {0} puntos.'.format(asgn_info['group_evaluation']['total_points'])
        elif not asgn_info['group_evaluation']['distribute_all'] and asgn_info['group_evaluation']['total_points'] < total:
            error = 'No puedes repartir más de {0} puntos.'.format(asgn_info['group_evaluation']['total_points'])
            
        if error is None:
            for (k,v) in evals.iteritems():
                db.user_group_evaluation.insert(group_evaluation=asgn_info['group_evaluation']['id'],
                                                evaluator=auth.user.id,
                                                the_user=k,
                                                score=v)
            session.flash = 'Evaluación guardada con éxito.'
        else:
            session.flash = error            
        
    redirect(URL('all_result', args=[assignmentId]))
    
@auth.requires_login()
def group_evaluation():
    assignmentId = int(request.args[0])
    asgn_info = get_assignment(db, assignmentId)
    
    user_role = get_user_role(db, asgn_info['instance_id'], auth.user.id)
    user_id = auth.user.id
    if user_roles[user_role] != 'Profesor' and user_roles[user_role] != 'Ayudante Jefe':
        redirect(URL('view', args=[assignmentId]))
    if len(request.args) > 1:
        user_id = int(request.args[1])
        
    user_group = get_user_assignment_group(db, asgn_info, user_id)
    
    g_evals = get_assignment_group_evaluation(db, asgn_info, user_group)
    
    return dict(asgn_info=asgn_info, user_group=user_group, g_evals=g_evals)