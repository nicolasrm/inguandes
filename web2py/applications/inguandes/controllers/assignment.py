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
            
    return dict(asgn_info=asgn_info, asgn_files=asgn_files)
    
@request.restful()
def assignment_files():

    def POST(assignment_id, **fields):        
        uploaded_files = []
        array_files = fields['files[]']
        if not isinstance(fields['files[]'], (list, tuple)):
            array_files = [fields['files[]']]
        for f in array_files:
            file_id = db.user_assignment_file.insert(   the_user=auth.user.id,
                                                        assignment=assignment_id,
                                                        file=db.user_assignment_file.file.store(f.file, f.filename))
                        
            uploaded_files.append(get_assignment_file_info(db, file_id))
        
        if request.ajax:
            if request.env.http_accept.find('application/json'):
                response.headers['Content-Type'] = 'application/json'
            else:
                response.headers['Content-Type'] = 'text/plain'
            
            if len(uploaded_files) > 0:
                return response.json(uploaded_files)
            else:
                response.status = 409
                return response.json([{
                    'code': 'Error',
                    'message': 'Error al guardar archivo'
                    }])
    
    def DELETE(file_id):
        db(db.user_assignment_file.id == file_id).delete()
        response.headers['Content-Type'] = 'application/json'
        response.status = 200
        return response.json({'mensaje': 'archivo ' + file_id + ' eliminado'})
    
    return locals()