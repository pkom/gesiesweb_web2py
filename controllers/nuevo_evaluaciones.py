# coding: utf8
# intente algo como
def index(): return dict(message="hello from nuevo_evaluaciones.py")

@auth.requires_login()
@auth.requires_membership(role='Profesores')
def mis_evaluaciones():
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
                  _href=URL('nuevo_evaluaciones','mi_evaluacion', user_signature=True, args=[evaluacion.id,row.grupo_profesor_asignatura.id])) for evaluacion in evaluaciones])))
    grid = SQLFORM.grid(query,ui='jquery-ui',field_id=db.grupo_profesor_asignatura.id,deletable=False,create=False,editable=False,csv=False,details=False,searchable=False,
                        fields=[db.grupo.grupo, db.asignatura.asignatura, db.profesor.apellidos,db.profesor.nombre,db.grupo_profesor_asignatura.id],links=links,
                        orderby=db.grupo.grupo|db.asignatura.asignatura)
    return dict(grid=grid)

@auth.requires_login()
@auth.requires_membership(role='Profesores')
@auth.requires_signature(True)
def mi_evaluacion_old():
    # tenemos que recuperar los parámetros de evaluación e id_grupo_profesor_asignatura
    evaluacion = db.curso_academico_evaluacion(request.args(0)) or redirect(URL('mis_evaluaciones'))
    id_grupo_profesor_asignatura = request.args(1) or redirect(URL('mis_evaluaciones'))
    # veamos grupo y asignatura
    asignatura = db.grupo_profesor_asignatura(id_grupo_profesor_asignatura).id_asignatura.asignatura
    asignatura += ' ('+db.grupo_profesor_asignatura(id_grupo_profesor_asignatura).id_asignatura.abreviatura+')'
    grupo = db.grupo_profesor_asignatura(id_grupo_profesor_asignatura).id_grupo_profesor.id_curso_academico_grupo.id_grupo.grupo
    query = ((db.grupo_profesor_asignatura_alumno.id_grupo_profesor_asignatura == id_grupo_profesor_asignatura) &
             (db.evaluacion_alumno.id_grupo_profesor_asignatura_alumno == db.grupo_profesor_asignatura_alumno.id) &
             (db.grupo_profesor_asignatura_alumno.id_grupo_alumno == db.grupo_alumno.id) &
             (db.grupo_alumno.id_alumno == db.alumno.id)
             )
    links = [dict(header=T('Alumn@'),body=lambda row:row.alumno.apellidos+', '+row.alumno.nombre)]
    db.alumno.apellidos.readable=False
    db.alumno.nombre.readable=False
    db.evaluacion_alumno.nivel.represent = lambda nivel,row:{100:"Sobresal.10",90:"Sobresal. 9",
                                                     80:"Notable 8",70:"Notable 7",60:"Bien",
                                                     50:"Suficiente",40:"Insufic. 4",
                                                     30:"Insufic. 3",20:"Insufic. 2",
                                                     10:"Insufic. 1",0:"Abandono"}[nivel]
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

    observacioneshtml =  A('observaciones' ,_href="javascript:void(0);", _onmouseover="return overlib('+db.evaluacion_alumno.observaciones+');", _onmouseout="return nd();")
    db.evaluacion_alumno.observaciones.represent = lambda value, row: DIV(value if value else '-',_class='observaciones', _id=str(row.evaluacion_alumno.id)+'.observaciones')
    #db.evaluacion_alumno.observaciones.represent = observacioneshtml


    grid = SQLFORM.grid(query,ui='jquery-ui',field_id=db.evaluacion_alumno.id,deletable=False,create=False,editable=False,csv=False,details=False,searchable=False,
                        paginate=0,sortable=False,links=links,links_placement='left',headers=headers,
                        fields=[db.alumno.apellidos,db.alumno.nombre,db.evaluacion_alumno.nivel,
                                db.evaluacion_alumno.trabajo_clase,db.evaluacion_alumno.trabajo_casa,
                                db.evaluacion_alumno.interes,db.evaluacion_alumno.participa,db.evaluacion_alumno.comportamiento,db.evaluacion_alumno.evaluacion,
                                db.evaluacion_alumno.observaciones],orderby=db.alumno.apellidos|db.alumno.nombre)
    return dict(grid=grid,evaluacion=evaluacion,asignatura=asignatura,grupo=grupo)

@auth.requires_login()
@auth.requires_membership(role='Profesores')
@auth.requires_signature(True)
def mi_evaluacion():
    # tenemos que recuperar los parámetros de evaluación e id_grupo_profesor_asignatura
    evaluacion = db.curso_academico_evaluacion(request.args(0)) or redirect(URL('mis_evaluaciones'))
    id_grupo_profesor_asignatura = request.args(1) or redirect(URL('mis_evaluaciones'))
    # veamos grupo y asignatura
    asignatura = db.grupo_profesor_asignatura(id_grupo_profesor_asignatura).id_asignatura.asignatura
    asignatura += ' ('+db.grupo_profesor_asignatura(id_grupo_profesor_asignatura).id_asignatura.abreviatura+')'
    grupo = db.grupo_profesor_asignatura(id_grupo_profesor_asignatura).id_grupo_profesor.id_curso_academico_grupo.id_grupo.grupo
    query = ((db.grupo_profesor_asignatura_alumno.id_grupo_profesor_asignatura == id_grupo_profesor_asignatura) &
             (db.evaluacion_alumno.id_grupo_profesor_asignatura_alumno == db.grupo_profesor_asignatura_alumno.id) &
             (db.grupo_profesor_asignatura_alumno.id_grupo_alumno == db.grupo_alumno.id) &
             (db.grupo_alumno.id_alumno == db.alumno.id)
             )
    links = [dict(header=T('Alumn@'),body=lambda row:row.alumno.apellidos+', '+row.alumno.nombre)]
    db.alumno.apellidos.readable=False
    db.alumno.nombre.readable=False
    db.evaluacion_alumno.nivel.represent = lambda nivel,row:{100:"Sobresal.10",90:"Sobresal. 9",
                                                     80:"Notable 8",70:"Notable 7",60:"Bien",
                                                     50:"Suficiente",40:"Insufic. 4",
                                                     30:"Insufic. 3",20:"Insufic. 2",
                                                     10:"Insufic. 1",0:"Abandono"}[nivel]
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

    observacioneshtml =  A('observaciones' ,_href="javascript:void(0);", _onmouseover="return overlib('+db.evaluacion_alumno.observaciones+');", _onmouseout="return nd();")
    db.evaluacion_alumno.observaciones.represent = lambda value, row: DIV(value if value else '-',_class='observaciones', _id=str(row.evaluacion_alumno.id)+'.observaciones')
    #db.evaluacion_alumno.observaciones.represent = observacioneshtml


    grid = SQLFORM.grid(query,ui='jquery-ui',field_id=db.evaluacion_alumno.id,deletable=False,create=False,editable=False,csv=False,details=False,searchable=False,
                        paginate=0,sortable=False,links=links,links_placement='left',headers=headers,
                        fields=[db.alumno.apellidos,db.alumno.nombre,db.evaluacion_alumno.nivel,
                                db.evaluacion_alumno.trabajo_clase,db.evaluacion_alumno.trabajo_casa,
                                db.evaluacion_alumno.interes,db.evaluacion_alumno.participa,db.evaluacion_alumno.comportamiento,db.evaluacion_alumno.evaluacion,
                                db.evaluacion_alumno.observaciones],orderby=db.alumno.apellidos|db.alumno.nombre)
    return dict(grid=grid,evaluacion=evaluacion,asignatura=asignatura,grupo=grupo,id_grupo_profesor_asignatura=id_grupo_profesor_asignatura)

