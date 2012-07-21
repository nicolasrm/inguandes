# -*- coding: utf-8 -*-
import datetime
import random

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
    asgn_info['file_types'] = cAsgn.file_types
    asgn_info['multiple'] = cAsgn.multiple
    asgn_info['instance'] = cAsgn.instance.title
    asgn_info['instance_id'] = cAsgn.instance
    
    return asgn_info