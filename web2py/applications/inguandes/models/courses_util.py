# -*- coding: utf-8 -*-

def get_courses(db):
    count = db.section.id.count()
    courses = db().select(  db.course.ALL, 
                            count,
                            left=db.section.on(db.course.id == db.section.course),
                            groupby=db.course.ALL,
                            orderby=db.course.name)
    courses_a = []
    for c in courses:
        course = dict(  id = c.course.id,
                        code = c.course.code,
                        name = c.course.name,
                        sections = c[count]
                        )
        courses_a.append(course)
    return courses_a