# -*- coding: utf-8 -*-
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import *
from reportlab.rl_config import defaultPageSize
from reportlab.lib.units import inch, mm
from reportlab.lib.enums import TA_LEFT, TA_RIGHT, TA_CENTER, TA_JUSTIFY
from reportlab.lib import colors
from pyPdf import PdfFileWriter, PdfFileReader
from uuid import uuid4
from cgi import escape
import os
import random
import string
import datetime

def get_user_practices(db, userId):
    ps = db(db.practice.the_user==userId).select(db.practice.ALL)
    
    ps_info = [get_practice(db, p.id) for p in ps]    
    return ps_info 
    
#####
# States:
# - pending
# - ready_to_validate
# - validation_sent
# - validation_ready
# - validation_rejected
# - approved
# - rejected
#####
def get_practice(db, pId):
    p = db(db.practice.id==pId).select(db.practice.ALL).first()
        
    p_info = {}
    p_info['id'] = p.id
    p_info['user'] = p.the_user
    p_info['user_name'] = p.the_user.last_name + ', ' + p.the_user.first_name
    p_info['user_specialty'] = specialties[p.the_user.specialty] if p.the_user.specialty is not None else None
    p_info['category'] = p.category
    p_info['category_name'] = practice_category[p.category]
    p_info['company'] = get_company(db, p.company)
    p_info['created'] = p.created
    p_info['validator'] = get_employee(db, p.validator)    
    p_info['description'] = p.description
    p_info['starting'] = p.starting
    p_info['ending'] = p.ending
    p_info['p_key'] = p.p_key    
    p_info['validation_sent'] = p.validation_sent
    p_info['validation_ready'] = p.validation_ready
    p_info['validation_result'] = p.validation_result
    p_info['approved'] = p.approved
    p_info['approved_date'] = p.approved_date
    p_info['approved_comment'] = p.approved_comment
    p_info['state'] = 'pending'
    if p_info['approved_date'] is not None:
        p_info['state'] = 'approved' if p_info['approved'] else 'rejected'
    elif p_info['validation_ready'] is not None:
        p_info['state'] = 'validation_ready' if p_info['validation_result'] else 'validation_rejected'
    elif p_info['validation_sent'] is not None:
        p_info['state'] = 'validation_sent'
    elif (p_info['company'] is not None and p_info['company']['is_complete'] and p_info['validator'] is not None and p_info['validator']['is_complete'] and p_info['description'] is not None 
            and len(p_info['description']) > 0 and p_info['starting'] is not None and p_info['ending'] is not None):
        p_info['state'] = 'ready_to_validate'
    
    return p_info 

def get_company(db, comId):
    com = db(db.company.id == comId).select(db.company.ALL).first()
    
    if com is not None:
        com_info = {}
        com_info['id'] = com.id
        com_info['rut'] = com.rut
        com_info['name'] = com.name
        com_info['businessLine'] = com.business_line
        com_info['address'] = com.address
        com_info['city'] = com.city
        com_info['country'] = com.country
        com_info['is_complete'] = False if com_info['rut'] is None or len(com_info['rut']) == 0 or com_info['name'] is None or len(com_info['name']) == 0 or com_info['businessLine'] is None or len(com_info['businessLine']) == 0 or com_info['address'] is None or len(com_info['address']) == 0 or com_info['city'] is None or len(com_info['city']) == 0 or com_info['country'] is None or len(com_info['country']) == 0 else True
        
        return com_info
    else:
        return None
        
def get_employee(db, empId):
    emp = db(db.company_employee.id == empId).select(db.company_employee.ALL).first()
    
    if emp is not None:
        emp_info = {}
        emp_info['id'] = emp.id
        emp_info['company'] = get_company(db, emp.company)
        emp_info['first_name'] = emp.first_name
        emp_info['last_name'] = emp.last_name
        emp_info['position'] = emp.position
        emp_info['department'] = emp.department
        emp_info['phone'] = emp.phone
        emp_info['email'] = emp.email
        emp_info['is_complete'] = False if emp_info['first_name'] is None or len(emp_info['first_name']) == 0 or emp_info['last_name'] is None or len(emp_info['last_name']) == 0 or emp_info['position'] is None or len(emp_info['position']) == 0 or emp_info['department'] is None or len(emp_info['department']) == 0 or emp_info['phone'] is None or len(emp_info['phone']) == 0 or emp_info['email'] is None or len(emp_info['email']) == 0 else True
        
        return emp_info
    else:
        return None
        
def generate_key(pId):
    p_key = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(6))
    p_key = p_key + str(pId)
    return p_key
        
def send_validation_email(db, pId):
    practice = db.practice[pId]
    validator = db.company_employee[practice.validator]
    the_user = db.auth_user[practice.the_user]
    company = db.company[practice.company]
    tos = [validator.email]
        
    message = 'Estimado,\r\nel alumno {} {} ha inscrito su práctica y lo ha definido a ud. como contacto para la validación de esta.\r\n'.format(the_user.first_name, the_user.last_name)
    message = message + 'La información entregada es la siguiente:\r\n'
    message = message + 'Rut empresa: {}\r\n'.format(company.rut)
    message = message + 'Nombre empresa: {}\r\n'.format(company.name)
    message = message + 'Dirección empresa: {}\r\n\r\n'.format(company.address)
    message = message + 'Descripción práctica: {}\r\n'.format(practice.description)
    message = message + 'Fecha estimada de inicio: {}\r\n'.format(practice.starting)
    message = message + 'Fecha estimada de fin: {}\r\n\r\n'.format(practice.ending)
    message = message + 'Si la información es correcta, le pedimos que presione en el siguiente link como validación de la inscripción de la práctica del alumno:\r\n\r\n'
    message = message + URL('practice', 'validate_practice', args=[practice.p_key, 1], scheme=True, host=True)
    message = message + '\r\n\r\nSi no conoce al alumno, o no le es posible validar esta inscripción, por favor presione el siguiente link:\r\n\r\n'
    message = message + URL('practice', 'validate_practice', args=[practice.p_key, 0], scheme=True, host=True)
    
    message = message + '\r\n--\r\nFacultad de Ingeniería y Ciencias Aplicadas\r\nUniversidad de los Andes\r\niuandes@miuandes.cl'
    subject = '[iuandes] Validación Inscripción Práctica'
    
    return mail_iua.send(   to=tos,
                            subject=subject,
                            message=message)
							

	

def get_practice_by_especialty(db):
    count = db.auth_user.specialty.count()
    practices = db((db.practice.the_user==db.auth_user.id) & (db.practice.approved==True)).select(db.practice.category, db.auth_user.specialty, count, groupby=(db.auth_user.specialty, db.practice.category), orderby=(db.auth_user.specialty | db.practice.category))
    ps_info=[]
    for i in range(4):
        print i
        n_info = {}
        count_op = 0
        count_e1 = 0
        count_e2 = 0
        for n in practices:
            if n['practice.category'] == 0 and n['auth_user.specialty']==i:
                count_op = n['COUNT(auth_user.specialty)']
            if n['practice.category'] == 1 and n['auth_user.specialty']==i:
                count_e1 = n['COUNT(auth_user.specialty)']
            if n['practice.category'] == 2 and n['auth_user.specialty']==i:
                count_e2 = n['COUNT(auth_user.specialty)']                
        n_info['specialty'] = specialties[i]
        n_info['ammount_OP'] = count_op
        n_info['ammount_E1'] = count_e1
        n_info['ammount_E2'] = count_e2
        ps_info.append(n_info)
    return ps_info 
    
def get_practice_by_state_ids(db, state):
    pids = []
    if state == 'pending':
        pids = db((db.practice.validation_sent == None) | (db.practice.validation_result == False)).select(db.practice.id, orderby=db.practice.created)
    elif state == 'validation_sent':
        pids = db((db.practice.validation_sent != None) & (db.practice.validation_ready == None)).select(db.practice.id, orderby=db.practice.validation_sent)
    elif state == 'validation_ready':
        pids = db((db.practice.validation_ready != None) & (db.practice.approved_date == None) & (db.practice.validation_result == True)).select(db.practice.id, orderby=db.practice.validation_ready)
    elif state == 'approved':
        pids = db((db.practice.approved_date != None) & (db.practice.approved == True)).select(db.practice.id, orderby=db.practice.approved_date)
    elif state == 'rejected':
        pids = db((db.practice.approved_date != None) & (db.practice.approved == False)).select(db.practice.id, orderby=db.practice.approved_date)
    elif state == 'ended':
        pids = []
    return pids
                            
def get_practice_by_state(db, state):
    pids = get_practice_by_state_ids(db, state)
        
    practices = [get_practice(db, pid) for pid in pids]
    return practices
    
def get_practices_state_counts(db):
    st_counts = {}
    states = ['pending', 'validation_sent', 'validation_ready', 'approved', 'rejected', 'ended']
    for st in states:
        st_counts[st] = len(get_practice_by_state_ids(db, st))
    
    return st_counts
        

def get_securefile(db,pid):
    practice = db.practice(id=pid)
    company = db.company(id = practice.company)
    alumn = db.auth_user(id=practice.the_user)
    today = datetime.datetime.now()
    baseFolder = request.folder
    output = PdfFileWriter()
    templatePath = os.path.join(baseFolder, 'static', 'templates', 'Secure.pdf')    
    pdfTemplate = PdfFileReader(open(templatePath, "rb"))
    pdfTemplatePage = pdfTemplate.getPage(0)
    tmpfilename=os.path.join(request.folder,'private',str(uuid4()))
    doc = SimpleDocTemplate(tmpfilename,pagesize=letter,
                            rightMargin=72,leftMargin=72,
                            topMargin=100,bottomMargin=18)
    styles=getSampleStyleSheet()
    styles.add(ParagraphStyle(name='Left', alignment=TA_LEFT))
    Story=[]
    day=today.day
    months= {
    1: 'Enero',
    2: 'Febrero',
    3: 'Marzo',
    4: 'Abril',
    5: 'Mayo',
    6: 'Junio',
    7: 'Julio',
    8: 'Agosto',
    9: 'Septiembre',
    10: 'Octubre',
    11: 'Noviembre',
    12: 'Diciembre'
    }
    month=months[today.month] 
    year=today.year
    Category=practice.category #category of practice.
    Name = alumn.first_name
    Last_Name=alumn.last_name
    Company = company.name 
    period = get_current_next_period(db,0)
    period_m = months[period['starting'].month]#it's not used
    period_y = period['starting'].year
    #default for data is category = 2
    Year ="sexto" #Year of practice
    Months="2" #Months of duration.
    Name_Category="Trabajo en la Empresa 2"; #Name of practice
    Days="40" #Days of duration practice
    spec = ""
    if Category==0: #Obrero
        Days="20"
        Name_Category="Obrero"
        Year="segundo"
        Months="1"
    elif Category ==1 : #Trabajo en empresa 1.
        Days="40"
        Name_Category="Trabajo en la Empresa 1"
        Year="cuarto"
    if alumn.specialty == 1 or alumn.specialty == 3:
        spec = " en "
    spec = spec + specialties[alumn.specialty] 
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='Justify', alignment=TA_JUSTIFY))
    styles.add(ParagraphStyle(name='RIGHT', alignment=TA_RIGHT))
    Story.append(Spacer(1, 12))
    ptext = '<font size=12>Santiago, %s de %s  %s</font>' %(day,month,year)
    Story.append(Paragraph(ptext, styles["RIGHT"]))
    ptext = '<font size=12>Señores</font>'
    Story.append(Paragraph(ptext, styles["Justify"]))
    ptext = '<font size=12>%s</font>' % Company
    Story.append(Paragraph(ptext, styles["Justify"]))
    ptext = '<font size=12>Presente</font>'
    Story.append(Paragraph(ptext, styles["Justify"]))
    Story.append(Spacer(1, 12))
    ptext = '<font size=12>De nuestra consideracion:</font>'
    Story.append(Paragraph(ptext, styles["Justify"]))
    Story.append(Spacer(1, 12))
    Story.append(Spacer(1, 12))
    ptext = '<font size=12>Me dirijo a ustedes para presentarles al señor(ita) %s, quien es alumno de la carrera de Ingeniería Civil %s.</font>'% (Name+" "+ Last_Name,spec)
    Story.append(Paragraph(ptext, styles["Justify"]))
    Story.append(Spacer(1, 12))
    ptext = '<font size=12>La carrera de Ingeniería Civil %s que ofrece nuestra Facultad incluye una Práctica de %s, que los alumnos deben realizar generalmente al término del %s año. Esta práctica tiene el propósito de insertar al alumno en un equipo profesional de la empresa, para que desarrolle un proyecto de actividades bien definido y previamente acordado con la empresa en cuestión.</font>'%(spec,Name_Category,Year)
    Story.append(Paragraph(ptext, styles["Justify"]))
    Story.append(Spacer(1, 12))
    if Category>0:
        ptext = '<font size=12>Nos interesa que el estudiante, en el desarrollo de su práctica, responda directamente al ingeniero a cargo del proceso productivo (el Gerente de Producción o su equivalente), el que también deberá participar en la evaluación final de la práctica. En este sentido, esta actividad difiere de las prácticas tradicionales, que son habitualmente supervisadas por profesionales de la Gerencia de Personal. </font>'
        Story.append(Paragraph(ptext, styles["Justify"]))
        Story.append(Spacer(1, 12))
    ptext = '<font size=12>Esta práctica tiene una duración mínima de %s meses (%s días hábiles)  y puede efectuarse desde Diciembre de %s en adelante. </font>'%(Months,Days,period_y)
    Story.append(Paragraph(ptext, styles["Justify"]))
    Story.append(Spacer(1, 12))
    ptext = '<font size=12>La Práctica de Ingeniería Civil %s, que es parte de las exigencias curriculares de la carrera, tiene también, como un propósito más amplio, el de lograr una vinculación lo más estrecha posible de nuestra Facultad con la realidad empresarial del país, de modo de explorar otros posibles vínculos de interés común.</font>' % spec
    Story.append(Paragraph(ptext, styles["Justify"]))
    Story.append(Spacer(1, 12))
    ptext = '<font size=12>La Universidad de los Andes está inscrita con fecha 9 de Febrero de 1990 en el Folio C Nº 38 del Registro de Universidades, y por ende sus alumnos están sujetos al seguro escolar contemplado en el artículo 3º de la ley Nº 16.744 sobre Accidentes del Trabajo y Enfermedades Profesionales, según lo establecido en el Decreto Nº 41 de 1985.</font>' 
    Story.append(Paragraph(ptext, styles["Justify"]))
    Story.append(Spacer(1, 12))
    ptext = '<font size=12>En la espera de poder establecer un vínculo con su empresa a través de esta actividad, lo saluda muy atentamente,</font>' 
    Story.append(Paragraph(ptext, styles["Justify"]))
    Story.append(Spacer(1, 12))
    doc.build(Story)
    response.headers['Content-Type']='application/pdf'
    pdf = PdfFileReader(open(tmpfilename, "rb"))
    for pageNumber in range(pdf.getNumPages()):
        page = pdf.getPage(pageNumber)
        page.mergePage(pdfTemplatePage)
        output.addPage(page)
    downloadFilename = "Carta Presentacion Practica.pdf"
    createfolder = os.path.join(request.folder,'private') 
    filepath = os.path.join(createfolder, downloadFilename)  
    outputStream = open(filepath, "wb")
    output.write(outputStream)
    outputStream.close()
    return filepath, downloadFilename
