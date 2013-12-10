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
#             (db.grupo_profesor_asignatura_alumno.id_grupo_profesor_asignatura == db.grupo_profesor_asignatura.id) &
             (db.curso_academico_grupo.id_tutor == db.profesor.id))
    evaluaciones = db(db.curso_academico_evaluacion.id_curso_academico == session.curso_academico_id).select(orderby=db.curso_academico_evaluacion.evaluacion)
    db.grupo_profesor_asignatura.id.readable = False
    db.profesor.apellidos.readable = False         
    db.profesor.nombre.readable = False
    links = [dict(header=T('Tutor/a'),body=lambda row:row.profesor.apellidos+', '+row.profesor.nombre)]     
    links.append(dict(header=CENTER(T('Evaluaciones')),body=lambda row:[A(SPAN(_class="ui-icon ui-icon-pencil"),SPAN(evaluacion.evaluacion.split()[0],_class="ui-button-text", 
                  _title=evaluacion.evaluacion),
                  _class='w2p_trap ui-button-text-icon-primary',
                  _href=URL('nuevo_evaluaciones','mi_evaluacion', args=[evaluacion.id,row.grupo_profesor_asignatura.id])) for evaluacion in evaluaciones]))
    grid = SQLFORM.grid(query,ui='jquery-ui',field_id=db.grupo_profesor_asignatura.id,deletable=False,create=False,editable=False,csv=False,details=False,searchable=False,
                        fields=[db.grupo.grupo, db.asignatura.asignatura, db.profesor.apellidos,db.profesor.nombre,db.grupo_profesor_asignatura.id],links=links,
                        orderby=db.grupo.grupo|db.asignatura.asignatura)
    return dict(grid=grid)
