# -*- coding: utf-8 -*-
import datetime

@auth.requires_login()
def call():
    return service()

@auth.requires_login()
def view():
    if len(request.args) == 0:
        redirect(URL('default', 'index'))
    assignmentId = int(request.args[0])
    asgn_info = get_assignment(db, assignmentId)
            
    return dict(asgn_info=asgn_info)