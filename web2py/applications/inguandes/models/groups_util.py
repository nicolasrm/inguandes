# -*- coding: utf-8 -*-
import datetime
import random
import math

def get_group_lists(db, instance_id):
    return db(db.group_list.instance == instance_id).select()
    
def get_grouplist_info(db, gl_id):
    gl = db.group_list[gl_id]
    cg = db.student_group.group_id.count()
    groups = db(db.student_group.group_list == gl_id).select(db.student_group.group_id, cg, groupby=(db.student_group.group_id), distinct=True)
    
    miss_stds = db.executesql('SELECT a.id, a.first_name, a.last_name FROM section s, user_section us, auth_user a WHERE s.instance = ' + str(gl.instance) + ' and us.section = s.id and a.id = us.the_user and us.the_role = 0 and a.id NOT IN (SELECT sg.student FROM student_group sg WHERE sg.group_list = ' + str(gl_id) + ');', as_dict=True)
    
    gl_info = {}
    gl_info['id'] = gl.id
    gl_info['name'] = gl.name
    gl_info['miss_students'] = miss_stds
    gl_info['groups'] = [(g.student_group.group_id, g[cg]) for g in groups]
    gl_info['instance'] = gl.instance
    
    return gl_info
    
def max_group_number(db, gl_id):    
    nmax = db.student_group.group_id.max()
    rmax = db(db.student_group.group_list == gl_id).select(nmax).first()
    
    return rmax[nmax] if rmax is not None and rmax[nmax] is not None else 0
    
def get_group_info(db, gl_id, g_id):
    stds = db((db.student_group.group_list == gl_id) & (db.student_group.group_id == g_id) & (db.student_group.student == db.auth_user.id)).select(db.auth_user.id, db.auth_user.first_name, db.auth_user.last_name, db.auth_user.email)
    
    g_info = {}
    g_info['id'] = g_id
    g_info['students'] = stds
    
    return g_info
    
def get_user_group(db, gl_id, user_id):
    gr = db((db.student_group.student == user_id) & (db.student_group.group_list == gl_id)).select(db.student_group.group_id).first()    
    return get_group_info(db, gl_id, gr.group_id) if gr is not None else None
    
def generate_random_groups(db, gl_info, size, adjust_option):
    # remove previos groups
    db(db.student_group.group_list == gl_info['id']).delete()
    
    stds = get_instance_users_by_role(db, gl_info['instance'], 0)
    stds_ids = [s.id for s in stds]
    print stds_ids
    rdm_stds = []
    while len(stds_ids) > 0:
        rdm = random.randint(0, len(stds_ids) - 1)
        rdm_stds.append(stds_ids[rdm])
        del stds_ids[rdm]
        
    # create groups
    g_count = int(math.floor(len(rdm_stds)/size))
    o_count = 0
    stds_remaining = len(rdm_stds) - g_count*size
    
    if adjust_option == 'smaller' and stds_remaining > 0:
        r = (size - 1) - stds_remaining
        g_count = g_count - r
        o_count = 1 + r
        
    for i in range(1, g_count + 1):
        for a in range(size):
            db.student_group.insert(student=rdm_stds.pop(),
                                    group_id=i,
                                    group_list=gl_info['id'])
                                    
    if adjust_option == 'smaller' and stds_remaining > 0:
        for i in range(g_count + 1, g_count + 1 + o_count):
            for a in range(size - 1):
                db.student_group.insert(student=rdm_stds.pop(),
                                        group_id=i,
                                        group_list=gl_info['id'])
    elif adjust_option == 'bigger' and stds_remaining > 0:
        for i in range(1, stds_remaining + 1):
            db.student_group.insert(student=rdm_stds.pop(),
                                    group_id=i,
                                    group_list=gl_info['id'])
    
