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
            _id="selectgruposinformes"), _id="fieldsetescogegrupo")
    tipos = FIELDSET("Escoge tipo: ", SELECT([OPTION("Individualizado", _value=0), OPTION("Resumen Evaluación", _value=1), OPTION("Resumen Curso", _value=2)],
            _id="selecttiposinformes"), _id="fieldsetescogetipo")
    oevaluaciones = obies.Evaluacion(db, session)
    evaluaciones = oevaluaciones.dame_evaluaciones()
    evaluas = FIELDSET("Escoge evaluación: ", SELECT(*[OPTION(evaluacion.evaluacion, _value=evaluacion.id) for evaluacion in evaluaciones], 
            _id="selectevaluacionesinformes"), _id="fieldsetescogeevaluacion")
    form = FORM([grup, tipos, evaluas, INPUT(_value="Generar informe", _type="submit", _id="pideinforme")], _id="forminformesevaluaciones")
    return dict(form=form)

@auth.requires_login()
@auth.requires_membership(role='Profesores')    
def evaluaciones_tutor():
    # comprobemos que somos tutores, sino nada
    if not session.profesor.esTutor:
        redirect(URL("default","index"))
    # primero rellenaremos los grupos activos en el curso actual y las evaluaciones existentes
    tipos = FIELDSET("Escoge tipo: ", SELECT([OPTION("Individualizado", _value=0), OPTION("Resumen Evaluación", _value=1), OPTION("Resumen Curso", _value=2)],
            _id="selecttiposinformes"), _id="fieldsetescogetipo")
    oevaluaciones = obies.Evaluacion(db, session)
    evaluaciones = oevaluaciones.dame_evaluaciones()
    evaluas = FIELDSET("Escoge evaluación: ", SELECT(*[OPTION(evaluacion.evaluacion, _value=evaluacion.id) for evaluacion in evaluaciones], 
            _id="selectevaluacionesinformes"), _id="fieldsetescogeevaluacion")
    form = FORM([tipos, evaluas, INPUT(_value="Generar informe", _type="submit", _id="pideinforme")], _id="forminformesevaluaciones")
    return dict(form=form)