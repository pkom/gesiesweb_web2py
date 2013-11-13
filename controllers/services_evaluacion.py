# coding: utf8

# intente algo como
def index(): return dict(message="hello from services_evaluacion.py")

@auth.requires_login()
@auth.requires(auth.has_membership(role='Responsables') or auth.has_membership(role="Administrativos"))
def call():
    session.forget()
    return service()

@service.json
def getGrupoProfesorAsignaturas():
    fields = ['grupo','profesor','asignatura']  
    rows = []
    if request.vars._search == 'true':
        searching = True
    else:
        searching = False    
    page = int(request.vars.page)
    pagesize = int(request.vars.rows)    
    limitby = (page * pagesize - pagesize,page * pagesize)
    
    if (request.vars.sord == 'desc' and request.vars.sidx == 'grupo'): 
        orderby = (~db.grupo.grupo | db.profesor.apellidos | db.profesor.nombre | db.asignatura.asignatura) 
    elif (request.vars.sord == 'asc' and request.vars.sidx == 'grupo'): 
        orderby = (db.grupo.grupo | db.profesor.apellidos | db.profesor.nombre | db.asignatura.asignatura)
    elif (request.vars.sord == 'desc' and request.vars.sidx == 'profesor'): 
        orderby = (~db.profesor.apellidos | ~db.profesor.nombre | db.grupo.grupo | db.asignatura.asignatura) 
    elif (request.vars.sord == 'asc' and request.vars.sidx == 'profesor'): 
        orderby = (db.profesor.apellidos | db.profesor.nombre | db.grupo.grupo | db.asignatura.asignatura)
    elif (request.vars.sord == 'desc' and request.vars.sidx == 'asignatura'): 
        orderby = (~db.asignatura.asignatura | db.grupo.grupo | db.profesor.apellidos | db.profesor.nombre)
    elif (request.vars.sord == 'asc' and request.vars.sidx == 'asignatura'): 
        orderby = (db.asignatura.asignatura | db.grupo.grupo | db.profesor.apellidos | db.profesor.nombre)
    else:       
        orderby = ~orderby               
    
    queries=[]
    queries.append(db.curso_academico_grupo.id_curso_academico == session.curso_academico_id)
    queries.append(db.curso_academico_grupo.id_grupo == db.grupo.id)    
    queries.append(db.grupo_profesor.id_curso_academico_grupo == db.curso_academico_grupo.id)
    queries.append(db.grupo_profesor.id_profesor == db.profesor.id)
    queries.append(db.grupo_profesor_asignatura.id_grupo_profesor == db.grupo_profesor.id)
    queries.append(db.grupo_profesor_asignatura.id_asignatura == db.asignatura.id)
    
    if searching:
        if request.vars.grupo:
            grupo = '%'+request.vars.grupo.lower()+'%'           
            queries.append(db.grupo.grupo.lower().like(grupo))
        if request.vars.profesor:
            profesor = '%'+request.vars.profesor.lower()+'%'
            queries.append((db.profesor.apellidos.lower().like(profesor) | db.profesor.nombre.lower().like(profesor)))             
        if request.vars.asignatura:    
            asignatura = '%'+request.vars.asignatura.lower()+'%'
            queries.append(db.asignatura.asignatura.lower().like(asignatura)) 
    query = reduce(lambda a,b:(a&b),queries)

    for r in db(query).select(db.grupo_profesor_asignatura.ALL, db.grupo.ALL, db.profesor.ALL, db.asignatura.ALL, limitby=limitby,orderby=orderby):
        vals = []
        for f in fields:
            if f == 'profesor':
                profesor = r.profesor.apellidos+', '+r.profesor.nombre
                vals.append(profesor)                
            elif f == 'grupo':
                grupo = r.grupo.grupo
                vals.append(grupo)
            elif f == 'asignatura':
                asignatura = r.asignatura.asignatura
                vals.append(asignatura)                
            else:
                rep = db.grupo_profesor_asignatura[f].represent
                if rep:
                    vals.append(rep(r.grupo_profesor_asignatura[f]))
                else:
                    vals.append(r.grupo_profesor_asignatura[f])
        rows.append(dict(id=r.grupo_profesor_asignatura.id,cell=vals))
    total = db(query).count()    
    if total <= pagesize:
        pages = 1
    else:   
        pages = int(total/pagesize)
        if total % pagesize <> 0:
            pages += 1
    data = dict(total=pages,page=page,records=total,rows=rows)
    return data
    
@service.json
def addGrupoProfesorAsignatura():
    grupoprofesor = int(request.vars.profesor)
    asignatura = int(request.vars.asignatura)
    tipo = request.vars.action
    if ((grupoprofesor == 0) or (asignatura == 0)):
        respuesta = 'datosincorrectos'
    else:
        try:
            if (db((db.grupo_profesor_asignatura.id_grupo_profesor == grupoprofesor) & (db.grupo_profesor_asignatura.id_asignatura == asignatura)).count() > 0):
                respuesta = "duplicado"
                return dict(response=respuesta)                       
            if (tipo == "add"):
                db.grupo_profesor_asignatura.insert(id_grupo_profesor=grupoprofesor, id_asignatura=asignatura)
            elif (tipo == "modify"):
                db(db.grupo_profesor_asignatura.id == idasignacion).update(id_grupo_alumno=grupoprofesor,
                                                      id_asignatura=asignatura)
                                       
            db.commit()
            respuesta = 'OK'    
        except:
            respuesta = 'fallo'    
    return dict(response=respuesta)

@service.json
def deleteAsignacion():
    idasignacion = int(request.vars.idasignacion)
    try:      
        #borramos
        db(db.grupo_profesor_asignatura.id == idasignacion).delete()
        db.commit()
        respuesta = 'OK'
    except:
        respuesta = 'fallo'    
    return dict(response=respuesta)

@service.json
def deleteAlumno():
    idalumno = int(request.vars.idalumno)
    try:      
        #borramos
        db(db.grupo_profesor_asignatura_alumno.id == idalumno).delete()
        db.commit()
        respuesta = 'OK'
    except:
        respuesta = 'fallo'    
    return dict(response=respuesta)

@service.json
def getAlumnos():
    fields = ['alumno']  
    rows = []
    if request.vars._search == 'true':
        searching = True
    else:
        searching = False    
        
    id_grupo_profesor_asignatura = int(request.vars.id)

    page = int(request.vars.page)
    pagesize = int(request.vars.rows)    
    limitby = (page * pagesize - pagesize,page * pagesize)
    
    queries=[]
    queries.append(db.grupo_profesor_asignatura.id == id_grupo_profesor_asignatura)    
    queries.append(db.grupo_profesor_asignatura_alumno.id_grupo_profesor_asignatura == db.grupo_profesor_asignatura.id)
    queries.append(db.grupo_profesor_asignatura_alumno.id_grupo_alumno == db.grupo_alumno.id)
    queries.append(db.grupo_alumno.id_alumno == db.alumno.id)

    query = reduce(lambda a,b:(a&b),queries)        
        
    for r in db(query).select(db.alumno.ALL, db.grupo_alumno.ALL, db.grupo_profesor_asignatura.ALL, db.grupo_profesor_asignatura_alumno.ALL,
                                 limitby=limitby,orderby=db.alumno.apellidos | db.alumno.nombre):
        vals = []
        for f in fields:
            if f == 'alumno':
                alumno = r.alumno.apellidos+', '+r.alumno.nombre
                vals.append(alumno)                
            else:
                pass
        rows.append(dict(id=r.grupo_profesor_asignatura_alumno.id,cell=vals))
    total = db(query).count()    
    if total <= pagesize:
        pages = 1
    else:   
        pages = int(total/pagesize)
        if total % pagesize <> 0:
            pages += 1
    data = dict(total=pages,page=page,records=total,rows=rows)
    return data
    
@service.json
def asignaAlumnos():
    idasignacion = int(request.vars.idasignacion)
    if (idasignacion == 0):
        respuesta = 'datosincorrectos'
    else:
        try:
            # solo añadiremos los alumnos que no hayan sido asignados ya a esa asignatura
            # recupero el id_asignatura
            # tengo que obtener el grupo a partir de idasignatura que se ha pasado como parámetro
            grupo_profesor_asignatura = db.grupo_profesor_asignatura(idasignacion)
            # para ello accedo a id_grupo_profesor actual de la asignatura
            id_grupo_profesor = grupo_profesor_asignatura.id_grupo_profesor
            id_asignatura = grupo_profesor_asignatura.id_asignatura
            # veamos si hay más asignaciones de la misma asignatura a otro profesor           
            # localizo el id_curso_academico_grupo de grupo_profesor
            grupo_profesor = db.grupo_profesor(id_grupo_profesor)
            id_curso_academico_grupo = grupo_profesor.id_curso_academico_grupo
            # creamos lista de profesores asignados excluyendo el mismo y que tengan la misma asignatura asignada
            otros_profesores_asignatura = db((db.grupo_profesor.id_curso_academico_grupo == id_curso_academico_grupo) &
                                            (db.grupo_profesor.id <> id_grupo_profesor) &
                                            (db.grupo_profesor_asignatura.id_grupo_profesor == db.grupo_profesor.id) &
                                            (db.grupo_profesor_asignatura.id_asignatura == id_asignatura)).select(db.grupo_profesor_asignatura.id)
            # filtro grupo_alumno con el id_curso_academico_grupo
            alumnos = db(db.grupo_alumno.id_curso_academico_grupo == id_curso_academico_grupo).select(db.grupo_alumno.ALL)
            # añadamos los alumno
            db.grupo_profesor_asignatura_alumno.id_grupo_profesor_asignatura.default = idasignacion
            for alumno in alumnos:
                # solo insertaremos si no existe esa entrada o bien no está en otro profesor misma asignatura
                if (db((db.grupo_profesor_asignatura_alumno.id_grupo_profesor_asignatura == idasignacion) &
                        (db.grupo_profesor_asignatura_alumno.id_grupo_alumno == alumno.id)).count() == 0):
                    esta = False    
                    # creo que de momento permitiré que los alumnos puedan ser asignados libremente a misma asignatura y otro profesor
                    # evitando la comprobación de que esté ya asignado, para evitar problemas con las sustituciones del profesorado
                    # y evaluaciones ya efectuadas.
                    #for id_grupo_profesor_asignatura in otros_profesores_asignatura:
                    #    if db((db.grupo_profesor_asignatura_alumno.id_grupo_profesor_asignatura == id_grupo_profesor_asignatura) &
                    #        (db.grupo_profesor_asignatura_alumno.id_grupo_alumno == alumno.id)).count() > 0:
                    #        esta = True
                    if not esta:        
                        db.grupo_profesor_asignatura_alumno.insert(id_grupo_alumno=alumno.id)                                      
            db.commit()
            respuesta = 'OK'    
        except:
            respuesta = 'fallo'    
    return dict(response=respuesta)

@service.json
def crearFichasEvaluacion():
    idevaluacion = int(request.args[0])
    if (idevaluacion == 0):
        respuesta = 'datosincorrectos'
    else:
        try:
            # todos los grupos asignados a profesores asignaturas y alumnos
            filas = db((db.grupo_profesor_asignatura_alumno.id_grupo_profesor_asignatura == db.grupo_profesor_asignatura.id) &
            (db.grupo_profesor_asignatura.id_grupo_profesor == db.grupo_profesor.id) &
            (db.grupo_profesor.id_curso_academico_grupo == db.curso_academico_grupo.id) &
            (db.curso_academico_grupo.id_curso_academico == db.curso_academico.id) &
            (db.curso_academico.id == session.curso_academico_id)).select()           
            # solo añadiremos los alumnos a evaluar que no tengan la ficha creada
            for fila in filas:
                # veo que no esté creada la ficha
                if db((db.evaluacion_alumno.id_curso_academico_evaluacion==idevaluacion) &
                      (db.evaluacion_alumno.id_grupo_profesor_asignatura_alumno==fila.grupo_profesor_asignatura_alumno.id)).count() == 0:
                    # no está creada la ficha a crearla
                    db.evaluacion_alumno.insert(id_curso_academico_evaluacion=idevaluacion,
                                                id_grupo_profesor_asignatura_alumno=fila.grupo_profesor_asignatura_alumno.id)
            db.commit()
            respuesta = 'OK'    
        except:
            respuesta = 'fallo'    
    return respuesta
