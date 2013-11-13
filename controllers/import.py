# coding: utf8
# intente algo como
def index(): return dict(message="hello from import.py")

import os
from rayuelaimport import Rayuela


@auth.requires_membership(role='Informaticos')
def truncate_tables():
    db.profesor.truncate()
    db.alumno.truncate()
    db.departamento.truncate()
    db.grupo.truncate()
    db.curso_academico_departamento.truncate()
    db.curso_academico_grupo.truncate()
    db.departamento_profesor.truncate()
    db.grupo_profesor.truncate()
    db.grupo_alumno.truncate()
    return "Se han vaciado las tablas"
    
@auth.requires_membership(role='Informaticos')
def import_rayuela_teachers():
    response.flash = T('Import teachers from rayuela...')
    carpeta = os.path.join(request.folder,'uploads')
    form = SQLFORM.factory(Field('xml_rayuela_profesores','upload',uploadfolder=carpeta))    
    if form.accepts(request.vars, session):
        try:
            archivo = os.path.join(carpeta,form.vars.xml_rayuela_profesores)
            rayuela = Rayuela(db,session,archivo)
            rayuela.gestiona_archivo()           
        except:
            response.flash = T('Error importing from Rayuela')
            raise
        else:    
            response.flash = T('Import from Rayuela finished')            
        finally:
            os.remove(archivo)  
    return dict(form = form)
    
    
@auth.requires_membership(role='Informaticos')
def import_rayuela_students():
    response.flash = T('Import students from rayuela...')
    carpeta = os.path.join(request.folder,'uploads')
    form = SQLFORM.factory(Field('zip_rayuela_alumnos','upload',autodelete=True,uploadfolder=carpeta))    
    if form.accepts(request.vars, session):
        try:
            archivo = os.path.join(carpeta,form.vars.zip_rayuela_alumnos)            
            rayuela = Rayuela(db,session,archivo)
            rayuela.gestiona_archivo()
        except:
            response.flash = T('Error importing from Rayuela')       
            raise         
        else:
            response.flash = T('Import from Rayuela finished')        
        finally:    
            os.remove(archivo)  
    return dict(form = form)
    
@auth.requires_membership(role='Informaticos')
def import_rayuela_grupos_tutores():
    response.flash = T('Importar grupos-tutores desde Rayuela...')
    carpeta = os.path.join(request.folder,'uploads')
    form = SQLFORM.factory(Field('xml_rayuela_grupos_tutores','upload',uploadfolder=carpeta))    
    if form.accepts(request.vars, session):
        try:
            archivo = os.path.join(carpeta,form.vars.xml_rayuela_grupos_tutores)
            rayuela = Rayuela(db,session,archivo)
            rayuela.gestiona_archivo()           
        except:
            response.flash = T('Error importing from Rayuela')
            raise
        else:    
            response.flash = T('Import from Rayuela finished')            
        finally:
            os.remove(archivo)  
    return dict(form = form)

@auth.requires_membership(role='Informaticos')
def result_import_rayuela():
    return dict(message = resultado)
