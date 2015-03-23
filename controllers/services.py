# coding: utf8
import delays

# intente algo como
def index(): return dict(message="hello from services.py")

@auth.requires_login()
@auth.requires(auth.has_membership(role='Responsables') or auth.has_membership(role="Administrativos") or auth.has_membership(role='Profesores'))
def call():
#    session.forget()
    return service()

@service.json
def getMyWarnings():
    #db.amonestacion.id_grupo_alumno.represent = lambda alumno: alumno.id_alumno.apellidos+', '+alumno.id_alumno.nombre+' ('+alumno.id_grupo.grupo+')'
    fields = ['id','fecha','grupo','alumno','parte','comunicada','cerrada']  
    rows = []
    if request.vars._search == 'true':
        searching = True
    else:
        searching = False    
    page = int(request.vars.page)
    pagesize = int(request.vars.rows)    
    limitby = (page * pagesize - pagesize,page * pagesize)
    
    if (request.vars.sord == 'desc' and request.vars.sidx == 'alumno'): 
        orderby = (~db.alumno.apellidos | ~db.alumno.nombre | ~db.amonestacion.fecha)
    elif (request.vars.sord == 'asc' and request.vars.sidx == 'alumno'): 
        orderby = (db.alumno.apellidos | db.alumno.nombre | ~db.amonestacion.fecha)
    elif (request.vars.sord == 'desc' and request.vars.sidx == 'fecha'):
        orderby = (~db.amonestacion.fecha | ~db.amonestacion.id)
    elif (request.vars.sord == 'asc' and request.vars.sidx == 'fecha'):
        orderby = (db.amonestacion.fecha | db.amonestacion.id)
    elif (request.vars.sord == 'asc' and request.vars.sidx == 'id'):
        orderby = db.amonestacion.id
    elif (request.vars.sord == 'desc' and request.vars.sidx == 'id'):
        orderby = ~db.amonestacion.id
    elif (request.vars.sord == 'asc' and request.vars.sidx == 'grupo'):
        orderby = (db.grupo.grupo | db.alumno.apellidos | db.alumno.nombre | ~db.amonestacion.fecha)
    elif (request.vars.sord == 'desc' and request.vars.sidx == 'grupo'):
        orderby = (~db.grupo.grupo | db.alumno.apellidos | db.alumno.nombre | ~db.amonestacion.fecha)        
    else:       
        orderby = ~orderby               

    
    queries=[]
    queries.append(db.amonestacion.id_departamento_profesor == session.profesor.id_departamento_profesor)
    queries.append(db.amonestacion.id_grupo_alumno == db.grupo_alumno.id)
    queries.append(db.grupo_alumno.id_curso_academico_grupo == db.curso_academico_grupo.id)
    queries.append(db.curso_academico_grupo.id_grupo == db.grupo.id)    
    queries.append(db.grupo_alumno.id_alumno == db.alumno.id)
    
    if searching:
        if request.vars.fecha:
            fecha = request.vars.fecha
            queries.append(db.amonestacion.fecha >= fecha)
        if request.vars.alumno:
            alumno = '%'+request.vars.alumno.lower()+'%'
            queries.append((db.alumno.apellidos.lower().like(alumno) | db.alumno.nombre.lower().like(alumno))) 
        if request.vars.grupo:    
            grupo = '%'+request.vars.grupo.lower()+'%'
            queries.append(db.grupo.grupo.lower().like(grupo)) 
    query = reduce(lambda a,b:(a&b),queries)

    for r in db(query).select(db.amonestacion.ALL,db.grupo.ALL,db.alumno.ALL,limitby=limitby,orderby=orderby):
        vals = []
        for f in fields:
            if f == 'alumno':
                alumno = r.alumno.apellidos+', '+r.alumno.nombre
                vals.append(alumno)
            elif f == 'grupo':
                grupo = r.grupo.grupo
                vals.append(grupo)
            else:
                rep = db.amonestacion[f].represent
                if rep:
                    vals.append(rep(r.amonestacion[f]))
                else:
                    vals.append(r.amonestacion[f])
        rows.append(dict(id=r.amonestacion.id,cell=vals))
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
def getMyWarningsTutor():
    #db.amonestacion.id_grupo_alumno.represent = lambda alumno: alumno.id_alumno.apellidos+', '+alumno.id_alumno.nombre+' ('+alumno.id_grupo.grupo+')'
    fields = ['id','fecha','profesor','alumno','parte','comunicada','cerrada']  
    rows = []
    if request.vars._search == 'true':
        searching = True
    else:
        searching = False    
    page = int(request.vars.page)
    pagesize = int(request.vars.rows)    
    limitby = (page * pagesize - pagesize,page * pagesize)
    
    if (request.vars.sord == 'desc' and request.vars.sidx == 'alumno'): 
        orderby = (~db.alumno.apellidos | ~db.alumno.nombre | ~db.amonestacion.fecha)
    elif (request.vars.sord == 'asc' and request.vars.sidx == 'alumno'): 
        orderby = (db.alumno.apellidos | db.alumno.nombre | ~db.amonestacion.fecha)
    elif (request.vars.sord == 'desc' and request.vars.sidx == 'profesor'): 
        orderby = (~db.profesor.apellidos | ~db.profesor.nombre | ~db.amonestacion.fecha)
    elif (request.vars.sord == 'asc' and request.vars.sidx == 'profesor'): 
        orderby = (db.profesor.apellidos | db.profesor.nombre | ~db.amonestacion.fecha)       
    elif (request.vars.sord == 'desc' and request.vars.sidx == 'fecha'):
        orderby = (~db.amonestacion.fecha | ~db.amonestacion.id)
    elif (request.vars.sord == 'asc' and request.vars.sidx == 'fecha'):
        orderby = (db.amonestacion.fecha | db.amonestacion.id)
    elif (request.vars.sord == 'asc' and request.vars.sidx == 'id'):
        orderby = db.amonestacion.id
    elif (request.vars.sord == 'desc' and request.vars.sidx == 'id'):
        orderby = ~db.amonestacion.id
    elif (request.vars.sord == 'asc' and request.vars.sidx == 'grupo'):
        orderby = (db.grupo.grupo | db.alumno.apellidos | db.alumno.nombre | ~db.amonestacion.fecha)
    elif (request.vars.sord == 'desc' and request.vars.sidx == 'grupo'):
        orderby = (~db.grupo.grupo  | db.alumno.apellidos | db.alumno.nombre | ~db.amonestacion.fecha)       
    else:       
        orderby = ~orderby               

    queries=[]
    queries.append(db.amonestacion.id_departamento_profesor == db.departamento_profesor.id)
    queries.append(db.departamento_profesor.id_profesor == db.profesor.id)
    queries.append(db.amonestacion.id_grupo_alumno == db.grupo_alumno.id)
    queries.append(db.grupo_alumno.id_curso_academico_grupo == db.curso_academico_grupo.id)    
    queries.append(db.curso_academico_grupo.id == session.profesor.tutor.id_curso_academico_grupo)
    queries.append(db.grupo_alumno.id_alumno == db.alumno.id)
    
    if searching:
        if request.vars.fecha:
            fecha = request.vars.fecha
            queries.append(db.amonestacion.fecha >= fecha)
        if request.vars.alumno:
            alumno = '%'+request.vars.alumno.lower()+'%'
            queries.append((db.alumno.apellidos.lower().like(alumno) | db.alumno.nombre.lower().like(alumno))) 
        if request.vars.grupo:    
            grupo = '%'+request.vars.grupo.lower()+'%'
            queries.append(db.grupo.grupo.lower().like(grupo)) 
        if request.vars.profesor:    
            profesor = '%'+request.vars.profesor.lower()+'%'
            queries.append((db.profesor.apellidos.lower().like(profesor) | db.profesor.nombre.lower().like(profesor)))
            
    query = reduce(lambda a,b:(a&b),queries)

    for r in db(query).select(db.amonestacion.ALL,limitby=limitby,orderby=orderby):
        vals = []
        for f in fields:
            if f == 'alumno':
                alumno = r.id_grupo_alumno.id_alumno.apellidos+', '+r.id_grupo_alumno.id_alumno.nombre
                vals.append(alumno)
            elif f == 'profesor':
                profesor = r.id_departamento_profesor.id_profesor.apellidos+', '+r.id_departamento_profesor.id_profesor.nombre
                vals.append(profesor)
            else:
                rep = db.amonestacion[f].represent
                if rep:
                    vals.append(rep(r[f]))
                else:
                    vals.append(r[f])
        rows.append(dict(id=r.id,cell=vals))
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
def updateComunicated():
    if request.vars.id:
        if request.vars.isChecked == 'true':
            db.amonestacion[request.vars.id] = dict(comunicada = True)
        else:
            db.amonestacion[request.vars.id] = dict(comunicada = False)
        db.commit()        
        return True
    else:
        return False
      
@service.json
def getGroups():
    query = db((db.curso_academico_grupo.id_curso_academico == session.curso_academico_id) &
                    (db.curso_academico_grupo.id_grupo == db.grupo.id))
    options = [{'valor':0, 'grupo':'Escoge grupo...'}]
    for grupo in query.select(orderby=db.grupo.grupo):
        options.append({'valor': grupo.curso_academico_grupo.id,'grupo':grupo.grupo.grupo}) 
    return dict(options=options)

@service.json
def getAsignaturas():
    query = db(db.asignatura.id > 0)
    options = [{'valor':0, 'asignatura':'Escoge asignatura...'}]
    for asignatura in query.select(orderby=db.asignatura.asignatura):
        options.append({'valor': asignatura.id,'asignatura':asignatura.asignatura+' ('+asignatura.abreviatura+')'}) 
    return dict(options=options)
                                      
                                                                                                                  
@service.json
def getStudentsGroup():
    #options = [{'valor':0, 'alumno':'Escoge alumno...'}]
    options = []
    
    if request.vars.grupo:
        query = db((db.grupo_alumno.id_curso_academico_grupo == int(request.vars.grupo)) &
                   (db.grupo_alumno.id_alumno == db.alumno.id))
                   
        for alumno in query.select(orderby=db.alumno.apellidos | db.alumno.nombre):
            options.append({'valor': alumno.grupo_alumno.id,'alumno':alumno.alumno.apellidos+','+alumno.alumno.nombre}) 
    return dict(options=options)

@service.json
def getTeachersGroup():
    options = []
    
    if request.vars.grupo:
        query = db((db.grupo_profesor.id_curso_academico_grupo == int(request.vars.grupo)) &
                   (db.grupo_profesor.id_profesor == db.profesor.id))
                   
        for profesor in query.select(orderby=db.profesor.apellidos | db.profesor.nombre):
            options.append({'valor': profesor.grupo_profesor.id,'profesor':profesor.profesor.apellidos+','+profesor.profesor.nombre}) 
    return dict(options=options)


@service.json
def getPhotoStudent():
    foto = ''
    if request.vars.alumno:
        query = db((db.grupo_alumno.id == int(request.vars.alumno)) &
                   (db.grupo_alumno.id_alumno == db.alumno.id))
        foto = query.select(db.alumno.foto).first()
    return dict(foto=foto)

@service.json
def addWarning():
    grupoaviso = int(request.vars.grupoaviso)
    alumnoaviso = int(request.vars.alumnoaviso)
    fechaaviso = request.vars.fechaaviso
    aviso = request.vars.aviso
    tipo = request.vars.action
    if request.vars.idaviso:
        idaviso = int(request.vars.idaviso)
    if ((grupoaviso == 0) or (alumnoaviso == 0) or (fechaaviso == '') or (aviso == '')):
        respuesta = 'datosincorrectos'
    else:
        if (tipo == "add"):
            db.amonestacion.id_departamento_profesor.default = session.profesor.id_departamento_profesor
                       
        try:
            if (tipo == "add"):
                db.amonestacion.insert(fecha=fechaaviso, id_grupo_alumno=alumnoaviso,
                                       amonestacion=aviso,
                                       parte=False, cerrada=False,
                                       comunicada=True if request.vars.comunicadaaviso else False)
            elif (tipo == "modify"):
                db(db.amonestacion.id == idaviso).update(fecha=fechaaviso, id_grupo_alumno=alumnoaviso,
                    amonestacion=aviso, comunicada=True if request.vars.comunicadaaviso else False)
            db.commit()
            respuesta = 'OK'    
        except:
            respuesta = 'fallo'    
    return dict(response=respuesta)

@service.json
def getWarning():
    idaviso = int(request.vars.id)
    aviso = None
    try:
        aviso = db((db.amonestacion.id == idaviso) &
                   (db.amonestacion.id_grupo_alumno == db.grupo_alumno.id) &
                   (db.grupo_alumno.id_curso_academico_grupo == db.curso_academico_grupo.id) &
                   (db.curso_academico_grupo.id_grupo == db.grupo.id)).select(db.curso_academico_grupo.ALL,db.amonestacion.ALL).first().as_dict()        
        respuesta = aviso
    except:
        respuesta = 'fallo'    
    return dict(response=respuesta)


@service.json
def getMyDelays():
    fields = ['id','fecha','grupo','alumno','hora','amonestado']  
    rows = []
    if request.vars._search == 'true':
        searching = True
    else:
        searching = False    
    page = int(request.vars.page)
    pagesize = int(request.vars.rows)    
    limitby = (page * pagesize - pagesize,page * pagesize)
    
    if (request.vars.sord == 'desc' and request.vars.sidx == 'alumno'): 
        orderby = (~db.alumno.apellidos | ~db.alumno.nombre | ~db.retraso.fecha)
    elif (request.vars.sord == 'asc' and request.vars.sidx == 'alumno'): 
        orderby = (db.alumno.apellidos | db.alumno.nombre | ~db.retraso.fecha)
    elif (request.vars.sord == 'desc' and request.vars.sidx == 'fecha'):
        orderby = (~db.retraso.fecha | ~db.retraso.id)
    elif (request.vars.sord == 'asc' and request.vars.sidx == 'fecha'):
        orderby = (db.retraso.fecha | db.retraso.id)
    elif (request.vars.sord == 'asc' and request.vars.sidx == 'id'):
        orderby = db.retraso.id
    elif (request.vars.sord == 'desc' and request.vars.sidx == 'id'):
        orderby = ~db.retraso.id
    elif (request.vars.sord == 'asc' and request.vars.sidx == 'grupo'):
        orderby = (db.grupo.grupo | db.alumno.apellidos | db.alumno.nombre | ~db.retraso.fecha)
    elif (request.vars.sord == 'desc' and request.vars.sidx == 'grupo'):
        orderby = (~db.grupo.grupo | db.alumno.apellidos | db.alumno.nombre | ~db.retraso.fecha)        
    else:       
        orderby = ~orderby               

    
    queries=[]
    queries.append(db.retraso.id_departamento_profesor == session.profesor.id_departamento_profesor)
    queries.append(db.retraso.id_grupo_alumno == db.grupo_alumno.id)
    queries.append(db.grupo_alumno.id_curso_academico_grupo == db.curso_academico_grupo.id)
    queries.append(db.curso_academico_grupo.id_grupo == db.grupo.id)
    queries.append(db.grupo_alumno.id_alumno == db.alumno.id)
    
    if searching:
        if request.vars.fecha:
            fecha = request.vars.fecha
            queries.append(db.retraso.fecha >= fecha)
        if request.vars.alumno:
            alumno = '%'+request.vars.alumno.lower()+'%'
            queries.append((db.alumno.apellidos.lower().like(alumno) | db.alumno.nombre.lower().like(alumno))) 
        if request.vars.grupo:    
            grupo = '%'+request.vars.grupo.lower()+'%'
            queries.append(db.grupo.grupo.lower().like(grupo)) 
    query = reduce(lambda a,b:(a&b),queries)

    for r in db(query).select(db.retraso.ALL, db.grupo.ALL, db.alumno.ALL, limitby=limitby,orderby=orderby):
        vals = []
        for f in fields:
            if f == 'alumno':
                alumno = r.alumno.apellidos+', '+r.alumno.nombre
                vals.append(alumno)
            elif f == 'grupo':
                grupo = r.grupo.grupo
                vals.append(grupo)
            elif f == 'amonestado':
               if db(db.amonestacion_retraso_retraso.id_retraso == r.retraso.id).count() > 0:
                   vals.append(True)
               else:
                   vals.append(False)    
            else:
                rep = db.retraso[f].represent
                if rep:
                    vals.append(rep(r.retraso[f]))
                else:
                    vals.append(r.retraso[f])
        rows.append(dict(id=r.retraso.id,cell=vals))
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
def getMyDelaysWarningsTutor():
    fields = ['id','fecha','profesor','alumno']  
    rows = []
    if request.vars._search == 'true':
        searching = True
    else:
        searching = False    
    page = int(request.vars.page)
    pagesize = int(request.vars.rows)    
    limitby = (page * pagesize - pagesize,page * pagesize)
    
    if (request.vars.sord == 'desc' and request.vars.sidx == 'alumno'): 
        orderby = (~db.alumno.apellidos | ~db.alumno.nombre | ~db.amonestacion_retraso.fecha)
    elif (request.vars.sord == 'asc' and request.vars.sidx == 'alumno'): 
        orderby = (db.alumno.apellidos | db.alumno.nombre | ~db.amonestacion_retraso.fecha)
    elif (request.vars.sord == 'desc' and request.vars.sidx == 'profesor'): 
        orderby = (~db.profesor.apellidos | ~db.profesor.nombre | ~db.amonestacion_retraso.fecha)
    elif (request.vars.sord == 'asc' and request.vars.sidx == 'profesor'): 
        orderby = (db.profesor.apellidos | db.profesor.nombre | ~db.amonestacion_retraso.fecha)       
    elif (request.vars.sord == 'desc' and request.vars.sidx == 'fecha'):
        orderby = (~db.amonestacion_retraso.fecha | ~db.amonestacion_retraso.id)
    elif (request.vars.sord == 'asc' and request.vars.sidx == 'fecha'):
        orderby = (db.amonestacion_retraso.fecha | db.amonestacion_retraso.id)
    elif (request.vars.sord == 'asc' and request.vars.sidx == 'id'):
        orderby = db.amonestacion_retraso.id
    elif (request.vars.sord == 'desc' and request.vars.sidx == 'id'):
        orderby = ~db.amonestacion_retraso.id
    elif (request.vars.sord == 'asc' and request.vars.sidx == 'grupo'):
        orderby = (db.grupo.grupo | db.alumno.apellidos | db.alumno.nombre | ~db.amonestacion_retraso.fecha)
    elif (request.vars.sord == 'desc' and request.vars.sidx == 'grupo'):
        orderby = (~db.grupo.grupo  | db.alumno.apellidos | db.alumno.nombre | ~db.amonestacion_retraso.fecha)       
    else:       
        orderby = ~orderby               

    queries=[]
    queries.append(db.amonestacion_retraso.id_departamento_profesor == db.departamento_profesor.id)
    queries.append(db.departamento_profesor.id_profesor == db.profesor.id)
    queries.append(db.amonestacion_retraso.id_grupo_alumno == db.grupo_alumno.id)
    queries.append(db.grupo_alumno.id_alumno == db.alumno.id)
    queries.append(db.grupo_alumno.id_curso_academico_grupo == db.curso_academico_grupo.id)
    queries.append(db.curso_academico_grupo.id == session.profesor.tutor.id_curso_academico_grupo)    
    queries.append(db.curso_academico_grupo.id_grupo == db.grupo.id)
    
   
    if searching:
        if request.vars.fecha:
            fecha = request.vars.fecha
            queries.append(db.amonestacion_retraso.fecha >= fecha)
        if request.vars.alumno:
            alumno = '%'+request.vars.alumno.lower()+'%'
            queries.append((db.alumno.apellidos.lower().like(alumno) | db.alumno.nombre.lower().like(alumno))) 
        if request.vars.profesor:
            profesor = '%'+request.vars.profesor.lower()+'%'
            queries.append((db.profesor.apellidos.lower().like(profesor) | db.profesor.nombre.lower().like(profesor)))             
        if request.vars.grupo:    
            grupo = '%'+request.vars.grupo.lower()+'%'
            queries.append(db.grupo.grupo.lower().like(grupo)) 
    query = reduce(lambda a,b:(a&b),queries)

    for r in db(query).select(db.amonestacion_retraso.ALL, db.profesor.ALL, db.alumno.ALL, db.grupo.ALL, limitby=limitby, orderby=orderby):
        vals = []
        for f in fields:
            if f == 'alumno':
                alumno = r.alumno.apellidos+', '+r.alumno.nombre
                vals.append(alumno)
            elif f == 'profesor':
                profesor = r.profesor.apellidos+', '+r.profesor.nombre
                vals.append(profesor)
            else:
                rep = db.amonestacion_retraso[f].represent
                if rep:
                    vals.append(rep(r.amonestacion_retraso[f]))
                else:
                    vals.append(r.amonestacion_retraso[f])
        rows.append(dict(id=r.amonestacion_retraso.id, cell=vals))
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
def addDelay():
    gruporetraso = int(request.vars.gruporetraso)
    alumnoretraso = int(request.vars.alumnoretraso)
    fecharetraso = request.vars.fecharetraso
    horaretraso = request.vars.horaretraso
    tipo = request.vars.action
    if request.vars.idretraso:
        idretraso = int(request.vars.idretraso)
        #debemos comprobar si el retraso pertenece ahora a otro alumno
        #si es así tenemos que borrar el retraso del alumno y procesarlo
        #y añadir el nuevo retraso procesando los del nuevo alumno
        
    if ((gruporetraso == 0) or (alumnoretraso == 0) or (fecharetraso == '')):
        respuesta = 'datosincorrectos'
    else:
        if (tipo == "add"):
            db.retraso.id_departamento_profesor.default = session.profesor.id_departamento_profesor
            db.retraso.procesar.default = True           
        try:
            #debemos comprobar que no exista ya un retraso para ese alumno, esa fecha y esa hora
            if (db((db.retraso.fecha == fecharetraso) & (db.retraso.id_grupo_alumno == alumnoretraso) &
                   (db.retraso.hora == horaretraso)).count() > 0):
                respuesta = "duplicado"
                return dict(response=respuesta)                       
            if (tipo == "add"):
                db.retraso.insert(fecha=fecharetraso,hora=horaretraso, id_grupo_alumno=alumnoretraso)
            elif (tipo == "modify"):
                db(db.retraso.id == idretraso).update(fecha=fecharetraso, hora=horaretraso, id_grupo_alumno=alumnoretraso,
                                                      id_departamento_profesor=session.profesor.id_departamento_profesor)
                
            #comprobación de generación de amonestación
            delays.procesa_retrasos(db,alumnoretraso,session.profesor.id_departamento_profesor,
                                    session.retrasos_para_amonestacion,session.curso_academico_id)
                        
            db.commit()
            respuesta = 'OK'    
        except:
            respuesta = 'fallo'    
    return dict(response=respuesta)

@service.json
def updateDelayJustify():
    if request.vars.id:
        if request.vars.isChecked == 'true':
            db.retraso[request.vars.id] = dict(justificado = True)
            #comprobemos y borremos la amonestacion si se provocó con este retraso            
            delays.justifica_retraso(db,request.vars.id)
        else:
            db.retraso[request.vars.id] = dict(justificado = False)                     
        #ahora procesemos los retrasos y amonestemos si se dan las condiciones
        delays.procesa_retrasos(db,db.retraso[request.vars.id].id_grupo_alumno,session.profesor.id_departamento_profesor,
                    session.retrasos_para_amonestacion,session.curso_academico_id)
        db.commit()        
        return dict(estado='OK')
    else:
        return dict(estado='NOPARAMETRO')
            

@service.json
def getDelay():
    idretraso = int(request.vars.id)
    retraso = None
    try:
        retraso = db((db.retraso.id == idretraso) &
                     (db.retraso.id_grupo_alumno == db.grupo_alumno.id) &
                     (db.grupo_alumno.id_curso_academico_grupo == db.curso_academico_grupo.id)).select(db.curso_academico_grupo.ALL,db.retraso.ALL).first().as_dict()        
        respuesta = retraso
    except:
        respuesta = 'fallo'    
    return dict(response=respuesta)

@service.json
def deleteDelay():
    idretraso = int(request.vars.idretraso)
    try:      
        # comprobemos si está amonestado y si es así borremos la amonestación en que participa
        id_amonestacion_retraso = db(db.amonestacion_retraso_retraso.id_retraso == idretraso).select().first()
        if id_amonestacion_retraso:
            #está amonestado
            id_grupo_alumno = db.retraso[idretraso].id_grupo_alumno
            #está amonestado el retraso, vamos a borras las asignaciones de retrasos a esa amonestación
            db(db.amonestacion_retraso_retraso.id_amonestacion_retraso == id_amonestacion_retraso.id_amonestacion_retraso).delete()
            #borramos la amonestación
            db(db.amonestacion_retraso.id == id_amonestacion_retraso.id_amonestacion_retraso).delete()
            #borramos el retraso    
            db(db.retraso.id == idretraso).delete()
            #comprobación de generación de amonestación
            delays.procesa_retrasos(db,id_grupo_alumno,session.profesor.id_departamento_profesor,
                                    session.retrasos_para_amonestacion,session.curso_academico_id)
        else:
            #borramos el retraso
            db(db.retraso.id == idretraso).delete()
                                    
        db.commit()
        respuesta = 'OK'
    except:
        respuesta = 'fallo'    
    return dict(response=respuesta)        

@service.json
def getDelaysFromWarning():
    idaviso = int(request.vars.id)
    respuesta = {}
    try:
        retrasos = db((db.amonestacion_retraso.id == idaviso) &
                      (db.amonestacion_retraso_retraso.id_amonestacion_retraso == db.amonestacion_retraso.id) &
                     (db.amonestacion_retraso_retraso.id_retraso == db.retraso.id)) \
                     .select(db.amonestacion_retraso.ALL, db.amonestacion_retraso_retraso.ALL, db.retraso.ALL, orderby=~db.retraso.fecha)
        respuesta['id_grupo_alumno'] = retrasos[0].amonestacion_retraso.id_grupo_alumno
        respuesta['retrasos'] = []
        for retraso in retrasos:
            respuesta['retrasos'].append({'id_retraso':retraso.retraso.id,
                                          'fecha':retraso.retraso.fecha,
                                          'hora':retraso.retraso.hora})                
    except:
        respuesta = 'fallo'    
    return dict(response=respuesta)

@service.json
def getDelaysFromWarningGrid():
    fields = ['fecha','hora']  
    horas = ['Primera', 'Segunda', 'Tercera', 'Cuarta', 'Quinta', 'Sexta', 'Séptima']
    rows = []
    idaviso = int(request.vars.id)
    for r in db((db.amonestacion_retraso.id == idaviso) &
                      (db.amonestacion_retraso_retraso.id_amonestacion_retraso == db.amonestacion_retraso.id) &
                     (db.amonestacion_retraso_retraso.id_retraso == db.retraso.id)) \
                     .select(db.amonestacion_retraso.ALL, db.amonestacion_retraso_retraso.ALL, db.retraso.ALL, orderby=~db.retraso.fecha):
        vals = []
        for f in fields:
            if f == 'hora':
                vals.append(horas[int(r.retraso.hora)-1])
            else:
                vals.append(r.retraso[f])
        rows.append(dict(id=r.retraso.id, cell=vals))
    return dict(rows=rows)


@service.json
def getMisGruposAsignaturas():
    fields = ['grupo','asignatura','tutor']  
    rows = []
    if request.vars._search == 'true':
        searching = True
    else:
        searching = False    
    page = int(request.vars.page)
    pagesize = int(request.vars.rows)    
    limitby = (page * pagesize - pagesize,page * pagesize)
    
    if (request.vars.sord == 'desc' and request.vars.sidx == 'grupo'):
        orderby = (~db.grupo.grupo | db.asignatura.asignatura)
    elif (request.vars.sord == 'asc' and request.vars.sidx == 'grupo'):
        orderby = (db.grupo.grupo | db.asignatura.asignatura)
    elif (request.vars.sord == 'asc' and request.vars.sidx == 'asignatura'):
        orderby = (db.asignatura.asignatura | db.grupo.grupo)
    elif (request.vars.sord == 'desc' and request.vars.sidx == 'asignatura'):
        orderby = (~db.asignatura.asignatura | db.grupo.grupo)
    elif (request.vars.sord == 'asc' and request.vars.sidx == 'tutor'):
        orderby = (db.profesor.apellidos | db.profesor.nombre)
    elif (request.vars.sord == 'desc' and request.vars.sidx == 'tutor'):
        orderby = (~db.profesor.apellidos | db.profesor.nombre)        
    else:       
        orderby = ~orderby               
    
    queries=[]
    queries.append(db.curso_academico_grupo.id_curso_academico == session.curso_academico_id)      
    queries.append(db.curso_academico_grupo.id_grupo == db.grupo.id)   
    queries.append(db.curso_academico_grupo.id_tutor == db.profesor.id)   
    queries.append(db.curso_academico_grupo.id == db.grupo_profesor.id_curso_academico_grupo)
    queries.append(db.grupo_profesor.id_profesor == session.profesor.id)
    queries.append(db.grupo_profesor.id == db.grupo_profesor_asignatura.id_grupo_profesor)
    queries.append(db.grupo_profesor_asignatura.id_asignatura == db.asignatura.id)
    
    if searching:
        if request.vars.grupo:
            grupo = '%'+request.vars.grupo.lower()+'%'
            queries.append(db.grupo.grupo.lower().like(grupo))
        if request.vars.asignatura:
            asignatura = '%'+request.vars.asignatura.lower()+'%'
            queries.append(db.asignatura.asignatura.lower().like(asignatura)) 
        if request.vars.tutor:    
            tutor = '%'+request.vars.tutor.lower()+'%'
            queries.append((db.profesor.apellidos.lower().like(tutor) | db.profesor.nombre.lower().like(tutor)))             

    query = reduce(lambda a,b:(a&b),queries)

    for r in db(query).select(db.grupo_profesor_asignatura.ALL,db.grupo.ALL,db.asignatura.ALL,db.profesor.ALL,limitby=limitby,orderby=orderby):
        vals = []
        for f in fields:
            if f == 'asignatura':
                asignatura = r.asignatura.asignatura+' ('+r.asignatura.abreviatura+')'
                vals.append(asignatura)
            elif f == 'grupo':
                grupo = r.grupo.grupo
                vals.append(grupo)
            elif f == 'tutor':
                tutor = r.profesor.apellidos+', '+r.profesor.nombre
                vals.append(tutor)                
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
def getMisEvaluaciones():
    id_grupo_profesor_asignatura = int(request.vars.id)    
    fields = ['evaluacion','bloqueada']  
    rows = []
    if request.vars._search == 'true':
        searching = True
    else:
        searching = False    
    page = int(request.vars.page)
    pagesize = int(request.vars.rows)    
    limitby = (page * pagesize - pagesize,page * pagesize)
    
    orderby = db.curso_academico_evaluacion.id
    
    queries=[]
    queries.append(db.grupo_profesor_asignatura_alumno.id_grupo_profesor_asignatura == id_grupo_profesor_asignatura)      
    queries.append(db.evaluacion_alumno.id_grupo_profesor_asignatura_alumno == db.grupo_profesor_asignatura_alumno.id)      
    queries.append(db.evaluacion_alumno.id_curso_academico_evaluacion == db.curso_academico_evaluacion.id)      
    queries.append(db.curso_academico_evaluacion.id_curso_academico == db.curso_academico.id)      

    query = reduce(lambda a,b:(a&b),queries)

    for r in db(query).select(db.curso_academico_evaluacion.ALL,db.evaluacion_alumno.ALL,limitby=limitby,orderby=orderby,groupby=db.curso_academico_evaluacion.id):
        vals = []
        for f in fields:
            if f == 'evaluacion':
                evaluacion = r.curso_academico_evaluacion.evaluacion
                vals.append(evaluacion)
            elif f == 'bloqueada':
                bloqueada = r.curso_academico_evaluacion.bloqueada
                vals.append(bloqueada)
            else:
                rep = db.curso_academico_evaluacion[f].represent
                if rep:
                    vals.append(rep(r.curso_academico_evaluacion[f]))
                else:
                    vals.append(r.curso_academico_evaluacion[f])
        rows.append(dict(id=r.curso_academico_evaluacion.id,cell=vals))
    total = db(query).count(distinct=db.curso_academico_evaluacion.id)    
    if total <= pagesize:
        pages = 1
    else:   
        pages = int(total/pagesize)
        if total % pagesize <> 0:
            pages += 1
    data = dict(total=pages,page=page,records=total,rows=rows)
    return data
    
@service.json
def getMiEvaluacion():
    id_grupo_profesor_asignatura = int(request.vars.idgrupoprofesorasignatura)
    # vamos a ver que porcentajes usaremos en la evaluación de esta asignatura
    if db.grupo_profesor_asignatura(id_grupo_profesor_asignatura).id_asignatura.usar_criterios_asignatura:
        # tenemos que usar los criterios específicos de esa asignatura
        session.peso_1 = float(db.grupo_profesor_asignatura(id_grupo_profesor_asignatura).id_asignatura.peso_1) * 0.06
        session.peso_2 = float(db.grupo_profesor_asignatura(id_grupo_profesor_asignatura).id_asignatura.peso_2) * 0.06
        session.peso_3 = float(db.grupo_profesor_asignatura(id_grupo_profesor_asignatura).id_asignatura.peso_3) * 0.06
        session.peso_4 = float(db.grupo_profesor_asignatura(id_grupo_profesor_asignatura).id_asignatura.peso_4) * 0.06
        session.peso_5 = float(db.grupo_profesor_asignatura(id_grupo_profesor_asignatura).id_asignatura.peso_5) * 0.06
        session.peso_6 = float(db.grupo_profesor_asignatura(id_grupo_profesor_asignatura).id_asignatura.peso_6) * 0.06
    elif db.grupo_profesor_asignatura(id_grupo_profesor_asignatura).id_asignatura.id_departamento.usar_criterios_departamento:
        # tenemos que usar los criterios específicos del departamento
        session.peso_1 = float(db.grupo_profesor_asignatura(id_grupo_profesor_asignatura).id_asignatura.id_departamento.peso_1) * 0.06
        session.peso_2 = float(db.grupo_profesor_asignatura(id_grupo_profesor_asignatura).id_asignatura.id_departamento.peso_2) * 0.06
        session.peso_3 = float(db.grupo_profesor_asignatura(id_grupo_profesor_asignatura).id_asignatura.id_departamento.peso_3) * 0.06
        session.peso_4 = float(db.grupo_profesor_asignatura(id_grupo_profesor_asignatura).id_asignatura.id_departamento.peso_4) * 0.06
        session.peso_5 = float(db.grupo_profesor_asignatura(id_grupo_profesor_asignatura).id_asignatura.id_departamento.peso_5) * 0.06
        session.peso_6 = float(db.grupo_profesor_asignatura(id_grupo_profesor_asignatura).id_asignatura.id_departamento.peso_6) * 0.06
    else:
        # usaremos los del curso académico
        session.peso_1 = float(db.curso_academico(session.curso_academico_id).peso_1) * 0.06
        session.peso_2 = float(db.curso_academico(session.curso_academico_id).peso_2) * 0.06
        session.peso_3 = float(db.curso_academico(session.curso_academico_id).peso_3) * 0.06
        session.peso_4 = float(db.curso_academico(session.curso_academico_id).peso_4) * 0.06
        session.peso_5 = float(db.curso_academico(session.curso_academico_id).peso_5) * 0.06
        session.peso_6 = float(db.curso_academico(session.curso_academico_id).peso_6) * 0.06
    id_evaluacion = int(request.vars.idevaluacion)
    fields = ['alumno','nivel','trabajo_clase','trabajo_casa','interes','participa','comportamiento','evaluacion','observaciones']  
    rows = []
    if request.vars._search == 'true':
        searching = True
    else:
        searching = False    
    page = int(request.vars.page)
    pagesize = int(request.vars.rows)    
    limitby = (page * pagesize - pagesize,page * pagesize)

    if (request.vars.sord == 'desc' and request.vars.sidx == 'alumno'):
        orderby = (~db.alumno.apellidos | db.alumno.nombre)
    elif (request.vars.sord == 'asc' and request.vars.sidx == 'alumno'):
        orderby = (db.alumno.apellidos | db.alumno.nombre)   
    elif (request.vars.sord == 'desc' and request.vars.sidx == 'nivel'):
        orderby = (~db.evaluacion_alumno.nivel | db.alumno.apellidos | db.alumno.nombre)
    elif (request.vars.sord == 'asc' and request.vars.sidx == 'nivel'):
        orderby = (db.evaluacion_alumno.nivel | db.alumno.apellidos | db.alumno.nombre)
    elif (request.vars.sord == 'asc' and request.vars.sidx == 'global'):
        orderby = (db.evaluacion_alumno.evaluacion | db.alumno.apellidos | db.alumno.nombre)
    elif (request.vars.sord == 'desc' and request.vars.sidx == 'global'):
        orderby = (~db.evaluacion_alumno.evaluacion | db.alumno.apellidos | db.alumno.nombre)
    else:           
        orderby = db.alumno.apellidos | db.alumno.nombre
    
    queries=[]
    queries.append(db.grupo_profesor_asignatura_alumno.id_grupo_profesor_asignatura == id_grupo_profesor_asignatura)      
    queries.append(db.evaluacion_alumno.id_curso_academico_evaluacion == id_evaluacion)          
    queries.append(db.evaluacion_alumno.id_grupo_profesor_asignatura_alumno == db.grupo_profesor_asignatura_alumno.id)      
    queries.append(db.evaluacion_alumno.id_curso_academico_evaluacion == db.curso_academico_evaluacion.id)      
    queries.append(db.evaluacion_alumno.id_grupo_profesor_asignatura_alumno == db.grupo_profesor_asignatura_alumno.id)      
    queries.append(db.grupo_profesor_asignatura_alumno.id_grupo_alumno == db.grupo_alumno.id)
    queries.append(db.grupo_alumno.id_alumno == db.alumno.id)

    query = reduce(lambda a,b:(a&b),queries)

    for r in db(query).select(db.alumno.ALL,db.evaluacion_alumno.ALL,limitby=limitby,orderby=orderby):
        vals = []
        for f in fields:
            if f == 'alumno':
                alumno = r.alumno.apellidos+', '+r.alumno.nombre
                vals.append(alumno)
            else:
                rep = db.evaluacion_alumno[f].represent
                if rep:
                    vals.append(rep(r.evaluacion_alumno[f]))
                else:
                    vals.append(r.evaluacion_alumno[f])
        rows.append(dict(id=r.evaluacion_alumno.id,cell=vals))
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
def modificaEvaluacion():
    # estamos editando evaluaciones
    if request.vars.oper == 'edit':
        idevaluacionalumno = int(request.vars.id)

        peso1 = float(session.peso_1)
        peso2 = float(session.peso_2)
        peso3 = float(session.peso_3)
        peso4 = float(session.peso_4)
        peso5 = float(session.peso_5)
        peso6 = float(session.peso_6)
                
                
        #peso1 = float(request.vars.peso1 or 4.5)
        #peso2 = float(request.vars.peso2 or 0.45)
        #peso3 = float(request.vars.peso3 or 0.45)
        #peso4 = float(request.vars.peso4 or 0.3)
        #peso5 = float(request.vars.peso5 or 0.3)
        #peso6 = float(request.vars.peso6 or 0)
        
        if request.vars.nivel:
            nivel = request.vars.nivel
            db.evaluacion_alumno[idevaluacionalumno] = dict(nivel = nivel)        
        if request.vars.trclase:
            trabajo_clase = int(request.vars.trclase)
            db.evaluacion_alumno[idevaluacionalumno] = dict(trabajo_clase = trabajo_clase)
        if request.vars.trcasa:
            trabajo_casa = int(request.vars.trcasa)
            db.evaluacion_alumno[idevaluacionalumno] = dict(trabajo_casa = trabajo_casa)
        if request.vars.interes:
            interes = int(request.vars.interes)
            db.evaluacion_alumno[idevaluacionalumno] = dict(interes = interes)
        if request.vars.participa:
            participa = int(request.vars.participa)
            db.evaluacion_alumno[idevaluacionalumno] = dict(participa = participa)
        if request.vars.comportamiento:
            comportamiento = int(request.vars.comportamiento)
            db.evaluacion_alumno[idevaluacionalumno] = dict(comportamiento = comportamiento)
        if request.vars.observaciones or request.vars.observaciones == "":
            db.evaluacion_alumno[idevaluacionalumno] = dict(observaciones = request.vars.observaciones)
        
        # procesemos el global    
        filaevaluacion = db(db.evaluacion_alumno.id == idevaluacionalumno).select().first()
        filaevaluacion.evaluacion = ((float(filaevaluacion.nivel)*peso1*10.0 + filaevaluacion.trabajo_clase*peso2 + filaevaluacion.trabajo_casa*peso3 +
            filaevaluacion.interes*peso4 + filaevaluacion.participa*peso5 + filaevaluacion.comportamiento*peso6)/float(6))/float(10)
                        
                        
        filaevaluacion.update_record()    
            
        db.commit()
        return (filaevaluacion.evaluacion)

@service.json
def getEvaluaciones():
    fields = ['evaluacion','bloqueada']  
    rows = []
    if request.vars._search == 'true':
        searching = True
    else:
        searching = False    
    page = int(request.vars.page)
    pagesize = int(request.vars.rows)    
    limitby = (page * pagesize - pagesize,page * pagesize)
    
    orderby = db.curso_academico_evaluacion.id
    
    queries=[]
    queries.append(db.curso_academico_evaluacion.id_curso_academico == session.curso_academico_id)      

    query = reduce(lambda a,b:(a&b),queries)

    for r in db(query).select(db.curso_academico_evaluacion.ALL,limitby=limitby,orderby=orderby):
        vals = []
        for f in fields:
            if f == 'evaluacion':
                evaluacion = r.evaluacion
                vals.append(evaluacion)
            elif f == 'bloqueada':
                bloqueada = r.bloqueada
                vals.append(bloqueada)
            else:
                rep = db.curso_academico_evaluacion[f].represent
                if rep:
                    vals.append(rep(r[f]))
                else:
                    vals.append(r[f])
        rows.append(dict(id=r.id,cell=vals))
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
def getEvaluacionesTutoria():
    id_curso_academico_grupo_tutoria = int(request.vars.idcursoacademicogrupotutoria)
    id_evaluacion = int(request.vars.idevaluacion)
    fields = ['asignatura','profesor']  
    rows = []
    if request.vars._search == 'true':
        searching = True
    else:
        searching = False    
    page = int(request.vars.page)
    pagesize = int(request.vars.rows)    
    limitby = (page * pagesize - pagesize,page * pagesize)

    orderby = db.asignatura.asignatura
    
    queries=[]
    queries.append(db.grupo_profesor.id_curso_academico_grupo == id_curso_academico_grupo_tutoria)      
    queries.append(db.grupo_profesor.id_profesor == db.profesor.id)      
    queries.append(db.grupo_profesor_asignatura.id_grupo_profesor == db.grupo_profesor.id)      
    queries.append(db.grupo_profesor_asignatura.id_asignatura == db.asignatura.id)      
    queries.append(db.grupo_profesor_asignatura_alumno.id_grupo_profesor_asignatura == db.grupo_profesor_asignatura.id)      
    queries.append(db.evaluacion_alumno.id_grupo_profesor_asignatura_alumno == db.grupo_profesor_asignatura_alumno.id)      
    queries.append(db.evaluacion_alumno.id_curso_academico_evaluacion == id_evaluacion)      

    query = reduce(lambda a,b:(a&b),queries)

    for r in db(query).select(db.grupo_profesor_asignatura.ALL,db.profesor.ALL,db.asignatura.ALL,
                                limitby=limitby,orderby=orderby,groupby=db.grupo_profesor_asignatura_alumno.id_grupo_profesor_asignatura):
        vals = []
        for f in fields:
            if f == 'profesor':
                profesor = r.profesor.apellidos+', '+r.profesor.nombre
                vals.append(profesor)
            elif f == 'asignatura':
                asignatura = r.asignatura.asignatura+' ('+r.asignatura.abreviatura+')'
                vals.append(asignatura)                
            else:
                rep = db.grupo_profesor_asignatura[f].represent
                if rep:
                    vals.append(rep(r.grupo_profesor_asignatura[f]))
                else:
                    vals.append(r.grupo_profesor_asignatura[f])
        rows.append(dict(id=r.grupo_profesor_asignatura.id,cell=vals))
    total = db(query).count(distinct=db.grupo_profesor_asignatura_alumno.id_grupo_profesor_asignatura)    
    if total <= pagesize:
        pages = 1
    else:   
        pages = int(total/pagesize)
        if total % pagesize <> 0:
            pages += 1
    data = dict(total=pages,page=page,records=total,rows=rows)
    return data

@service.json
def cargarDatosEvaluacion():
    aEvaluacion = int(request.vars['aEvaluacion'])
    desdeEvaluacion = int(request.vars['desdeEvaluacion'])
    id_grupo_profesor_asignatura = int(request.vars['id_grupo_profesor_asignatura'])
    bloqueada = True
    aEvaluacionDb = db(db.curso_academico_evaluacion.id == aEvaluacion).select().first()
    if aEvaluacionDb:
        if aEvaluacionDb.bloqueada:
            respuesta = 'Eval. bloqueada'
            return respuesta
    if (id_grupo_profesor_asignatura == 0 or aEvaluacion == 0 or desdeEvaluacion == 0 or aEvaluacionDb == None):
        respuesta = 'Datos incorrectos'
    else:
        try:
            # obtengamos los alumnos de esa asignatura y ese profesor
            grupoProfesorAsignaturaAlumno = db(db.grupo_profesor_asignatura_alumno.id_grupo_profesor_asignatura ==
                                                id_grupo_profesor_asignatura).select()

            # ahora recorramos los datos de la evaluación desdeEvaluacion
            for evaluacionAlumno in grupoProfesorAsignaturaAlumno:
                evaluacionAnterior = db((db.evaluacion_alumno.id_grupo_profesor_asignatura_alumno == evaluacionAlumno.id) &
                                        (db.evaluacion_alumno.id_curso_academico_evaluacion == desdeEvaluacion)).select().first()
                # veamos la de ahora
                evaluacionActual = db((db.evaluacion_alumno.id_grupo_profesor_asignatura_alumno == evaluacionAlumno.id) &
                                        (db.evaluacion_alumno.id_curso_academico_evaluacion == aEvaluacion)).select().first()

                if evaluacionActual and evaluacionAnterior:
                    evaluacionActual.update_record(nivel = evaluacionAnterior.nivel,
                                                   trabajo_clase = evaluacionAnterior.trabajo_clase,
                                                   trabajo_casa = evaluacionAnterior.trabajo_casa,
                                                   interes = evaluacionAnterior.interes,
                                                   participa = evaluacionAnterior.participa,
                                                   comportamiento = evaluacionAnterior.comportamiento,
                                                   observaciones = evaluacionAnterior.observaciones,
                                                   evaluacion = evaluacionAnterior.evaluacion)

            db.commit()
            respuesta = 'OK'
        except:
            raise
            respuesta = 'Fallo'
    return respuesta
