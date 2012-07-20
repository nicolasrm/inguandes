# -*- coding: utf-8 -*-
#import courses_util

##############################################################################
### CRUD term
def view_terms():
    terms = db().select(db.term.ALL, orderby=db.term.starting)
    return dict(terms=terms)
    
def add_term():
    if request.vars.name is not None and request.vars.starting is not None and request.vars.ending is not None:
        db.term.insert( name=request.vars.name,
                            starting=request.vars.starting,
                            ending=request.vars.ending)
    redirect(URL('view_terms'))
    
def edit_term():
    if request.vars.termid is not None and request.vars.name is not None and request.vars.starting is not None and request.vars.ending is not None:
        termId = int(request.vars.termid)        
        db.term[termId].update_record(   name=request.vars.name,
                                            starting=request.vars.starting,
                                            ending=request.vars.ending)
    redirect(URL('view_terms'))
    
def delete_term():
    if request.vars.termid is not None:
        termId = int(request.vars.termid)    
        del db.term[termId]
    redirect(URL('view_terms'))
    
##############################################################################

##############################################################################
### CRUD courses 
    
def view_courses():
    #courses = courses_util.get_courses()
    courses = get_courses(db)
    return dict(courses=courses)
    
def add_course():
    if request.vars.code is not None and request.vars.name is not None:
        db.course.insert(   name=request.vars.name,
                            code=request.vars.code)
    redirect(URL('view_courses'))
    
def edit_course():
    if request.vars.courseid is not None and request.vars.name is not None and request.vars.code:
        courseId = int(request.vars.courseid)    
        db.course[courseId].update_record(  name=request.vars.name,
                                            code=request.vars.code)
    redirect(URL('view_courses'))
    
def delete_course():
    if request.vars.courseid is not None:
        courseId = int(request.vars.courseid)
        del db.course[courseId]
    redirect(URL('view_courses'))
    
##############################################################################

##############################################################################
### CRUD sections

def view_sections(): 
    if len(request.args) == 0:
        redirect(URL('view_courses'))
    
    courseId = int(request.args[0])
    course = db.course[courseId]
    courseTitle = course.code + "-" + course.name
    
    sections = get_sections(db, courseId)
    
    terms = db().select(db.term.ALL)
    
    return dict(course=course, courseTitle=courseTitle, sections=sections, terms=terms)

def add_section():
    courseId = int(request.vars.courseid)
    if request.vars.nrc is not None and request.vars.term is not None:
        db.section.insert(  nrc=int(request.vars.nrc),
                            term=request.vars.term,
                            course=courseId
                            )
    redirect(URL('view_sections', args=[courseId]))
    
def edit_section():
    courseId = int(request.vars.courseid)
    if request.vars.nrc is not None and request.vars.term is not None:
        sectionId = int(request.vars.sectionid)    
        db.section[sectionId].update_record(nrc=int(request.vars.nrc),
                                            term=request.vars.term)
    redirect(URL('view_sections', args=[courseId]))
    
def delete_section():
    courseId = int(request.vars.courseid)
    if request.vars.courseid is not None:
        sectionId = int(request.vars.sectionid)    
        del db.section[sectionId]
    redirect(URL('view_sections', args=[courseId]))
    
##############################################################################

##############################################################################
### CRUD user_section

def add_relation():
    courseId = int(request.vars.courseid)
    if request.vars.user_email is not None and request.vars.user_role is not None:
        sectionId = int(request.vars.sectionid)
        user = db(db.auth_user.email==request.vars.user_email).select().first()
        if user is not None:
            db.user_section.insert( section=sectionId,
                                    the_user=user,
                                    the_role=request.vars.user_role
                                    )
        else:
            session.flash = "Usuario con email {0} no existe".format(request.vars.user_email)
    redirect(URL('view_sections', args=[courseId]))
    
##############################################################################

##############################################################################
### CRUD instances

def view_instances():    
    instances = get_instances(db)
    sections = get_sections(db)
    return dict(instances=instances, sections=sections)
    
def add_instance():
    if request.vars.title is not None:
        db.instance.insert( title=request.vars.title)
    redirect(URL('view_instances'))
    
def delete_instance():
    if request.vars.instanceid is not None:
        instanceidId = int(request.vars.instanceid)
        del db.instance[instanceidId]
    redirect(URL('view_instances'))
    
def add_instance_relation():    
    if request.vars.section is not None:
        instanceId = int(request.vars.instanceid)
        sectionId = int(request.vars.section)
        db.section[sectionId].update_record(instance=instanceId)
        
    redirect(URL('view_instances'))