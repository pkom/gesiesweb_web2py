# coding: utf8
# intente algo como

import obies
from gluon.storage import Storage

crud.settings.controller = 'management'

def index(): return dict(message="hello from management.py")

@auth.requires_membership(role='Responsables')
def show_center():
    centro = db(db.config).select().first()
    if centro == None:
        db.config.insert(codigo_centro = T('To be filled with data'), nombre_centro = T('To be filled with data'), nombre_director = T('To be filled with data'))
        centro = db(db.config).select().first()
    form = crud.update(db.config, centro, deletable = False, next = URL('show_center'), message = T('Center updated'))
    return dict(form=form, centro = centro)

@auth.requires_membership(role='Responsables')
def add_course():
    form=SQLFORM(db.curso_academico, showid=False, submit_button='Enviar')
    form = crud.create(db.curso_academico, next = URL('show_courses'), message = T('Course added'))       
    return dict(form=form)

@auth.requires_membership(role='Responsables')
def show_course():
    curso = db.curso_academico(request.args(0)) or redirect(URL('index'))
    # deberemos controlar el deletable en el form, de forma que no puedan borrarse cursos con datos,
    # o bien no se elimine el curso por defecto en la configuración
    config = db(db.config).select().first()
    if config.curso_academico_defecto.id == curso.id:
        borrable = False
    else:
        borrable = True
    form = crud.update(db.curso_academico, curso, deletable=borrable, next = URL('show_courses'), message = T('Course updated'))    
    return dict(form=form, curso = curso)

@auth.requires_membership(role='Responsables')
def show_courses():
    grid = SQLFORM.grid(db.curso_academico, paginate=10, ui='jquery-ui', maxtextlength={'curso_academico.curso':50}, 
            deletable=False, csv=False, fields=[db.curso_academico.id, db.curso_academico.curso], onvalidation=valida_pesos)
    return dict(grid = grid)

def valida_pesos(form):
    suma = form.vars.peso_1 + form.vars.peso_2 + form.vars.peso_3 + form.vars.peso_4 + form.vars.peso_5 + form.vars.peso_6
    if suma <> 100:
        form.errors.peso_6 = T('La suma de los porcentajes debe ser igual a 100')

@auth.requires_membership(role='Responsables')
def show_courses_old():
    form=SQLFORM(db.curso_academico, showid=False, submit_button='Enviar')
    form = crud.create(db.curso_academico, next = URL('show_courses'), message = T('Course added'))
    ocursos = obies.Curso(db, session)
    cursos = ocursos.dame_cursos()
    return dict(form=form, cursos = cursos)

@auth.requires(auth.has_membership(role='Responsables') or auth.has_membership(role="Administrativos"))
def show_students():
    response.flash = T('Searching students...')
    form=FORM(TABLE(TR(T('Teclea cualquier carácter en el nombre del alumno/a para buscar:'),
                       INPUT(_type="text",_length="40", _id = "buscar", _name="buscar", _onkeyup="ajax('busca_alumnos', ['buscar'], 'resultado')"))))
    return dict(form = form)

@auth.requires(auth.has_membership(role='Responsables') or auth.has_membership(role="Administrativos"))
def busca_alumnos():
    if not request.vars.buscar:
        return DIV(T('No data'))
    oalumno = obies.Alumno(db, session)
    alumnos = oalumno.dame_alumnos_buscados(request.vars.buscar)
    return DIV(*[SPAN(A(alumno.alumno.apellidos, ', ', alumno.alumno.nombre, _href=URL('show_student', args=alumno.alumno.id)),
                 ' (',A(alumno.grupo_alumno.id_curso_academico_grupo.id_grupo.grupo, _href=URL('show_group', args=alumno.grupo_alumno.id_curso_academico_grupo.id)), ')',
                 BR()) for alumno in alumnos]).xml()

@auth.requires(auth.has_membership(role='Responsables') or auth.has_membership(role="Administrativos"))
def show_student():
    alumno = db.alumno(request.args(0)) or redirect(URL('index'))
    form = crud.update(db.alumno, alumno, deletable = False, next = URL('show_students'), message = T('Student updated'))
    ogrupo = obies.Grupo(db, session)
    grupos = ogrupo.dame_grupo_alumno(alumno)
    return dict(form=form, alumno=alumno, grupos=grupos)

@auth.requires(auth.has_membership(role='Responsables') or auth.has_membership(role="Administrativos"))
def show_teachers():
    oprofesor = obies.Profesor(db, session)
    profesores = oprofesor.dame_profesores_curso()
    return dict(profesores = profesores)

@auth.requires(auth.has_membership(role='Responsables') or auth.has_membership(role="Administrativos"))
def show_teacher():
    profesor = db.profesor(request.args(0)) or redirect(URL('index'))
    form = crud.update(db.profesor, profesor, deletable = False, next = URL('show_teachers'), message = T('Teacher updated'))
    oprofesor = obies.Profesor(db, session)
    dptos = oprofesor.dame_profesor_departamentos(profesor.id)
    grupos = oprofesor.dame_profesor_grupos(profesor.id)
    return dict(form=form, profesor=profesor, grupos=grupos, dptos=dptos)

@auth.requires(auth.has_membership(role='Responsables') or auth.has_membership(role="Administrativos"))
def show_group():
    grupo = request.args(0) or redirect(URL('show_groups'))
    nombregrupo = db.curso_academico_grupo(grupo).id_grupo.grupo
    tutor = db.curso_academico_grupo(grupo).id_tutor
    oprofesor = obies.Profesor(db, session)
    oalumno = obies.Alumno(db, session)
    profesoresgrupo = oprofesor.dame_profesores_grupo(grupo)
    alumnosgrupo = oalumno.dame_alumnos_grupo(grupo)
    profesoresselect = SELECT(OPTION('Sin asignar', _value = -1),_id='selecttutor')
    for profe in profesoresgrupo:
        if tutor and tutor.id == profe.profesor.id:
            profesoresselect.append(OPTION(profe.profesor.apellidos+', '+profe.profesor.nombre, _value=profe.profesor.id, _selected='selected'))
        else:
            profesoresselect.append(OPTION(profe.profesor.apellidos+', '+profe.profesor.nombre, _value=profe.profesor.id))            
    return dict(grupoid=grupo, gruponombre=nombregrupo, tutor = profesoresselect, profesores = profesoresgrupo, alumnos = alumnosgrupo)

@auth.requires(auth.has_membership(role='Responsables') or auth.has_membership(role="Administrativos"))
def show_groups():
    ogrupo = obies.Grupo(db, session)
    grupos = ogrupo.dame_grupos_curso()
    return dict(grupos = grupos)

@auth.requires(auth.has_membership(role='Responsables') or auth.has_membership(role="Administrativos"))
def show_departament():
    departamento = request.args(0) or redirect(URL('show_departaments'))
    nombredpto = db.curso_academico_departamento(departamento).id_departamento.departamento
    pesos = {}
    pesos["peso_1"] = db.curso_academico_departamento(departamento).id_departamento.peso_1
    pesos["peso_2"] = db.curso_academico_departamento(departamento).id_departamento.peso_2
    pesos["peso_3"] = db.curso_academico_departamento(departamento).id_departamento.peso_3
    pesos["peso_4"] = db.curso_academico_departamento(departamento).id_departamento.peso_4
    pesos["peso_5"] = db.curso_academico_departamento(departamento).id_departamento.peso_5
    pesos["peso_6"] = db.curso_academico_departamento(departamento).id_departamento.peso_6
    usar = db.curso_academico_departamento(departamento).id_departamento.usar_criterios_departamento
                                                                                                    
    jefe = db.curso_academico_departamento(departamento).id_jefe
    oprofesor = obies.Profesor(db, session)
    profesoresdpto = oprofesor.dame_profesores_departamento(departamento)
    asignaturas = db(db.asignatura.id_departamento==db.curso_academico_departamento(departamento).id_departamento.id).select(db.asignatura.ALL,orderby=db.asignatura.asignatura)
    profesoresselect = SELECT(OPTION('Sin asignar', _value = -1),_id='selectjefe')
    for profe in profesoresdpto:
        if jefe and jefe.id == profe.profesor.id:
            profesoresselect.append(OPTION(profe.profesor.apellidos+', '+profe.profesor.nombre, _value=profe.profesor.id, _selected='selected'))
        else:
            profesoresselect.append(OPTION(profe.profesor.apellidos+', '+profe.profesor.nombre, _value=profe.profesor.id))            
    return dict(departamentoid=departamento, nombredpto=nombredpto, pesos=pesos, usar=usar, jefe = profesoresselect, profesores = profesoresdpto, asignaturas=asignaturas)

@auth.requires(auth.has_membership(role='Responsables') or auth.has_membership(role="Administrativos"))
def show_departaments():
    odepartamento = obies.Departamento(db, session)
    departamentos = odepartamento.dame_departamentos_curso()
    return dict(departamentos = departamentos)

@auth.requires_membership(role='Responsables')
def delete_responsible():
    responsable = request.args(0) or redirect(URL('index'))
    if responsable != auth.user.username:
        usuario = db(db.auth_user.username==responsable).select(db.auth_user.id).first()
        if usuario:
            auth.del_membership(group_id=1, user_id=usuario)
            session.flash = T('Responsible deleted')
    else:
        session.flash = T('No delete current responsible')
    redirect(URL('show_responsibles'))
    return dict()

@auth.requires_membership(role='Responsables')
def show_responsibles():
    oprofesor = obies.Profesor(db, session)
    profesores = oprofesor.dame_profesores_curso()
    responsables = []
        
    for profesor in profesores:
        #comprobemos si el usuario existe en la tabla auth_user
        usuario = db(db.auth_user.username == profesor.profesor.usuario_rayuela).select(db.auth_user.ALL).first()
        if usuario:
            db(db.auth_user.id==usuario.id).select().first().update_record(first_name=profesor.profesor.nombre, last_name=profesor.profesor.apellidos)
            if auth.has_membership(role = 'Responsables', user_id = usuario.id):
                usu = Storage(usuario.as_dict())
                usua = db(usuario.username == db.profesor.usuario_rayuela).select(db.profesor.ALL).first()
                usu.idprofesor = usua.id
                responsables.append(usu)    
        else:
            #no existe usuario autentificación asociado al profesor
            id = db.auth_user.insert(username=profesor.profesor.usuario_rayuela, first_name=profesor.profesor.nombre, last_name=profesor.profesor.apellidos)
            auth.add_membership(role = 'Profesores', user_id = id)           
                  
    form = FORM(TABLE(TR(T('Teacher')+':', SELECT(_name='profe', *[OPTION(p.profesor.apellidos+', '+p.profesor.nombre, _value=p.profesor.usuario_rayuela) for p in profesores])),
                      TR("", INPUT(_type="submit",_value=T("Add responsible")))))
                      
    if form.accepts(request.vars, session):
        #debemos insertar al profesor en el grupo responsables
        usuario = db(db.auth_user.username==form.vars.profe).select(db.auth_user.id).first()
        if auth.has_membership(user_id=usuario, role='Responsables'):
            session.flash = T('Responsible already defined')
        else:
            auth.add_membership(role='Responsables', user_id=usuario)        
            session.flash = T('new responsible inserted')
        redirect(URL('show_responsibles'))                        
    return dict(form=form, responsables=responsables)

@auth.requires_membership(role='Profesores')
def departamento():
    if not session.profesor.esJefe:
        redirect(URL('default', 'index'))
    departamento = db.departamento(session.profesor.id_departamento)
    form = crud.update(db.departamento, departamento, deletable = False, create=False, next = URL('departamento'), message = T('Departamento actualizado'), onvalidation=valida_pesos)    
    return dict(form=form)

@auth.requires_membership(role='Profesores')
def asignaturas():
    if not session.profesor.esJefe:
        redirect(URL('default', 'index'))
    db.asignatura.id.readable=False
    db.asignatura.id_departamento.writable=False       
    grid = SQLFORM.grid(db.asignatura.id_departamento == session.profesor.id_departamento, paginate=10, ui='jquery-ui', maxtextlengths={'asignatura.abreviatura':10,'asignatura.asignatura':50}, csv=False, deletable=False, create=False, 
                        fields=[db.asignatura.id, db.asignatura.abreviatura, db.asignatura.asignatura], onvalidation=valida_pesos)
    return dict(grid = grid)

def valida_pesos(form):
    if form.vars.usar_criterios_departamento or form.vars.usar_criterios_asignatura:
        suma = form.vars.peso_1 + form.vars.peso_2 + form.vars.peso_3 + form.vars.peso_4 + form.vars.peso_5 + form.vars.peso_6
        if suma <> 100:
            form.errors.peso_6 = T('La suma de los porcentajes debe ser igual a 100')
