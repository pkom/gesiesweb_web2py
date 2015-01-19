# coding: utf8
import delays

# intente algo como
def index(): return dict(message="hello from services_responsables.py")

@auth.requires_login()
@auth.requires_membership(role='Responsables')
def call():
    session.forget()
    return service()

@service.json
def getAllWarnings():
    #db.amonestacion.id_grupo_alumno.represent = lambda alumno: alumno.id_alumno.apellidos+', '+alumno.id_alumno.nombre+' ('+alumno.id_grupo.grupo+')'
    fields = ['id','fecha','grupo','profesor','alumno','parte','comunicada','cerrada','id_grupo_alumno','id_departamento_profesor']  
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
        orderby = (~db.profesor.apellidos | ~db.profesor.nombre | db.grupo.grupo |
            db.alumno.apellidos | db.alumno.nombre| ~db.amonestacion.fecha)
    elif (request.vars.sord == 'asc' and request.vars.sidx == 'profesor'): 
        orderby = (db.profesor.apellidos | db.profesor.nombre | db.grupo.grupo |
            db.alumno.apellidos | db.alumno.nombre| ~db.amonestacion.fecha)        
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
    queries.append(db.amonestacion.id_grupo_alumno == db.grupo_alumno.id)
    queries.append(db.amonestacion.id_departamento_profesor == db.departamento_profesor.id)   
    queries.append(db.grupo_alumno.id_curso_academico_grupo == db.curso_academico_grupo.id)
    queries.append(db.curso_academico_grupo.id_grupo == db.grupo.id)   
    queries.append(db.curso_academico_grupo.id_curso_academico == session.curso_academico_id)    
    queries.append(db.grupo_alumno.id_alumno == db.alumno.id)
    queries.append(db.departamento_profesor.id_profesor == db.profesor.id)    
       
    if request.vars.comunicada:
        if request.vars.comunicada == 'comunicadas':
            queries.append(db.amonestacion.comunicada == True)           
        else:
            queries.append(db.amonestacion.comunicada == False)    

    
    if searching:
        if request.vars.fecha:
            fecha = request.vars.fecha
            queries.append(db.amonestacion.fecha >= fecha)
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

    for r in db(query).select(db.amonestacion.ALL, db.grupo.ALL, db.profesor.ALL, db.alumno.ALL, limitby=limitby,orderby=orderby):
        vals = []
        for f in fields:
            if f == 'alumno':
                alumno = r.alumno.apellidos+', '+r.alumno.nombre
                vals.append(alumno)
            elif f == 'profesor':
                profesor = r.profesor.apellidos+', '+r.profesor.nombre
                vals.append(profesor)                
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
def getStatsWarnings():   
    queries=[]
    queries.append(db.amonestacion.id_grupo_alumno == db.grupo_alumno.id)
    queries.append(db.amonestacion.id_departamento_profesor == db.departamento_profesor.id)   
    queries.append(db.grupo_alumno.id_curso_academico_grupo == db.curso_academico_grupo.id)
    queries.append(db.curso_academico_grupo.id_grupo == db.grupo.id)   
    queries.append(db.curso_academico_grupo.id_curso_academico == session.curso_academico_id)    
    queries.append(db.grupo_alumno.id_alumno == db.alumno.id)
    queries.append(db.departamento_profesor.id_profesor == db.profesor.id)    
    query = reduce(lambda a,b:(a&b),queries)    
    total = db(query).count()
    queries.append(db.amonestacion.comunicada == True)           
    query = reduce(lambda a,b:(a&b),queries)       
    comunicadas = db(query).count()
    data = dict(total=total,comunicadas=comunicadas,no_comunicadas=total-comunicadas)
    return data

@service.json
def getAllAbsentismos():
    fields = ['id','fecha','grupo','profesor','alumno','comunicada','id_grupo_alumno','id_departamento_profesor']  
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
        orderby = (~db.profesor.apellidos | ~db.profesor.nombre | db.grupo.grupo |
            db.alumno.apellidos | db.alumno.nombre| ~db.amonestacion_absentismo.fecha)
    elif (request.vars.sord == 'asc' and request.vars.sidx == 'profesor'): 
        orderby = (db.profesor.apellidos | db.profesor.nombre | db.grupo.grupo |
            db.alumno.apellidos | db.alumno.nombre| ~db.amonestacion_absentismo.fecha)        
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
    queries.append(db.amonestacion_absentismo.id_grupo_alumno == db.grupo_alumno.id)
    queries.append(db.amonestacion_absentismo.id_departamento_profesor == db.departamento_profesor.id)   
    queries.append(db.grupo_alumno.id_curso_academico_grupo == db.curso_academico_grupo.id)
    queries.append(db.curso_academico_grupo.id_grupo == db.grupo.id)   
    queries.append(db.curso_academico_grupo.id_curso_academico == session.curso_academico_id)    
    queries.append(db.grupo_alumno.id_alumno == db.alumno.id)
    queries.append(db.departamento_profesor.id_profesor == db.profesor.id)    
       
    if request.vars.comunicada:
        if request.vars.comunicada == 'comunicadas':
            queries.append(db.amonestacion_absentismo.comunicada == True)           
        else:
            queries.append(db.amonestacion_absentismo.comunicada == False)    

    
    if searching:
        if request.vars.fecha:
            fecha = request.vars.fecha
            queries.append(db.amonestacion_absentismo.fecha >= fecha)
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

    for r in db(query).select(db.amonestacion_absentismo.ALL, db.grupo.ALL, db.profesor.ALL, db.alumno.ALL, limitby=limitby,orderby=orderby):
        vals = []
        for f in fields:
            if f == 'alumno':
                alumno = r.alumno.apellidos+', '+r.alumno.nombre
                vals.append(alumno)
            elif f == 'profesor':
                profesor = r.profesor.apellidos+', '+r.profesor.nombre
                vals.append(profesor)                
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
def getWarningsStudent():
    #db.amonestacion.id_grupo_alumno.represent = lambda alumno: alumno.id_alumno.apellidos+', '+alumno.id_alumno.nombre+' ('+alumno.id_grupo.grupo+')'
    fields = ['id','fecha','profesor','parte','comunicada','cerrada']  
    rows = []
    if request.vars._search == 'true':
        searching = True
    else:
        searching = False    
    id_grupo_alumno = int(request.vars.id_grupo_alumno)
    page = int(request.vars.page)
    pagesize = int(request.vars.rows)    
    limitby = (page * pagesize - pagesize,page * pagesize)
    
    if (request.vars.sord == 'desc' and request.vars.sidx == 'profesor'): 
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
    else:       
        orderby = ~orderby               

    
    queries=[]
    queries.append(db.amonestacion.id_grupo_alumno == id_grupo_alumno)    
    queries.append(db.amonestacion.id_grupo_alumno == db.grupo_alumno.id)
    queries.append(db.amonestacion.id_departamento_profesor == db.departamento_profesor.id)   
    queries.append(db.grupo_alumno.id_curso_academico_grupo == db.curso_academico_grupo.id)
    queries.append(db.curso_academico_grupo.id_grupo == db.grupo.id)   
    queries.append(db.curso_academico_grupo.id_curso_academico == session.curso_academico_id)    
    queries.append(db.grupo_alumno.id_alumno == db.alumno.id)
    queries.append(db.departamento_profesor.id_profesor == db.profesor.id)    
       
    if request.vars.comunicada:
        if request.vars.comunicada == 'comunicadas':
            queries.append(db.amonestacion.comunicada == True)           
        else:
            queries.append(db.amonestacion.comunicada == False)    

    
    if searching:
        if request.vars.fecha:
            fecha = request.vars.fecha
            queries.append(db.amonestacion.fecha >= fecha)
        if request.vars.profesor:
            profesor = '%'+request.vars.profesor.lower()+'%'
            queries.append((db.profesor.apellidos.lower().like(profesor) | db.profesor.nombre.lower().like(profesor))) 
        if request.vars.grupo:    
            grupo = '%'+request.vars.grupo.lower()+'%'
            queries.append(db.grupo.grupo.lower().like(grupo))                         
    query = reduce(lambda a,b:(a&b),queries)

    for r in db(query).select(db.amonestacion.ALL, db.grupo.ALL, db.profesor.ALL, db.alumno.ALL, limitby=limitby,orderby=orderby):
        vals = []
        for f in fields:
            if f == 'profesor':
                profesor = r.profesor.apellidos+', '+r.profesor.nombre
                vals.append(profesor)                
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
def getAbsentismosStudent():
    fields = ['id','fecha','profesor','comunicada']  
    rows = []
    if request.vars._search == 'true':
        searching = True
    else:
        searching = False    
    id_grupo_alumno = int(request.vars.id_grupo_alumno)
    page = int(request.vars.page)
    pagesize = int(request.vars.rows)    
    limitby = (page * pagesize - pagesize,page * pagesize)
    
    if (request.vars.sord == 'desc' and request.vars.sidx == 'profesor'): 
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
    else:       
        orderby = ~orderby               

    
    queries=[]
    queries.append(db.amonestacion_absentismo.id_grupo_alumno == id_grupo_alumno)    
    queries.append(db.amonestacion_absentismo.id_grupo_alumno == db.grupo_alumno.id)
    queries.append(db.amonestacion_absentismo.id_departamento_profesor == db.departamento_profesor.id)   
    queries.append(db.grupo_alumno.id_curso_academico_grupo == db.curso_academico_grupo.id)
    queries.append(db.curso_academico_grupo.id_grupo == db.grupo.id)   
    queries.append(db.curso_academico_grupo.id_curso_academico == session.curso_academico_id)    
    queries.append(db.grupo_alumno.id_alumno == db.alumno.id)
    queries.append(db.departamento_profesor.id_profesor == db.profesor.id)    
       
    if request.vars.comunicada:
        if request.vars.comunicada == 'comunicadas':
            queries.append(db.amonestacion_absentismo.comunicada == True)           
        else:
            queries.append(db.amonestacion_absentismo.comunicada == False)    

    
    if searching:
        if request.vars.fecha:
            fecha = request.vars.fecha
            queries.append(db.amonestacion_absentismo.fecha >= fecha)
        if request.vars.profesor:
            profesor = '%'+request.vars.profesor.lower()+'%'
            queries.append((db.profesor.apellidos.lower().like(profesor) | db.profesor.nombre.lower().like(profesor))) 
        if request.vars.grupo:    
            grupo = '%'+request.vars.grupo.lower()+'%'
            queries.append(db.grupo.grupo.lower().like(grupo))                         
    query = reduce(lambda a,b:(a&b),queries)

    for r in db(query).select(db.amonestacion_absentismo.ALL, db.grupo.ALL, db.profesor.ALL, db.alumno.ALL, limitby=limitby,orderby=orderby):
        vals = []
        for f in fields:
            if f == 'profesor':
                profesor = r.profesor.apellidos+', '+r.profesor.nombre
                vals.append(profesor)                
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
def getWarningsDelaysStudent():
    fields = ['id','fecha','profesor']  
    rows = []
    if request.vars._search == 'true':
        searching = True
    else:
        searching = False    
    id_grupo_alumno = int(request.vars.id_grupo_alumno)
    page = int(request.vars.page)
    pagesize = int(request.vars.rows)    
    limitby = (page * pagesize - pagesize,page * pagesize)
    
    if (request.vars.sord == 'desc' and request.vars.sidx == 'profesor'): 
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
    else:       
        orderby = ~orderby               

    
    queries=[]
    queries.append(db.amonestacion_retraso.id_grupo_alumno == id_grupo_alumno)    
    queries.append(db.amonestacion_retraso.id_grupo_alumno == db.grupo_alumno.id)
    queries.append(db.amonestacion_retraso.id_departamento_profesor == db.departamento_profesor.id)   
    queries.append(db.grupo_alumno.id_curso_academico_grupo == db.curso_academico_grupo.id)
    queries.append(db.curso_academico_grupo.id_grupo == db.grupo.id)   
    queries.append(db.curso_academico_grupo.id_curso_academico == session.curso_academico_id)    
    queries.append(db.grupo_alumno.id_alumno == db.alumno.id)
    queries.append(db.departamento_profesor.id_profesor == db.profesor.id)    
           
    if searching:
        if request.vars.fecha:
            fecha = request.vars.fecha
            queries.append(db.amonestacion_retraso.fecha >= fecha)
        if request.vars.profesor:
            profesor = '%'+request.vars.profesor.lower()+'%'
            queries.append((db.profesor.apellidos.lower().like(profesor) | db.profesor.nombre.lower().like(profesor))) 
        if request.vars.grupo:    
            grupo = '%'+request.vars.grupo.lower()+'%'
            queries.append(db.grupo.grupo.lower().like(grupo))                         
    query = reduce(lambda a,b:(a&b),queries)

    for r in db(query).select(db.amonestacion_retraso.ALL, db.grupo.ALL, db.profesor.ALL, db.alumno.ALL, limitby=limitby,orderby=orderby):
        vals = []
        for f in fields:
            if f == 'profesor':
                profesor = r.profesor.apellidos+', '+r.profesor.nombre
                vals.append(profesor)                
            else:
                rep = db.amonestacion_retraso[f].represent
                if rep:
                    vals.append(rep(r.amonestacion_retraso[f]))
                else:
                    vals.append(r.amonestacion_retraso[f])
        rows.append(dict(id=r.amonestacion_retraso.id,cell=vals))
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
def getWarningsTeacher():
    fields = ['id','fecha','alumno','grupo','parte','comunicada','cerrada']  
    rows = []
    if request.vars._search == 'true':
        searching = True
    else:
        searching = False    
    id_departamento_profesor = int(request.vars.id_departamento_profesor)
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
    elif (request.vars.sord == 'desc' and request.vars.sidx == 'grupo'):
        orderby = (~db.grupo.grupo | ~db.amonestacion.id)
    elif (request.vars.sord == 'asc' and request.vars.sidx == 'grupo'):
        orderby = (db.grupo.grupo | db.amonestacion.id)        
    elif (request.vars.sord == 'asc' and request.vars.sidx == 'id'):
        orderby = db.amonestacion.id
    elif (request.vars.sord == 'desc' and request.vars.sidx == 'id'):
        orderby = ~db.amonestacion.id
    else:       
        orderby = ~orderby               

    
    queries=[]
    queries.append(db.amonestacion.id_departamento_profesor == id_departamento_profesor)    
    queries.append(db.amonestacion.id_grupo_alumno == db.grupo_alumno.id)
    queries.append(db.amonestacion.id_departamento_profesor == db.departamento_profesor.id)   
    queries.append(db.grupo_alumno.id_curso_academico_grupo == db.curso_academico_grupo.id)
    queries.append(db.curso_academico_grupo.id_grupo == db.grupo.id)   
    queries.append(db.curso_academico_grupo.id_curso_academico == session.curso_academico_id)    
    queries.append(db.grupo_alumno.id_alumno == db.alumno.id)
    queries.append(db.departamento_profesor.id_profesor == db.profesor.id)    
       
    if request.vars.comunicada:
        if request.vars.comunicada == 'comunicadas':
            queries.append(db.amonestacion.comunicada == True)           
        else:
            queries.append(db.amonestacion.comunicada == False)    

    
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

    for r in db(query).select(db.amonestacion.ALL, db.grupo.ALL, db.alumno.ALL, db.alumno.ALL, limitby=limitby,orderby=orderby):
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
def getAbsentismosTeacher():
    fields = ['id','fecha','alumno','grupo','comunicada']  
    rows = []
    if request.vars._search == 'true':
        searching = True
    else:
        searching = False    
    id_departamento_profesor = int(request.vars.id_departamento_profesor)
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
    elif (request.vars.sord == 'desc' and request.vars.sidx == 'grupo'):
        orderby = (~db.grupo.grupo | ~db.amonestacion_absentismo.id)
    elif (request.vars.sord == 'asc' and request.vars.sidx == 'grupo'):
        orderby = (db.grupo.grupo | db.amonestacion_absentismo.id)        
    elif (request.vars.sord == 'asc' and request.vars.sidx == 'id'):
        orderby = db.amonestacion_absentismo.id
    elif (request.vars.sord == 'desc' and request.vars.sidx == 'id'):
        orderby = ~db.amonestacion_absentismo.id
    else:       
        orderby = ~orderby               

    
    queries=[]
    queries.append(db.amonestacion_absentismo.id_departamento_profesor == id_departamento_profesor)    
    queries.append(db.amonestacion_absentismo.id_grupo_alumno == db.grupo_alumno.id)
    queries.append(db.amonestacion_absentismo.id_departamento_profesor == db.departamento_profesor.id)   
    queries.append(db.grupo_alumno.id_curso_academico_grupo == db.curso_academico_grupo.id)
    queries.append(db.curso_academico_grupo.id_grupo == db.grupo.id)   
    queries.append(db.curso_academico_grupo.id_curso_academico == session.curso_academico_id)    
    queries.append(db.grupo_alumno.id_alumno == db.alumno.id)
    queries.append(db.departamento_profesor.id_profesor == db.profesor.id)    
       
    if request.vars.comunicada:
        if request.vars.comunicada == 'comunicadas':
            queries.append(db.amonestacion_absentismo.comunicada == True)           
        else:
            queries.append(db.amonestacion_absentismo.comunicada == False)    

    
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

    for r in db(query).select(db.amonestacion_absentismo.ALL, db.grupo.ALL, db.alumno.ALL, db.alumno.ALL, limitby=limitby,orderby=orderby):
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
def updateReported():
    if request.vars.id:
        if request.vars.isChecked == 'true':
            db.amonestacion[request.vars.id] = dict(parte = True)
        else:
            db.amonestacion[request.vars.id] = dict(parte = False)
        db.commit()        
        return True
    else:
        return False

@service.json
def updateClosed():
    if request.vars.id:
        if request.vars.isChecked == 'true':
            db.amonestacion[request.vars.id] = dict(cerrada = True)
        else:
            db.amonestacion[request.vars.id] = dict(cerrada = False)
        db.commit()        
        return True
    else:
        return False

@service.json
def updateDelayClosed():
    if request.vars.id:
        if request.vars.isChecked == 'true':
            db.amonestacion_retraso[request.vars.id] = dict(cerrada = True)
        else:
            db.amonestacion_retraso[request.vars.id] = dict(cerrada = False)
        db.commit()        
        return True
    else:
        return False

@service.json
def updateDelayComunicated():
    if request.vars.id:
        if request.vars.isChecked == 'true':
            db.amonestacion_retraso[request.vars.id] = dict(comunicada = True)
        else:
            db.amonestacion_retraso[request.vars.id] = dict(comunicada = False)
        db.commit()        
        return True
    else:
        return False


@service.json
def updateHeadDepartament():
    idjefe = int(request.vars.idjefe)
    idcursoacademicodepartamento = int(request.vars.idcursoacademicodepartamento)
    if idjefe and idcursoacademicodepartamento:
        try:
            if idjefe == -1: 
                db.curso_academico_departamento[idcursoacademicodepartamento] = dict(id_jefe = None)
            else:
                db.curso_academico_departamento[idcursoacademicodepartamento] = dict(id_jefe = idjefe)
        except: 
            return dict(estado='Fallo')
        db.commit()
        return dict(estado='OK')
    else:
        return dict(estado='NOPARAMETRO')

@service.json
def updateTutor():
    idtutor = int(request.vars.idtutor)
    idcursoacademicogrupo = int(request.vars.idcursoacademicogrupo)
    if idtutor and idcursoacademicogrupo:
        try:
            if idtutor == -1: 
                db.curso_academico_grupo[idcursoacademicogrupo] = dict(id_tutor = None)
            else:
                db.curso_academico_grupo[idcursoacademicogrupo] = dict(id_tutor = idtutor)
        except: 
            return dict(estado='Fallo')
        db.commit()
        return dict(estado='OK')
    else:
        return dict(estado='NOPARAMETRO')

@service.json
def getSeguimientos():
    fields = ['fecha','responsable','seguimiento']  
    rows = []
    if request.vars._search == 'true':
        searching = True
    else:
        searching = False    
        
    id_amonestacion = int(request.vars.id)    
    page = int(request.vars.page)
    pagesize = int(request.vars.rows)    
    limitby = (page * pagesize - pagesize,page * pagesize)
    
    if (request.vars.sord == 'desc' and request.vars.sidx == 'responsable'): 
        orderby = (~db.profesor.apellidos | ~db.profesor.nombre | ~db.seguimiento.fecha)
    elif (request.vars.sord == 'asc' and request.vars.sidx == 'responsable'): 
        orderby = (db.profesor.apellidos | db.profesor.nombre | ~db.seguimiento.fecha)
    elif (request.vars.sord == 'desc' and request.vars.sidx == 'fecha'):
        orderby = (~db.seguimiento.fecha | ~db.seguimiento.id)
    elif (request.vars.sord == 'asc' and request.vars.sidx == 'fecha'):
        orderby = (db.seguimiento.fecha | db.seguimiento.id)
    elif (request.vars.sord == 'asc' and request.vars.sidx == 'id'):
        orderby = db.seguimiento.id
    elif (request.vars.sord == 'desc' and request.vars.sidx == 'id'):
        orderby = ~db.seguimiento.id
    else:       
        orderby = ~orderby               

    
    queries=[]
    queries.append(db.seguimiento.id_amonestacion == id_amonestacion)
    queries.append(db.seguimiento.id_responsable == db.departamento_profesor.id)
    queries.append(db.departamento_profesor.id_profesor == db.profesor.id)    
          
    if searching:
        if request.vars.fecha:
            fecha = request.vars.fecha
            queries.append(db.seguimiento.fecha >= fecha)
        if request.vars.seguimiento:
            seguimiento = '%'+request.vars.seguimiento.lower()+'%'
            queries.append(db.seguimiento.seguimiento.lower().like(seguimiento)) 
    query = reduce(lambda a,b:(a&b),queries)

    for r in db(query).select(db.seguimiento.ALL, db.profesor.ALL, db.departamento_profesor.ALL, limitby=limitby,orderby=orderby):
        vals = []
        for f in fields:
            if f == 'responsable':
                responsable = r.profesor.apellidos+', '+r.profesor.nombre
                vals.append(responsable)
            else:
                rep = db.seguimiento[f].represent
                if rep:
                    vals.append(rep(r.seguimiento[f]))
                else:
                    vals.append(r.seguimiento[f])
        rows.append(dict(id=r.seguimiento.id,cell=vals))
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
def addSeguimiento():
    fecha = request.vars.fecha
    id_aviso = request.vars.id_aviso
    oper = request.vars.oper
    seguimiento = request.vars.seguimiento 
    id_seguimiento = request.vars.id
    if oper == "add":
        db.seguimiento.insert(id_amonestacion=id_aviso,fecha=fecha,seguimiento=seguimiento,id_responsable=session.profesor.id_departamento_profesor)
    if oper == "del":
        del db.seguimiento[id_seguimiento]
    if oper == "edit":
        db.seguimiento[id_seguimiento].update_record(fecha=fecha,seguimiento=seguimiento,id_responsable=session.profesor.id_departamento_profesor)
    db.commit()

@service.json
def getAllWarningsDelays():
    fields = ['id','fecha','grupo','alumno','comunicada','cerrada','id_grupo_alumno']  
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
        orderby = (~db.grupo.grupo | db.alumno.apellidos | db.alumno.nombre | ~db.amonestacion_retraso.fecha)        
    else:       
        orderby = ~orderby               

    
    queries=[]
    queries.append(db.amonestacion_retraso.id_grupo_alumno == db.grupo_alumno.id)
    queries.append(db.grupo_alumno.id_curso_academico_grupo == db.curso_academico_grupo.id)
    queries.append(db.curso_academico_grupo.id_grupo == db.grupo.id)   
    queries.append(db.curso_academico_grupo.id_curso_academico == session.curso_academico_id)           
    queries.append(db.grupo_alumno.id_alumno == db.alumno.id)


    if request.vars.comunicado:
        if request.vars.comunicado == 'comunicados':
            queries.append(db.amonestacion_retraso.comunicada == True)           
        else:
            queries.append(db.amonestacion_retraso.comunicada == False)    

    if request.vars.cerrado:
        if request.vars.cerrado == 'cerrados':
            queries.append(db.amonestacion_retraso.cerrada == True)           
        else:
            queries.append(db.amonestacion_retraso.cerrada == False)    
    

          
    if searching:
        if request.vars.fecha:
            fecha = request.vars.fecha
            queries.append(db.amonestacion_retraso.fecha >= fecha)
        if request.vars.alumno:
            alumno = '%'+request.vars.alumno.lower()+'%'
            queries.append((db.alumno.apellidos.lower().like(alumno) | db.alumno.nombre.lower().like(alumno))) 
        if request.vars.grupo:    
            grupo = '%'+request.vars.grupo.lower()+'%'
            queries.append(db.grupo.grupo.lower().like(grupo)) 
    query = reduce(lambda a,b:(a&b),queries)

    for r in db(query).select(db.amonestacion_retraso.ALL, db.grupo.ALL, db.alumno.ALL, limitby=limitby,orderby=orderby):
        vals = []
        for f in fields:
            if f == 'alumno':
                alumno = r.alumno.apellidos+', '+r.alumno.nombre
                vals.append(alumno)
            elif f == 'grupo':
                grupo = r.grupo.grupo
                vals.append(grupo)
            else:
                rep = db.amonestacion_retraso[f].represent
                if rep:
                    vals.append(rep(r.amonestacion_retraso[f]))
                else:
                    vals.append(r.amonestacion_retraso[f])
        rows.append(dict(id=r.amonestacion_retraso.id,cell=vals))
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
def getRetrasos():
    fields = ['id','fecha','hora','profesor']  
    rows = []
    if request.vars._search == 'true':
        searching = True
    else:
        searching = False    
        
    id_amonestacion_retraso = int(request.vars.id)    
    page = int(request.vars.page)
    pagesize = int(request.vars.rows)    
    limitby = (page * pagesize - pagesize,page * pagesize)
    
    if (request.vars.sord == 'desc' and request.vars.sidx == 'profesor'): 
        orderby = (~db.profesor.apellidos | ~db.profesor.nombre | ~db.retraso.fecha)
    elif (request.vars.sord == 'asc' and request.vars.sidx == 'profesor'): 
        orderby = (db.profesor.apellidos | db.profesor.nombre | ~db.retraso.fecha)
    elif (request.vars.sord == 'desc' and request.vars.sidx == 'fecha'):
        orderby = (~db.retraso.fecha | ~db.retraso.id)
    elif (request.vars.sord == 'asc' and request.vars.sidx == 'fecha'):
        orderby = (db.retraso.fecha | db.retraso.id)
    elif (request.vars.sord == 'asc' and request.vars.sidx == 'hora'):
        orderby = db.retraso.hora
    elif (request.vars.sord == 'desc' and request.vars.sidx == 'hora'):
        orderby = ~db.retraso.hora
    elif (request.vars.sord == 'asc' and request.vars.sidx == 'id'):
        orderby = db.retraso.id
    elif (request.vars.sord == 'desc' and request.vars.sidx == 'id'):
        orderby = ~db.retraso.id
        
    else:       
        orderby = ~orderby               

    
    queries=[]
    queries.append(db.amonestacion_retraso_retraso.id_amonestacion_retraso == id_amonestacion_retraso)
    queries.append(db.amonestacion_retraso_retraso.id_retraso == db.retraso.id)
    queries.append(db.retraso.id_departamento_profesor == db.departamento_profesor.id)    
    queries.append(db.departamento_profesor.id_profesor == db.profesor.id)    
          
    if searching:
        if request.vars.fecha:
            fecha = request.vars.fecha
            queries.append(db.retraso.fecha >= fecha)
    query = reduce(lambda a,b:(a&b),queries)

    for r in db(query).select(db.amonestacion_retraso_retraso.ALL, db.retraso.ALL, db.profesor.ALL, db.departamento_profesor.ALL, limitby=limitby,orderby=orderby):
        vals = []
        for f in fields:
            if f == 'profesor':
                profesor = r.profesor.apellidos+', '+r.profesor.nombre
                vals.append(profesor)
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
def getStudentsResume():
    fields = ['alumno','grupo','totalavisos','totalavisoscomunicados','totalavisosnocomunicados',
    'id_grupo_alumno']  
    rows = []
    if request.vars._search == 'true':
        searching = True
    else:
        searching = False    
    page = int(request.vars.page)
    pagesize = int(request.vars.rows)    

    totalavisos = db.amonestacion.id.count()
       
    queries=[]
    queries.append(db.amonestacion.id_grupo_alumno == db.grupo_alumno.id)
    queries.append(db.grupo_alumno.id_curso_academico_grupo == db.curso_academico_grupo.id)
    queries.append(db.curso_academico_grupo.id_grupo == db.grupo.id)   
    queries.append(db.curso_academico_grupo.id_curso_academico == session.curso_academico_id)           
    queries.append(db.grupo_alumno.id_alumno == db.alumno.id)
          
    if searching:
        if request.vars.alumno:
            alumno = '%'+request.vars.alumno.lower()+'%'
            queries.append((db.alumno.apellidos.lower().like(alumno) | db.alumno.nombre.lower().like(alumno))) 
        if request.vars.grupo:    
            grupo = '%'+request.vars.grupo.lower()+'%'
            queries.append(db.grupo.grupo.lower().like(grupo)) 
    query = reduce(lambda a,b:(a&b),queries)
    
    # for r in db(query).select(db.amonestacion.ALL, db.grupo.ALL, db.alumno.ALL, totalavisos, orderby=~totalavisos, groupby=db.amonestacion.id_grupo_alumno):
    #     vals = []
    #     for f in fields:
    #         if f == 'alumno':
    #             vals.append(r.alumno.apellidos+', '+r.alumno.nombre)
    #         elif f == 'grupo':
    #             vals.append(r.grupo.grupo)
    #         elif f == 'totalavisos':
    #             vals.append(r[totalavisos])                
    #         else:
    #             rep = db.amonestacion[f].represent
    #             if rep:
    #                 vals.append(rep(r.amonestacion[f]))
    #             else:
    #                 vals.append(r.amonestacion[f])
    #     rows.append(dict(id=r.amonestacion.id_grupo_alumno,cell=vals))

    datos = dict()
    for r in db(query).select(db.amonestacion.ALL, db.grupo.ALL, db.alumno.ALL):
        if r.amonestacion.id_grupo_alumno in datos:
            datos[r.amonestacion.id_grupo_alumno][2] += 1
            if r.amonestacion.comunicada:
                datos[r.amonestacion.id_grupo_alumno][3] += 1         
            else:
                datos[r.amonestacion.id_grupo_alumno][4] += 1           
        else:
            datos[r.amonestacion.id_grupo_alumno] = []
            datos[r.amonestacion.id_grupo_alumno].append(r.alumno.apellidos+', '+r.alumno.nombre)
            datos[r.amonestacion.id_grupo_alumno].append(r.grupo.grupo)
            datos[r.amonestacion.id_grupo_alumno].append(1)
            if r.amonestacion.comunicada:
                datos[r.amonestacion.id_grupo_alumno].append(1)         
                datos[r.amonestacion.id_grupo_alumno].append(0)
            else:
                datos[r.amonestacion.id_grupo_alumno].append(0)         
                datos[r.amonestacion.id_grupo_alumno].append(1)
            datos[r.amonestacion.id_grupo_alumno].append(r.amonestacion.id_grupo_alumno)

    listadatos = datos.items()
    listadatos.sort(key=lambda x: x[1][2])
    rows = []
    while listadatos:
        p = listadatos.pop()
        d = dict(cell=p[1], id=p[0])
        rows.append(d)

      
    total = len(rows)
    if total <= pagesize:
        pages = 1
    else:   
        pages = int(total/pagesize)
        if total % pagesize <> 0:
            pages += 1
            
            
    limitby = (page * pagesize - pagesize,page * pagesize)
    data = dict(total=pages,page=page,records=total,rows=rows[limitby[0]:limitby[1]])
    return data
    
@service.json
def getStudentsAbsentismoResume():
    fields = ['alumno','grupo','totalavisos','id_grupo_alumno']  
    rows = []
    if request.vars._search == 'true':
        searching = True
    else:
        searching = False    
    page = int(request.vars.page)
    pagesize = int(request.vars.rows)    

    totalavisos = db.amonestacion_absentismo.id.count()
       
    queries=[]
    queries.append(db.amonestacion_absentismo.id_grupo_alumno == db.grupo_alumno.id)
    queries.append(db.grupo_alumno.id_curso_academico_grupo == db.curso_academico_grupo.id)
    queries.append(db.curso_academico_grupo.id_grupo == db.grupo.id)   
    queries.append(db.curso_academico_grupo.id_curso_academico == session.curso_academico_id)           
    queries.append(db.grupo_alumno.id_alumno == db.alumno.id)
          
    if searching:
        if request.vars.alumno:
            alumno = '%'+request.vars.alumno.lower()+'%'
            queries.append((db.alumno.apellidos.lower().like(alumno) | db.alumno.nombre.lower().like(alumno))) 
        if request.vars.grupo:    
            grupo = '%'+request.vars.grupo.lower()+'%'
            queries.append(db.grupo.grupo.lower().like(grupo)) 
    query = reduce(lambda a,b:(a&b),queries)
    
    for r in db(query).select(db.amonestacion_absentismo.ALL, db.grupo.ALL, db.alumno.ALL, totalavisos, orderby=~totalavisos, groupby=db.amonestacion_absentismo.id_grupo_alumno):
        vals = []
        for f in fields:
            if f == 'alumno':
                vals.append(r.alumno.apellidos+', '+r.alumno.nombre)
            elif f == 'grupo':
                vals.append(r.grupo.grupo)
            elif f == 'totalavisos':
                vals.append(r[totalavisos])                
            else:
                rep = db.amonestacion_absentismo[f].represent
                if rep:
                    vals.append(rep(r.amonestacion_absentismo[f]))
                else:
                    vals.append(r.amonestacion_absentismo[f])
        rows.append(dict(id=r.amonestacion_absentismo.id_grupo_alumno,cell=vals))
      
    total = len(rows)
    if total <= pagesize:
        pages = 1
    else:   
        pages = int(total/pagesize)
        if total % pagesize <> 0:
            pages += 1
            
            
    limitby = (page * pagesize - pagesize,page * pagesize)
    data = dict(total=pages,page=page,records=total,rows=rows[limitby[0]:limitby[1]])
    return data    
    
@service.json
def getTeachersResume():
    fields = ['profesor','departamento','totalavisos','totalavisoscomunicados', 'totalavisosnocomunicados',
    'id_departamento_profesor']  
    rows = []
    if request.vars._search == 'true':
        searching = True
    else:
        searching = False    
    page = int(request.vars.page)
    pagesize = int(request.vars.rows)    

    totalavisos = db.amonestacion.id.count()
       
    queries=[]
    queries.append(db.amonestacion.id_departamento_profesor == db.departamento_profesor.id)
    queries.append(db.departamento_profesor.id_curso_academico_departamento == db.curso_academico_departamento.id)
    queries.append(db.curso_academico_departamento.id_departamento == db.departamento.id)   
    queries.append(db.curso_academico_departamento.id_curso_academico == session.curso_academico_id)           
    queries.append(db.departamento_profesor.id_profesor == db.profesor.id)
          
    if searching:
        if request.vars.profesor:
            profesor = '%'+request.vars.profesor.lower()+'%'
            queries.append((db.profesor.apellidos.lower().like(profesor) | db.profesor.nombre.lower().like(profesor))) 
        if request.vars.departamento:    
            departamento = '%'+request.vars.departamento.lower()+'%'
            queries.append(db.departamento.departamento.lower().like(departamento)) 
    query = reduce(lambda a,b:(a&b),queries)


    # for r in db(query).select(db.amonestacion.ALL, db.departamento.ALL, db.profesor.ALL, totalavisos, orderby=~totalavisos, groupby=db.amonestacion.id_departamento_profesor):
    #     vals = []
    #     for f in fields:
    #         if f == 'profesor':
    #             vals.append(r.profesor.apellidos+', '+r.profesor.nombre)
    #         elif f == 'departamento':
    #             vals.append(r.departamento.departamento)
    #         elif f == 'totalavisos':
    #             vals.append(r[totalavisos])                
    #         elif f == 'totalavisoscomunicados':
    #             vals.append(0)                
    #         elif f == 'totalavisosnocomunicados':
    #             vals.append(0)                
    #         else:
    #             rep = db.amonestacion[f].represent
    #             if rep:
    #                 vals.append(rep(r.amonestacion[f]))
    #             else:
    #                 vals.append(r.amonestacion[f])
    #     rows.append(dict(id=r.amonestacion.id_departamento_profesor,cell=vals))

    datos = dict()
    for r in db(query).select(db.amonestacion.ALL, db.departamento.ALL, db.profesor.ALL):
        if r.amonestacion.id_departamento_profesor in datos:
            datos[r.amonestacion.id_departamento_profesor][2] += 1
            if r.amonestacion.comunicada:
                datos[r.amonestacion.id_departamento_profesor][3] += 1         
            else:
                datos[r.amonestacion.id_departamento_profesor][4] += 1           
        else:
            datos[r.amonestacion.id_departamento_profesor] = []
            datos[r.amonestacion.id_departamento_profesor].append(r.profesor.apellidos+', '+r.profesor.nombre)
            datos[r.amonestacion.id_departamento_profesor].append(r.departamento.departamento)
            datos[r.amonestacion.id_departamento_profesor].append(1)
            if r.amonestacion.comunicada:
                datos[r.amonestacion.id_departamento_profesor].append(1)         
                datos[r.amonestacion.id_departamento_profesor].append(0)
            else:
                datos[r.amonestacion.id_departamento_profesor].append(0)         
                datos[r.amonestacion.id_departamento_profesor].append(1)
            datos[r.amonestacion.id_departamento_profesor].append(r.amonestacion.id_departamento_profesor)

    listadatos = datos.items()
    listadatos.sort(key=lambda x: x[1][2])
    rows = []
    while listadatos:
        p = listadatos.pop()
        d = dict(cell=p[1], id=p[0])
        rows.append(d)

    total = len(rows)
    if total <= pagesize:
        pages = 1
    else:   
        pages = int(total/pagesize)
        if total % pagesize <> 0:
            pages += 1
            
            
    limitby = (page * pagesize - pagesize,page * pagesize)
    data = dict(total=pages,page=page,records=total,rows=rows[limitby[0]:limitby[1]])
    return data

@service.json
def getTeachersAbsentismoResume():
    fields = ['profesor','departamento','totalavisos','id_departamento_profesor']  
    rows = []
    if request.vars._search == 'true':
        searching = True
    else:
        searching = False    
    page = int(request.vars.page)
    pagesize = int(request.vars.rows)    

    totalavisos = db.amonestacion_absentismo.id.count()
       
    queries=[]
    queries.append(db.amonestacion_absentismo.id_departamento_profesor == db.departamento_profesor.id)
    queries.append(db.departamento_profesor.id_curso_academico_departamento == db.curso_academico_departamento.id)
    queries.append(db.curso_academico_departamento.id_departamento == db.departamento.id)   
    queries.append(db.curso_academico_departamento.id_curso_academico == session.curso_academico_id)           
    queries.append(db.departamento_profesor.id_profesor == db.profesor.id)
          
    if searching:
        if request.vars.profesor:
            profesor = '%'+request.vars.profesor.lower()+'%'
            queries.append((db.profesor.apellidos.lower().like(profesor) | db.profesor.nombre.lower().like(profesor))) 
        if request.vars.departamento:    
            departamento = '%'+request.vars.departamento.lower()+'%'
            queries.append(db.departamento.departamento.lower().like(departamento)) 
    query = reduce(lambda a,b:(a&b),queries)
    
    for r in db(query).select(db.amonestacion_absentismo.ALL, db.departamento.ALL, db.profesor.ALL, totalavisos, orderby=~totalavisos,
                                 groupby=db.amonestacion_absentismo.id_departamento_profesor):
        vals = []
        for f in fields:
            if f == 'profesor':
                vals.append(r.profesor.apellidos+', '+r.profesor.nombre)
            elif f == 'departamento':
                vals.append(r.departamento.departamento)
            elif f == 'totalavisos':
                vals.append(r[totalavisos])                
            else:
                rep = db.amonestacion_absentismo[f].represent
                if rep:
                    vals.append(rep(r.amonestacion_absentismo[f]))
                else:
                    vals.append(r.amonestacion_absentismo[f])
        rows.append(dict(id=r.amonestacion_absentismo.id_departamento_profesor,cell=vals))
      
    total = len(rows)
    if total <= pagesize:
        pages = 1
    else:   
        pages = int(total/pagesize)
        if total % pagesize <> 0:
            pages += 1
            
            
    limitby = (page * pagesize - pagesize,page * pagesize)
    data = dict(total=pages,page=page,records=total,rows=rows[limitby[0]:limitby[1]])
    return data


@service.json
def getWarning():
    idaviso = int(request.vars.id)
    aviso = None
    try:
        consulta = db((db.amonestacion.id == idaviso) &
                   (db.amonestacion.id_grupo_alumno == db.grupo_alumno.id) &
                   (db.grupo_alumno.id_curso_academico_grupo == db.curso_academico_grupo.id) &
                   (db.curso_academico_grupo.id_grupo == db.grupo.id)).select(db.curso_academico_grupo.ALL,db.amonestacion.ALL,db.seguimiento.ALL,
                       left=db.seguimiento.on(db.amonestacion.id==db.seguimiento.id_amonestacion),orderby=~db.seguimiento.id)
        aviso = consulta.as_list()
        respuesta = aviso
    except:
        respuesta = 'fallo'    
    return dict(response=respuesta)

@service.json
def getStudentsResumeDelays():
    fields = ['alumno','grupo','totalavisos','id_grupo_alumno']  
    rows = []
    if request.vars._search == 'true':
        searching = True
    else:
        searching = False    
    page = int(request.vars.page)
    pagesize = int(request.vars.rows)    

    totalavisos = db.amonestacion_retraso.id.count()
       
    queries=[]
    queries.append(db.amonestacion_retraso.id_grupo_alumno == db.grupo_alumno.id)
    queries.append(db.grupo_alumno.id_curso_academico_grupo == db.curso_academico_grupo.id)
    queries.append(db.curso_academico_grupo.id_grupo == db.grupo.id)   
    queries.append(db.curso_academico_grupo.id_curso_academico == session.curso_academico_id)           
    queries.append(db.grupo_alumno.id_alumno == db.alumno.id)
          
    if searching:
        if request.vars.alumno:
            alumno = '%'+request.vars.alumno.lower()+'%'
            queries.append((db.alumno.apellidos.lower().like(alumno) | db.alumno.nombre.lower().like(alumno))) 
        if request.vars.grupo:    
            grupo = '%'+request.vars.grupo.lower()+'%'
            queries.append(db.grupo.grupo.lower().like(grupo)) 
    query = reduce(lambda a,b:(a&b),queries)
    
    for r in db(query).select(db.amonestacion_retraso.ALL, db.grupo.ALL, db.alumno.ALL, totalavisos, orderby=~totalavisos, groupby=db.amonestacion_retraso.id_grupo_alumno):
        vals = []
        for f in fields:
            if f == 'alumno':
                vals.append(r.alumno.apellidos+', '+r.alumno.nombre)
            elif f == 'grupo':
                vals.append(r.grupo.grupo)
            elif f == 'totalavisos':
                vals.append(r[totalavisos])                
            else:
                rep = db.amonestacion_retraso[f].represent
                if rep:
                    vals.append(rep(r.amonestacion_retraso[f]))
                else:
                    vals.append(r.amonestacion_retraso[f])
        rows.append(dict(id=r.amonestacion_retraso.id_grupo_alumno,cell=vals))
      
    total = len(rows)
    if total <= pagesize:
        pages = 1
    else:   
        pages = int(total/pagesize)
        if total % pagesize <> 0:
            pages += 1
            
            
    limitby = (page * pagesize - pagesize,page * pagesize)
    data = dict(total=pages,page=page,records=total,rows=rows[limitby[0]:limitby[1]])
    return data

@service.json
def realizaSustitucion():
    iddepartamentoprofesor = int(request.vars.iddepartamentoprofesor) or None
    idsustituido = int(request.vars.idsustituido) or None
    if iddepartamentoprofesor and idsustituido:
        try:
            if idsustituido == -1: 
                db.departamento_profesor[iddepartamentoprofesor] = dict(sustituye = None)
            else:
                db.departamento_profesor[iddepartamentoprofesor] = dict(sustituye = idsustituido)
        except: 
            return dict(estado='Fallo')
        db.commit()
        return dict(estado='OK')
    else:
        return dict(estado='NOPARAMETRO')
