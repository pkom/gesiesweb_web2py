# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations
#########################################################################
## Customize your APP title, subtitle and menus here
#########################################################################

response.title = settings.title
response.subtitle = settings.subtitle
response.meta.author = settings.author
response.meta.description = settings.description
response.meta.keywords = settings.keywords
response.meta.generator = 'Web2py Enterprise Framework'
response.meta.copyright = 'Copyright 2013'

response.centro = 'I.E.S. Maestro Juan Calero - Monesterio (BA)'

response.menu = [
    (T('Inicio'), False, URL('default','index'), [])
    ]

if session.esProfesor:
    response.menu += [(T('Partes'), False, None, [
            (T('Mis Partes'), False, URL('warnings', 'warnings'), [])
            ]
    )]
    
if session.profesor.esTutor:
    response.menu[1][3].append((T('Partes tutoría %s', session.profesor.tutor.curso), False, URL('warnings', 'warningstutor'), []))
    
if session.esProfesor:
    response.menu += [(T('Retrasos'), False, None, [
            (T('Mis Retrasos'), False, URL('delays', 'delays'), [])
            ]
    )]

if session.profesor.esTutor:
    response.menu[2][3].append((T('Partes Retrasos tutoría %s', session.profesor.tutor.curso), False, URL('delays', 'delaystutor'), []))

if session.esProfesor:
    response.menu += [(T('Absentismo'), False, None, [
            (T('Absentismo Pasivo'), False, URL('absentismo', 'absentismo'), [])
            ]
    )]

if session.profesor.esTutor:
    response.menu[3][3].append((T('Absentismo Pasivo tutoría %s', session.profesor.tutor.curso), False, URL('absentismo', 'absentismotutor'), []))

if session.esProfesor:
    response.menu += [(T('Evaluación'), False, None, [
            (T('Mis Evaluaciones'), False, URL('evaluaciones', 'evaluacion'), [])
            ]
    )]

if session.profesor.esTutor:
    response.menu[4][3].append((T('Evaluaciones tutoría %s', session.profesor.tutor.curso), False, URL('evaluaciones', 'evaluacionestutoria'), []))                                                
                                                                                
                                                
if session.esResponsable:
    response.menu += [(T('Estadísticas'), False, None, [
            (T('Partes Registrados'), False, None, [(T('Disciplinarios'),False,URL('statistics','warnings'),[]),
                                        (T('Por Retrasos'), False, URL('statistics', 'delays'), []),
                                        (T('Absentismo Pasivo'), False, URL('statistics', 'absentismo'), [])
            ]),
            (T('Resumen Alumnado'), False, None, [(T('Disciplinarios'), False, URL('statistics', 'resumestudents'), []),
                                                  (T('Por Retrasos'), False, URL('statistics', 'resumestudentsdelays'), []),            
                                                  (T('Absentismo Pasivo'), False, URL('statistics', 'resumestudentsabsentismo'), [])
            ]),
            (T('Resumen Profesorado'), False, None, [(T('Disciplinarios'), False, URL('statistics', 'resumeteachers'), []),
                                                     (T('Absentismo Pasivo'), False, URL('statistics', 'resumeteachersabsentismo'), [])
            ]),
            (T('Informes Evaluaciones'), False, URL('informes', 'evaluaciones'), [])                                                                    
        ]
    )]

if session.profesor.esJefe:
    response.menu += [(T('Criterios Eval.'), False, None, [
        (T('Departamento'), False,  URL('management','departamento'), []),
        (T('Asignaturas'), False, URL('management','asignaturas'), [])
        ])]
        
#para Responsables
if session.esResponsable or session.esAdministrativo:
    response.menu+=[
        (T('Gestión Centro'), False, None, [
            (T('Centro'), False, URL('management', 'show_center'), []),
            (T('Cursos Académicos'), False, URL('management', 'show_courses'), []),
            (T('Alumnado'), False, URL('management', 'show_students'), []),
            (T('Profesorado'), False, URL('management', 'show_teachers'), []),
            (T('Grupos'), False, URL('management', 'show_groups'), []),
            (T('Departamentos'), False, URL('management', 'show_departaments'), []),
            (T('Responsables'), False, URL('management', 'show_responsibles'), []),
            (T('Evaluaciones'), False, None, [
                (T('Asignaturas'), False, URL('evaluaciones', 'show_asignaturas'), []),
                (T('Evaluaciones'), False, URL('evaluaciones', 'show_evaluaciones'), []),                
                (T('Asignaciones Grupo Profesor Asignatura Alumnos'), False, URL('evaluaciones', 'show_grupo_profesor_asignaturas'), []),                                
                ]),
        ]
    )]
   

#para Informáticos
if session.esInformatico:
    response.menu[-1][-1].append(
            (T('Importación Rayuela'), False, None, [
                (T('Profesorado'), False, URL('import', 'import_rayuela_teachers')),
                (T('Alumnado'), False, URL('import', 'import_rayuela_students')),
                (T('Grupos-Tutores'), False, URL('import', 'import_rayuela_grupos_tutores')),               
                ]))

"""
response.menu+=[
    (T('This App'), False, URL('admin', 'default', 'design/%s' % request.application),
     [
            (T('Controller'), False,
             URL('admin', 'default', 'edit/%s/controllers/%s.py' \
                     % (request.application,request.controller=='appadmin' and
                        'default' or request.controller))),
            (T('View'), False,
             URL('admin', 'default', 'edit/%s/views/%s' \
                     % (request.application,response.view))),
            (T('Layout'), False,
             URL('admin', 'default', 'edit/%s/views/layout.html' \
                     % request.application)),
            (T('Stylesheet'), False,
             URL('admin', 'default', 'edit/%s/static/base.css' \
                     % request.application)),
            (T('DB Model'), False,
             URL('admin', 'default', 'edit/%s/models/db.py' \
                     % request.application)),
            (T('Menu Model'), False,
             URL('admin', 'default', 'edit/%s/models/menu.py' \
                     % request.application)),
            (T('Database'), False,
             URL(request.application, 'appadmin', 'index')),

            (T('Errors'), False,
             URL('admin', 'default', 'errors/%s' \
                     % request.application)),

            (T('About'), False,
             URL('admin', 'default', 'about/%s' \
                     % request.application)),

            ]
   )]


##########################################
## this is here to provide shortcuts to some resources
## during development. remove in production
##
## mind that plugins may also affect menu
##########################################

response.menu+=[(T('Resources'), False, None,
     [
    (T('Documentation'), False, 'http://www.web2py.com/book', 
        [
        (T('Preface'), False, 'http://www.web2py.com/book/default/chapter/00'),
        (T('Introduction'), False, 'http://www.web2py.com/book/default/chapter/01'),
        (T('Python'), False, 'http://www.web2py.com/book/default/chapter/02'),
        (T('Overview'), False, 'http://www.web2py.com/book/default/chapter/03'),
        (T('The Core'), False, 'http://www.web2py.com/book/default/chapter/04'),
        (T('The Views'), False, 'http://www.web2py.com/book/default/chapter/05'),
        (T('Database'), False, 'http://www.web2py.com/book/default/chapter/06'),
        (T('Forms and Validators'), False, 'http://www.web2py.com/book/default/chapter/07'),
        (T('Access Control'), False, 'http://www.web2py.com/book/default/chapter/08'),
        (T('Services'), False, 'http://www.web2py.com/book/default/chapter/09'),
        (T('Ajax Recipes'), False, 'http://www.web2py.com/book/default/chapter/10'),
        (T('Deployment Recipes'), False, 'http://www.web2py.com/book/default/chapter/11'),
        (T('Other Recipes'), False, 'http://www.web2py.com/book/default/chapter/12'),
        (T('Buy this book'), False, 'http://stores.lulu.com/web2py'),
        ]),

    (T('Community'), False, None,
        [
        (T('Groups'), False, 'http://www.web2py.com/examples/default/usergroups'),
        (T('Twitter'), False, 'http://twitter.com/web2py'),
        (T('Live chat'), False, 'http://mibbit.com/?channel=%23web2py&server=irc.mibbit.net'),
        (T('User Voice'), False, 'http://web2py.uservoice.com/'),
        ]),
        
    (T('Web2py'), False, 'http://www.web2py.com',
        [
        (T('Download'), False, 'http://www.web2py.com/examples/default/download'),
        (T('Support'), False, 'http://www.web2py.com/examples/default/support'),
        (T('Quick Examples'), False, 'http://web2py.com/examples/default/examples'),
        (T('FAQ'), False, 'http://web2py.com/AlterEgo'),
        (T('Free Applications'), False, 'http://web2py.com/appliances'),
        (T('Plugins'), False, 'http://web2py.com/plugins'),
        (T('Recipes'), False, 'http://web2pyslices.com/'),
        (T('Demo'), False, 'http://web2py.com/demo_admin'),
        (T('Semantic'), False, 'http://web2py.com/semantic'),
        (T('Layouts'), False, 'http://web2py.com/layouts'),
        (T('Videos'), False, 'http://www.web2py.com/examples/default/videos/'),
        ]),        
    ]
   )]
"""
