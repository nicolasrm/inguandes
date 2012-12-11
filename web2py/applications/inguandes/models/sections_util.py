# -*- coding: utf-8 -*-

def get_sections(db, courseid=None):    
    q = (db.section.term==db.term.id)
    if courseid is not None:
        q = (db.section.course==courseid) & (db.section.term==db.term.id)
    sections = db(q).select(db.section.ALL,
                            db.term.name,
                            orderby=~db.term.name)
    sections_a = []
    for s in sections:
        section = dict( id = s.section.id,
                        nrc = s.section.nrc,
                        term = s.section.term,
                        term_name = s.term.name
                        )
        section['students'] = db((db.user_section.section==s.section.id) & (db.user_section.the_role==0)&(db.user_section.the_user==db.auth_user.id)).select()
        section['assistants'] = db((db.user_section.section==s.section.id) & (db.user_section.the_role==1)&(db.user_section.the_user==db.auth_user.id)).select()
        section['assistants_boss'] = db((db.user_section.section==s.section.id) & (db.user_section.the_role==2)&(db.user_section.the_user==db.auth_user.id)).select()
        section['professors'] = db((db.user_section.section==s.section.id) & (db.user_section.the_role==3)&(db.user_section.the_user==db.auth_user.id)).select()
        sections_a.append(section)
    return sections_a

def get_section_info(db, sectionId):
    s = db.section[sectionId]
    s_info = {}
    s_info['id'] = s.id
    s_info['nrc'] = s.nrc
    s_info['course_id'] = s.course
    s_info['course'] = s.course.name
    s_info['instance_id'] = s.instance
    s_info['instance'] = s.instance.title
    s_info['course_code'] = s.course.code
    s_info['professors'] = get_section_professors(db, s.id)
    
    return s_info
    
def get_section_professors(db, sectionId):
    proffs = db((db.user_section.section == sectionId) & (db.user_section.the_role == 3) & (db.auth_user.id == db.user_section.the_user)).select(db.auth_user.ALL)
    profs_info = []
    for p in proffs:
        pi = {}
        pi['id'] = p.id
        pi['first_name'] = p.first_name
        pi['last_name'] = p.last_name
        pi['name'] = '{0} {1}'.format(p.first_name, p.last_name)
        pi['email'] = p.email
        
        profs_info.append(pi)
    
    return profs_info