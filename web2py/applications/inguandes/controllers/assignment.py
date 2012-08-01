# -*- coding: utf-8 -*-
import datetime
import os

@auth.requires_login()
def call():
    return service()

@auth.requires_login()
def view():
    if len(request.args) == 0:
        redirect(URL('default', 'index'))
    assignmentId = int(request.args[0])
    asgn_info = get_assignment(db, assignmentId)
    asgn_files = get_user_files(db, assignmentId, auth.user.id)
    
    user_group = get_user_assignment_group(db, asgn_info, auth.user.id)
            
    return dict(asgn_info=asgn_info, asgn_files=asgn_files, user_group=user_group)
    
@request.restful()
def assignment_files():

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
    
    def DELETE(file_id):
        u_file = db.user_assignment_file[file_id]
        asgn_info = get_assignment(db, u_file.assignment)
        response.headers['Content-Type'] = 'application/json'
        response.status = 200
        
        if asgn_info['is_available']:
            db.user_assignment_file[file_id].update_record(available=False)        
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