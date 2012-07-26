# -*- coding: utf-8 -*-
import datetime
import random

def get_group_lists(db, instance_id):
    return db(db.group_list.instance == instance_id).select()
    
def get_grouplist_info(db, gl_id):
    gl = db.group_list[gl_id]
    
    gl_info = {}
    gl_info['id'] = gl.id
    gl_info['name'] = gl.name