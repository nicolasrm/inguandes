# -*- coding: utf-8 -*-

import datetime
from gluon.contrib.populate import populate
from gluon.utils import hmac_hash
import random

# Create courses
courses_id = {}
if not db(db.course).count():
    courses = { 'ING4130':'Bases de Datos Aplicadas',
                'ING1310':'Introducción a la Computación'}
                
    for (k,v) in courses.iteritems():
        id = db.course.insert(  code=k,
                                name=v)
        courses_id[k] = id

# Create questions
if not db(db.question).count():
    questions = [   '¿Pregunta simple?',
                    '¿Una pregunta más larga y con <b>énfasis</b>?',
                    '<p>Una pregunta mas compleja, que usa una tabla</p><table><tr><th>Id</th><th>Nombre</th><th>Edad</th></tr><tr><td>1</td><td>Juan</td><td>35</td></tr><tr><td>2</td><td>María</td><td>28</td></tr><tr><td>3</td><td>Juan Pablo</td><td>31</td></tr></table>',
                    '¿Otra pregunta no tan compleja?',
                    'Una pregunta que prueba las listas <ul><li>Bla 1</li><li>Bla 2</li><li>Bla bla 3</li></ul>']
    base_text = "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Quisque ut commodo augue. Aenean quis risus a nunc aliquet faucibus imperdiet vitae mauris. Maecenas eu orci bibendum enim tempor ornare. Vestibulum facilisis tellus eu leo lacinia vestibulum. Class aptent taciti sociosqu ad litora torquent per conubia nostra, per inceptos himenaeos. Donec sed nibh erat. Morbi bibendum mattis sodales. Aenean faucibus, turpis ac aliquet suscipit, velit sem dictum justo, a semper purus nisl sed est. Nullam porttitor consectetur libero sed dictum. Proin posuere laoreet felis vitae scelerisque. Duis ante dolor, imperdiet quis aliquam vel, congue quis velit. Quisque arcu est, aliquet et tempus id, faucibus sed risus. Nunc commodo justo a lorem congue sit amet ullamcorper velit euismod. Nunc et ante quis erat tincidunt suscipit a euismod odio"
    categories = ['una categoria', 'categoria otra', 'la-categoria']
    for q in questions:
        q_id = db.question.insert(  text=q,
                                    category=categories[random.randint(0, len(categories)-1)],
                                    course=courses_id['ING4130'])
        # Create random alternatives
        for i in range(0, random.randint(2,5)):
            start_idx = random.randint(0,len(base_text)/2)
            alt_text = base_text[start_idx:random.randint(start_idx + 10, len(base_text))]
            db.question_alternative.insert( text=alt_text,
                                            is_correct=True if i==0 else False,
                                            question=q_id)

# Create terms
terms_id = {}
if not db(db.term).count():
    terms_id['201202'] = db.term.insert(name='201202',
                                        starting='2012-07-30',
                                        ending='2012-12-15')
    terms_id['201203'] = db.term.insert(name='201203',
                                        starting='2012-12-10',
                                        ending='2013-01-30')
                                        
# Create instances
instances_id = []
if not db(db.instance).count():
    instances = ['Bases de Datos Aplicadas 201202', 'Introducción a la Computación 201202', 'Introducción a la Computación 201203']
    for inst in instances:
        id = db.instance.insert(title=inst)
        instances_id.append(id)
        
# Create sections
sections_id = []
if not db(db.section).count():
    sections = [[111,courses_id['ING4130'],terms_id['201202'],instances_id[0]],
                [222,courses_id['ING1310'],terms_id['201202'],instances_id[1]],
                [333,courses_id['ING1310'],terms_id['201202'],instances_id[1]],
                [444,courses_id['ING1310'],terms_id['201202'],instances_id[1]],
                [555,courses_id['ING1310'],terms_id['201203'],instances_id[2]]
                ]
    for s in sections:
        id = db.section.insert( nrc=s[0],
                                course=s[1],
                                term=s[2],
                                instance=s[3])
        sections_id.append(id)

# Basic setup instance 0 - 'Bases de Datos Aplicadas 201202'
if not db(db.content_group).count():
    # Create content groups
    cgs_id = []
    cgs = ['Entidad-Relación', 'Modelo Relacional', 'Normalización', 'Álgebra Relacional', 'SQL']
    for cg in cgs:
        id = db.content_group.insert(   title=cg,
                                        instance=instances_id[0])
        cgs_id.append(id)        
    # Add some elements to content group
    c_videos = [['Video 1',True,'http://www.youtube.com/embed/xSPyT6q-_4I',cgs_id[0], 'Video 1 muy interesante, ver completo'],
                ['Video 2',True,'http://www.youtube.com/embed/pazq09wpxAM',cgs_id[0], ''],
                ['Video 3',False,'http://www.youtube.com/embed/_U1uMWzQcIM',cgs_id[0], 'Video 3 muy interesante, ver completo'],
                ['Un video con un texto mas largo que los otros 4',True,'http://www.youtube.com/embed/zNf4lB_GIU0',cgs_id[0], 'Video 4 muy interesante, ver completo'],
                ['Video 5',False,'http://www.youtube.com/embed/ue0iiJSx7d0',cgs_id[1], None],
                ['Video 6',False,'http://www.youtube.com/embed/ndq6SVtW3TU',cgs_id[1], 'Video 1 muy interesante, ver completo'],
                ['Video 7',True,'http://www.youtube.com/embed/R6zRWmRakSI',cgs_id[1]], None]
    for v in c_videos:
        db.content_video.insert(name=v[0],
                                is_required=v[1],
                                url=v[2],
                                content_group=v[3],
                                description=v[4])
    
    c_links = [ ['Link 1',True,'https://twitter.com/',cgs_id[0]],
                ['Un link más grande que los anteriores 2',False,'http://www.latercera.com/',cgs_id[0]],
                ['Link 3',True,'http://www.emol.com/',cgs_id[0]],
                ['Link 4',False,'http://www.marca.es/',cgs_id[1]],
                ['Link 5',False,'http://www.fayerwayer.com/cl/',cgs_id[1]]]
    for l in c_links:
        db.content_link.insert( name=l[0],
                                is_required=l[1],
                                url=l[2],
                                content_group=l[3])
                                
    # TODO: create quiz        
    quiz_id = db.quiz.insert(name='Quiz 1',
                             starting='2012-07-17',
                             ending='2012-07-24',
                             instance=instances_id[0])   
    quiz_cats = {'una categoria': 2, 
                 'categoria otra': 3, 
                 'la-categoria': 2}
    for (k,v) in quiz_cats.iteritems():
        db.quiz_category.insert(category=k,
                                count=v,
                                quiz=quiz_id)