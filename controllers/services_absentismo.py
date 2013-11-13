# coding: utf8
# intente algo como
def index(): return dict(message="hello from services_absentismo.py")

@auth.requires_login()
@auth.requires_membership(role='Profesores')
def call():
    session.forget()
    return service()

@service.json
def getMisAbsentismos():
    fields = ['id','fecha','grupo','alumno','comunicada',]  
    rows = []
    if request.vars._search == 'true':
        searching = True
    else:
        searching = False    
    page = int(request.vars.page)
    pagesize = int(request.vars.rows)    
    limitby = (page * pagesize - pagesize,page * pagesize)
    
    if (request.vars.sord == 'desc' and request.vars.sidx == 'alumno'): 
        orderby = (~db.alumno.apellidos | ~db.alumno.nombre | ~db.amonestacion_absentismo.fecha)
    elif (request.vars.sord == 'asc' and request.vars.sidx == 'alumno'): 
        orderby = (db.alumno.apellidos | db.alumno.nombre | ~db.amonestacion_absentismo.fecha)
    elif (request.vars.sord == 'desc' and request.vars.sidx == 'fecha'):
        orderby = (~db.amonestacion_absentismo.fecha | ~db.amonestacion_absentismo.id)
    elif (request.vars.sord == 'asc' and request.vars.sidx == 'fecha'):
        orderby = (db.amonestacion_absentismo.fecha | db.amonestacion_absentismo.id)
    elif (request.vars.sord == 'asc' and request.vars.sidx == 'id'):
        orderby = db.amonestacion_absentismo.id
    elif (request.vars.sord == 'desc' and request.vars.sidx == 'id'):
        orderby = ~db.amonestacion_absentismo.id
    elif (request.vars.sord == 'asc' and request.vars.sidx == 'grupo'):
        orderby = (db.grupo.grupo | db.alumno.apellidos | db.alumno.nombre | ~db.amonestacion_absentismo.fecha)
    elif (request.vars.sord == 'desc' and request.vars.sidx == 'grupo'):
        orderby = (~db.grupo.grupo | db.alumno.apellidos | db.alumno.nombre | ~db.amonestacion_absentismo.fecha)        
    else:       
        orderby = ~orderby               

    
    queries=[]
    queries.append(db.amonestacion_absentismo.id_departamento_profesor == session.profesor.id_departamento_profesor)
    queries.append(db.amonestacion_absentismo.id_grupo_alumno == db.grupo_alumno.id)
    queries.append(db.grupo_alumno.id_curso_academico_grupo == db.curso_academico_grupo.id)
    queries.append(db.curso_academico_grupo.id_grupo == db.grupo.id)    
    queries.append(db.grupo_alumno.id_alumno == db.alumno.id)
    
    if searching:
        if request.vars.fecha:
            fecha = request.vars.fecha
            queries.append(db.amonestacion_absentismo.fecha >= fecha)
        if request.vars.alumno:
            alumno = '%'+request.vars.alumno.lower()+'%'
            queries.append((db.alumno.apellidos.lower().like(alumno) | db.alumno.nombre.lower().like(alumno))) 
        if request.vars.grupo:    
            grupo = '%'+request.vars.grupo.lower()+'%'
            queries.append(db.grupo.grupo.lower().like(grupo)) 
    query = reduce(lambda a,b:(a&b),queries)

    for r in db(query).select(db.amonestacion_absentismo.ALL,db.grupo.ALL,db.alumno.ALL,limitby=limitby,orderby=orderby):
        vals = []
        for f in fields:
            if f == 'alumno':
                alumno = r.alumno.apellidos+', '+r.alumno.nombre
                vals.append(alumno)
            elif f == 'grupo':
                grupo = r.grupo.grupo
                vals.append(grupo)
            else:
                rep = db.amonestacion_absentismo[f].represent
                if rep:
                    vals.append(rep(r.amonestacion_absentismo[f]))
                else:
                    vals.append(r.amonestacion_absentismo[f])
        rows.append(dict(id=r.amonestacion_absentismo.id,cell=vals))
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
def getAbsentismo():
    idaviso = int(request.vars.id)
    aviso = None
    try:
        aviso = db((db.amonestacion_absentismo.id == idaviso) &
                   (db.amonestacion_absentismo.id_grupo_alumno == db.grupo_alumno.id) &
                   (db.grupo_alumno.id_curso_academico_grupo == db.curso_academico_grupo.id) &
                   (db.curso_academico_grupo.id_grupo == db.grupo.id)).select(db.curso_academico_grupo.ALL,db.amonestacion_absentismo.ALL).first().as_dict()        
        respuesta = aviso
    except:
        respuesta = 'fallo'    
    return dict(response=respuesta)

@service.json
def updateComunicated():
    if request.vars.id:
        if request.vars.isChecked == 'true':
            db.amonestacion_absentismo[request.vars.id] = dict(comunicada = True)
        else:
            db.amonestacion_absentismo[request.vars.id] = dict(comunicada = False)
        db.commit()        
        return True
    else:
        return False


@service.json
def addAbsentismo():
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
            db.amonestacion_absentismo.id_departamento_profesor.default = session.profesor.id_departamento_profesor
                       
        try:
            if (tipo == "add"):
                db.amonestacion_absentismo.insert(fecha=fechaaviso, id_grupo_alumno=alumnoaviso,
                                       absentismo=aviso,
                                       comunicada=True if request.vars.comunicadaaviso else False)
            elif (tipo == "modify"):
                db(db.amonestacion_absentismo.id == idaviso).update(fecha=fechaaviso, id_grupo_alumno=alumnoaviso,
                    absentismo=aviso, comunicada=True if request.vars.comunicadaaviso else False)
            db.commit()
            respuesta = 'OK'    
        except:
            respuesta = 'fallo'    
    return dict(response=respuesta)


@service.json
def getMisAbsentismosTutor():
    fields = ['id','fecha','profesor','alumno','comunicada']  
    rows = []
    if request.vars._search == 'true':
        searching = True
    else:
        searching = False    
    page = int(request.vars.page)
    pagesize = int(request.vars.rows)    
    limitby = (page * pagesize - pagesize,page * pagesize)
    
    if (request.vars.sord == 'desc' and request.vars.sidx == 'alumno'): 
        orderby = (~db.alumno.apellidos | ~db.alumno.nombre | ~db.amonestacion_absentismo.fecha)
    elif (request.vars.sord == 'asc' and request.vars.sidx == 'alumno'): 
        orderby = (db.alumno.apellidos | db.alumno.nombre | ~db.amonestacion_absentismo.fecha)
    elif (request.vars.sord == 'desc' and request.vars.sidx == 'profesor'): 
        orderby = (~db.profesor.apellidos | ~db.profesor.nombre | ~db.amonestacion_absentismo.fecha)
    elif (request.vars.sord == 'asc' and request.vars.sidx == 'profesor'): 
        orderby = (db.profesor.apellidos | db.profesor.nombre | ~db.amonestacion_absentismo.fecha)       
    elif (request.vars.sord == 'desc' and request.vars.sidx == 'fecha'):
        orderby = (~db.amonestacion_absentismo.fecha | ~db.amonestacion_absentismo.id)
    elif (request.vars.sord == 'asc' and request.vars.sidx == 'fecha'):
        orderby = (db.amonestacion_absentismo.fecha | db.amonestacion_absentismo.id)
    elif (request.vars.sord == 'asc' and request.vars.sidx == 'id'):
        orderby = db.amonestacion_absentismo.id
    elif (request.vars.sord == 'desc' and request.vars.sidx == 'id'):
        orderby = ~db.amonestacion_absentismo.id
    elif (request.vars.sord == 'asc' and request.vars.sidx == 'grupo'):
        orderby = (db.grupo.grupo | db.alumno.apellidos | db.alumno.nombre | ~db.amonestacion_absentismo.fecha)
    elif (request.vars.sord == 'desc' and request.vars.sidx == 'grupo'):
        orderby = (~db.grupo.grupo  | db.alumno.apellidos | db.alumno.nombre | ~db.amonestacion_absentismo.fecha)       
    else:       
        orderby = ~orderby               

    queries=[]
    queries.append(db.amonestacion_absentismo.id_departamento_profesor == db.departamento_profesor.id)
    queries.append(db.departamento_profesor.id_profesor == db.profesor.id)
    queries.append(db.amonestacion_absentismo.id_grupo_alumno == db.grupo_alumno.id)
    queries.append(db.grupo_alumno.id_curso_academico_grupo == db.curso_academico_grupo.id)    
    queries.append(db.curso_academico_grupo.id == session.profesor.tutor.id_curso_academico_grupo)
    queries.append(db.grupo_alumno.id_alumno == db.alumno.id)
    
    if searching:
        if request.vars.fecha:
            fecha = request.vars.fecha
            queries.append(db.amonestacion_absentismo.fecha >= fecha)
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

    for r in db(query).select(db.amonestacion_absentismo.ALL,limitby=limitby,orderby=orderby):
        vals = []
        for f in fields:
            if f == 'alumno':
                alumno = r.id_grupo_alumno.id_alumno.apellidos+', '+r.id_grupo_alumno.id_alumno.nombre
                vals.append(alumno)
            elif f == 'profesor':
                profesor = r.id_departamento_profesor.id_profesor.apellidos+', '+r.id_departamento_profesor.id_profesor.nombre
                vals.append(profesor)
            else:
                rep = db.amonestacion_absentismo[f].represent
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
