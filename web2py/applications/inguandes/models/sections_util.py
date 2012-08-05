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
        section['students'] = db((db.user_section.section==s.section.id) & (db.user_section.the_role==0)).count()
        section['assistants'] = db((db.user_section.section==s.section.id) & (db.user_section.the_role==1)).count()
        section['assistants_boss'] = db((db.user_section.section==s.section.id) & (db.user_section.the_role==2)).count()
        section['professors'] = db((db.user_section.section==s.section.id) & (db.user_section.the_role==3)).count()
        sections_a.append(section)
    return sections_a