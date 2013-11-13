#!/usr/bin/env python
# coding: utf8
import datetime
import utils
from gluon import *

def justifica_retraso(db,idretraso):
    retraso_amonestado = db(db.amonestacion_retraso_retraso.id_retraso == idretraso).select(db.amonestacion_retraso_retraso.ALL).first()
    if retraso_amonestado:
        #si existe una amonestacion para ese retraso que se ha justificado
        idamonestacionretraso = retraso_amonestado.id_amonestacion_retraso
        #obtenemos el id de la amonestación generada
        db(db.amonestacion_retraso_retraso.id_amonestacion_retraso == idamonestacionretraso).delete()
        #borramos las asignaciones de los retrasos para la amonestación que estamos borrando
        db(db.amonestacion_retraso.id == idamonestacionretraso).delete()
        #borramos la propia amonestación
    return

def procesa_retrasos(db,alumno,profesor,retrasos_para_amonestacion,curso_academico):
    #primero obtengamos la fecha del sistema y la fecha de inicio y fin del trimestre actual
    fecha_hoy = datetime.date.today()
    if ((fecha_hoy >= db.curso_academico[curso_academico].inicio_trimestre_1) and (fecha_hoy <= db.curso_academico[curso_academico].fin_trimestre_1)):
        fecha_inicio_trimestre_actual = db.curso_academico[curso_academico].inicio_trimestre_1
        fecha_fin_trimestre_actual = db.curso_academico[curso_academico].fin_trimestre_1
    elif ((fecha_hoy >= db.curso_academico[curso_academico].inicio_trimestre_2) and (fecha_hoy <= db.curso_academico[curso_academico].fin_trimestre_2)):
        fecha_inicio_trimestre_actual = db.curso_academico[curso_academico].inicio_trimestre_2
        fecha_fin_trimestre_actual = db.curso_academico[curso_academico].fin_trimestre_2
    else:
        fecha_inicio_trimestre_actual = db.curso_academico[curso_academico].inicio_trimestre_3
        fecha_fin_trimestre_actual = db.curso_academico[curso_academico].fin_trimestre_3
        
    while True:
        retrasos_pendientes = []
        for retraso in db((db.retraso.procesar == True) &
                          (db.retraso.id_grupo_alumno == alumno) &
                          (db.retraso.id_grupo_alumno == db.grupo_alumno.id) &
                          (db.grupo_alumno.id_curso_academico_grupo == db.curso_academico_grupo.id) &
                          (db.curso_academico_grupo.id_curso_academico == curso_academico)).select(db.retraso.ALL,orderby=~db.retraso.fecha):
            if not db(db.amonestacion_retraso_retraso.id_retraso == retraso.id).select():
                #aquí debería comprobar que el retraso esté en el trimestre actual para ponerlo pendiente
                #para ello veamos la fecha del sistema y comprobaremos 
                if ((retraso.fecha >= fecha_inicio_trimestre_actual) and (retraso.fecha <= fecha_fin_trimestre_actual)):
                    retrasos_pendientes.append(retraso.id)
        if (len(retrasos_pendientes) < retrasos_para_amonestacion):
            return False        
        else:
            #crear amonestacion por retraso
            idamonestacion = db.amonestacion_retraso.insert(id_grupo_alumno=alumno,id_departamento_profesor=profesor,
                fecha=datetime.date.today())
            #insertar retrasos amonestados
            for i in range(retrasos_para_amonestacion):
                db.amonestacion_retraso_retraso.insert(id_amonestacion_retraso=idamonestacion,id_retraso=retrasos_pendientes[i])      
    return True
