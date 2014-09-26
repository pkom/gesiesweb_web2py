'''
Created on 01/03/2012

@author: fmoras01
'''

class Comun(object):
    def __init__(self, db, sesion):
        self.db = db
        self.sesion = sesion    

class Curso(Comun):   
    def dame_cursos(self, conactual=True):
        if conactual:
            return self.db(self.db.curso_academico.id > 0).select(self.db.curso_academico.ALL, orderby=~self.db.curso_academico.curso)
        else:
            return self.db((self.db.curso_academico.id > 0) & (self.db.curso_academico.id != self.sesion.curso_academico_id)) \
                            .select(self.db.curso_academico.ALL, orderby=~self.db.curso_academico.curso)

    
class Departamento(Comun):   
    def dame_departamentos(self):
        return self.db().select(self.db.departamento.ALL,orderby=self.db.departamento.departamento)
    
    def dame_departamentos_curso(self, idcurso = None):
        if idcurso == None:
            idcurso = self.sesion.curso_academico_id
        return self.db((self.db.curso_academico_departamento.id_departamento == self.db.departamento.id) &
                       (self.db.curso_academico_departamento.id_curso_academico == idcurso)) \
                       .select(self.db.curso_academico_departamento.ALL,
                               self.db.departamento.ALL,
                               orderby=self.db.departamento.departamento)

    def dame_asignaturas_departamento(self, iddepartamento):
        return self.db(self.db.asignatura.id_departamento == iddepartamento) \
        .select(self.db.asignatura.ALL,orderby=self.db.asignatura.asignatura)
         
class Alumno(Comun):
    def dame_alumnos(self):
        return self.db().select(self.db.alumno.ALL,orderby=self.db.alumno.apellidos|self.alumno.nombre)

    def dame_alumnos_curso(self, idcurso = None):
        if idcurso == None:
            idcurso = self.sesion.curso_academico_id
        return self.db((self.db.grupo_alumno.id_curso_academico_grupo == self.db.curso_academico_grupo.id) &
                       (self.db.curso_academico_grupo.id_curso_academico == idcurso) &
                       (self.db.grupo_alumno.id_alumno == self.db.alumno.id)).select(self.db.grupo_alumno.ALL,
                               self.db.alumno.ALL,
                               orderby=self.db.alumno.apellidos|self.db.alumno.nombre)
                               
    def dame_alumnos_buscados(self, buscar, idcurso = None):
        if idcurso == None:
            idcurso = self.sesion.curso_academico_id  
        buscar = '%'+buscar.lower()+'%'           
        return self.db((self.db.grupo_alumno.id_curso_academico_grupo == self.db.curso_academico_grupo.id) &
                       (self.db.curso_academico_grupo.id_curso_academico == idcurso) &
                       (self.db.grupo_alumno.id_alumno == self.db.alumno.id) &
                       (self.db.alumno.apellidos.lower().like(buscar) | self.db.alumno.nombre.lower().like(buscar))).select(self.db.grupo_alumno.ALL,
                               self.db.alumno.ALL,
                               orderby=self.db.alumno.apellidos|self.db.alumno.nombre)
                               

    def dame_alumnos_grupo(self, idgrupo, idcurso = None):
        if idcurso == None:
            idcurso = self.sesion.curso_academico_id
        return self.db((self.db.curso_academico_grupo.id == idgrupo) &
                       (self.db.curso_academico_grupo.id_curso_academico == idcurso) &
                       (self.db.grupo_alumno.id_curso_academico_grupo == self.db.curso_academico_grupo.id) &
                       (self.db.grupo_alumno.id_alumno == self.db.alumno.id)).select(self.db.grupo_alumno.ALL,
                               self.db.alumno.ALL,
                               orderby=self.db.alumno.apellidos|self.db.alumno.nombre)
                                                             
class Profesor(Comun):        
    def dame_profesores(self):
        return self.db().select(self.db.profesor.ALL,orderby=self.db.profesor.apellidos|self.profesor.nombre)
        
    def dame_profesores_curso(self, idcurso = None):
        if idcurso == None:
            idcurso = self.sesion.curso_academico_id
        return self.db((self.db.departamento_profesor.id_curso_academico_departamento == self.db.curso_academico_departamento.id) &
                       (self.db.curso_academico_departamento.id_curso_academico == idcurso) &
                       (self.db.departamento_profesor.id_profesor == self.db.profesor.id)).select(self.db.departamento_profesor.ALL,
                               self.db.profesor.ALL,
                               orderby=self.db.profesor.apellidos|self.db.profesor.nombre)

    def dame_profesores_departamento(self, iddepartamento, idcurso = None):
        if idcurso == None:
            idcurso = self.sesion.curso_academico_id
        return self.db((self.db.curso_academico_departamento.id == iddepartamento) &
                       (self.db.curso_academico_departamento.id_curso_academico == idcurso) &
                       (self.db.curso_academico_departamento.id == self.db.departamento_profesor.id_curso_academico_departamento) &
                       (self.db.departamento_profesor.id_profesor == self.db.profesor.id)).select(self.db.departamento_profesor.ALL,
                               self.db.profesor.ALL,
                               orderby=self.db.profesor.apellidos|self.db.profesor.nombre)
                               
    def dame_profesores_grupo(self, idgrupo, idcurso = None):
        if idcurso == None:
            idcurso = self.sesion.curso_academico_id
        return self.db((self.db.curso_academico_grupo.id == idgrupo) &
                       (self.db.curso_academico_grupo.id_curso_academico == idcurso) &
                       (self.db.curso_academico_grupo.id == self.db.grupo_profesor.id_curso_academico_grupo) &
                       (self.db.grupo_profesor.id_profesor == self.db.profesor.id)).select(self.db.grupo_profesor.ALL,
                               self.db.profesor.ALL,
                               orderby=self.db.profesor.apellidos|self.db.profesor.nombre)  
                                                            
    def dame_profesor_grupos(self, idprofesor, idcurso = None):
        if idcurso == None:
            idcurso = self.sesion.curso_academico_id
        return self.db((self.db.curso_academico_grupo.id_curso_academico == idcurso) &
                       (self.db.curso_academico_grupo.id == self.db.grupo_profesor.id_curso_academico_grupo) &                      
                       (self.db.curso_academico_grupo.id_grupo == self.db.grupo.id) &
                       (self.db.grupo_profesor.id_profesor == self.db.profesor.id) &                      
                       (self.db.grupo_profesor.id_profesor == idprofesor)).select(self.db.grupo_profesor.ALL,
                               self.db.grupo.ALL, self.db.profesor.ALL,
                               orderby=self.db.grupo.grupo)  

    def dame_profesor_departamentos(self, idprofesor, idcurso = None):
        if idcurso == None:
            idcurso = self.sesion.curso_academico_id
        return self.db((self.db.curso_academico_departamento.id_curso_academico == idcurso) &
                       (self.db.curso_academico_departamento.id_departamento == self.db.departamento.id) &
                       (self.db.curso_academico_departamento.id == self.db.departamento_profesor.id_curso_academico_departamento) &                      
                       (self.db.departamento_profesor.id_profesor == self.db.profesor.id) &
                       (self.db.departamento_profesor.id_profesor == idprofesor)).select(self.db.departamento_profesor.ALL,
                               self.db.departamento.ALL, self.db.profesor.ALL,
                               orderby=self.db.departamento.departamento)  
           
class Grupo(Comun):        
    def dame_grupos(self):
        return self.db().select(self.db.grupo.ALL,orderby=self.db.grupo.grupo)
    
    def dame_grupos_curso(self, idcurso=None, contutor=False):
        if idcurso == None:
            idcurso = self.sesion.curso_academico_id
        if contutor:
            return self.db((self.db.curso_academico_grupo.id_curso_academico == idcurso) &
                       (self.db.curso_academico_grupo.id_tutor != None) &
                       (self.db.curso_academico_grupo.id_grupo == self.db.grupo.id)).select(self.db.curso_academico_grupo.ALL,
                               self.db.grupo.ALL,
                               orderby=self.db.grupo.grupo)
        else:
            return self.db((self.db.curso_academico_grupo.id_curso_academico == idcurso) &
                       (self.db.curso_academico_grupo.id_grupo == self.db.grupo.id)).select(self.db.curso_academico_grupo.ALL,
                               self.db.grupo.ALL,
                               orderby=self.db.grupo.grupo)

    def dame_grupo_alumno(self, idalumno, idcurso = None):
        if idcurso == None:
            idcurso = self.sesion.curso_academico_id
        return self.db((self.db.curso_academico_grupo.id_curso_academico == idcurso) &
                       (self.db.curso_academico_grupo.id_grupo == self.db.grupo.id) &
                       (self.db.grupo_alumno.id_curso_academico_grupo == self.db.curso_academico_grupo.id) &
                       (self.db.grupo_alumno.id_alumno == idalumno)).select(self.db.grupo_alumno.ALL,
                               self.db.grupo.ALL,
                               orderby=self.db.grupo.grupo)

class Aviso(Comun):        
    def dame_avisos_alumno(self, idgrupoalumno, idcurso = None):
        if idcurso == None:
            idcurso = self.sesion.curso_academico_id
        return self.db((self.db.amonestacion.id_grupo_alumno == idgrupoalumno) &
                       (self.db.amonestacion.id_grupo_alumno == self.db.grupo_alumno.id) &
                       (self.db.grupo_alumno.id_alumno == self.db.alumno.id) &
                       (self.db.grupo_alumno.id_curso_academico_grupo == self.db.curso_academico_grupo.id) &
                       (self.db.curso_academico_grupo.id_grupo == self.db.grupo.id) &
                       (self.db.curso_academico_grupo.id_curso_academico == idcurso) &
                       (self.db.amonestacion.id_departamento_profesor == self.db.departamento_profesor.id) &
                       (self.db.departamento_profesor.id_profesor == self.db.profesor.id))\
                       .select(self.db.amonestacion.ALL, self.db.grupo.ALL, self.db.alumno.ALL, self.db.profesor.ALL, 
                               orderby=~self.db.amonestacion.fecha | ~self.db.amonestacion.id)

    def dame_avisos_retrasos_alumno(self, idgrupoalumno, idcurso = None):
        if idcurso == None:
            idcurso = self.sesion.curso_academico_id
        return self.db((self.db.amonestacion_retraso.id_grupo_alumno == idgrupoalumno) &
                       (self.db.amonestacion_retraso.id_grupo_alumno == self.db.grupo_alumno.id) &
                       (self.db.grupo_alumno.id_alumno == self.db.alumno.id) &
                       (self.db.grupo_alumno.id_curso_academico_grupo == self.db.curso_academico_grupo.id) &
                       (self.db.curso_academico_grupo.id_grupo == self.db.grupo.id) &
                       (self.db.curso_academico_grupo.id_curso_academico == idcurso) &
                       (self.db.amonestacion_retraso.id_departamento_profesor == self.db.departamento_profesor.id) &
                       (self.db.departamento_profesor.id_profesor == self.db.profesor.id))\
                       .select(self.db.amonestacion_retraso.ALL, self.db.grupo.ALL, self.db.alumno.ALL, self.db.profesor.ALL, 
                               orderby=~self.db.amonestacion_retraso.fecha | ~self.db.amonestacion_retraso.id)

    def dame_avisos_profesor(self, iddepartamentoprofesor, idcurso = None):
        if idcurso == None:
            idcurso = self.sesion.curso_academico_id
        return self.db((self.db.amonestacion.id_departamento_profesor == iddepartamentoprofesor) &
                       (self.db.amonestacion.id_grupo_alumno == self.db.grupo_alumno.id) &
                       (self.db.grupo_alumno.id_alumno == self.db.alumno.id) &
                       (self.db.grupo_alumno.id_curso_academico_grupo == self.db.curso_academico_grupo.id) &
                       (self.db.curso_academico_grupo.id_grupo == self.db.grupo.id) &
                       (self.db.curso_academico_grupo.id_curso_academico == idcurso) &
                       (self.db.amonestacion.id_departamento_profesor == self.db.departamento_profesor.id) &
                       (self.db.departamento_profesor.id_profesor == self.db.profesor.id))\
                       .select(self.db.amonestacion.ALL, self.db.grupo.ALL, self.db.alumno.ALL, self.db.profesor.ALL, 
                               orderby=~self.db.amonestacion.fecha | ~self.db.amonestacion.id)

    def dame_seguimientos(self, idamonestacion):
        return self.db((self.db.seguimiento.id_amonestacion == idamonestacion) &
                       (self.db.seguimiento.id_responsable == self.db.departamento_profesor.id) &
                       (self.db.departamento_profesor.id_profesor == self.db.profesor.id))\
                       .select(self.db.seguimiento.ALL, self.db.profesor.ALL,
                               orderby=~self.db.seguimiento.fecha | ~self.db.seguimiento.id)

    def dame_retrasos(self, idamonestacionretraso):
        return self.db((self.db.amonestacion_retraso_retraso.id_amonestacion_retraso == idamonestacionretraso) &
                       (self.db.amonestacion_retraso_retraso.id_retraso == self.db.retraso.id) &
                       (self.db.retraso.id_departamento_profesor == self.db.departamento_profesor.id) &
                       (self.db.departamento_profesor.id_profesor == self.db.profesor.id))\
                       .select(self.db.amonestacion_retraso_retraso.ALL,self.db.retraso.ALL, self.db.profesor.ALL,
                               orderby=~self.db.retraso.fecha | ~self.db.retraso.id)

class Absentismo(Comun):        
    def dame_absentismos_alumno(self, idgrupoalumno, idcurso = None):
        if idcurso == None:
            idcurso = self.sesion.curso_academico_id
        return self.db((self.db.amonestacion_absentismo.id_grupo_alumno == idgrupoalumno) &
                       (self.db.amonestacion_absentismo.id_grupo_alumno == self.db.grupo_alumno.id) &
                       (self.db.grupo_alumno.id_alumno == self.db.alumno.id) &
                       (self.db.grupo_alumno.id_curso_academico_grupo == self.db.curso_academico_grupo.id) &
                       (self.db.curso_academico_grupo.id_grupo == self.db.grupo.id) &
                       (self.db.curso_academico_grupo.id_curso_academico == idcurso) &
                       (self.db.amonestacion_absentismo.id_departamento_profesor == self.db.departamento_profesor.id) &
                       (self.db.departamento_profesor.id_profesor == self.db.profesor.id))\
                       .select(self.db.amonestacion_absentismo.ALL, self.db.grupo.ALL, self.db.alumno.ALL, self.db.profesor.ALL, 
                               orderby=~self.db.amonestacion_absentismo.fecha | ~self.db.amonestacion_absentismo.id)

    def dame_absentismos_profesor(self, iddepartamentoprofesor, idcurso = None):
        if idcurso == None:
            idcurso = self.sesion.curso_academico_id
        return self.db((self.db.amonestacion_absentismo.id_departamento_profesor == iddepartamentoprofesor) &
                       (self.db.amonestacion_absentismo.id_grupo_alumno == self.db.grupo_alumno.id) &
                       (self.db.grupo_alumno.id_alumno == self.db.alumno.id) &
                       (self.db.grupo_alumno.id_curso_academico_grupo == self.db.curso_academico_grupo.id) &
                       (self.db.curso_academico_grupo.id_grupo == self.db.grupo.id) &
                       (self.db.curso_academico_grupo.id_curso_academico == idcurso) &
                       (self.db.amonestacion_absentismo.id_departamento_profesor == self.db.departamento_profesor.id) &
                       (self.db.departamento_profesor.id_profesor == self.db.profesor.id))\
                       .select(self.db.amonestacion_absentismo.ALL, self.db.grupo.ALL, self.db.alumno.ALL, self.db.profesor.ALL, 
                               orderby=~self.db.amonestacion_absentismo.fecha | ~self.db.amonestacion_absentismo.id)

class Asignatura(Comun):   
    def dame_asignaturas(self):
        return self.db(self.db.asignatura.id > 0).select(self.db.asignatura.ALL, orderby=self.db.asignatura.abreviatura)


class Evaluacion(Comun):        
    def dame_evaluacion_alumnos_tutoria(self, idevaluacion, idgrupoprofesortutoria):
        if idevaluacion <> 0:
            # una evaluacion en particular
            return self.db((self.db.curso_academico_grupo.id == idgrupoprofesortutoria) &
                    (self.db.curso_academico_grupo.id_grupo == self.db.grupo.id) &
                    (self.db.grupo_profesor.id_curso_academico_grupo == self.db.curso_academico_grupo.id) &
                    (self.db.grupo_profesor_asignatura.id_grupo_profesor == self.db.grupo_profesor.id) &
                    (self.db.grupo_profesor_asignatura.id_asignatura == self.db.asignatura.id) &
                    (self.db.grupo_profesor_asignatura.id_grupo_profesor == self.db.grupo_profesor.id) &
                    (self.db.grupo_profesor.id_profesor == self.db.profesor.id) &
                    (self.db.grupo_profesor_asignatura_alumno.id_grupo_profesor_asignatura == self.db.grupo_profesor_asignatura.id) &
                    (self.db.grupo_profesor_asignatura_alumno.id_grupo_alumno == self.db.grupo_alumno.id) &
                    (self.db.grupo_alumno.id_alumno == self.db.alumno.id) &
                    (self.db.evaluacion_alumno.id_grupo_profesor_asignatura_alumno == self.db.grupo_profesor_asignatura_alumno.id) &
                    (self.db.evaluacion_alumno.id_curso_academico_evaluacion == idevaluacion) &
                    (self.db.evaluacion_alumno.id_curso_academico_evaluacion == self.db.curso_academico_evaluacion.id)).select(self.db.evaluacion_alumno.ALL,
                                self.db.alumno.ALL,self.db.asignatura.ALL,self.db.profesor.ALL,self.db.grupo.ALL,self.db.curso_academico_evaluacion.ALL,
                                orderby = self.db.alumno.apellidos | self.db.alumno.nombre | self.db.asignatura.asignatura)
        else:
            # las evaluaciones del curso
            return self.db((self.db.curso_academico_grupo.id == idgrupoprofesortutoria) &
                    (self.db.curso_academico_grupo.id_grupo == self.db.grupo.id) &
                    (self.db.grupo_profesor.id_curso_academico_grupo == self.db.curso_academico_grupo.id) &
                    (self.db.grupo_profesor_asignatura.id_grupo_profesor == self.db.grupo_profesor.id) &
                    (self.db.grupo_profesor_asignatura.id_asignatura == self.db.asignatura.id) &
                    (self.db.grupo_profesor_asignatura.id_grupo_profesor == self.db.grupo_profesor.id) &
                    (self.db.grupo_profesor.id_profesor == self.db.profesor.id) &
                    (self.db.grupo_profesor_asignatura_alumno.id_grupo_profesor_asignatura == self.db.grupo_profesor_asignatura.id) &
                    (self.db.grupo_profesor_asignatura_alumno.id_grupo_alumno == self.db.grupo_alumno.id) &
                    (self.db.grupo_alumno.id_alumno == self.db.alumno.id) &
                    (self.db.evaluacion_alumno.id_grupo_profesor_asignatura_alumno == self.db.grupo_profesor_asignatura_alumno.id) &
                    (self.db.evaluacion_alumno.id_curso_academico_evaluacion == self.db.curso_academico_evaluacion.id) &
                    (self.db.curso_academico_evaluacion.id_curso_academico == self.sesion.curso_academico_id) &
                    (self.db.evaluacion_alumno.id_curso_academico_evaluacion == self.db.curso_academico_evaluacion.id)).select(self.db.evaluacion_alumno.ALL,
                                self.db.alumno.ALL,self.db.asignatura.ALL,self.db.profesor.ALL,self.db.grupo.ALL,self.db.curso_academico_evaluacion.ALL,
                                orderby = self.db.alumno.apellidos | self.db.alumno.nombre | self.db.asignatura.asignatura)
                    
    def dame_evaluaciones(self):
        return self.db((self.db.curso_academico_evaluacion.id_curso_academico == self.sesion.curso_academico_id)).select(
                        self.db.curso_academico_evaluacion.ALL, orderby = self.db.curso_academico_evaluacion.id)
