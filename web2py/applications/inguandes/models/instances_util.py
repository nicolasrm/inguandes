# -*- coding: utf-8 -*-

def get_instances(db):
    count = db.section.id.count()
    instances = db().select(db.instance.ALL, 
                            count,
                            left=db.section.on(db.instance.id == db.section.instance),
                            groupby=db.instance.ALL,
                            orderby=db.instance.title)
    instances_a = []
    for c in instances:
        inst = dict(id = c.instance.id,
                    title = c.instance.title,
                    sections = c[count]
                    )
        instances_a.append(inst)
    return instances_a
    
def get_instance_content(db, instanceId):
    files = db((db.content_file.content_group == db.content_group.id) & (db.content_group.instance == instanceId)).select(db.content_file.ALL)
    videos = db((db.content_video.content_group == db.content_group.id) & (db.content_group.instance == instanceId)).select(db.content_video.ALL)
    links = db((db.content_link.content_group == db.content_group.id) & (db.content_group.instance == instanceId)).select(db.content_link.ALL)    
    
    contents = {}
    add_organized_content(files, ['id', 'name', 'description'], 'file', 'file', 'file', {'_target':'_blank'}, contents, URL('instance', 'download_content_file'))
    add_organized_content(videos, ['id', 'name', 'url', 'description'], 'video', 'facetime-video', None, None, contents)
    add_organized_content(links, ['id', 'name', 'url', 'description'], 'link', 'bookmark', 'url', {'_target':'_blank'}, contents)
                
    return contents
    
def add_organized_content(list, cols, type, icon, col_href, a_attrs, contents, preHref=None):
    if a_attrs is None:
        a_attrs = {}
    
    for c in list:
        c_cg = c['content_group']
        if c_cg not in contents:
            contents[c_cg] = {}
            contents[c_cg]['required'] = []
            contents[c_cg]['optional'] = []
        
        obj = {}
        obj['icon'] = icon
        obj['a_attrs'] = a_attrs.copy()
        obj['a_attrs']['_data-content-type'] = type
        obj['a_attrs']['_data-icon'] = icon
        obj['a_attrs']['_data-content-required'] = 'T' if c['is_required'] else 'F'
        
        if col_href is not None:
            obj['href'] = c[col_href] if preHref is None else preHref + '/' + c[col_href]
        else:
            obj['href'] = '#'
        for col in cols:
            obj[col] = c[col]
            obj['a_attrs']['_data-content-' + col] = obj[col]
            
        if c['is_required']:
            contents[c_cg]['required'].append(obj)
        else:
            contents[c_cg]['optional'].append(obj)

def get_instance_professors(db, instanceId):
    pfs = db((db.section.instance == instanceId) & (db.user_section.section == db.section.id) & (db.auth_user.id == db.user_section.the_user) & (db.user_section.the_role == 3)).select(db.auth_user.id, db.auth_user.first_name, db.auth_user.last_name)
    return pfs
            
def get_instance_info(db, instanceId):
    inst = db.instance[instanceId]
    pfs = get_instance_professors(db, instanceId)
    
    inst_info = {}
    inst_info['id'] = inst.id
    inst_info['title'] = inst.title
    inst_info['professors'] = pfs
    
    return inst_info
    
def get_user_instances(db, userId):
    u_insts = db((db.user_section.the_user == userId) & (db.user_section.section == db.section.id) & (db.section.instance == db.instance.id)).select(db.instance.ALL)
    u_insts_info = [get_instance_info(db, inst.id) for inst in u_insts]
    return u_insts_info
    
def get_user_role(db, instanceId, userId):
    u_role = db((db.user_section.the_user == userId) & (db.user_section.section == db.section.id) & (db.section.instance == instanceId)).select(db.user_section.the_role).first()
    return u_role.the_role if u_role is not None else None

def get_user_tasks(db, instanceId, userId):
    u_qzs = get_quizzes(db, instanceId, userId)
    u_asgs = get_assignments(db, instanceId, userId)
    
    u_tasks = u_qzs
    for (k,v) in u_asgs.iteritems():
        if k in u_tasks:
            u_tasks[k] = u_tasks[k] + v
        else:
            u_tasks[k] = v
            
    return u_tasks
    
def log_user_content(db, user, content_type, content_id):
    db.content_log.insert(  the_user=user,
                            content_type=content_type,
                            content_id=content_id)
    
def get_instance_ticket_categories(instanceId):
    categories = db(db.ticket_category_index.instance==instanceId).select(db.ticket_category_index.id, db.ticket_category_index.name).as_list()
    cats = [c['name'] for c in categories]
    return cats, categories
    
def get_instance_sections(db, instanceId):
    return db(db.section.instance==instanceId).select(orderby=db.section.nrc)

def get_user_student_instances(db, user_id, only_active=True):
    return db.executesql('SELECT DISTINCT i.* FROM instance i, section s, user_section us, term t WHERE us.the_user='+str(user_id)+
    ' AND us.the_role=0 AND us.section=s.id AND s.instance=i.id' + ' AND s.term=t.id AND t.starting <= NOW() AND t.ending>= NOW();' if only_active else ';', as_dict=True)

def get_instance_news(db, instanceId):
    return db(db.instance_new.instance == instanceId).select(orderby=~db.instance_new.created_on)
    
def get_instance_moderators(db, instanceId):
    return db.executesql('SELECT DISTINCT au.id, au.email FROM section s, user_section us, auth_user au WHERE s.instance='+str(instanceId)+
    ' AND s.id=us.section AND us.the_role > 1 AND us.the_user=au.id ORDER BY 2;', as_dict=True)