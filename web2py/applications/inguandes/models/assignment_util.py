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
    now = datetime.datetime.now()
    for a in asgns:
        # u_quiz = get_user_quiz(db, a.id, userId)
        a['type'] = 'assignment'
        a['icon'] = 'icon-upload'
        if a.starting > now:
            asgn_dict['pending'].append(a)
        elif a.ending >= now:
            asgn_dict['actived'].append(a)
        else:
            asgn_dict['closed'].append(a)
    
    return asgn_dict
    
def get_assignment(db, asgnId):
    cAsgn = db.assignment[asgnId]
    asgn_files = db(db.assignment_file.assignment == asgnId).select()
    
    asgn_info = {}
    asgn_info['id'] = cAsgn.id
    asgn_info['name'] = cAsgn.name
    asgn_info['starting'] = cAsgn.starting
    asgn_info['ending'] = cAsgn.ending
    asgn_info['file_types'] = cAsgn.file_types.split(';') if cAsgn.file_types is not None and len(cAsgn.file_types.strip()) > 0 else None
    asgn_info['file_types_text'] = cAsgn.file_types
    asgn_info['multiple'] = cAsgn.multiple
    asgn_info['max_size'] = cAsgn.max_size
    asgn_info['max_size_kb'] = file_size_options_kb[cAsgn.max_size]
    asgn_info['instance'] = cAsgn.instance.title
    asgn_info['instance_id'] = cAsgn.instance
    asgn_info['is_available'] = cAsgn.ending >= datetime.datetime.now()
    asgn_info['files'] = asgn_files
    
    return asgn_info
    
def get_assignment_file_info(db, file_id):
    up_file = db.user_assignment_file[file_id]
    filename, file_stream = db.user_assignment_file.file.retrieve(up_file.file)
    only_name, file_extension = os.path.splitext(up_file.original_filename)
    same_name_files = db(db.user_assignment_file.original_filename == up_file.original_filename).select(db.user_assignment_file.id, orderby=~db.user_assignment_file.created_on)
    
    return {'filename': only_name,
            'id': up_file.id,
            'size': round(os.fstat(file_stream.fileno()).st_size/1024, 1),
            'type': file_extension,
            'uploaded': up_file.created_on,
            'available': up_file.available,
            'file': up_file.file,
            'history': [sf.id for sf in same_name_files]
            }

def get_user_files(db, asgnId, userId):
    u_files = db((db.user_assignment_file.the_user == userId) & (db.user_assignment_file.assignment == asgnId)).select(orderby =~ db.user_assignment_file.created_on)
    files_info = []
    for uf in u_files:
        files_info.append(get_assignment_file_info(db, uf.id))
        
    return files_info       

def log_download(db, userId, file):
    u_file = db(db.user_assignment_file.file == file).select().first()
    if u_file is not None:
        db.download_file_log.insert(the_user=userId,
                                    assignment_file=u_file.id)