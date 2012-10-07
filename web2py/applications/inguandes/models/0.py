# -*- coding: utf-8 -*-
# Configuraciones básicas de la plataforma.

from gluon.storage import Storage
settings = Storage()

settings.migrate = True # Deshabilitar migraciones automáticas en caso de cambio del modelo relacional
settings.title = 'IngUandes Cursos'
settings.subtitle = 'Facultad de Ingeniería y Ciencias Aplicadas'
settings.author = 'ICC'
settings.author_email = 'ing.computacion@miuandes.cl'
settings.keywords = ''
settings.description = ''
settings.layout_theme = 'Default'
settings.database_uri = 'postgres://inguandes:pRamS44hex*NoteS49rUle@localhost/inguandes'
settings.login_method = 'local'
settings.login_config = ''
settings.plugins = []
settings.email_server = 'smtp.gmail.com:587'
settings.email_sender = 'cursos@inguandes.cl'
settings.email_login = 'cursos@inguandes.cl:LarCh?reC~inLet~pepoS54'
