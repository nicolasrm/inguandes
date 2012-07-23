# -*- coding: utf-8 -*-
import datetime
import random
import os

def get_assignments(db, instanceId, userId):
    asgns = db(db.assignment.instance==instanceId).select(db.assignment.ALL)
    
    asgn_dict = {}
    asgn_dict['pending'] = []
    asgn_dict['actived'] = []
    asgn_dict['closed'] = []
    today = datetime.date.today()
    for a in asgns:
        # u_quiz = get_user_quiz(db, a.id, userId)
        a['type'] = 'assignment'
        a['icon'] = 'icon-upload'
        if a.starting > today:
            asgn_dict['pending'].append(a)
        elif a.ending >= today:
            asgn_dict['actived'].append(a)
        else:
            asgn_dict['closed'].append(a)
    
    return asgn_dict
    
def get_assignment(db, asgnId):
    cAsgn = db.assignment[asgnId]
    
    asgn_info = {}
    asgn_info['id'] = cAsgn.id
    asgn_info['name'] = cAsgn.name
    asgn_info['starting'] = cAsgn.starting
    asgn_info['ending'] = cAsgn.ending
    asgn_info['file_types'] = cAsgn.file_types.split(';')
    asgn_info['file_types_text'] = cAsgn.file_types
    asgn_info['multiple'] = cAsgn.multiple
    asgn_info['max_size'] = cAsgn.max_size
    asgn_info['instance'] = cAsgn.instance.title
    asgn_info['instance_id'] = cAsgn.instance
    
    return asgn_info
    
def get_assignment_file_info(db, file_id):
    up_file = db.user_assignment_file[file_id]
    filename, file_stream = db.user_assignment_file.file.retrieve(up_file.file)
    only_name, file_extension = os.path.splitext(filename)
    
    return {'filename': up_file.original_filename,
            'id': up_file.id,
            'size': round(os.fstat(file_stream.fileno()).st_size/1024, 1),
            'type': file_extension,
            'uploaded': up_file.created_on
            }

def get_user_files(db, asgnId, userId):
    u_files = db((db.user_assignment_file.the_user == userId) & (db.user_assignment_file.assignment == asgnId)).select()
    files_info = []
    for uf in u_files:
        files_info.append(get_assignment_file_info(db, uf.id))
        
    return files_info