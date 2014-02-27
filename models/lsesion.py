# coding: utf8
# Recuperemos variables generales como datos del centro, así como curso académico por defecto
import datetime
from gluon.storage import Storage, List

def initSession():
    hoy = datetime.date.today()
    session.fecha_hoy = hoy.isoformat()
    
    session.profesor = Storage()
    session.profesor.esJefe = False
    session.profesor.esTutor = False    
    session.profesor.grupos = List()
    session.usuarios_ultima_hora = List()
    
    if not db(db.config).select().first():
        return      

    config = db(db.config).select().first()

    if not session.curso_academico_defecto:
        session.curso_academico_defecto = config.curso_academico_defecto

    if not session.trimestre_actual:
        if ((hoy >= db.curso_academico[session.curso_academico_defecto].inicio_trimestre_1) and
            (hoy <= db.curso_academico[session.curso_academico_defecto].fin_trimestre_1)):
            session.trimestre_actual = 1
        elif ((hoy >= db.curso_academico[session.curso_academico_defecto].inicio_trimestre_2) and
            (hoy <= db.curso_academico[session.curso_academico_defecto].fin_trimestre_2)):
            session.trimestre_actual = 2
        else:
            session.trimestre_actual = 3
 
    session.curso_academico_id = db.curso_academico[session.curso_academico_defecto].id
    session.curso_academico_nombre = db.curso_academico[session.curso_academico_defecto].curso
    session.codigo_centro = config.codigo_centro
    session.nombre_centro = config.nombre_centro
    session.retrasos_para_amonestacion = db.curso_academico[session.curso_academico_defecto].retrasos_para_amonestacion
    session.retrasos_por_trimestres = db.curso_academico[session.curso_academico_defecto].retrasos_por_trimestres
    session.nombre_director = config.nombre_director
    session.firma_director = config.firma_director   
    session.logo_centro = config.logo_centro
    session.sello_centro = config.sello_centro
        
    session.cursos = db(db.curso_academico).select(orderby=~db.curso_academico.curso).as_list()

    session.esProfesor = False
    session.esResponsable = False
    session.esInformatico = False
    session.esAdministrativo = False
    session.esSustituto = False
    
    if auth.has_membership('Responsables'):
        session.esResponsable = True

    if auth.has_membership('Informaticos'):
        session.esInformatico = True

    if auth.has_membership('Administrativos'):
        session.esAdministrativo = True
    
            
    # Accedemos a la información del usuario en la tabla de profesores 
    profesor = db((db.auth_user.username == db.profesor.usuario_rayuela) &
                          (db.auth_user.id == auth.user_id)).select(db.profesor.ALL).first()
    if profesor:
        session.esProfesor = True
        session.profesor.apellidos = profesor.apellidos
        session.profesor.dni = profesor.dni
        session.profesor.id = profesor.id
        session.profesor.nombre = profesor.nombre
        session.profesor.usuario_rayuela = profesor.usuario_rayuela
        if not auth.has_membership('Profesores', auth.user.id):
            auth.add_membership(auth.id_group('Profesores'), auth.user.id)
            
    # Accedemos al id_departamento_profesor
    if session.esProfesor:
        departamento_profesor = db((db.curso_academico_departamento.id == db.departamento_profesor.id_curso_academico_departamento) &
                                   (db.curso_academico_departamento.id_curso_academico == session.curso_academico_id) &
                                   (db.departamento_profesor.id_profesor == session.profesor.id)).select(db.departamento_profesor.ALL).first()
        if departamento_profesor:
            session.profesor.id_departamento_profesor = departamento_profesor.id
            session.profesor.id_curso_academico_departamento = departamento_profesor.id_curso_academico_departamento
            session.profesor.id_departamento = departamento_profesor.id_curso_academico_departamento.id_departamento
            session.profesor.departamento = departamento_profesor.id_curso_academico_departamento.id_departamento.departamento

        if departamento_profesor.sustituye:
            session.esSustituto = True
            # pongamos ahora el codigo del profesor sustituido
            session.sustituye = departamento_profesor.sustituye

        grupo_profesor = db((db.curso_academico_grupo.id == db.grupo_profesor.id_curso_academico_grupo) &
                            (db.curso_academico_grupo.id_curso_academico == session.curso_academico_id) &
                            (db.grupo_profesor.id_profesor == session.profesor.id)).select(db.grupo_profesor.ALL)
        if grupo_profesor:
            for gp in grupo_profesor:
                grupo = Storage()
                grupo.id_grupo_profesor = gp.id
                grupo.id_curso_academico_grupo = gp.id_curso_academico_grupo
                grupo.grupo = gp.id_curso_academico_grupo.id_grupo.grupo
                session.profesor.grupos.append(grupo)

        # Veamos si es tutor
        if session.esSustituto:
            session.idProfesorSustituido = db.departamento_profesor[session.sustituye].id_profesor
            tutor_grupo = db((db.curso_academico_grupo.id_curso_academico == session.curso_academico_id) & 
                              (db.curso_academico_grupo.id_tutor == session.idProfesorSustituido)).select(db.curso_academico_grupo.ALL).first()            
        else:
            tutor_grupo = db((db.curso_academico_grupo.id_curso_academico == session.curso_academico_id) & 
                              (db.curso_academico_grupo.id_tutor == session.profesor.id)).select(db.curso_academico_grupo.ALL).first()
        if tutor_grupo:
            session.profesor.esTutor = True
            session.profesor.tutor = Storage()
            session.profesor.tutor.id_curso_academico_grupo = tutor_grupo.id
            session.profesor.tutor.curso = tutor_grupo.id_grupo.grupo
                           
        # Veamos si es jefe de departamento
        jefe = db((db.curso_academico_departamento.id_curso_academico == session.curso_academico_id) &
                          (db.curso_academico_departamento.id_jefe == session.profesor.id)).select(db.curso_academico_departamento.ALL).first()
        if jefe:
            session.profesor.esJefe = True
            session.profesor.jefe = Storage()
            session.profesor.jefe.id_curso_academico_departamento = jefe.id
            session.profesor.jefe.departamento = jefe.id_departamento.departamento
              
#establece_variables()
initSession()
