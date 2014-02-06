# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

import obies

@auth.requires_login()
@auth.requires_membership(role='Responsables')    
def evaluaciones():
    # primero rellenaremos los grupos activos en el curso actual y las evaluaciones existentes
    ogrupo = obies.Grupo(db, session)
    grupos = ogrupo.dame_grupos_curso()
    grup = FIELDSET("Escoge grupo: ", SELECT(*[OPTION(grupo.grupo.grupo+" ("+grupo.curso_academico_grupo.id_tutor.apellidos+", "+
             grupo.curso_academico_grupo.id_tutor.nombre+")", _value=grupo.curso_academico_grupo.id) for grupo in grupos],
            _id="selectgruposinformes", _name="selectgruposinformes"), _id="fieldsetescogegrupo")
    tipos = FIELDSET("Escoge tipo: ", SELECT([OPTION("Individualizado Grupo", _value=0), OPTION("Resumen Evaluación Grupo", _value=1), OPTION("Resumen Curso Grupo", _value=2),
        OPTION("Fichas-Registro Grupo", _value=3), OPTION("Resumen Evaluación Agrupados", _value=4), OPTION("Resumen Curso Agrupados", _value=5)],
        _id="selecttiposinformes", _name="selecttiposinformes"), _id="fieldsetescogetipo")
    oevaluaciones = obies.Evaluacion(db, session)
    evaluaciones = oevaluaciones.dame_evaluaciones()
    evaluas = FIELDSET("Escoge evaluación: ", SELECT(*[OPTION(evaluacion.evaluacion, _value=evaluacion.id) for evaluacion in evaluaciones], 
            _id="selectevaluacionesinformes", _name="selectevaluacionesinformes"), _id="fieldsetescogeevaluacion")
    otrosgrupos = FIELDSET("Escoge grupos para agrupar: ", SELECT(*[OPTION(grupo.grupo.grupo+" ("+grupo.curso_academico_grupo.id_tutor.apellidos+", "+
             grupo.curso_academico_grupo.id_tutor.nombre+")", _value=grupo.curso_academico_grupo.id) for grupo in grupos],
            _id="selectotrosgruposinformes", _name="selectotrosgruposinformes",_multiple="true",_size="10"), _id="fieldsetescogeotrosgrupos")
    form = FORM([grup, tipos, evaluas, otrosgrupos, INPUT(_value="Generar informe", _type="submit", _id="pideinforme")], _id="forminformesevaluaciones")
    """
    if form.accepts(request,session):        
        if form.vars.selecttiposinformes == '0':
            redirect(URL(c='reportspyfpdf',f='hojasevaluacion',args=(form.vars.selectevaluacionesinformes,form.vars.selectgruposinformes)))
        elif form.vars.selecttiposinformes == '1':
            redirect(URL(c='reportspyfpdf',f='informeevaluacion',args=(form.vars.selectevaluacionesinformes,form.vars.selectgruposinformes)))
        elif form.vars.selecttiposinformes == '2':
            redirect(URL(c='reportspyfpdf',f='informecurso',args=(form.vars.selectgruposinformes)))
        elif form.vars.selecttiposinformes == '3':
            redirect(URL(c='reportspyfpdf',f='informefichas',args=(form.vars.selectgruposinformes)))
    """            
    return dict(form=form)

@auth.requires_login()
@auth.requires_membership(role='Profesores')    
def evaluaciones_tutor():
    # comprobemos que somos tutores, sino nada
    if not session.profesor.esTutor:
        redirect(URL("default","index"))
    # primero rellenaremos los grupos activos en el curso actual y las evaluaciones existentes
    tipos = FIELDSET("Escoge tipo: ", SELECT([OPTION("Individualizado", _value=0), OPTION("Resumen Evaluación", _value=1), OPTION("Resumen Curso", _value=2),
                                            OPTION("Fichas-Registro", _value=3)],
            _id="selecttiposinformes",_name="selecttiposinformes"), _id="fieldsetescogetipo")
    oevaluaciones = obies.Evaluacion(db, session)
    evaluaciones = oevaluaciones.dame_evaluaciones()
    evaluas = FIELDSET("Escoge evaluación: ", SELECT(*[OPTION(evaluacion.evaluacion, _value=evaluacion.id) for evaluacion in evaluaciones], 
            _id="selectevaluacionesinformes", _name="selectevaluacionesinformes"), _id="fieldsetescogeevaluacion")
    form = FORM([tipos, evaluas, INPUT(_value="Generar informe", _type="submit", _id="pideinforme")], _id="forminformesevaluacionestutor")
    """
    if form.accepts(request,session):
        if form.vars.selecttiposinformes == '0':
            redirect(URL(c='reportspyfpdf',f='hojasevaluacion',args=(form.vars.selectevaluacionesinformes,session.profesor.tutor.id_curso_academico_grupo)))
        elif form.vars.selecttiposinformes == '1':
            redirect(URL(c='reportspyfpdf',f='informeevaluacion',args=(form.vars.selectevaluacionesinformes,session.profesor.tutor.id_curso_academico_grupo)))
        elif form.vars.selecttiposinformes == '2':
            redirect(URL(c='reportspyfpdf',f='informecurso',args=(session.profesor.tutor.id_curso_academico_grupo)))
        elif form.vars.selecttiposinformes == '3':
            redirect(URL(c='reportspyfpdf',f='informefichas',args=(session.profesor.tutor.id_curso_academico_grupo)))
    """
    return dict(form=form)