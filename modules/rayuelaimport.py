#!/usr/bin/env python
# coding: utf8
from gluon.storage import Storage, List
import os, zipfile, shutil, Image
from xml.sax import make_parser
from xml.sax.handler import ContentHandler
import cStringIO


class Rayuela(object):

    def __init__(self,db,sesion,archivo):
        self.db = db
        self.sesion = sesion        
        self.archivo = archivo
        self.esAlumnos = False
        
    def gestiona_archivo(self):
        """Función principal que a partir del archivo hace todo en la base de datos"""        
        self.esAlumnos=(self.archivo[-4:].lower()==".zip")       
        parser = make_parser()
        if self.esAlumnos:
            intento=self.unzip_alumnos(self.archivo)
            if intento!="": 
                print "PROBLEMAS",intento
            else:
                curHandler = AlumnoHandler(self.db,self.sesion)
                parser.setContentHandler(curHandler)
                parser.parse(open("/tmp/rayuela-ldap/Alumnos.xml"))        
                shutil.rmtree("/tmp/rayuela-ldap", True)                
        elif self.archivo.lower()=="ExportacionGruposCentro.xml":
            curHandler = CursosGruposHandler(self.db,self.sesion)           
            parser.setContentHandler(curHandler)
            parser.parse(open(self.archivo))        
        else:
            curHandler = ProfesorHandler(self.db,self.sesion)           
            parser.setContentHandler(curHandler)
            parser.parse(open(self.archivo))
        return True

    def unzip_alumnos(self,archivo_zip):
        """ Descomprime el archivo de alumnos en el directorio
        /tmp/rayuela-ldap"""
        try:
            if os.path.exists("/tmp/rayuela-ldap"):
                shutil.rmtree("/tmp/rayuela-ldap")
            os.mkdir("/tmp/rayuela-ldap", 0777)
            try:
                zfobj = zipfile.ZipFile(archivo_zip)
            except zipfile.BadZipfile:
                original = open(archivo_zip, 'rb')
                try:
                    data = original.read()
                finally:
                    original.close()
                position = data.rindex(zipfile.stringEndArchive, -(22 + 100), -20)
                coredata = cStringIO.StringIO(data[: 22 + position])
                zfobj = zipfile.ZipFile(coredata)
                
            for name in zfobj.namelist():
                if name.endswith('/'):
                        os.mkdir(os.path.join("/tmp/rayuela-ldap", name))
                else:
                        outfile = open(os.path.join("/tmp/rayuela-ldap", name), 'wb')
                        outfile.write(zfobj.read(name))
                        outfile.close()
            
        except Exception,e:
            raise
            return e
            
        if not os.path.exists("/tmp/rayuela-ldap/Alumnos.xml"):
            return "No es un archivo de importación de alumnos"
            
        return "" #todo ha ido bien    
    
class ProfesorHandler(ContentHandler):
    def __init__(self,db,sesion):
        self.db = db
        self.sesion = sesion
        self.profesores_procesados = 0
        self.datos = Storage()
        self.datos.centro = Storage()
        self.datos.centro.codigo = ''
        self.datos.centro.denominacion = ''
        self.datos.profesores = List()
        self.datos_profesor = Storage()
        self.isprofesorado_centro = 0
        self.iscentro = 0
        self.iscodigo = 0
        self.codigo = ""
        self.isdenominacion = 0
        self.denominacion = ""
        self.isprofesor = 0
        self.isdni = 0
        self.dni = ""
        self.isnombre = 0
        self.nombre = ""
        self.isprimer_apellido = 0
        self.primer_apellido = ""
        self.issegundo_apellido = 0
        self.segundo_apellido = ""
        self.isdatos_usuario_rayuela = 0
        self.ises_usuario = 0
        self.es_usuario = ""
        self.islogin = 0
        self.login = ""
        self.isid_usuario = 0
        self.id_usuario = ""
        self.isdepartamento = 0
        self.departamento = ""
        self.isgrupos = 0
        self.grupos = []
        self.isgrupo = 0
        self.grupo = ""
    
    def startElement(self, name, attrs):
        if name == 'codigo':
            self.iscodigo = 1
            self.codigo = ""
        if name == 'denominacion':
            self.isdenominacion = 1
            self.denominacion = ""
        if name == 'profesor':
            self.profesores_procesados = self.profesores_procesados + 1
            self.datos_profesor = Storage()
        if name == 'dni':
            self.isdni = 1
            self.dni = ""              
        if name == 'nombre':
            self.isnombre = 1
            self.nombre = ""
        if name == 'primer-apellido':
            self.isprimer_apellido = 1
            self.primer_apellido = ""
        if name == 'segundo-apellido':
            self.issegundo_apellido = 1
            self.segundo_apellido = ""
        if name == 'es-usuario':
            self.ises_usuario = 1
            self.es_usuario = ""
        if name == 'login':
            self.islogin = 1
            self.login = ""
        if name == 'id-usuario':
            self.isid_usuario = 1
            self.id_usuario = ""
        if name == 'departamento':
            self.isdepartamento = 1
            self.departamento = ""
        if name == 'grupos':
            self.isgrupos = 1
            self.grupos = []
        if name == 'grupo':
            self.isgrupo = 1
            self.grupo = ""           
        return

    def endElement(self, name):
        if name == 'centro':
            self.iscentro = 0                          
        if name == 'codigo':
            self.iscodigo = 0
            self.datos.centro.codigo = self.codigo           
        if name == 'denominacion':
            self.isdenominacion = 0
            self.datos.centro.denominacion = self.denominacion           
        if name == 'profesor':
            self.isprofesor = 0
            # acabamos de procesar un profesor, debemos añadir en la lista de profes del diccionario
            self.datos.profesores.append(self.datos_profesor)     
        if name == 'grupos':
            self.isgrupos = 0
            # acabamos de procesar los grupos del profesor
            if not self.datos_profesor.grupos:
                self.datos_profesor.grupos = List()
            self.datos_profesor.grupos = self.grupos
        if name == 'grupo':
            # acabamos de procesar uno de los posibles grupos del profesor
            self.isgrupo = 0
            self.grupos.append(self.grupo)
        if name == 'dni':
            self.isdni = 0
            self.datos_profesor.dni = self.dni
        if name == 'nombre':
            self.isnombre = 0
            self.datos_profesor.nombre = self.nombre
        if name == 'primer-apellido':
            self.isprimer_apellido = 0
            self.datos_profesor.primer_apellido = self.primer_apellido
        if name == 'segundo-apellido':
            self.issegundo_apellido = 0
            self.datos_profesor.segundo_apellido = self.segundo_apellido
        if name == 'datos-usuario-rayuela':
            self.isdatos_usuario_rayuela = 0           
        if name == 'es-usuario':
            self.ises_usuario = 0
            self.datos_profesor.es_usuario = self.es_usuario
        if name == 'login':
            self.islogin = 0
            self.datos_profesor.login = self.login
        if name == 'id-usuario':
            self.isid_usuario = 0
            self.datos_profesor.id_usuario = self.id_usuario
        if name == 'departamento':
            self.isdepartamento = 0
            self.datos_profesor.departamento = self.departamento                    
        if name == 'profesorado-centro':
            self.isprofesorado_centro = 0
            # aquí deberemos procesar el diccionario self.datos que contiene el parseado del XML
            if self.datos.centro.codigo:
                # compruebo que existe algún valor de configuración
                # si existe ignoramos los datos de rayuela
                centro = self.db(self.db.config).select().first()
                if centro == None:
                    self.db.config.insert(codigo_centro = self.datos.centro.codigo, nombre_centro = self.datos.centro.denominacion)
            # procesaremos todos los profesor
            for profesor in self.datos.profesores:                
                if profesor.dni:
                    # miraremos si existe en la tabla de profesores primero, y si no lo insertaremos
                    filaprofesor = self.db(self.db.profesor.dni == profesor.dni).select().first()
                    if filaprofesor == None:
                        idprofesor = self.db.profesor.insert(dni = profesor.dni, 
                                                    nombre = profesor.nombre, 
                                                    apellidos = profesor.primer_apellido+' '+profesor.segundo_apellido,
                                                    usuario_rayuela = profesor.login)
                    else:
                        filaprofesor.update_record(nombre = profesor.nombre, 
                                            apellidos = profesor.primer_apellido+' '+profesor.segundo_apellido,
                                            usuario_rayuela = profesor.login)
                        idprofesor = filaprofesor.id                    
                                        
                if profesor.departamento: 
                    # miraremos si existe en la tabla de departamentos, y si no lo insertaremos
                    filadepartamento = self.db(self.db.departamento.departamento == profesor.departamento.strip()).select().first()
                    if filadepartamento == None:
                        iddepartamento = self.db.departamento.insert(departamento = profesor.departamento.strip())
                    else:    
                        iddepartamento = filadepartamento.id    
                    # miremos si existe ese departamento en el curso academico y si no se inserta
                    filacursoacademicodepartamento = self.db((self.db.curso_academico_departamento.id_curso_academico == self.sesion.curso_academico_id) &
                                               (self.db.curso_academico_departamento.id_departamento == iddepartamento)).select().first()
                    if filacursoacademicodepartamento == None:
                        idcursoacademicodepartamento = self.db.curso_academico_departamento.insert(id_curso_academico=self.sesion.curso_academico_id,
                                            id_departamento = iddepartamento)
                    else:
                        idcursoacademicodepartamento = filacursoacademicodepartamento.id                        

                    filadepartamentoprofesor = self.db((self.db.departamento_profesor.id_curso_academico_departamento == idcursoacademicodepartamento) &
                                               (self.db.departamento_profesor.id_profesor == idprofesor)).select().first()

                    if filadepartamentoprofesor == None:
                        #comprobemos antes si tiene alguna asignación anterior a otro departamento en el curso actual
                        filasdepartamentoprofesor = self.db(self.db.departamento_profesor.id_profesor == idprofesor).select()
                        #veamos si corresponden al curso academico actual, y si es así reemplazamos su departamento
                        #para poder reutilizar la fila de la tabla
                        dpid = None
                        for fila in filasdepartamentoprofesor:
                            if fila.id_curso_academico_departamento.id_curso_academico == self.sesion.curso_academico_id:
                                #estamos en una fila de departamento del curso actual para ese profesor, debemos actualizarla
                                dpid = fila.id
                                break
                        if dpid == None:
                            #debemos insertar una nueva asignación del profesor al departamento
                            self.db.departamento_profesor.insert(id_curso_academico_departamento = idcursoacademicodepartamento,
                                                                                          id_profesor = idprofesor)                            
                        else:
                            #debemos modificar la existente con la nueva
                            self.db.departamento_profesor[dpid] = dict(id_curso_academico_departamento = idcursoacademicodepartamento)
                else:
                    #este profesor no tiene asignado departamento, hay que asignarlo al departamento Sin_Departamento
                    #comprobaremos si hemos creado el departamento Sin_Departamento, si no es así lo creamos
                    #y asignaremos el profesor a este departamento
                    #esto lo hacemos para importar "todos" los profesores de rayuela, incluso aquellos que no hayan
                    #sido aun asignados a departamentos en rayuela...
                    filadepartamentosindepartamento = self.db(self.db.departamento.departamento == "Sin_Departamento").select().first()
                    if filadepartamentosindepartamento == None:
                        iddepartamentosindepartamento = self.db.departamento.insert(departamento = "Sin_Departamento")
                    else:    
                        iddepartamentosindepartamento = filadepartamentosindepartamento.id    
                    # miremos si existe ese el dpto Sin_Departamento en el curso academico y si no se inserta
                    filacursoacademicodepartamentosindepartamento = self.db((self.db.curso_academico_departamento.id_curso_academico == self.sesion.curso_academico_id) &
                                               (self.db.curso_academico_departamento.id_departamento == iddepartamentosindepartamento)).select().first()
                    if filacursoacademicodepartamentosindepartamento == None:
                        idcursoacademicodepartamentosindepartamento = self.db.curso_academico_departamento.insert(id_curso_academico=self.sesion.curso_academico_id,
                                            id_departamento = iddepartamentosindepartamento)
                    else:
                        idcursoacademicodepartamentosindepartamento = filacursoacademicodepartamentosindepartamento.id                        
                    #asignemos el profesor a Sin_Departamento
                    self.db.departamento_profesor.insert(id_curso_academico_departamento = idcursoacademicodepartamentosindepartamento,
                                                                                          id_profesor = idprofesor)                            
                        
                if profesor.grupos:
                    for grupo in profesor.grupos:
                        # miraremos si existen en la tabla de grupos, y si no lo insertaremos                
                        filagrupo = self.db(self.db.grupo.grupo == grupo.strip()).select().first()
                        if filagrupo == None:
                            idgrupo = self.db.grupo.insert(grupo = grupo.strip())
                        else:
                            idgrupo = filagrupo.id    
                        #miremos que exista el grupo en el curso academico                            
                        filacursoacademicogrupo = self.db((self.db.curso_academico_grupo.id_curso_academico == self.sesion.curso_academico_id) &
                                               (self.db.curso_academico_grupo.id_grupo == idgrupo)).select().first()
                        if filacursoacademicogrupo == None:                       
                            idcursoacademicogrupo = self.db.curso_academico_grupo.insert(id_curso_academico=self.sesion.curso_academico_id,
                                            id_grupo = idgrupo)
                        else:
                            idcursoacademicogrupo = filacursoacademicogrupo.id
                        filagrupoprofesor = self.db((self.db.grupo_profesor.id_curso_academico_grupo == idcursoacademicogrupo) &
                                                    (self.db.grupo_profesor.id_profesor == idprofesor)).select().first()
                        if filagrupoprofesor == None:                                                    
                            self.db.grupo_profesor.insert(id_curso_academico_grupo = idcursoacademicogrupo,
                                                                       id_profesor = idprofesor)
        return
        
    def characters(self, ch):
        if self.iscodigo == 1:
            self.codigo += ch
        if self.isdenominacion == 1:
            self.denominacion += ch                       
        if self.isdni == 1:
            self.dni += ch                   
        if self.isnombre == 1:
            self.nombre += ch                       
        if self.isprimer_apellido == 1:
            self.primer_apellido += ch
        if self.issegundo_apellido == 1:
            self.segundo_apellido += ch
        if self.ises_usuario == 1:
            self.es_usuario += ch
        if self.islogin == 1:
            self.login += ch
        if self.isid_usuario == 1:
            self.id_usuario += ch
        if self.isdepartamento == 1:
            self.departamento += ch
        if self.isgrupo == 1:
            self.grupo += ch
            
class AlumnoHandler(ContentHandler):
    def __init__(self,db,sesion):
        self.db = db
        self.sesion = sesion
        self.alumnos_procesados = 0       
        self.datos = Storage()
        self.datos.centro = Storage()
        self.datos.centro.codigo = ''
        self.datos.centro.denominacion = ''
        self.datos.alumnos = List()
        self.datos_alumno = Storage()        
        self.isalumnado_centro = 0
        self.iscentro = 0
        self.iscodigo = 0
        self.isdenominacion = 0       
        self.codigo = ""
        self.denominacion = ""
        self.isalumno = 0
        self.isnie = 0
        self.nie = ""
        self.isnombre = 0
        self.nombre = ""
        self.isprimer_apellido = 0
        self.primer_apellido = ""
        self.issegundo_apellido = 0
        self.segundo_apellido = ""
        self.isfecha_nacimiento = 0
        self.fecha_nacimiento = ""
        self.isdatos_usuario_rayuela = 0
        self.ises_usuario = 0
        self.es_usuario = ""
        self.islogin = 0
        self.login = ""
        self.isid_usuario = 0
        self.id_usuario = ""
        self.isgrupo = 0
        self.grupo = ""
        self.isfoto = 0
        self.iscon_foto = 0
        self.con_foto = ""
        self.isformato = 0
        self.formato = ""
        self.isnombre_fichero = 0
        self.nombre_fichero = ""
    
    def startElement(self, name, attrs):
        if name == 'codigo':
            self.iscodigo = 1
            self.codigo = ""
        if name == 'denominacion':
            self.isdenominacion = 1
            self.denominacion = ""
        if name == 'alumno':
            self.alumnos_procesados = self.alumnos_procesados + 1
            self.datos_alumno = Storage()
        if name == 'nie':
            self.isnie = 1
            self.nie = ""              
        if name == 'nombre':
            self.isnombre = 1
            self.nombre = ""
        if name == 'primer-apellido':
            self.isprimer_apellido = 1
            self.primer_apellido = ""
        if name == 'segundo-apellido':
            self.issegundo_apellido = 1
            self.segundo_apellido = ""
        if name == 'fecha-nacimiento':
            self.isfecha_nacimiento = 1
            self.fecha_nacimiento = ""            
        if name == 'es-usuario':
            self.ises_usuario = 1
            self.es_usuario = ""
        if name == 'login':
            self.islogin = 1
            self.login = ""
        if name == 'id-usuario':
            self.isid_usuario = 1
            self.id_usuario = ""
        if name == 'grupo':
            self.isgrupo = 1
            self.grupo = ""
        if name == 'con-foto':
            self.iscon_foto = 1
            self.con_foto = ""
        if name == 'formato':
            self.isformato = 1
            self.formato = ""           
        if name == 'nombre-fichero':
            self.isnombre_fichero = 1
            self.nombre_fichero = ""           

        return

    def endElement(self, name):
        if name == 'centro':
            self.iscentro = 0                          
        if name == 'codigo':
            self.iscodigo = 0
            self.datos.centro.codigo = self.codigo           
        if name == 'denominacion':
            self.isdenominacion = 0
            self.datos.centro.denominacion = self.denominacion           
        if name == 'alumno':
            self.isalumno = 0
            # acabamos de procesar un alumno, debemos añadir en la lista de alumnos del diccionario
            self.datos.alumnos.append(self.datos_alumno)     
        if name == 'nie':
            self.isnie = 0
            self.datos_alumno.nie = self.nie
        if name == 'nombre':
            self.isnombre = 0
            self.datos_alumno.nombre = self.nombre
        if name == 'primer-apellido':
            self.isprimer_apellido = 0
            self.datos_alumno.primer_apellido = self.primer_apellido
        if name == 'segundo-apellido':
            self.issegundo_apellido = 0
            self.datos_alumno.segundo_apellido = self.segundo_apellido
        if name == 'fecha-nacimiento':
            self.isfecha_nacimiento = 0
            self.datos_alumno.fecha_nacimiento = self.fecha_nacimiento[6:]+'/'+self.fecha_nacimiento[3:5]+'/'+self.fecha_nacimiento[:2]
        if name == 'es-usuario':
            self.ises_usuario = 0
            self.datos_alumno.es_usuario = self.es_usuario
        if name == 'login':
            self.islogin = 0
            self.datos_alumno.login = self.login
        if name == 'id-usuario':
            self.isid_usuario = 0
            self.datos_alumno.id_usuario = self.id_usuario
        if name == 'grupo':
            self.isgrupo = 0
            self.datos_alumno.grupo = self.grupo
        if name == 'con-foto':
            self.iscon_foto = 0
            self.datos_alumno.con_foto = self.con_foto
        if name == 'formato':
            self.isformato = 0
            self.datos_alumno.formato = self.formato
        if name == 'nombre-fichero':
            self.isnombre_fichero = 0
            self.datos_alumno.nombre_fichero = self.nombre_fichero
        if name == 'alumnado-centro':
            self.isalumnado_centro = 0
            # aquí deberemos procesar el diccionario self.datos que contiene el parseado del XML
            if self.datos.centro.codigo:
                # compruebo que existe algún valor de configuración
                # si existe ignoramos los datos de rayuela
                centro = self.db(self.db.config).select().first()
                if centro == None:
                    self.db.config.insert(codigo_centro = self.datos.centro.codigo, nombre_centro = self.datos.centro.denominacion)
            # procesaremos todos los alumnos
            for alumno in self.datos.alumnos:                
                if alumno.nie:
                    # vemos si tiene archivo con la foto
                    if alumno.nombre_fichero:
                        filename = '/tmp/rayuela-ldap/'+alumno.nombre_fichero
                        foto = Image.open(filename)
                        ancho, alto = (80, 100)
                        tamanio = (ancho, alto)
                        foto.thumbnail(tamanio, Image.ANTIALIAS)
                        foto.save(filename)                        
                        stream = open(filename, 'rb')                
                    
                    # miraremos si existe en la tabla de alumnos primero, y si no lo insertaremos
                    filaalumno = self.db(self.db.alumno.nie == alumno.nie).select().first()
                    if filaalumno == None:
                        idalumno = self.db.alumno.insert(nie = alumno.nie, 
                                                    nombre = alumno.nombre, 
                                                    apellidos = alumno.primer_apellido+' '+alumno.segundo_apellido,
                                                    fecha_nacimiento = alumno.fecha_nacimiento,
                                                    usuario_rayuela = alumno.login,
#                                                    foto = self.db.alumno.foto.store(stream,filename))
                                                    foto = stream)
                    else:
                        filaalumno.update_record(nombre = alumno.nombre, 
                                            apellidos = alumno.primer_apellido+' '+alumno.segundo_apellido,
                                            fecha_nacimiento = alumno.fecha_nacimiento,
                                            usuario_rayuela = alumno.login,
#                                            foto = self.db.alumno.foto.store(stream,filename))                                            
                                            foto = stream)                                            
                        idalumno = filaalumno.id                   
                        
                if alumno.grupo:                 
                    # miraremos si existen en la tabla de grupos, y si no lo insertaremos                
                    filagrupo = self.db(self.db.grupo.grupo == alumno.grupo.strip()).select().first()
                    if filagrupo == None:
                        idgrupo = self.db.grupo.insert(grupo = alumno.grupo.strip())
                    else:
                        idgrupo = filagrupo.id    
                    #miremos que exista el grupo en el curso academico                            
                    filacursoacademicogrupo = self.db((self.db.curso_academico_grupo.id_curso_academico == self.sesion.curso_academico_id) &
                                                      (self.db.curso_academico_grupo.id_grupo == idgrupo)).select().first()
                    if filacursoacademicogrupo == None:                       
                        idcursoacademicogrupo = self.db.curso_academico_grupo.insert(id_curso_academico=self.sesion.curso_academico_id,
                                                                                     id_grupo = idgrupo)
                    else:
                        idcursoacademicogrupo = filacursoacademicogrupo.id                

                    # me queda decir que en el curso académico actual el alumno pertenece al grupo, tabla grupo_alumno        
                    filagrupoalumno = self.db((self.db.grupo_alumno.id_curso_academico_grupo == idcursoacademicogrupo) &
                                               (self.db.grupo_alumno.id_alumno == idalumno)).select().first()

                    if filagrupoalumno == None:
                        #comprobemos antes si tiene alguna asignación anterior a otro grupo en el curso actual
                        filasgrupoalumno = self.db(self.db.grupo_alumno.id_alumno == idalumno).select()
                        #veamos si corresponden al curso academico actual, y si es así reemplazamos su grupo
                        #para poder reutilizar la fila de la tabla
                        gaid = None
                        for fila in filasgrupoalumno:
                            if fila.id_curso_academico_grupo.id_curso_academico == self.sesion.curso_academico_id:
                                #estamos en una fila de departamento del curso actual para ese profesor, debemos actualizarla
                                gaid = fila.id
                                break
                        if gaid == None:
                            #debemos insertar una nueva asignación del profesor al departamento
                            self.db.grupo_alumno.insert(id_curso_academico_grupo = idcursoacademicogrupo,
                                                                                          id_alumno = idalumno)                            
                        else:
                            #debemos modificar la existente con la nueva
                            self.db.grupo_alumno[gaid] = dict(id_curso_academico_grupo = idcursoacademicogrupo)
                else:
                    #este alumno no tiene asignado grupo, hay que asignarlo al grupo Sin_Grupo
                    #comprobaremos si hemos creado el grupo Sin_Grupo, si no es así lo creamos
                    #y asignaremos el alumno a este grupo
                    #esto lo hacemos para importar "todos" los alumnos de rayuela, incluso aquellos que no hayan
                    #sido aun asignados a grupos en rayuela...
                    filagruposingrupo = self.db(self.db.grupo.grupo == "Sin_Grupo").select().first()
                    if filagruposingrupo == None:
                        idgruposingrupo = self.db.grupo.insert(grupo = "Sin_Grupo")
                    else:    
                        idgruposingrupo = filagruposingrupo.id    
                    # miremos si existe ese el dpto Sin_Departamento en el curso academico y si no se inserta
                    filacursoacademicogruposingrupo = self.db((self.db.curso_academico_departamento.id_curso_academico == self.sesion.curso_academico_id) &
                                               (self.db.curso_academico_grupo.id_grupo == idgruposingrupo)).select().first()
                    if filacursoacademicogruposingrupo == None:
                        idcursoacademicogruposingrupo = self.db.curso_academico_grupo.insert(id_curso_academico=self.sesion.curso_academico_id,
                                            id_grupo = idgruposingrupo)
                    else:
                        idcursoacademicogruposingrupo = filacursoacademicogruposingrupo.id                        
                    #asignemos el alumno a Sin_Grupo
                    self.db.grupo_alumno.insert(id_curso_academico_grupo = idcursoacademicogruposingrupo, id_alumno = idalumno)                  
        return
        
    def characters(self, ch):
        if self.iscodigo == 1:
            self.codigo += ch
        if self.isdenominacion == 1:
            self.denominacion += ch                       
        if self.isnie == 1:
            self.nie += ch                   
        if self.isnombre == 1:
            self.nombre += ch                       
        if self.isprimer_apellido == 1:
            self.primer_apellido += ch
        if self.issegundo_apellido == 1:
            self.segundo_apellido += ch
        if self.isfecha_nacimiento == 1:
            self.fecha_nacimiento += ch
        if self.ises_usuario == 1:
            self.es_usuario += ch
        if self.islogin == 1:
            self.login += ch
        if self.isid_usuario == 1:
            self.id_usuario += ch
        if self.isgrupo == 1:
            self.grupo += ch
        if self.iscon_foto == 1:
            self.con_foto += ch
        if self.isformato == 1:
            self.formato += ch
        if self.isnombre_fichero == 1:
            self.nombre_fichero += ch


class CursosGruposHandler(ContentHandler):
    def __init__(self,db,sesion):
        self.db = db
        self.sesion = sesion
        self.cursos_procesados = 0
        self.grupos_procesados = 0
        self.datos = Storage()
        self.datos.centro = Storage()
        self.datos.centro.codigo = ''
        self.datos.centro.denominacion = ''
        self.datos.cursos = List()
        self.datos_curso = Storage()
        self.datos_curso.nombrecurso = ''
        self.datos_curso.grupos = List()
        self.isgruposcentro = 0
        self.iscentro = 0
        self.iscodigo = 0
        self.codigo = ''
        self.isdenominacion = 0
        self.denominacion = ''
        self.iscurso = 0
        self.isnombrecurso = 0
        self.nombrecurso = ''
        self.isgrupocurso = 0
        self.isnombregrupo = 0
        self.nombregrupo = ''
        self.isdnitutorgrupo = 0
        self.dnitutorgrupo = ''
        
    
    def startElement(self, name, attrs):
        if name == 'grupos-centro':
            self.isgruposcentro = 1
        if name == 'centro':
            self.iscentro = 1
        if name == 'codigo':
            self.iscodigo = 1
            self.codigo = ""
        if name == 'denominacion':
            self.isdenominacion = 1
            self.denominacion = ""
        if name == 'curso':
            self.iscurso = 1
            self.cursos_procesados = self.cursos_procesados + 1
            self.datos_curso = Storage()
            self.datos_curso.nombrecurso = ''
            self.datos_curso.grupos = List()
        if name == 'nombre-curso':
            self.isnombrecurso = 1
            self.nombrecurso = ''
        if name == 'grupo-curso':
            self.isgrupocurso = 1
            self.grupos_procesados = self.grupos_procesados + 1
            self.datos_grupo = Storage()
            self.datos_grupo.nombregrupo = ''
            self.datos_grupo.dnitutorgrupo = ''
        if name == 'nombre-grupo':
            self.isnombregrupo = 1
            self.nombregrupo = ''
        if name == 'dnitutorgrupo':
            self.isdnitutorgrupo = 1
            self.dnitutorgrupo = ''
        return

    def endElement(self, name):
        if name == 'centro':
            self.iscentro = 0                          
        if name == 'codigo':
            self.iscodigo = 0
            self.datos.centro.codigo = self.codigo           
        if name == 'denominacion':
            self.isdenominacion = 0
            self.datos.centro.denominacion = self.denominacion           
        if name == 'nombre-curso':
            self.isnombrecurso = 0
            self.datos_curso.nombrecurso = self.nombrecurso
        if name == 'nombre-grupo':
            self.isnombregrupo = 0
            self.datos_grupo.nombregrupo = self.nombregrupo
        if name == 'dni-tutor-grupo':
            self.isdnitutorgrupo = 0
            self.datos_grupo.dnitutorgrupo = self.dnitutorgrupo
        if name == 'grupo-curso':
            self.isgrupocurso = 0
            #añadir el grupo al curso
            self.datos_curso.grupos.append(self.datos_grupo)
        if name == 'curso':
            self.iscurso = 0
            # acabamos de procesar un curso, con su nombre y la lista de grupos
            self.datos.cursos.append(self.datos_curso)
        if name == 'grupos-centro':
            self.isgruposcentro = 0
            # aquí deberemos procesar el diccionario self.datos que contiene el parseado del XML
            if self.datos.centro.codigo:
                # compruebo que existe algún valor de configuración
                # si existe ignoramos los datos de rayuela
                centro = self.db(self.db.config).select().first()
                if centro == None:
                    self.db.config.insert(codigo_centro = self.datos.centro.codigo, nombre_centro = self.datos.centro.denominacion)
            # procesaremos todos los cursos
            settings.logger.debug('Inicio el procesado de datos del archivo XML del grupos y tutores')
            for curso in self.datos.cursos:
                settings.logger.debug('    Procesando curso %s' % curso.nombrecurso)
                for grupo in curso.grupos:
                    # código que actualizará los tutores de los grupos
                    settings.logger.debug('        Procesando grupo %s tutor %s' % (grupo.nombregrupo, grupo.dnitutorgrupo))
        return
        
    def characters(self, ch):
        if self.iscodigo == 1:
            self.codigo += ch
        if self.isdenominacion == 1:
            self.denominacion += ch                       
        if self.isnombrecurso == 1:
            self.nombrecurso += ch                   
        if self.isnombregrupo == 1:
            self.nombregrupo += ch                   
        if self.isdnitutorgrupo == 1:
            self.dnitutorgrupo += ch
