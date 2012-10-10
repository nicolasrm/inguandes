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
auth.settings.actions_disabled = ['change_password']
auth.settings.login_methods.append(email_auth("smtp.gmail.com:587", "@miuandes.cl"))

auth.settings.extra_fields[auth.settings.table_user_name] = [Field('rut', type='string')]

## create all tables needed by auth if not custom tables
auth.define_tables()

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
        Field('email', type='string'),
        Field('course', type=db.course),
        Field('term', type=db.term),        
        Field('instance', type=db.instance),
        )
        
db.define_table('user_section',
        Field('the_user', type=db.auth_user),
        Field('section', type=db.section),
        Field('the_role', type='integer', requires=IS_IN_SET(user_roles))
        )
        
########## Instance content ##########
        
db.define_table('content_group',
        Field('title', type='string'),
        Field('instance', type=db.instance)
        )
        
db.define_table('content_file',
        Field('name', type='string'),
        Field('is_required', type='boolean'),
        Field('file', type='upload'),
        Field('content_group', type=db.content_group),
        Field('description', type='text')
        )
        
db.define_table('content_video',
        Field('name', type='string'),
        Field('is_required', type='boolean'),
        Field('url', type='string'),
        Field('content_group', type=db.content_group),
        Field('description', type='text')
        )
        
db.define_table('content_link',
        Field('name', type='string'),
        Field('is_required', type='boolean'),
        Field('url', type='string'),
        Field('content_group', type=db.content_group),
        Field('description', type='text')
        )
        
db.define_table('instance_link',
        Field('icon', type='string'),
        Field('url', type='string'),
        Field('instance', type=db.instance),
        Field('description', type='text')
        )
        
db.define_table('instance_grade_link',
        Field('description', type='string'),
        Field('url', type='string'),
        Field('instance', type=db.instance),        
        )
        
db.define_table('group_list',
        Field('name', type='string'),
        Field('instance', type=db.instance)
        )
        
db.define_table('student_group',
        Field('student', type=db.auth_user),
        Field('group_id', type='integer'),
        Field('group_list', type=db.group_list)
        )
        
db.define_table('content_log',
        Field('the_user', type=db.auth_user),
        Field('content_type', type='string'),
        Field('content_id', type='integer'),
        Field('created_on', type='datetime', default=request.now),
        Field('request_ip', type='string', default=request.env["remote_addr"])
        )
        
db.define_table('instance_new',
        Field('title', type='string'),
        Field('content', type='text'),
        Field('creator', type=db.auth_user),
        Field('created_on', type='datetime', default=request.now),
        Field('instance', type=db.instance)
        )

########## Questions & Quizzes ##########
db.define_table('question',
        Field('text', type='text'),
        Field('category', type='string'),
        Field('time', type='integer'),
        Field('course', type=db.course)
        )
        
db.define_table('question_alternative',
        Field('text', type='text'),
        Field('is_correct', type='boolean'),        
        Field('question', type=db.question)
        )
        
db.define_table('quiz',
        Field('name', type='string'),
        Field('starting', type='datetime'),
        Field('ending', type='datetime'),
        Field('discount_val', type='integer', default=0),
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
        Field('answer_on', type='datetime'),
        Field('request_ip', type='string', default=request.env["remote_addr"])
        )

########## Assignments ##########
file_size_options = {
    0: '500 KB',
    1: '1 MB',
    2: '5 MB',
    3: '10 MB',
    4: '50 MB'
}

file_size_options_kb = {
    0: '500',
    1: '1024',
    2: '5120',
    3: '10240',
    4: '51200'
}

db.define_table('group_evaluation',
        Field('ending', type='datetime'),
        Field('include_myself', type='boolean'),
        Field('distribute_all', type='boolean'),
        Field('total_points', type='integer'),
        Field('max_individual_points', type='integer'),
        )
        
db.define_table('user_group_evaluation',
        Field('group_evaluation', type=db.group_evaluation),
        Field('evaluator', type=db.auth_user),
        Field('the_user', type=db.auth_user),
        Field('score', type='integer'),
        Field('created_on', type='datetime', default=request.now),
        )

db.define_table('assignment',
        Field('name', type='string', requires=IS_NOT_EMPTY()),
        Field('starting', type='datetime'),
        Field('ending', type='datetime'),
        Field('instance', type=db.instance, notnull=True),
        Field('file_types', type='string'),
        Field('multiple', type='boolean', default=False),
        Field('max_size', type='integer', requires=IS_IN_SET(file_size_options)),
        Field('in_groups', type='boolean', default=False),
        Field('group_list', type=db.group_list),
        Field('group_evaluation', type=db.group_evaluation),
        )

db.define_table('assignment_section',
        Field('assignment', type=db.assignment, notnull=True),
        Field('section', type=db.section, notnull=True),
        Field('starting', type='datetime'),
        Field('ending', type='datetime'),
        )

db.define_table('assignment_file',
        Field('assignment', type=db.assignment),
        Field('created_on', type='datetime', default=request.now),
        Field('original_filename', type='string'),
        Field('file', type='upload')
        )        
        
db.define_table('user_assignment_file',
        Field('the_user', type=db.auth_user),
        Field('assignment', type=db.assignment),
        Field('created_on', type='datetime', default=request.now),
        Field('original_filename', type='string'),
        Field('file', type='upload'),
        Field('available', type='boolean', default=True),
        Field('request_ip', type='string', default=request.env["remote_addr"])
        )
        
db.define_table('download_file_log',
        Field('the_user', type=db.auth_user),
        Field('assignment_file', type=db.user_assignment_file),
        Field('created_on', type='datetime', default=request.now),
        Field('request_ip', type='string', default=request.env["remote_addr"])
        )

########## Log ##########
db.define_table('action_log',
        Field('the_user', type=db.auth_user),
        Field('table_name', type='string'),
        Field('element_id', type='integer'),
        Field('action', type='string'),
        Field('created_on', type='datetime', default=request.now),
        Field('request_ip', type='string', default=request.env["remote_addr"])
        )

########## Forum ##########
db.define_table('forum_topic',
        Field('instance', type=db.instance),
        Field('name', type='string'),
        Field('available', type='boolean', default=True)
        )
        
db.define_table('forum_thread',
        Field('forum_topic', type=db.forum_topic),
        Field('title', type='string'),
        Field('content', type='text'),
        Field('the_user', type=db.auth_user),
        Field('open', type='boolean', default=True),
        Field('available', type='boolean', default=True),
        Field('created_on', type='datetime', default=request.now),
        Field('request_ip', type='string', default=request.env["remote_addr"])
        )
        
db.define_table('forum_post',
        Field('forum_thread', type=db.forum_thread),
        Field('content', type='text'),
        Field('the_user', type=db.auth_user),
        Field('best_answer', type='boolean', default=False),
        Field('available', type='boolean', default=True),
        Field('created_on', type='datetime', default=request.now),        
        Field('request_ip', type='string', default=request.env["remote_addr"])
        )
        
db.define_table('forum_visit',
        Field('instance', type=db.instance),
        Field('the_user', type=db.auth_user),
        Field('visited_on', type='datetime', default=request.now),
        Field('request_ip', type='string', default=request.env["remote_addr"])
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

####### Practice ############
practice_category = {
    0: 'Práctica de Operario',
    1: 'Trabajo en la Empresa I',
    2: 'Trabajo en la Empresa II',
}

db.define_table('company',
        Field('rut', type='string', notnull=True),
        Field('name', type='string', notnull=True),
        Field('businessLine', type='string', notnull=True),
        Field('address', type='text', notnull=True),
        Field('city', type='string', notnull=True),
        Field('country', type='string', notnull=True)
        )
        
db.define_table('company_employee',        
        Field('company', type=db.company, notnull=True),
        Field('first_name', type='string', notnull=True),
        Field('last_name', type='string', notnull=True),
        Field('position', type='string', notnull=True),
        Field('department', type='string', notnull=True),
        Field('phone', type='string', notnull=True),
        Field('email', type='string', notnull=True)
        )
        
db.define_table('practice',
        Field('the_user', type=db.auth_user, notnull=True),
        Field('company', type=db.company),
        Field('validator', type=db.company),
        Field('category', type='integer', requires=IS_IN_SET(practice_category)),
        Field('starting', type='datetime'),
        Field('ending', type='datetime'),
        Field('description', type='text'),
        Field('created', type='datetime', default=request.now),
        )
        
####### Constants ############
datetime_format = '%d-%m-%Y %H:%M'