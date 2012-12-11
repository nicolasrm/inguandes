# -*- coding: utf-8 -*-
#import courses_util

##############################################################################
### CRUD term
@auth.requires_membership(role='admin')
def view_terms():
    terms = db().select(db.term.ALL, orderby=db.term.starting)
    return dict(terms=terms)

@auth.requires_membership(role='admin')
def add_term():
    if request.vars.name is not None and request.vars.starting is not None and request.vars.ending is not None:
        db.term.insert( name=request.vars.name,
                            starting=request.vars.starting,
                            ending=request.vars.ending)
    redirect(URL('view_terms'))
    
@auth.requires_membership(role='admin')
def edit_term():
    if request.vars.termid is not None and request.vars.name is not None and request.vars.starting is not None and request.vars.ending is not None:
        termId = int(request.vars.termid)        
        db.term[termId].update_record(   name=request.vars.name,
                                            starting=request.vars.starting,
                                            ending=request.vars.ending)
    redirect(URL('view_terms'))
    
@auth.requires_membership(role='admin')
def delete_term():
    if request.vars.termid is not None:
        termId = int(request.vars.termid)    
        del db.term[termId]
    redirect(URL('view_terms'))
    
##############################################################################

##############################################################################
### CRUD courses 
@auth.requires_membership(role='admin')
def view_courses():
    #courses = courses_util.get_courses()
    courses = get_courses(db)
    return dict(courses=courses)
    
@auth.requires_membership(role='admin')
def add_course():
    if request.vars.code is not None and request.vars.name is not None:
        db.course.insert(   name=request.vars.name,
                            code=request.vars.code)
    redirect(URL('view_courses'))
    
@auth.requires_membership(role='admin')
def edit_course():
    if request.vars.courseid is not None and request.vars.name is not None and request.vars.code:
        courseId = int(request.vars.courseid)    
        db.course[courseId].update_record(  name=request.vars.name,
                                            code=request.vars.code)
    redirect(URL('view_courses'))
    
@auth.requires_membership(role='admin')
def delete_course():
    if request.vars.courseid is not None:
        courseId = int(request.vars.courseid)
        del db.course[courseId]
    redirect(URL('view_courses'))
    
##############################################################################

##############################################################################
### CRUD sections

@auth.requires_membership(role='admin')
def view_sections(): 
    if len(request.args) == 0:
        redirect(URL('view_courses'))
    
    courseId = int(request.args[0])
    course = db.course[courseId]
    courseTitle = course.code + "-" + course.name
    
    sections = get_sections(db, courseId)
    
    terms = db().select(db.term.ALL)
        
    return dict(the_course=course, courseTitle=courseTitle, sections=sections, terms=terms)
 
@auth.requires_membership(role='admin') 
def get_user_section():
    sectionsId = int(request.vars.sectionid)
    user = int(request.vars.typeuser)
    list_user = db((db.user_section.section==sectionsId) & (db.user_section.the_role==user)&(db.user_section.the_user==db.auth_user.id)).select().as_list()
    
    return dict(list=list_user)
    
@auth.requires_membership(role='admin')
def add_section():
    courseId = int(request.vars.courseid)
    if request.vars.nrc is not None and request.vars.term is not None:
        db.section.insert(  nrc=int(request.vars.nrc),
                            email=request.vars.email if request.vars.email is not None and len(request.vars.email.strip()) > 4 else None,
                            term=request.vars.term,                            
                            course=courseId
                            )
    redirect(URL('view_sections', args=[courseId]))
    
@auth.requires_membership(role='admin')
def edit_section():
    courseId = int(request.vars.courseid)
    if request.vars.nrc is not None and request.vars.term is not None:
        sectionId = int(request.vars.sectionid)    
        db.section[sectionId].update_record(nrc=int(request.vars.nrc),
                                            term=request.vars.term)
    redirect(URL('view_sections', args=[courseId]))
    
@auth.requires_membership(role='admin')
def delete_section():
    courseId = int(request.vars.courseid)
    if request.vars.courseid is not None:
        sectionId = int(request.vars.sectionid)    
        del db.section[sectionId]
    redirect(URL('view_sections', args=[courseId]))
    
##############################################################################

##############################################################################
### CRUD user_section

@auth.requires_membership(role='admin')
def add_relation():
    courseId = int(request.vars.courseid)
    if request.vars.user_email is not None and request.vars.user_role is not None:
        sectionId = int(request.vars.sectionid)
        user = db(db.auth_user.email==request.vars.user_email).select().first()
        if user is None:
            email = request.vars.user_email
            firstname = email[:email.find('@')]
            user = db.auth_user.insert( first_name=firstname,
                                        last_name='',
                                        email=email
                                        )
        db.user_section.insert( section=sectionId,
                                the_user=user,
                                the_role=request.vars.user_role
                                )
    redirect(URL('view_sections', args=[courseId]))

@auth.requires_membership(role='admin')
def remove_user_section():
    sectionId = int(request.vars.sectionid)
    userId = int(request.vars.userid)
    role = int(request.vars.role)
    idRelation =  db((db.user_section.the_user == userId)&(db.user_section.section == sectionId)&(db.user_section.the_role == role)).select()[0].id
    del db.user_section[idRelation]
    return 0
    
##############################################################################

##############################################################################
### CRUD instances

@auth.requires_membership(role='admin')
def view_instances():    
    instances = get_instances(db)
    sections = get_sections(db)
    return dict(instances=instances, sections=sections)
    
@auth.requires_membership(role='admin')
def add_instance():
    if request.vars.title is not None:
        db.instance.insert( title=request.vars.title)
    redirect(URL('view_instances'))
    
@auth.requires_membership(role='admin')
def delete_instance():
    if request.vars.instanceid is not None:
        instanceidId = int(request.vars.instanceid)
        del db.instance[instanceidId]
    redirect(URL('view_instances'))
    
@auth.requires_membership(role='admin')
def edit_instance():
    if request.vars.instanceid is not None:
        instanceidId = int(request.vars.instanceid)
        db.instance[instanceidId].update_record(title=request.vars.title)
    redirect(URL('view_instances'))
    
@auth.requires_membership(role='admin')
def add_instance_relation():    
    if request.vars.section is not None:
        instanceId = int(request.vars.instanceid)
        sectionId = int(request.vars.section)
        db.section[sectionId].update_record(instance=instanceId)
        
    redirect(URL('view_instances'))