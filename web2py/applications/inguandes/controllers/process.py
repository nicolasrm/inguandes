# -*- coding: utf-8 -*-
@auth.requires_membership(role='ing-admin')   
def periods():
    selected_state = request.vars.state
    if selected_state is None:
        selected_state = 'open'
        
    periods = get_periods_by_state(db, selected_state)
    
    return dict(selected_state=selected_state, periods=periods)
    
@auth.requires_membership(role='ing-admin')
def add_period():
    db.process_period.insert(   process=request.vars.process,
                                starting=request.vars.starting,
                                ending=request.vars.ending)

    redirect(URL('periods'))
