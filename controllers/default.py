# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

#########################################################################
## This is a samples controller
## - index is the default action of any application
## - user is required for authentication and authorization
## - download is for downloading files uploaded in the db (does streaming)
## - call exposes all registered services (none by default)
#########################################################################

import datetime
import obies

def index():
    """
    example action using the internationalization operator T and flash
    rendered by views/default/index.html or views/generic.html
    """
    #logger.debug('pagina de inicio...')
    
    if not db(db.config).select().first():
        # Estamos ejecutando la aplicación por primera vez, no se han establecido datos correctos.
        # Insertaremos datos, importante crear el curso académico actual y establecerlo por defecto.
        # Comprobaremos que existen los roles Responsables, Profesores e Informaticos
        if not auth.id_group('Responsables'):
            auth.add_group('Responsables', 'Usuarios de responsabilidad')
        if not auth.id_group('Profesores'):    
            auth.add_group('Profesores', 'Usuarios profesores')
        if not auth.id_group('Informaticos'):
            auth.add_group('Informaticos', 'Usuarios administradores informáticos')
        if not auth.id_group('Administrativos'):
            auth.add_group('Administrativos', 'Usuarios administrativos')
            
            
        form = SQLFORM.factory(Field('Login_Administrador', requires=IS_NOT_EMPTY()),
                               Field('Nombre_Administrador', requires=IS_NOT_EMPTY()),
                               Field('Apellidos_Administrador', requires=IS_NOT_EMPTY()),
                               Field('Login_Administrativo', requires=IS_NOT_EMPTY()),
                               Field('Nombre_Administrativo', requires=IS_NOT_EMPTY()),
                               Field('Apellidos_Administrativo', requires=IS_NOT_EMPTY()),
                               Field('Codigo_Centro', requires=IS_NOT_EMPTY()),
                               Field('Nombre_Centro', requires=IS_NOT_EMPTY()),
                               Field('Director_Centro', requires=IS_NOT_EMPTY()),
                               Field('Curso_a_crear', requires=IS_NOT_EMPTY()),
                               Field('Retrasos_por_trimestres', 'boolean', default=True, requires=IS_NOT_EMPTY()),
                               Field('Retrasos_para_amonestacion', 'integer', default=2, requires=IS_NOT_EMPTY()),
                               Field('Fecha_Inicio_1_Trimestre', type='date',requires=[IS_NOT_EMPTY(),IS_DATE(format=T('%Y-%m-%d'))]),
                               Field('Fecha_Fin_1_Trimestre', type='date', requires=[IS_NOT_EMPTY(),IS_DATE(format=T('%Y-%m-%d'))]),
                               Field('Fecha_Inicio_2_Trimestre', type='date', requires=[IS_NOT_EMPTY(),IS_DATE(format=T('%Y-%m-%d'))]),
                               Field('Fecha_Fin_2_Trimestre', type='date', requires=[IS_NOT_EMPTY(),IS_DATE(format=T('%Y-%m-%d'))]),
                               Field('Fecha_Inicio_3_Trimestre', type='date', requires=[IS_NOT_EMPTY(),IS_DATE(format=T('%Y-%m-%d'))]),
                               Field('Fecha_Fin_3_Trimestre', type='date', requires=[IS_NOT_EMPTY(),IS_DATE(format=T('%Y-%m-%d'))]))
                    
        if form.process().accepted:

            # Procesaremos el usuario administrador informático
            informatico = db.auth_user.insert(username=form.vars.Login_Administrador, first_name=form.vars.Nombre_Administrador, last_name=form.vars.Apellidos_Administrador)
            auth.add_membership(role='Responsables', user_id = informatico)
            auth.add_membership(role='Informaticos', user_id = informatico)

            # Procesaremos el usuario administrativo
            administrativo = db.auth_user.insert(username=form.vars.Login_Administrativo, first_name=form.vars.Nombre_Administrativo, last_name=form.vars.Apellidos_Administrativo)
            auth.add_membership(role='Administrativos', user_id = administrativo)           
            
            # Procesemos la configuración inicial del sistema
            db.curso_academico.insert(curso = form.vars.Curso_a_crear,
                              retrasos_para_amonestacion=form.vars.Retrasos_para_amonestacion,
                              retrasos_por_trimestres=form.vars.Retrasos_por_trimestres,
                              inicio_trimestre_1 = form.vars.Fecha_Inicio_1_Trimestre, 
                              fin_trimestre_1 = form.vars.Fecha_Fin_1_Trimestre, inicio_trimestre_2 = form.vars.Fecha_Inicio_2_Trimestre,
                              fin_trimestre_2 = form.vars.Fecha_Fin_2_Trimestre, inicio_trimestre_3 = form.vars.Fecha_Inicio_3_Trimestre,
                              fin_trimestre_3 = form.vars.Fecha_Fin_3_Trimestre)
            db.config.insert(codigo_centro = form.vars.Codigo_Centro, nombre_centro = form.vars.Nombre_Centro, nombre_director = form.vars.Director_Centro,
                              curso_academico_defecto = db(db.curso_academico).select().first().id, 
                 )
            db.commit()
            response.flash = T('Setup success')     
            redirect(URL(c='default/user', f='login'))
        elif form.errors:
            response.flash = T('Setup errors')
        else:
            response.flash = T('Initial application setup')

        return dict(form=form, message=T('Disciplinary Management in secondary schools'))
    else:
        return dict(form=None, message=T('Disciplinary Management in secondary schools'))

def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    """
    return dict(form=auth())


def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request,db)


def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    session.forget()
    return service()

def logout():
    """ Logout handler """
    session.flash = 'Salida del sistema'
    session.authorized = None
    session.clear
    if MULTI_USER_MODE:
        redirect(URL('user/logout'))
    redirect(URL('index'))
    
def datoscentro():
    return dict()

def cabecerausuario():
    return dict()
