# -*- coding: utf-8 -*-
import datetime
import random

def get_group_lists(db, instance_id):
    return db(db.group_list.instance == instance_id).select()
    
def get_grouplist_info(db, gl_id):
    gl = db.group_list[gl_id]
    
    stds = db(  (db.section.instance == gl.instance) & 
                (db.user_section.section == db.section.id) & 
                (db.auth_user.id == db.user_section.the_user) & 
                (db.user_section.the_role == 0)).select(db.auth_user.first_name, db.auth_user.last_name, db.auth_user.email, orderby=(db.auth_user.last_name, db.auth_user.first_name))
    
    gl_info = {}
    gl_info['id'] = gl.id
    gl_info['name'] = gl.name
    gl_info['miss_students'] = stds
    
    return gl_info