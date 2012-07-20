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
    add_organized_content(files, ['id', 'name'], 'file', 'file', 'file', {'_target':'_blank'}, contents, URL('instance', 'download_content_file'))
    add_organized_content(videos, ['id', 'name', 'url'], 'video', 'facetime-video', None, None, contents)
    add_organized_content(links, ['id', 'name', 'url'], 'link', 'bookmark', 'url', {'_target':'_blank'}, contents)
            
    return contents
    
def add_organized_content(list, cols, type, icon, col_href, a_attrs, contents, preHref=None):
    for c in list:
        c_cg = c['content_group']
        if c_cg not in contents:
            contents[c_cg] = {}
            contents[c_cg]['required'] = []
            contents[c_cg]['optional'] = []
        
        if a_attrs is None:
            a_attrs = {}
        
        obj = {}
        obj['icon'] = icon
        obj['a_attrs'] = a_attrs
        obj['a_attrs']['_data-content-type'] = type
        
        if col_href is not None:
            obj['href'] = c[col_href] if preHref is None else preHref + '/' + c[col_href]
        else:
            obj['href'] = '#'
        for col in cols:
            obj[col] = c[col]
            obj['a_attrs']['_data-content-' + col] = c[col]
            
        if c['is_required']:
            contents[c_cg]['required'].append(obj)
        else:
            contents[c_cg]['optional'].append(obj)
            
def get_user_instances(db, userId):
    u_insts = db((db.user_section.the_user == userId) & (db.user_section.section == db.section.id) & (db.section.instance == db.instance.id)).select(db.instance.ALL)
    return u_insts
    
def get_user_role(db, instanceId, userId):
    u_role = db((db.user_section.the_user == userId) & (db.user_section.section == db.section.id) & (db.section.instance == instanceId)).select(db.user_section.the_role).first()
    return u_role.the_role

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
    
def get_instance_ticket_categories(instanceId):
    categories = db(db.ticket_category_index.instance==instanceId).select(db.ticket_category_index.id, db.ticket_category_index.name).as_list()
    cats = [c['name'] for c in categories]
    return cats, categories

def get_instance_sections(instanceId):
    return db(db.section.instance==instanceId).select(orderby=db.section.nrc)

def get_instance_moderators(instanceId):
    return db.executesql('SELECT DISTINCT au.id, au.email FROM section s, user_section us, auth_user au WHERE s.instance='+str(instanceId)+' AND s.id=us.section AND us.the_role > 1 AND us.the_user=au.id ORDER BY 2;', as_dict=True)
    