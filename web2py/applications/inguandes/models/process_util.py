# -*- coding: utf-8 -*-
import datetime

def get_periods_by_state(db, state):
    now = datetime.datetime.now()
    pss = []
    if state == 'open':
        pss = db((db.process_period.starting <= now) & (db.process_period.ending > now)).select(db.process_period.id)
    elif state == 'pending':
        pss = db(db.process_period.starting > now).select(db.process_period.id)
    else:
        pss = db(db.process_period.ending <= now).select(db.process_period.id)
    
    ps_infos = [get_period(db, p.id) for p in pss]    
    return ps_infos 
    
def get_period(db, pid):
    now = datetime.datetime.now()
    period = db.process_period[pid]
    p_info = {}
    p_info['id'] = period.id
    p_info['process'] = period.process
    p_info['process_name'] = process_list[period.process]
    p_info['starting'] = period.starting
    p_info['ending'] = period.ending
    p_info['is_open'] = True if p_info['starting'] <= now and p_info['ending'] > now else False
    
    return p_info
    
def is_process_open(db, process_idx):
    now = datetime.datetime.now()
    pss = db((db.process_period.starting <= now) & (db.process_period.ending > now) & (db.process_period.process==process_idx)).select(db.process_period.id)
    if len(pss) > 0:
        return True
    else:
        return False
        
def get_current_next_period(db, process_idx):
    now = datetime.datetime.now()
    period = db((db.process_period.ending > now) & (db.process_period.process==process_idx)).select(db.process_period.id, orderby=db.process_period.ending).first()
    
    return None if period is None else get_period(db, period.id)
