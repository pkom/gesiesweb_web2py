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
@auth.requires_membership(role='Responsables')    
def form_alumnos_asignaturas(): 
    form=FORM(DIV(TABLE(),
                  _id="contenedor",_style="width:75%;float:left;"),_id="form_data_alumnos_asignaturas")
    return dict(form=form)

@auth.requires_login()        
@auth.requires_membership(role='Profesores')    
def form_evaluacion(): 
    return dict(message="hello from form_evaluacion")

@auth.requires_login()
@auth.requires_membership(role='Profesores')    
def evaluacion_old():
    return dict(message="hello from evaluacion profesor")

@auth.requires_login()
@auth.requires_membership(role='Profesores')    
def evaluacion():
    query = ((db.grupo_profesor.id_profesor == session.profesor.id) &
             (db.grupo_profesor.id_curso_academico_grupo == db.curso_academico_grupo.id) &
             (db.curso_academico_grupo.id_curso_academico == session.curso_academico_id) &
             (db.curso_academico_grupo.id_grupo == db.grupo.id) &
             (db.grupo_profesor_asignatura.id_grupo_profesor == db.grupo_profesor.id) &
             (db.grupo_profesor_asignatura.id_asignatura == db.asignatura.id) &
             (db.curso_academico_grupo.id_tutor == db.profesor.id))
    evaluaciones = db(db.curso_academico_evaluacion.id_curso_academico == session.curso_academico_id).select(orderby=db.curso_academico_evaluacion.evaluacion)
    db.grupo_profesor_asignatura.id.readable = False
    db.profesor.apellidos.readable = False
    db.profesor.nombre.readable = False
    links = [dict(header=T('Tutor/a'),body=lambda row:row.profesor.apellidos+', '+row.profesor.nombre)]
    links.append(dict(header=CENTER(T('Evaluaciones')),body=lambda row:CENTER([A(SPAN(_class='icon magnifier'
                                     if evaluacion.bloqueada else 'icon pen'),evaluacion.evaluacion.split()[0],
                  _class='button',_title=evaluacion.evaluacion,
                  _href=URL('evaluaciones','mi_evaluacion', user_signature=True, args=[evaluacion.id,row.grupo_profesor_asignatura.id])) for evaluacion in evaluaciones])))
    grid = SQLFORM.grid(query,ui='jquery-ui',field_id=db.grupo_profesor_asignatura.id,deletable=False,create=False,editable=False,csv=False,details=False,searchable=False,
                        fields=[db.grupo.grupo, db.asignatura.asignatura, db.profesor.apellidos,db.profesor.nombre,db.grupo_profesor_asignatura.id],links=links,
                        orderby=db.grupo.grupo|db.asignatura.asignatura)
    return dict(grid=grid)

@auth.requires_login()
@auth.requires_membership(role='Profesores')
@auth.requires_signature(True)
def mi_evaluacion():
    # tenemos que recuperar los parámetros de evaluación e id_grupo_profesor_asignatura
    evaluacion = db.curso_academico_evaluacion(request.args(0)) or redirect(URL('mis_evaluaciones'))
    id_grupo_profesor_asignatura = request.args(1) or redirect(URL('mis_evaluaciones'))
    # veamos grupo y asignatura
    grupo = db.grupo_profesor_asignatura(id_grupo_profesor_asignatura).id_grupo_profesor.id_curso_academico_grupo.id_grupo.grupo
    asignatura = db.grupo_profesor_asignatura(id_grupo_profesor_asignatura).id_asignatura.asignatura
    asignatura += ' ('+db.grupo_profesor_asignatura(id_grupo_profesor_asignatura).id_asignatura.abreviatura+')'
    profesor = db.grupo_profesor_asignatura(id_grupo_profesor_asignatura).id_grupo_profesor.id_profesor.apellidos+', '+ \
               db.grupo_profesor_asignatura(id_grupo_profesor_asignatura).id_grupo_profesor.id_profesor.nombre
    caption = evaluacion.evaluacion+' ('+(T('Bloqueada') if evaluacion.bloqueada else 
                 T('Abierta'))+') '+ T('del grupo')+': '+grupo+' '+T('de la asignatura')+': '+asignatura+' '+T('Profesor/a: '+profesor)
    return dict(evaluacion=evaluacion,id_grupo_profesor_asignatura=id_grupo_profesor_asignatura,caption=caption)

@auth.requires_login()
@auth.requires_membership(role='Profesores')    
def evaluaciones_tutoria():
    # comprobemos que somos tutores, sino nada
    if not session.profesor.esTutor:
        redirect(URL("default","index"))
   
    query = ((db.grupo_profesor.id_curso_academico_grupo == session.profesor.tutor.id_curso_academico_grupo) &
             (db.grupo_profesor.id_profesor == db.profesor.id) &
             (db.grupo_profesor.id == db.grupo_profesor_asignatura.id_grupo_profesor) &
             (db.grupo_profesor_asignatura.id_asignatura == db.asignatura.id)) 

    evaluaciones = db(db.curso_academico_evaluacion.id_curso_academico == session.curso_academico_id).select(orderby=db.curso_academico_evaluacion.evaluacion)
    links = [dict(header=T('Profesor/a'),body=lambda row:row.profesor.apellidos+', '+row.profesor.nombre)]
    links.append(dict(header=CENTER(T('Evaluaciones')),body=lambda row:CENTER([A(SPAN(_class='icon magnifier'),evaluacion.evaluacion.split()[0],
                  _class='button',_title=evaluacion.evaluacion,
                  _href=URL('evaluaciones','evaluacion_tutoria', user_signature=True, args=[evaluacion.id,row.grupo_profesor_asignatura.id])) for evaluacion in evaluaciones])))
    db.profesor.apellidos.readable = False
    db.profesor.nombre.readable = False
    db.grupo_profesor_asignatura.id.readable = False
    grid = SQLFORM.grid(query,ui='jquery-ui',field_id=db.grupo_profesor_asignatura.id,deletable=False,create=False,editable=False,csv=False,details=False,searchable=False,
                        fields=[db.asignatura.asignatura, db.asignatura.abreviatura, db.profesor.apellidos,db.profesor.nombre,db.grupo_profesor_asignatura.id],
                        links=links,orderby=db.asignatura.abreviatura)
    return dict(grid=grid)


@auth.requires_login()
@auth.requires_membership(role='Profesores')
@auth.requires_signature(True)
def evaluacion_tutoria():
    # tenemos que recuperar los parámetros de evaluación e id_grupo_profesor_asignatura
    evaluacion = db.curso_academico_evaluacion(request.args(0)) or redirect(URL('mis_evaluaciones'))
    id_grupo_profesor_asignatura = request.args(1) or redirect(URL('mis_evaluaciones'))
    # veamos grupo y asignatura
    asignatura = db.grupo_profesor_asignatura(id_grupo_profesor_asignatura).id_asignatura.asignatura
    asignatura += ' ('+db.grupo_profesor_asignatura(id_grupo_profesor_asignatura).id_asignatura.abreviatura+')'
    grupo = db.grupo_profesor_asignatura(id_grupo_profesor_asignatura).id_grupo_profesor.id_curso_academico_grupo.id_grupo.grupo
    profesor = db.grupo_profesor_asignatura(id_grupo_profesor_asignatura).id_grupo_profesor.id_profesor.apellidos+", "
    profesor += db.grupo_profesor_asignatura(id_grupo_profesor_asignatura).id_grupo_profesor.id_profesor.nombre
    query = ((db.grupo_profesor_asignatura_alumno.id_grupo_profesor_asignatura == id_grupo_profesor_asignatura) &
             (db.evaluacion_alumno.id_curso_academico_evaluacion == evaluacion.id) &      
             (db.evaluacion_alumno.id_grupo_profesor_asignatura_alumno == db.grupo_profesor_asignatura_alumno.id) &
             (db.grupo_profesor_asignatura_alumno.id_grupo_alumno == db.grupo_alumno.id) &
             (db.grupo_alumno.id_alumno == db.alumno.id)
             )
    links = [dict(header=T('Alumn@'),body=lambda row:row.alumno.apellidos+', '+row.alumno.nombre)]
    db.alumno.apellidos.readable=False
    db.alumno.nombre.readable=False
    db.evaluacion_alumno.trabajo_clase.represent = lambda trabajo_clase,row:{100:"Habitualm.",75:"A veces",50:"Casi nunca",0:"Nunca"}[trabajo_clase]
    db.evaluacion_alumno.trabajo_casa.represent = lambda trabajo_casa,row:{100:"Habitualm.",75:"A veces",50:"Casi nunca",0:"Nunca"}[trabajo_casa]
    db.evaluacion_alumno.interes.represent = lambda interes,row:{100:"Mucho",75:"Normal",50:"Poco",0:"Nada"}[interes]
    db.evaluacion_alumno.participa.represent = lambda participa,row:{100:"Mucho",75:"Normal",50:"Poco",0:"Nada"}[participa]
    db.evaluacion_alumno.comportamiento.represent = lambda comportamiento,row:{100:"Muy bueno",75:"Bueno",50:"Puede mejorar",0:"Disruptivo"}[comportamiento]
    
    headers={'evaluacion_alumno.trabajo_clase':T('T.Clase'),'evaluacion_alumno.trabajo_casa':T('T.Casa'),'evaluacion_alumno.interes':T('Interés'),
             'evaluacion_alumno.comportamiento':T('Comport.'),'evaluacion_alumno.evaluacion':T('Global'),'evaluacion_alumno.observaciones':T('Observ.')}

    db.evaluacion_alumno.nivel.represent = lambda value, row: DIV(value if value else '-',_class='nivel', _id=str(row.evaluacion_alumno.id)+'.nivel')
    db.evaluacion_alumno.trabajo_clase.represent = lambda value, row: DIV({100:"Habitualm.",75:"A veces",50:"Casi nunca",0:"Nunca"}[value] if value else 'No eval.',
                                                                          _class='trabajo_clase', _id=str(row.evaluacion_alumno.id)+'.trabajo_clase')

#    observacioneshtml =  A('observaciones' ,_href="javascript:void(0);", _onmouseover="return overlib('+db.evaluacion_alumno.observaciones+');", _onmouseout="return nd();")
#    db.evaluacion_alumno.observaciones.represent = lambda value, row: DIV(value if value else '-',_class='observaciones', _id=str(row.evaluacion_alumno.id)+'.observaciones')

    db.evaluacion_alumno.observaciones.represent = lambda value, row: DIV(
        A('****' ,_href="javascript:void(0);", _onmouseover="return overlib('"+row.evaluacion_alumno.observaciones+"', CSSSTYLE, TEXTSIZEUNIT);", _onmouseout="return nd();")
        if value else '-',_class='observaciones', _id=str(row.evaluacion_alumno.id)+'.observaciones')


    caption = evaluacion.evaluacion+' ('+(T('Bloqueada') if evaluacion.bloqueada else 
                 T('Abierta'))+') '+ T('del grupo')+': '+grupo+' '+T('de la asignatura')+': '+asignatura+' '+T('Profesor/a: '+profesor)

    grid = SQLFORM.grid(query,ui='jquery-ui',field_id=db.evaluacion_alumno.id,deletable=False,create=False,editable=False,csv=False,details=False,searchable=False,
                        paginate=0,sortable=False,links=links,links_placement='left',headers=headers,
                        fields=[db.alumno.apellidos,db.alumno.nombre,db.evaluacion_alumno.nivel,
                                db.evaluacion_alumno.trabajo_clase,db.evaluacion_alumno.trabajo_casa,
                                db.evaluacion_alumno.interes,db.evaluacion_alumno.participa,db.evaluacion_alumno.comportamiento,db.evaluacion_alumno.evaluacion,
                                db.evaluacion_alumno.observaciones],orderby=db.alumno.apellidos|db.alumno.nombre)
    return dict(grid=grid,evaluacion=evaluacion,asignatura=asignatura,grupo=grupo,caption=caption)


@auth.requires_login()
@auth.requires_membership(role='Profesores')    
def evaluacionestutoria():
    # comprobemos que somos tutores, sino nada
    if not session.profesor.esTutor:
        redirect(URL("default","index"))
    return dict(message="hello from evaluacion para tutores")
