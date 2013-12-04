# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

import datetime

from gluon.tools import *

if request.env.web2py_runtime_gae:            
    db = DAL('gae')                           
    session.connect(request, response, db = db)
else:                                         
    db = DAL(settings.db_uri, migrate=settings.migrate, migrate_enabled=settings.migrate, pool_size=10)

mail = Mail()                                  # mailer
auth = Auth(globals(),db)                      # authentication/authorization
crud = Crud(globals(),db)                      # for CRUD helpers using auth
service = Service(globals())                   # for json, xml, jsonrpc, xmlrpc, amfrpc
plugins = PluginManager()

#Activar vistas por defecto
response.generic_patterns = ['*']


mail.settings.server = settings.email_server   # your SMTP server
mail.settings.sender = settings.email_sender   # your email
mail.settings.login = settings.email_login    # your credentials or None

auth.settings.hmac_key = 'sha512:9882e830-d3b9-4e91-80c3-b043a11f505c'   # before define_tables()
auth.define_tables(username=True, migrate=not settings.produccion)                           # creates all needed tables
auth.settings.mailer = mail                    # for user email verification
auth.settings.registration_requires_verification = False
auth.settings.registration_requires_approval = False
auth.messages.verify_email = 'Click on the link http://'+request.env.http_host+URL('default','user',args=['verify_email'])+'/%(key)s to verify your email'
auth.settings.reset_password_requires_verification = True
auth.messages.reset_password = 'Click on the link http://'+request.env.http_host+URL('default','user',args=['reset_password'])+'/%(key)s to reset your password'
auth.settings.actions_disabled=['register','change_password','request_reset_password', 'retrieve_username']
auth.settings.login_methods = settings.login_method
auth.settings.create_user_groups = False
auth.settings.remember_me_form = False
auth.settings.expiration = settings.expiracion

def mi_logout(form):
    session.clear()

#olvida datos de profesor en cada login
auth.settings.logout_onlogout = mi_logout

crud.settings.auth = None                      # =auth to enforce authorization on crud

#opcional el widget para fechas jquery datepicker
def date_widget(f,v):
    wrapper = DIV()
    inp = SQLFORM.widgets.string.widget(f,v,_class="jqdate")
    jqscr = SCRIPT("jQuery(document).ready(function(){jQuery('#%s').datepicker({dateFormat:'dd/mm/yyyy'});});" % inp['_id'],_type="text/javascript")
    wrapper.components.extend([inp,jqscr])
    return wrapper

#para anytime
from plugin_anytime_widget import anytime_widget, anydate_widget, anydatetime_widget

#########################################################################
## Define your tables
#########################################################################
db.define_table("curso_academico",
      Field("curso", length=9, unique=True, notnull=True, required=True),
      Field("retrasos_para_amonestacion", "integer", notnull=True, required=True, default=2),
      Field("retrasos_por_trimestres", "boolean", notnull=True, required=True, default=True),              
      Field("inicio_trimestre_1", "date", notnull=True, required=True),
      Field("fin_trimestre_1", "date", notnull=True, required=True),
      Field("inicio_trimestre_2", "date", notnull=True, required=True),
      Field("fin_trimestre_2", "date", notnull=True, required=True),
      Field("inicio_trimestre_3", "date", notnull=True, required=True),
      Field("fin_trimestre_3", "date", notnull=True, required=True),
      Field("peso_1", "decimal(4,2)", notnull=True, required=True),
      Field("peso_2", "decimal(4,2)", notnull=True, required=True),
      Field("peso_3", "decimal(4,2)", notnull=True, required=True),
      Field("peso_4", "decimal(4,2)", notnull=True, required=True),
      Field("peso_5", "decimal(4,2)", notnull=True, required=True),
      Field("peso_6", "decimal(4,2)", notnull=True, required=True),      
      migrate='curso_academico.table',    
      format='%(curso)s')
      
db.define_table("config",
      Field("codigo_centro", length=15, unique=True, notnull=True, required=True),
      Field("nombre_centro", length=50, unique=True, notnull=True, required=True),
      Field("curso_academico_defecto", db.curso_academico),     
      Field("nombre_director", length=50),
      Field("firma_director", "upload", autodelete=True),          
      Field("sello_centro", "upload", autodelete=True),
      Field("logo_centro", "upload", autodelete=True),
      migrate='config.table',    
      format='%(codigo_centro)s %(nombre_centro)s')

db.define_table("profesor",
      Field("dni", length=15, unique=True, notnull=True, required=True),
      Field("nombre", length=20, notnull=True, required=True),
      Field("apellidos", length=40, notnull=True, required=True),
      Field("usuario_rayuela", length=20, unique=True, notnull=True, required=True),
      migrate='profesor.table',        
      format='%(apellidos)s, %(nombre)s')

db.define_table("alumno",
      Field("nie", length=15, unique=True, required=True, notnull=True),
      Field("nombre", length=20, notnull=True, required=True),
      Field("apellidos", length=40, notnull=True, required=True),
      Field("fecha_nacimiento", "date"),
      Field("foto", "upload", uploadseparate=True, autodelete=True),
      Field("usuario_rayuela", length=20),
      migrate='alumno.table',                    
      format='%(apellidos)s, %(nombre)s')

db.define_table("grupo",
      Field("grupo", length=60, unique=True, required=True, notnull=True),
      migrate='grupo.table',      
      format='%(grupo)s')

db.define_table("departamento",
      Field("departamento", length=60, unique=True, required=True, notnull=True),
      Field("usar_criterios_departamento", "boolean", notnull=True, required=True),
      Field("peso_1", "decimal(4,2)", notnull=True, required=True),
      Field("peso_2", "decimal(4,2)", notnull=True, required=True),
      Field("peso_3", "decimal(4,2)", notnull=True, required=True),
      Field("peso_4", "decimal(4,2)", notnull=True, required=True),
      Field("peso_5", "decimal(4,2)", notnull=True, required=True),
      Field("peso_6", "decimal(4,2)", notnull=True, required=True),       
      migrate='departamento.table',      
      format='%(departamento)s')
      
db.define_table("curso_academico_grupo",
      Field("id_curso_academico", db.curso_academico),
      Field("id_grupo", db.grupo),
      Field("id_tutor", db.profesor),
      migrate='curso_academico_grupo.table',      
      format='%(id)s')    

db.define_table("curso_academico_departamento",
      Field("id_curso_academico", db.curso_academico),
      Field("id_departamento", db.departamento),
      Field("id_jefe", db.profesor),
      migrate='curso_academico_departamento.table',      
      format='%(id)s')    

db.define_table("grupo_alumno",
      Field("id_curso_academico_grupo", db.curso_academico_grupo),
      Field("id_alumno", db.alumno),
      migrate='grupo_alumno.table',      
      format='%(id)s')

db.define_table("grupo_profesor",
      Field("id_curso_academico_grupo", db.curso_academico_grupo),
      Field("id_profesor", db.profesor),
      migrate='grupo_profesor.table',      
      format='%(id)s')    

db.define_table("departamento_profesor",
      Field("id_curso_academico_departamento", db.curso_academico_departamento),
      Field("id_profesor", db.profesor),
      migrate='departamento_profesor.table',      
      format='%(id)s')    

db.define_table("amonestacion",
      Field("fecha", "date", required=True, notnull=True, default=datetime.date.today()),
      Field("id_grupo_alumno", db.grupo_alumno),
      Field("id_departamento_profesor", db.departamento_profesor),
      Field("amonestacion", "text", required=True, notnull=True, default=''),
      Field("parte", "boolean", required=True, notnull=True, default = False),
      Field("comunicada", "boolean", required=True, notnull=True, default = False),
      Field("cerrada", "boolean", required=True, notnull=True, default = False),
      migrate='amonestacion.table',      
      format='%(id)s')

db.define_table("seguimiento",
      Field("id_amonestacion", db.amonestacion),
      Field("fecha", "date", required=True, notnull=True, default=datetime.date.today()),
      Field("seguimiento", "text", required=True, notnull=True, default=''),
      Field("id_responsable", db.departamento_profesor),
      migrate='seguimiento.table',      
      format='%(id)s')

db.define_table("amonestacion_retraso",
      Field("fecha", "date", required=True, notnull=True, default=datetime.date.today()),
      Field("id_grupo_alumno", db.grupo_alumno),
      Field("id_departamento_profesor", db.departamento_profesor),
      migrate='amonestacion_retraso.table',      
      format='%(id)s')

db.define_table("retraso",
      Field("fecha", "date", required=True, notnull=True, default=datetime.date.today()),
      Field("hora", length=1, required=True, notnull=True, default='1'),
      Field("id_grupo_alumno", db.grupo_alumno),
      Field("id_departamento_profesor", db.departamento_profesor),
      Field("procesar", "boolean", default = True),
      migrate='retraso.table',      
      format='%(id)s')
      
db.define_table("amonestacion_retraso_retraso",
      Field("id_amonestacion_retraso", db.amonestacion_retraso),
      Field("id_retraso", db.retraso),
      migrate='amonestacion_retraso_retraso.table',      
      format='%(id)s')      
      
db.define_table("amonestacion_absentismo",
      Field("fecha", "date", required=True, notnull=True, default=datetime.date.today()),
      Field("id_grupo_alumno", db.grupo_alumno),
      Field("id_departamento_profesor", db.departamento_profesor),
      Field("absentismo", "text", required=True, notnull=True, default=''),
      Field("comunicada", "boolean", required=True, notnull=True, default = False),
      migrate='amonestacion_absentismo.table',      
      format='%(id)s')      

db.define_table("asignatura",
      Field("abreviatura", 'string', length=10, required=True, notnull=True),
      Field("asignatura", length=50, required=True, notnull=True),
      Field("usar_criterios_asignatura", "boolean", notnull=True, required=True),
      Field("peso_1", "decimal(4,2)", notnull=True, required=True),
      Field("peso_2", "decimal(4,2)", notnull=True, required=True),
      Field("peso_3", "decimal(4,2)", notnull=True, required=True),
      Field("peso_4", "decimal(4,2)", notnull=True, required=True),
      Field("peso_5", "decimal(4,2)", notnull=True, required=True),
      Field("peso_6", "decimal(4,2)", notnull=True, required=True),       
      
      
      Field("id_departamento", db.departamento),
      migrate='asignatura.table',      
      format='%(asignatura)s')
      
db.define_table("curso_academico_evaluacion",
      Field("id_curso_academico", db.curso_academico),
      Field("evaluacion", length=50, required=True, notnull=True),
      Field("fecha", "date", required=True, notnull=True),
      Field("bloqueada", "boolean", required=True, notnull=True, default=True),      
      migrate='curso_academico_evaluacion.table',      
      format='%(evaluacion)s')      
      
db.define_table("grupo_profesor_asignatura",
      Field("id_grupo_profesor", db.grupo_profesor),
      Field("id_asignatura", db.asignatura),
      migrate='grupo_profesor_asignatura.table')

db.define_table("grupo_profesor_asignatura_alumno",
      Field("id_grupo_profesor_asignatura", db.grupo_profesor_asignatura),
      Field("id_grupo_alumno", db.grupo_alumno),
      migrate='grupo_profesor_asignatura_alumno.table')

db.define_table("evaluacion_alumno",
      Field("id_curso_academico_evaluacion", db.curso_academico_evaluacion),
      Field("id_grupo_profesor_asignatura_alumno", db.grupo_profesor_asignatura_alumno),
      Field("nivel", "integer", default=0),
      Field("trabajo_clase", "integer", default=0),
      Field("trabajo_casa", "integer", default=0),
      Field("interes", "integer", default=0),
      Field("participa", "integer", default=0),
      Field("comportamiento", "integer", default=0),
      Field("observaciones", "text", default=""),
      Field("evaluacion", "decimal(4,2)", default=0),
      migrate='evaluacion_alumno.table')
                                        

db.curso_academico.curso.required = True
db.curso_academico.curso.requires = [IS_NOT_EMPTY(error_message=T('Value required')), IS_NOT_IN_DB(db, 'curso_academico.curso',error_message=T('Value duplicated'))]
db.curso_academico.retrasos_para_amonestacion.required = True
db.curso_academico.retrasos_para_amonestacion.default = 2
db.curso_academico.retrasos_por_trimestres.required = True
db.curso_academico.retrasos_por_trimestres.default = True
db.curso_academico.inicio_trimestre_1.required = True
db.curso_academico.fin_trimestre_1.required = True
db.curso_academico.inicio_trimestre_2.required = True
db.curso_academico.fin_trimestre_2.required = True
db.curso_academico.inicio_trimestre_3.required = True
db.curso_academico.fin_trimestre_3.required = True
db.curso_academico.peso_1.default = 75
db.curso_academico.peso_1.label = T('Prueba de nivel')
db.curso_academico.peso_2.default = 7.5
db.curso_academico.peso_2.label = T('Trabajo en clase')
db.curso_academico.peso_3.default = 7.5
db.curso_academico.peso_3.label = T('Trabajo en casa')
db.curso_academico.peso_4.default = 5
db.curso_academico.peso_4.label = T('Interés')
db.curso_academico.peso_5.default = 5
db.curso_academico.peso_5.label = T('Participa')
db.curso_academico.peso_6.default = 0
db.curso_academico.peso_6.label = T('Comportamiento')

db.config.codigo_centro.required = True
db.config.codigo_centro.requires = [IS_NOT_EMPTY(error_message=T('Value required')), IS_NOT_IN_DB(db, 'config.codigo_centro',error_message=T('Value duplicated'))]
db.config.nombre_centro.required = True
db.config.nombre_centro.requires = [IS_NOT_EMPTY(error_message=T('Value required')), IS_NOT_IN_DB(db, 'config.nombre_centro',error_message=T('Value duplicated'))]
db.config.curso_academico_defecto.requires = IS_NULL_OR(IS_IN_DB(db, 'curso_academico.id', '%(curso)s', error_message=T('Academic course not found')))
db.config.firma_director.requires = IS_NULL_OR(IS_IMAGE(error_message = T('Only photos allowed')))
db.config.sello_centro.requires = IS_NULL_OR(IS_IMAGE(error_message = T('Only photos allowed')))
db.config.logo_centro.requires = IS_NULL_OR(IS_IMAGE(error_message = T('Only photos allowed')))

db.profesor.dni.required = True
db.profesor.dni.requires = [IS_NOT_EMPTY(error_message=T('Value required')), IS_NOT_IN_DB(db, 'profesor.dni',error_message=T('Value duplicated'))]
db.profesor.nombre.required = True
db.profesor.nombre.requires = IS_NOT_EMPTY(error_message=T('Value required'))
db.profesor.apellidos.required = True
db.profesor.apellidos.requires = IS_NOT_EMPTY(error_message=T('Value required'))
db.profesor.usuario_rayuela.required = True
db.profesor.usuario_rayuela.requires = [IS_NOT_EMPTY(error_message=T('Value required')), IS_NOT_IN_DB(db, 'profesor.usuario_rayuela',error_message=T('Value duplicated'))]

db.alumno.nie.required = True
db.alumno.nie.requires = [IS_NOT_EMPTY(error_message=T('Value required')), IS_NOT_IN_DB(db, 'alumno.nie',error_message=T('Value duplicated'))]
db.alumno.nombre.required = True
db.alumno.nombre.requires = IS_NOT_EMPTY(error_message=T('Value required'))
db.alumno.apellidos.required = True
db.alumno.apellidos.requires = IS_NOT_EMPTY(error_message=T('Value required'))
#db.alumno.fecha_nacimiento.widget = anydate_widget
db.alumno.foto.requires = IS_NULL_OR(IS_IMAGE(error_message = T('Only photos allowed')))

db.grupo.grupo.required = True
db.grupo.grupo.requires = [IS_NOT_EMPTY(error_message=T('Value required')), IS_NOT_IN_DB(db, 'grupo.grupo',error_message=T('Value duplicated'))]

db.departamento.departamento.required = True
db.departamento.departamento.requires = [IS_NOT_EMPTY(error_message=T('Value required')), IS_NOT_IN_DB(db, 'departamento.departamento',error_message=T('Value duplicated'))]
db.departamento.usar_criterios_departamento.default = True
db.departamento.peso_1.default = 75
db.departamento.peso_2.default = 7.5
db.departamento.peso_3.default = 7.5
db.departamento.peso_4.default = 5
db.departamento.peso_5.default = 5
db.departamento.peso_6.default = 0
db.departamento.peso_1.label = T('Prueba de nivel')
db.departamento.peso_2.label = T('Trabajo en clase')
db.departamento.peso_3.label = T('Trabajo en casa')
db.departamento.peso_4.label = T('Interés')
db.departamento.peso_5.label = T('Participa')
db.departamento.peso_6.label = T('Comportamiento')

db.asignatura.abreviatura.required = True
db.asignatura.abreviatura.requires = [IS_NOT_EMPTY(error_message=T('Value required')), IS_NOT_IN_DB(db, 'asignatura.abreviatura',error_message=T('Value duplicated'))]
db.asignatura.asignatura.required = True
db.asignatura.asignatura.requires = [IS_NOT_EMPTY(error_message=T('Value required')), IS_NOT_IN_DB(db, 'asignatura.asignatura',error_message=T('Value duplicated'))]
db.asignatura.usar_criterios_asignatura.default = False
db.asignatura.id_departamento.label = T('Departamento')
db.asignatura.peso_1.default = 75
db.asignatura.peso_2.default = 7.5
db.asignatura.peso_3.default = 7.5
db.asignatura.peso_4.default = 5
db.asignatura.peso_5.default = 5
db.asignatura.peso_6.default = 0
db.asignatura.peso_1.label = T('Prueba de nivel')
db.asignatura.peso_2.label = T('Trabajo en clase')
db.asignatura.peso_3.label = T('Trabajo en casa')
db.asignatura.peso_4.label = T('Interés')
db.asignatura.peso_5.label = T('Participa')
db.asignatura.peso_6.label = T('Comportamiento')


db.curso_academico_evaluacion.id_curso_academico.readable =  db.curso_academico_evaluacion.id_curso_academico.writable = False
db.curso_academico_evaluacion.evaluacion.required = True
db.curso_academico_evaluacion.evaluacion.requires = IS_NOT_EMPTY(error_message=T('Value required'))
db.curso_academico_evaluacion.fecha.required = True
