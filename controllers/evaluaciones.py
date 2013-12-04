# coding: utf8

crud.settings.controller = 'evaluaciones' 

def index(): return dict(message="hello from evaluaciones.py")

@auth.requires_login()
@auth.requires(auth.has_membership(role='Responsables') or auth.has_membership(role="Administrativos"))
def show_asignaturas():
    grid = SQLFORM.grid(db.asignatura, paginate=10, ui='jquery-ui', maxtextlengths={'asignatura.abreviatura':10,'asignatura.asignatura':50}, csv=False,
                        fields=[db.asignatura.id, db.asignatura.abreviatura, db.asignatura.asignatura], onvalidation=valida_pesos)
    return dict(grid = grid)

def valida_pesos(form):
    if form.vars.usar_criterios_asignatura:
        suma = form.vars.peso_1 + form.vars.peso_2 + form.vars.peso_3 + form.vars.peso_4 + form.vars.peso_5 + form.vars.peso_6
        if suma <> 100:
            form.errors.peso_6 = T('La suma de los porcentajes debe ser igual a 100')

@auth.requires_login()     
@auth.requires_membership(role='Responsables')
def show_evaluaciones():
    db.curso_academico_evaluacion.id_curso_academico.default = session.curso_academico_id
    query = db.curso_academico_evaluacion.id_curso_academico == session.curso_academico_id
    grid = SQLFORM.grid(query, paginate=10, ui='jquery-ui', orderby=db.curso_academico_evaluacion.evaluacion,searchable=False,onvalidation=comprueba_evaluacion,
                         fields=[db.curso_academico_evaluacion.evaluacion,db.curso_academico_evaluacion.fecha,db.curso_academico_evaluacion.bloqueada],
                         csv=False, maxtextlengths={'curso_academico_evaluacion.evaluacion':50,'curso_academico_evaluacion.fecha':15},
                         links=[dict(header='Procesos',body=lambda row: BUTTON('Crear fichas', _title='Generar fichas de evaluación de los alumnos', 
                         _onclick="ajax('%s',[]);"%URL(c='services_evaluacion',f='crearFichasEvaluacion',args=[row.id])))],
                         links_placement='left')
    return dict(grid = grid)
    
def comprueba_evaluacion(form):
    # comprobemos que no hayamos definido ya una evaluación
    if request.args(-2) == 'new':
        evaluacion = form.vars.evaluacion
        if db((db.curso_academico_evaluacion.id_curso_academico == session.curso_academico_id) &
            (db.curso_academico_evaluacion.evaluacion.lower() == evaluacion.lower())).count() > 0:
            form.errors.evaluacion = "Evaluación ya existente"

@auth.requires_login()
@auth.requires(auth.has_membership(role='Responsables') or auth.has_membership(role="Administrativos"))
def show_grupo_profesor_asignaturas(): 
    return dict(message="hello from grupo_profesor_asignaturas for responsibles")  

@auth.requires_login()
@auth.requires_membership(role='Responsables')
def show_grupo_profesor_asignaturas_old():
    query = (db.curso_academico_grupo.id_curso_academico == session.curso_academico_id) \
             & (db.curso_academico_grupo.id_grupo == db.grupo.id) \
             & (db.curso_academico_grupo.id == db.grupo_profesor.id_curso_academico_grupo) \
             & (db.grupo_profesor.id_profesor == db.profesor.id) \
             & (db.grupo_profesor.id == db.grupo_profesor_asignatura.id_grupo_profesor) \
             & (db.grupo_profesor_asignatura.id_asignatura == db.asignatura.id)                     
    grid = SQLFORM.grid(query, paginate=10, ui='jquery-ui', field_id=db.grupo_profesor_asignatura.id, 
                        fields=[db.grupo.grupo,db.profesor.apellidos,db.profesor.nombre,db.asignatura.asignatura], csv=False,
                        headers={'profesor.apellidos':'Apellidos del profesor/a','profesor.nombre':'Nombre del profesor/a','asignatura.asignatura':'Asignatura impartida'},
                        maxtextlengths={'profesor.apellidos':60,'profesor.nombre':40,'asignatura.asignatura':80},
                        orderby=db.grupo.grupo)
    #check if form is a create form
    if  len(request.args)>1 and request.args[-2]=='new' and grid.create_form:
        grupodiv = TR(LABEL('Grupo'),INPUT(_name='grupo',_type='select'))
        grid.create_form[0].insert(0,grupodiv)    
        profesordiv = TR(LABEL('Profesor'),INPUT(_name='profesor',_type='select'))
        grid.create_form[0].insert(1,profesordiv)    
    return dict(grid = grid)

@auth.requires_login()        
@auth.requires_membership(role='Responsables')    
def form(): 
    return dict(message="hello from form")

@auth.requires_login()        
@auth.requires_membership(role='Profesores')    
def form_evaluacion(): 
    return dict(message="hello from form_evaluacion")

@auth.requires_login()
@auth.requires_membership(role='Profesores')    
def evaluacion():
    return dict(message="hello from evaluacion profesor")

@auth.requires_login()
@auth.requires_membership(role='Profesores')    
def evaluacionestutoria():
    return dict(message="hello from evaluacion para tutores")
