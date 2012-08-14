# -*- coding: utf-8 -*-
import datetime
import random
import os
import shutil

def get_assignments(db, instanceId, userId, section_info=None, user_role=None):
    asgns = db(db.assignment.instance==instanceId).select(db.assignment.ALL)
    
    asgn_dict = {}
    asgn_dict['pending'] = []
    asgn_dict['actived'] = []
    asgn_dict['closed'] = []
    now = datetime.datetime.now()
    for a in asgns:
        a_info = get_assignment(db, a.id, section_info)
        ais = []
        
        if user_role is not None and user_role >= 2 and a_info['section_dates'] is not None and len(a_info['section_dates']) > 0:
            inst_sections = get_instance_sections(db, instanceId)
            for s in inst_sections:
                ai = a_info.copy()
                ai['name'] = '{0} ({1})'.format(ai['name'], s['nrc'])                
                if s['id'] in ai['section_dates']:
                    ai['starting'] = ai['section_dates'][s['id']]['starting']
                    ai['ending'] = ai['section_dates'][s['id']]['ending']          
                
                ais.append(ai)
        else:        
            ais.append(a_info)
            
        for ai in ais:
            if ai['starting'] > now:
                asgn_dict['pending'].append(ai)
            elif ai['ending'] >= now:
                asgn_dict['actived'].append(ai)
            else:
                asgn_dict['closed'].append(ai)
    
    return asgn_dict
    
def get_assignment(db, asgnId, section_info=None):
    cAsgn = db.assignment[asgnId]
    asgn_files = db(db.assignment_file.assignment == asgnId).select()
    
    section_dates = get_assignment_section_dates(db, asgnId)
    
    asgn_info = {}
    asgn_info['id'] = cAsgn.id
    asgn_info['name'] = cAsgn.name
    asgn_info['starting'] = cAsgn.starting if section_info == None or section_info['id'] not in section_dates else section_dates[section_info['id']]['starting']
    asgn_info['ending'] = cAsgn.ending if section_info == None or section_info['id'] not in section_dates else section_dates[section_info['id']]['ending']
    asgn_info['file_types'] = cAsgn.file_types.split(';') if cAsgn.file_types is not None and len(cAsgn.file_types.strip()) > 0 else None
    asgn_info['file_types_text'] = cAsgn.file_types
    asgn_info['multiple'] = cAsgn.multiple
    asgn_info['max_size'] = cAsgn.max_size
    asgn_info['max_size_kb'] = file_size_options_kb[cAsgn.max_size]
    asgn_info['instance'] = cAsgn.instance.title
    asgn_info['instance_id'] = cAsgn.instance
    asgn_info['is_available'] = cAsgn.ending >= datetime.datetime.now()
    asgn_info['files'] = asgn_files
    asgn_info['in_groups'] = cAsgn.in_groups
    asgn_info['group_list'] = cAsgn.group_list
    asgn_info['section_dates'] = section_dates
    asgn_info['type'] = 'assignment'
    asgn_info['icon'] = 'icon-upload'
    
    return asgn_info
    
def get_assignment_section_dates(db, asgnId):
    asections = db(db.assignment_section.assignment == asgnId).select()
    section_dates = {}
    for s in asections:
        as_info = {}
        as_info['starting'] = s['starting']
        as_info['ending'] = s['ending']
        as_info['nrc'] = s.section.nrc
        section_dates[s['section']] = as_info
    
    return section_dates
    
def get_assignment_file_info(db, file_id):
    up_file = db.user_assignment_file[file_id]
    filename, file_stream = db.user_assignment_file.file.retrieve(up_file.file)
    only_name, file_extension = os.path.splitext(up_file.original_filename)
    same_name_files = db(db.user_assignment_file.original_filename == up_file.original_filename).select(db.user_assignment_file.id, orderby=~db.user_assignment_file.created_on)
    
    return {'filename': only_name,
            'original_filename': up_file.original_filename,
            'id': up_file.id,
            'size': round(os.fstat(file_stream.fileno()).st_size/1024, 1),
            'type': file_extension,
            'uploaded': up_file.created_on,
            'user': up_file.the_user.first_name + ' ' + up_file.the_user.last_name,
            'available': up_file.available,
            'file': up_file.file,
            'history': [sf.id for sf in same_name_files]
            }

def get_group_files(db, asgn_info, userId):
    user_group = get_user_assignment_group(db, asgn_info, userId)
    files_info = []
    if user_group is None:
        files_info = get_user_files(db, asgn_info, userId)
    if user_group is not None:
        for std in user_group['students']:
            files_info = files_info + get_user_files(db, asgn_info, std['id'])
        
    return files_info       
    
def get_user_files(db, asgn_info, userId):
    u_files = db((db.user_assignment_file.the_user == userId) & (db.user_assignment_file.assignment == asgn_info['id'])).select(orderby =~ db.user_assignment_file.created_on)
    files_info = []
    for uf in u_files:
        files_info.append(get_assignment_file_info(db, uf.id))
    
    return files_info   

def log_download(db, userId, file):
    u_file = db(db.user_assignment_file.file == file).select().first()
    if u_file is not None:
        db.download_file_log.insert(the_user=userId,
                                    assignment_file=u_file.id)
                                    
def get_user_assignment_group(db, asgn_info, userId):
    if not asgn_info['in_groups']:
        return None
    else:
        return get_user_group(db, asgn_info['group_list'], userId)
        
def get_last(file_info):
    return file_info
            
def assignment_group_result(db, asgn_info, userId, user_group):
    gr_files = get_group_files(db, asgn_info, userId)
    user = db.auth_user[userId]
    
    gr_result = {}
    gr_result['user_id'] = userId
    gr_result['files'] = gr_files
    gr_result['name'] = 'Grupo ' + str(user_group['id']) if user_group is not None else user.last_name + ', ' + user.first_name
    gr_result['last_modification'] = max([f['uploaded'] for f in gr_files]) if len(gr_files) > 0 else '-'
    gr_result['files_count'] = len([f for f in gr_files if f['available']])
    gr_result['modifications_count'] = sum([len(f['history']) for f in gr_files]) if len(gr_files) > 0 else '-'
    
    return gr_result
        
def assignment_results(db, asgn_info):
    stds = get_instance_users_by_role(db, asgn_info['instance_id'], 0)
    a_results = {}
    for s in stds:
        user_group = get_user_assignment_group(db, asgn_info, s.id)
        if user_group is None or user_group['id'] not in a_results:
            gr = assignment_group_result(db, asgn_info, s.id, user_group)
            key = user_group['id'] if user_group is not None else s.id
            if gr is not None:
                a_results[key] = gr
    
    return a_results
    
def zip_assignment(db, asgn_info):
    stds = get_instance_users_by_role(db, asgn_info['instance_id'], 0)
    
    asgn_name = asgn_info['name'].replace(':', '-')
    
    zip_filename = asgn_name
    temp_path = os.path.join(request.folder, 'uploads', 'temp')
    
    if not os.path.exists(temp_path):
        os.makedirs(temp_path)
        
    new_temp_path = os.path.join(temp_path, 'temp')
    zip_file_path = os.path.join(temp_path, zip_filename)        
    
    if os.path.exists(new_temp_path):
        shutil.rmtree(new_temp_path)
    os.makedirs(new_temp_path)    
    asgn_folder_path = os.path.join(new_temp_path, asgn_name)        
    
    groups_ready = []
    for s in stds:
        user_group = get_user_assignment_group(db, asgn_info, s.id)
        if user_group is None or user_group['id'] not in groups_ready:            
            groups_ready.append(user_group['id'] if user_group is not None else s.id)
            gr = assignment_group_result(db, asgn_info, s.id, user_group)
            group_base_path = os.path.join(asgn_folder_path, gr['name'])
            if not os.path.exists(group_base_path):
                os.makedirs(group_base_path)
            
            for file in [f for f in gr['files'] if f['available']]:
                file_dest = os.path.join(group_base_path, file['original_filename'])
                file_src = os.path.join(request.folder, 'uploads', file['file'])                                
                shutil.copyfile(file_src, file_dest)
    
    shutil.make_archive(zip_file_path, 'zip', new_temp_path)
    
    return zip_file_path + '.zip'