# -*- coding: utf-8 -*-

## if SSL/HTTPS is properly configured and you want all HTTP requests to
## be redirected to HTTPS, uncomment the line below:
# request.requires_https()

db = DAL(settings.database_uri)

## by default give a view/generic.extension to all actions from localhost
## none otherwise. a pattern can be 'controller/function.extension'
response.generic_patterns = ['*'] if request.is_local else []
## (optional) optimize handling of static files
# response.optimize_css = 'concat,minify,inline'
# response.optimize_js = 'concat,minify,inline'

## Inicializar módulo de autentificación de web2py
from gluon.tools import Auth, Crud, Service, PluginManager, prettydate
auth = Auth(db, hmac_key=Auth.get_or_create_key())
crud, service, plugins = Crud(db), Service(), PluginManager()

## Forzar a usar versión localizada en español de todos los strings
T.force('es-es')

## create all tables needed by auth if not custom tables
auth.define_tables()

## configure email
mail=auth.settings.mailer
mail.settings.server = settings.email_server
mail.settings.sender = settings.email_sender
mail.settings.login = settings.email_login

## configure auth policy
auth.settings.registration_requires_verification = False
auth.settings.registration_requires_approval = False
auth.settings.reset_password_requires_verification = True

# Use miuandes as authentification
from gluon.contrib.login_methods.email_auth import email_auth
auth.settings.actions_disabled = ['register','change_password','request_reset_password']
auth.settings.login_methods = [email_auth("smtp.gmail.com:587", "@miuandes.cl")]

user_roles = {    
    0: 'Estudiante',
    1: 'Ayudante',
    2: 'Ayudante Jefe',
    3: 'Profesor'
}

db.define_table('course',
        Field('code', type='string', notnull=True),
        Field('name', type='string', notnull=True)
        )
        
db.define_table('term',
        Field('name', type='string'),
        Field('starting', type='date'),
        Field('ending', type='date')
        )

db.define_table('instance',
        Field('title', type='string')
        )
        
db.define_table('section',
        Field('nrc', type='integer'),
        Field('course', type=db.course),
        Field('term', type=db.term),
        Field('instance', type=db.instance),
        )
        
db.define_table('user_section',
        Field('the_user', type=db.auth_user),
        Field('section', type=db.section),
        Field('the_role', type='integer', requires=IS_IN_SET(user_roles))
        )
        
db.define_table('content_group',
        Field('title', type='string'),
        Field('instance', type=db.instance)
        )
        
db.define_table('content_file',
        Field('name', type='string'),
        Field('is_required', type='boolean'),
        Field('file', type='upload'),
        Field('content_group', type=db.content_group)
        )
        
db.define_table('content_video',
        Field('name', type='string'),
        Field('is_required', type='boolean'),
        Field('url', type='string'),
        Field('content_group', type=db.content_group)
        )
        
db.define_table('content_link',
        Field('name', type='string'),
        Field('is_required', type='boolean'),
        Field('url', type='string'),
        Field('content_group', type=db.content_group)
        )

########## Questions & Quizzes ##########
db.define_table('question',
        Field('text', type='text'),
        Field('category', type='string'),
        Field('course', type=db.course)
        )
        
db.define_table('question_alternative',
        Field('text', type='text'),
        Field('is_correct', type='boolean'),
        Field('question', type=db.question)
        )
        
db.define_table('quiz',
        Field('name', type='string'),
        Field('starting', type='date'),
        Field('ending', type='date'),
        Field('instance', type=db.instance)
        )
        
db.define_table('quiz_category',
        Field('category', type='string'),
        Field('count', type='integer'),
        Field('quiz', type=db.quiz)
        )
        
db.define_table('user_quiz',
        Field('the_user', type=db.auth_user),
        Field('quiz', type=db.quiz),
        Field('started_on', type='datetime', default=request.now)
        )
        
db.define_table('user_quiz_question',
        Field('user_quiz', type=db.user_quiz),
        Field('question', type=db.question),
        Field('alternative', type=db.question_alternative),
        Field('started_on', type='datetime'),
        Field('answer_on', type='datetime')
        )

########## Assignments ##########
db.define_table('assignment',
        Field('name', type='string', requires=IS_NOT_EMPTY()),
        Field('starting', type='date'),
        Field('ending', type='date'),
        Field('instance', type=db.instance, notnull=True),
        Field('file_types', type='string'),
        Field('multiple', type='boolean', default=False),
        )   
        
########## Tickets ##########

ticket_status = {
    0: 'Cerrado',
    1: 'Pendiente',
    2: 'Rechazado',
    3: 'Re-abierto',
    4: 'En trámite',
    5: 'Apelado'
}

db.define_table('ticket_category_index',
        Field('name', type='string', requires=IS_NOT_EMPTY()),
        Field('instance', type=db.instance, notnull=True)
        )

db.define_table('section_ticket_subcategory',
        Field('the_section', type=db.section, notnull=True),
        Field('opening', type='datetime', default=request.now),
        Field('closing', type='datetime'),
        Field('moderator', type=db.auth_user, notnull=True)
        )

db.define_table('ticket_subcategory',
        Field('name', type='string', requires=IS_NOT_EMPTY()),
        Field('multiple', type='boolean', default=False),
        Field('is_appealable', type='boolean', default=True),
        Field('index', type=db.ticket_category_index, notnull=True),
        Field('sections_config', type='list:reference section_ticket_subcategory', notnull=True)
        )

db.define_table('ticket',
        Field('the_status', type='integer', requires=IS_IN_SET(ticket_status)),
        Field('author', type=db.auth_user, notnull=True),
        Field('responsible', type=db.auth_user, notnull=True),
        Field('description', type='text', requires=IS_NOT_EMPTY()),
        Field('created', type='datetime', default=request.now),
        Field('updated', type='datetime', default=request.now, update=request.now)
        )

db.define_table('message',
        Field('ticket', type=db.ticket, notnull=True),
        Field('author', type=db.auth_user, notnull=True),
        Field('the_message', type='text', requires=IS_NOT_EMPTY()),
        Field('created', type='datetime', default=request.now),
        Field('prev_status', type='integer', requires=IS_IN_SET(ticket_status)),
        Field('next_status', type='integer', requires=IS_IN_SET(ticket_status))
        )