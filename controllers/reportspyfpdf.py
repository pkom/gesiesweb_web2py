# coding: utf8

import os.path
import datetime
import uuid

from pygooglechart import GroupedVerticalBarChart, Axis

from gluon.contrib.pyfpdf import FPDF

from obies import Aviso, Absentismo, Evaluacion

def parsestr(txt):
    return unicode(txt, 'utf-8').encode('iso-8859-1')

@auth.requires_login()
@auth.requires_membership(role='Responsables')
def warningsStudent():
    idgrupoalumno = int(request.args[0]) or redirect('default', 'index')
    oaviso = Aviso(db, session)
    avisos = oaviso.dame_avisos_alumno(idgrupoalumno)
    nombreAlumno = avisos[0].alumno.apellidos+', '+avisos[0].alumno.nombre if len(avisos) > 0 else ""
    total = len(avisos)
    parte = 0
    comunicadas = 0
    cerradas = 0
    for aviso in avisos:
        if aviso.amonestacion.parte:
            parte+=1
        if aviso.amonestacion.comunicada:
            comunicadas+=1
        if aviso.amonestacion.cerrada:
            cerradas+=1        
    resumen = "Total de partes: "+str(total)+", con parte: "+str(parte)+" comunicadas: "+str(comunicadas)+" cerradas: "+str(cerradas)
    nie = avisos[0].alumno.nie if len(avisos) > 0 else ""
    fnac = avisos[0].alumno.fecha_nacimiento if len(avisos) > 0 else ""
    grupo = avisos[0].grupo.grupo if len(avisos) > 0 else ""
    tutor = '%s, %s' % (avisos[0].amonestacion.id_grupo_alumno.id_curso_academico_grupo.id_tutor.apellidos,
            avisos[0].amonestacion.id_grupo_alumno.id_curso_academico_grupo.id_tutor.nombre) \
            if (len(avisos) > 0 and avisos[0].amonestacion.id_grupo_alumno.id_curso_academico_grupo.id_tutor) else ''
    logo = os.path.join(request.env.web2py_path,"applications",request.application,"uploads", session.logo_centro)   
    cad = avisos[0].alumno.foto.split(".")
    subpath = cad[:2]
    subpath = os.path.join(".".join(subpath), cad[2][:2])
    cad = ".".join(cad)
    foto = os.path.join(request.folder,"uploads",subpath,cad)
    titulo = "Partes del alumno/a: "+nombreAlumno
    tnombre = "Alumno/a:"
    tnie = "N.I.E.:"
    tfecha = "Fec.Nac.:"
    tgrupo = "Grupo:"
    ttutor = "Tutor/a:"  
    tcentro = session.codigo_centro+' '+session.nombre_centro
    tcurso = session.curso_academico_nombre

    class WarningsFPDF(FPDF):
        def header(self): 
            #Arial bold 15
            self.set_font('Arial','B',15)
            #Poner código del centro y nombre el la parte izquierda superior
            self.cell(w=0,h=0,txt=parsestr(tcentro),border=0,ln=0,align='L',fill=0)
            #Ahora el curso académico en la parte derecha superior
            self.cell(w=0,h=0,txt="Curso: "+parsestr(tcurso),border=0,ln=1,align='R',fill=0)
            #Dibujamos una linea de separación
            #self.set_line_width(.5)
            self.line(5,13,205,13)
            #Calcular ancho del texto (titulo) y establecer posición
            w=self.get_string_width(titulo)+6
            self.set_x((210-w)/2)
            #Titulo
            self.cell(w=w,h=17,txt=parsestr(titulo),border=0,ln=1,align='C',fill=0)
            #Linea
            self.line(5,23,205,23)
            #Fuente más pequeña sin bold
            self.set_font('','',8)      
            #Nombre alumno      
            self.cell(w=20,h=0,txt=parsestr(tnombre),border=0,ln=0,align='R',fill=0)
            self.set_font('','B',10)                        
            self.cell(w=20,h=0,txt=parsestr(nombreAlumno),border=0,ln=1,align="L",fill=0)
            
            #Foto alumno
            try:
                self.image(foto,180,25,17,22)
            except:
                pass
           
            #Nie alumno
            self.set_font('','',8)                        
            self.cell(w=20,h=9,txt=parsestr(tnie),border=0,ln=0,align='R',fill=0)            
            self.set_font('','B',10)                                    
            self.cell(w=20,h=9,txt=parsestr(nie),border=0,ln=1,align="L",fill=0)
            
            #Fecha nacimiento
            self.set_font('','',8)                                    
            self.cell(w=20,h=0,txt=parsestr(tfecha),border=0,ln=0,align='R',fill=0)        
            self.set_font('','B',10)                                                
            self.cell(w=20,h=0,txt=fnac.isoformat(),border=0,ln=1,align="L",fill=0)
            
            #Grupo
            self.set_font('','',8)                                                
            self.cell(w=20,h=9,txt=parsestr(tgrupo),border=0,ln=0,align='R',fill=0)
            self.set_font('','B',10)                                                            
            self.cell(w=20,h=9,txt=parsestr(grupo),border=0,ln=1,align="L",fill=0)             

            #Tutor
            self.set_font('','',8)                                                            
            self.cell(w=20,h=0,txt=parsestr(ttutor),border=0,ln=0,align='R',fill=0)            
            self.set_font('','B',10)                                                                        
            self.cell(w=20,h=0,txt=parsestr(tutor),border=0,ln=1,align="L",fill=0)           
            self.line(5,48,205,48)
            self.set_font('','B',9)
            self.cell(w=10,h=11,txt=parsestr("Número"))
            self.cell(10)
            self.cell(w=10,h=11,txt=parsestr("Fecha"))
            self.cell(10)            
            self.cell(w=10,h=11,txt=parsestr("Profesor/a"))
            self.cell(80)            
            self.cell(w=10,h=11,txt=parsestr("Cerrada"))
            self.cell(12)            
            self.cell(w=10,h=11,txt=parsestr("Parte"))
            self.cell(10)           
            self.cell(w=10,h=11,txt=parsestr("Comunicada"))
            self.line(5,53,205,53)
            #Salto de línea
            self.ln(10)           
              
        def footer(self):
            "hook to draw custom page header (printing page numbers)"
            self.line(5,280,205,280)
            self.set_y(-19)
            self.set_font('Arial','I',8)
            self.cell(w=0,h=9,txt=parsestr(titulo),border=0,ln=0,align='L',fill=0)
            marcaid = parsestr(("Impreso por %s a las %s" % (session.auth.user.first_name+" "+session.auth.user.last_name,datetime.datetime.now().strftime("%H:%M:%S %d/%m/%Y"))))
            self.cell(w=0,h=9,txt=marcaid,border=0,ln=1,align='R',fill=0)
            #Resumen
            self.cell(w=0,h=0,txt=parsestr(resumen),ln=0)            
            txt = parsestr('Página')+' %s de %s' % (self.page_no(), self.alias_nb_pages())
            self.cell(w=0,h=0,txt=txt,border=0,ln=0,align='R',fill=0)
                  
    pdf=WarningsFPDF()
    pdf.alias_nb_pages()
    pdf.add_page()
    pdf.set_font('Arial','',8)
    pdf.set_fill_color(230,230,230)    
    for aviso in avisos:
        pdf.cell(w=10,h=5,txt=parsestr(str(aviso.amonestacion.id)),border=0,ln=0,align="R",fill=0)
        pdf.cell(8)
        pdf.cell(w=10,h=5,txt=aviso.amonestacion.fecha.isoformat())
        pdf.cell(10)
        pdf.cell(w=10,h=5,txt=parsestr(aviso.profesor.apellidos+', '+aviso.profesor.nombre))
        pdf.cell(85)            
        pdf.cell(w=10,h=5,txt=parsestr("Sí" if aviso.amonestacion.cerrada else "No"))
        pdf.cell(10)            
        pdf.cell(w=10,h=5,txt=parsestr("Sí" if aviso.amonestacion.parte else "No"))
        pdf.cell(15)           
        pdf.cell(w=10,h=5,txt=parsestr("Sí" if aviso.amonestacion.comunicada else "No"),ln=1)
        pdf.cell(19)
        pdf.multi_cell(w=0,h=5,txt=parsestr(aviso.amonestacion.amonestacion),border=0,align="J",fill=1)
        seguimientos = oaviso.dame_seguimientos(aviso.amonestacion.id)
        if len(seguimientos) > 0:
            # aquí debo imprimir los seguimientos del aviso
            pdf.ln(1)
            pdf.line(pdf.get_x()+30,pdf.get_y(),pdf.get_x()+190,pdf.get_y())            
            pdf.cell(30)       
            pdf.cell(w=10,h=5,txt=parsestr("Seguimientos"))
            pdf.cell(23)
            pdf.cell(w=10,h=5,txt=parsestr("Fecha"))
            pdf.cell(20)
            pdf.cell(w=10,h=5,txt=parsestr("Responsable"))        
            pdf.cell(40)            
            pdf.cell(w=10,h=5,txt=parsestr("Seguimiento"),ln=1)
            pdf.line(pdf.get_x()+30,pdf.get_y(),pdf.get_x()+190,pdf.get_y())
            pdf.ln(1)
            for seguimiento in seguimientos:
                pdf.cell(60)
                pdf.cell(w=10,h=4,txt=parsestr(seguimiento.seguimiento.fecha.isoformat()))       
                pdf.cell(10)
                pdf.cell(w=10,h=4,txt=parsestr(seguimiento.profesor.apellidos+", "+seguimiento.profesor.nombre))    
                pdf.cell(40)
                pdf.multi_cell(w=60,h=4,txt=parsestr(seguimiento.seguimiento.seguimiento),border=0,align="J",fill=1)    
                pdf.ln(1)
    
        pdf.line(pdf.get_x(),pdf.get_y(),pdf.get_x()+190,pdf.get_y())            
       
    response.headers['Content-Type']='application/pdf'
    return pdf.output(dest='S')

@auth.requires_login()
@auth.requires_membership(role='Responsables')
def absentismosStudent():
    idgrupoalumno = int(request.args[0]) or redirect('default', 'index')
    oaviso = Absentismo(db, session)
    avisos = oaviso.dame_absentismos_alumno(idgrupoalumno)
    nombreAlumno = avisos[0].alumno.apellidos+', '+avisos[0].alumno.nombre if len(avisos) > 0 else ""
    total = len(avisos)
    comunicadas = 0
    for aviso in avisos:
        if aviso.amonestacion_absentismo.comunicada:
            comunicadas+=1
    resumen = "Total de partes: "+str(total)+" comunicadas: "+str(comunicadas)
    nie = avisos[0].alumno.nie if len(avisos) > 0 else ""
    fnac = avisos[0].alumno.fecha_nacimiento if len(avisos) > 0 else ""
    grupo = avisos[0].grupo.grupo if len(avisos) > 0 else ""
    tutor = '%s, %s' % (avisos[0].amonestacion_absentismo.id_grupo_alumno.id_curso_academico_grupo.id_tutor.apellidos,
            avisos[0].amonestacion_absentismo.id_grupo_alumno.id_curso_academico_grupo.id_tutor.nombre) \
            if (len(avisos) > 0 and avisos[0].amonestacion_absentismo.id_grupo_alumno.id_curso_academico_grupo.id_tutor) else ''
    logo = os.path.join(request.env.web2py_path,"applications",request.application,"uploads", session.logo_centro)   
    cad = avisos[0].alumno.foto.split(".")
    subpath = cad[:2]
    subpath = os.path.join(".".join(subpath), cad[2][:2])
    cad = ".".join(cad)
    foto = os.path.join(request.folder,"uploads",subpath,cad)
    titulo = "Absentismos pasivos del alumno/a: "+nombreAlumno
    tnombre = "Alumno/a:"
    tnie = "N.I.E.:"
    tfecha = "Fec.Nac.:"
    tgrupo = "Grupo:"
    ttutor = "Tutor/a:"  
    tcentro = session.codigo_centro+' '+session.nombre_centro
    tcurso = session.curso_academico_nombre

    class AbsentismosFPDF(FPDF):
        def header(self): 
            #Arial bold 15
            self.set_font('Arial','B',15)
            #Poner código del centro y nombre el la parte izquierda superior
            self.cell(w=0,h=0,txt=parsestr(tcentro),border=0,ln=0,align='L',fill=0)
            #Ahora el curso académico en la parte derecha superior
            self.cell(w=0,h=0,txt="Curso: "+parsestr(tcurso),border=0,ln=1,align='R',fill=0)
            #Dibujamos una linea de separación
            #self.set_line_width(.5)
            self.line(5,13,205,13)
            #Calcular ancho del texto (titulo) y establecer posición
            w=self.get_string_width(titulo)+6
            self.set_x((210-w)/2)
            #Titulo
            self.cell(w=w,h=17,txt=parsestr(titulo),border=0,ln=1,align='C',fill=0)
            #Linea
            self.line(5,23,205,23)
            #Fuente más pequeña sin bold
            self.set_font('','',8)      
            #Nombre alumno      
            self.cell(w=20,h=0,txt=parsestr(tnombre),border=0,ln=0,align='R',fill=0)
            self.set_font('','B',10)                        
            self.cell(w=20,h=0,txt=parsestr(nombreAlumno),border=0,ln=1,align="L",fill=0)
            
            #Foto alumno
            try:
                self.image(foto,180,25,17,22)
            except:
                pass
           
            #Nie alumno
            self.set_font('','',8)                        
            self.cell(w=20,h=9,txt=parsestr(tnie),border=0,ln=0,align='R',fill=0)            
            self.set_font('','B',10)                                    
            self.cell(w=20,h=9,txt=parsestr(nie),border=0,ln=1,align="L",fill=0)
            
            #Fecha nacimiento
            self.set_font('','',8)                                    
            self.cell(w=20,h=0,txt=parsestr(tfecha),border=0,ln=0,align='R',fill=0)        
            self.set_font('','B',10)                                                
            self.cell(w=20,h=0,txt=fnac.isoformat(),border=0,ln=1,align="L",fill=0)
            
            #Grupo
            self.set_font('','',8)                                                
            self.cell(w=20,h=9,txt=parsestr(tgrupo),border=0,ln=0,align='R',fill=0)
            self.set_font('','B',10)                                                            
            self.cell(w=20,h=9,txt=parsestr(grupo),border=0,ln=1,align="L",fill=0)             

            #Tutor
            self.set_font('','',8)                                                            
            self.cell(w=20,h=0,txt=parsestr(ttutor),border=0,ln=0,align='R',fill=0)            
            self.set_font('','B',10)                                                                        
            self.cell(w=20,h=0,txt=parsestr(tutor),border=0,ln=1,align="L",fill=0)           
            self.line(5,48,205,48)
            self.set_font('','B',9)
            self.cell(w=10,h=11,txt=parsestr("Número"))
            self.cell(10)
            self.cell(w=10,h=11,txt=parsestr("Fecha"))
            self.cell(10)            
            self.cell(w=10,h=11,txt=parsestr("Profesor/a"))
            self.cell(30)            
            self.cell(w=10,h=11,txt=parsestr("Comunicado"))
            self.line(5,53,205,53)
            #Salto de línea
            self.ln(10)           
              
        def footer(self):
            "hook to draw custom page header (printing page numbers)"
            self.line(5,280,205,280)
            self.set_y(-19)
            self.set_font('Arial','I',8)
            self.cell(w=0,h=9,txt=parsestr(titulo),border=0,ln=0,align='L',fill=0)
            marcaid = parsestr(("Impreso por %s a las %s" % (session.auth.user.first_name+" "+session.auth.user.last_name,datetime.datetime.now().strftime("%H:%M:%S %d/%m/%Y"))))
            self.cell(w=0,h=9,txt=marcaid,border=0,ln=1,align='R',fill=0)
            #Resumen
            self.cell(w=0,h=0,txt=parsestr(resumen),ln=0)            
            txt = parsestr('Página')+' %s de %s' % (self.page_no(), self.alias_nb_pages())
            self.cell(w=0,h=0,txt=txt,border=0,ln=0,align='R',fill=0)
                  
    pdf=AbsentismosFPDF()
    pdf.alias_nb_pages()
    pdf.add_page()
    pdf.set_font('Arial','',8)
    pdf.set_fill_color(230,230,230)    
    for aviso in avisos:
        pdf.cell(w=10,h=5,txt=parsestr(str(aviso.amonestacion_absentismo.id)),border=0,ln=0,align="R",fill=0)
        pdf.cell(8)
        pdf.cell(w=10,h=5,txt=aviso.amonestacion_absentismo.fecha.isoformat())
        pdf.cell(10)
        pdf.cell(w=10,h=5,txt=parsestr(aviso.profesor.apellidos+', '+aviso.profesor.nombre))
        pdf.cell(35)            
        pdf.cell(w=10,h=5,txt=parsestr("Sí" if aviso.amonestacion_absentismo.comunicada else "No"))
        pdf.cell(10)
        pdf.multi_cell(w=0,h=5,txt=parsestr(aviso.amonestacion_absentismo.absentismo),border=0,align="J",fill=1)    
        pdf.line(pdf.get_x(),pdf.get_y(),pdf.get_x()+190,pdf.get_y())            
       
    response.headers['Content-Type']='application/pdf'
    return pdf.output(dest='S')     
                
def warningsDelaysStudent():
    idgrupoalumno = int(request.args[0]) or redirect('default', 'index')
    oaviso = Aviso(db, session)
    avisosretraso = oaviso.dame_avisos_retrasos_alumno(idgrupoalumno)
    nombreAlumno = avisosretraso[0].alumno.apellidos+', '+avisosretraso[0].alumno.nombre if len(avisosretraso) > 0 else ""
    nie = avisosretraso[0].alumno.nie if len(avisosretraso) > 0 else ""
    fnac = avisosretraso[0].alumno.fecha_nacimiento if len(avisosretraso) > 0 else ""
    grupo = avisosretraso[0].grupo.grupo if len(avisosretraso) > 0 else ""
    tutor = '%s, %s' % (avisosretraso[0].amonestacion_retraso.id_grupo_alumno.id_curso_academico_grupo.id_tutor.apellidos,
            avisosretraso[0].amonestacion_retraso.id_grupo_alumno.id_curso_academico_grupo.id_tutor.nombre) \
            if (len(avisosretraso) > 0 and avisosretraso[0].amonestacion_retraso.id_grupo_alumno.id_curso_academico_grupo.id_tutor) else ''
    logo = os.path.join(request.env.web2py_path,"applications",request.application,"uploads", session.logo_centro)   
    cad = avisosretraso[0].alumno.foto.split(".")
    subpath = cad[:2]
    subpath = os.path.join(".".join(subpath), cad[2][:2])
    cad = ".".join(cad)
    foto = os.path.join(request.folder,"uploads",subpath,cad)
    total = len(avisosretraso)

    comunicadas = 0
    cerradas = 0
    for aviso in avisosretraso:
        if aviso.amonestacion_retraso.comunicada:
            comunicadas+=1
        if aviso.amonestacion_retraso.cerrada:
            cerradas+=1        
    resumen = "Total de partes: "+str(total)+", comunicados: "+str(comunicadas)+" cerrados: "+str(cerradas)

    #resumen = "Total de partes por retrasos: "+str(total)   
    titulo = "Partes por Retrasos de Alumno/a: "+nombreAlumno
    tnombre = "Alumno/a:"
    tnie = "N.I.E.:"
    tfecha = "Fec.Nac.:"
    tgrupo = "Grupo:"
    ttutor = "Tutor/a:"  
    tcentro = session.codigo_centro+' '+session.nombre_centro
    tcurso = session.curso_academico_nombre

    class delaysWarningsFPDF(FPDF):
        def header(self): 
            #Arial bold 15
            self.set_font('Arial','B',15)
            #Poner código del centro y nombre el la parte izquierda superior
            self.cell(w=0,h=0,txt=parsestr(tcentro),border=0,ln=0,align='L',fill=0)
            #Ahora el curso académico en la parte derecha superior
            self.cell(w=0,h=0,txt="Curso: "+parsestr(tcurso),border=0,ln=1,align='R',fill=0)
            #Dibujamos una linea de separación
            #self.set_line_width(.5)
            self.line(5,13,205,13)
            #Calcular ancho del texto (titulo) y establecer posición
            w=self.get_string_width(titulo)+6
            self.set_x((210-w)/2)
            #Titulo
            self.cell(w=w,h=17,txt=parsestr(titulo),border=0,ln=1,align='C',fill=0)
            #Linea
            self.line(5,23,205,23)
            #Fuente más pequeña sin bold
            self.set_font('','',8)      
            #Nombre alumno      
            self.cell(w=20,h=0,txt=parsestr(tnombre),border=0,ln=0,align='R',fill=0)
            self.set_font('','B',10)                        
            self.cell(w=20,h=0,txt=parsestr(nombreAlumno),border=0,ln=1,align="L",fill=0)
            
            #Foto alumno
            try:
                self.image(foto,180,25,17,22)
            except:
                pass
           
            #Nie alumno
            self.set_font('','',8)                        
            self.cell(w=20,h=9,txt=parsestr(tnie),border=0,ln=0,align='R',fill=0)            
            self.set_font('','B',10)                                    
            self.cell(w=20,h=9,txt=parsestr(nie),border=0,ln=1,align="L",fill=0)
            
            #Fecha nacimiento
            self.set_font('','',8)                                    
            self.cell(w=20,h=0,txt=parsestr(tfecha),border=0,ln=0,align='R',fill=0)        
            self.set_font('','B',10)                                                
            self.cell(w=20,h=0,txt=fnac.isoformat(),border=0,ln=1,align="L",fill=0)
            
            #Grupo
            self.set_font('','',8)                                                
            self.cell(w=20,h=9,txt=parsestr(tgrupo),border=0,ln=0,align='R',fill=0)
            self.set_font('','B',10)                                                            
            self.cell(w=20,h=9,txt=parsestr(grupo),border=0,ln=1,align="L",fill=0)             

            #Tutor
            self.set_font('','',8)                                                            
            self.cell(w=20,h=0,txt=parsestr(ttutor),border=0,ln=0,align='R',fill=0)            
            self.set_font('','B',10)                                                                        
            self.cell(w=20,h=0,txt=parsestr(tutor),border=0,ln=1,align="L",fill=0)           
            self.line(5,48,205,48)
            self.set_font('','B',9)
            self.cell(w=10,h=11,txt=parsestr("Número"))
            self.cell(10)
            self.cell(w=10,h=11,txt=parsestr("Fecha"))
            #self.cell(10)            
            #self.cell(w=10,h=11,txt=parsestr("Profesor/a"))
            self.cell(120)            
            self.cell(w=10,h=11,txt=parsestr("Comunicado"))
            #self.cell(12)            
            #self.cell(w=10,h=11,txt=parsestr("Parte"))
            self.cell(10)           
            self.cell(w=10,h=11,txt=parsestr("Cerrado"))
            self.line(5,53,205,53)
            #Salto de línea
            self.ln(10)           
              
        def footer(self):
            "hook to draw custom page header (printing page numbers)"
            self.line(5,280,205,280)
            self.set_y(-19)
            self.set_font('Arial','I',8)
            self.cell(w=0,h=9,txt=parsestr(titulo),border=0,ln=0,align='L',fill=0)
            marcaid = parsestr(("Impreso por %s a las %s" % (session.auth.user.first_name+" "+session.auth.user.last_name,datetime.datetime.now().strftime("%H:%M:%S %d/%m/%Y"))))
            self.cell(w=0,h=9,txt=marcaid,border=0,ln=1,align='R',fill=0)
            #Resumen
            self.cell(w=0,h=0,txt=parsestr(resumen),ln=0)                        
            txt = parsestr('Página')+' %s de %s' % (self.page_no(), self.alias_nb_pages())
            self.cell(w=0,h=0,txt=txt,border=0,ln=0,align='R',fill=0)
                  
    pdf=delaysWarningsFPDF()
    pdf.alias_nb_pages()
    pdf.add_page()
    pdf.set_font('Arial','',8)
    pdf.set_fill_color(230,230,230)    
    for aviso in avisosretraso:
        pdf.cell(w=10,h=5,txt=parsestr(str(aviso.amonestacion_retraso.id)),border=0,ln=0,align="R",fill=0)
        pdf.cell(8)
        pdf.cell(w=10,h=5,txt=aviso.amonestacion_retraso.fecha.isoformat())
        #pdf.cell(10)
        #pdf.cell(w=10,h=5,txt=parsestr(aviso.profesor.apellidos+', '+aviso.profesor.nombre))
        pdf.cell(130)            
        pdf.cell(w=10,h=5,txt=parsestr("Sí" if aviso.amonestacion_retraso.comunicada else "No"))
        #pdf.cell(10)            
        #pdf.cell(w=10,h=5,txt=parsestr("Sí" if aviso.amonestacion.parte else "No"))
        pdf.cell(7)           
        pdf.cell(w=10,h=5,txt=parsestr("Sí" if aviso.amonestacion_retraso.cerrada else "No"),ln=1)
        pdf.cell(19)
        pdf.multi_cell(w=0,h=5,txt=parsestr("Parte por retrasos acumulados"),border=0,align="J",fill=1)
        retrasos = oaviso.dame_retrasos(aviso.amonestacion_retraso.id)
        if len(retrasos) > 0:
            # aquí debo imprimir los seguimientos del aviso
            pdf.ln(1)
            pdf.line(pdf.get_x()+30,pdf.get_y(),pdf.get_x()+190,pdf.get_y())            
            pdf.cell(30)       
            pdf.cell(w=10,h=5,txt=parsestr("Retrasos"))
            pdf.cell(23)
            pdf.cell(w=10,h=5,txt=parsestr("Fecha"))
            pdf.cell(20)
            pdf.cell(w=10,h=5,txt=parsestr("Hora"))        
            pdf.cell(40)            
            pdf.cell(w=10,h=5,txt=parsestr("Profesor"),ln=1)
            pdf.line(pdf.get_x()+30,pdf.get_y(),pdf.get_x()+190,pdf.get_y())
            pdf.ln(1)
            for retraso in retrasos:
                pdf.cell(60)
                pdf.cell(w=10,h=4,txt=parsestr(retraso.retraso.fecha.isoformat()))       
                pdf.cell(10)
                pdf.cell(w=10,h=4,txt=parsestr(retraso.retraso.hora))
                pdf.cell(40)
                pdf.multi_cell(w=60,h=4,txt=parsestr(retraso.profesor.apellidos+", "+retraso.profesor.nombre),
                               border=0,align="J",fill=1)    
                pdf.ln(1)
    
        pdf.line(pdf.get_x(),pdf.get_y(),pdf.get_x()+190,pdf.get_y())            
       
    response.headers['Content-Type']='application/pdf'
    return pdf.output(dest='S')

@auth.requires_login()
@auth.requires_membership(role='Responsables')
def warningsTeacher():
    iddepartamentoprofesor = int(request.args[0]) or redirect('default', 'index')
    oaviso = Aviso(db, session)
    avisos = oaviso.dame_avisos_profesor(iddepartamentoprofesor)
    nombreProfesor = avisos[0].profesor.apellidos+', '+avisos[0].profesor.nombre if len(avisos) > 0 else ""
    dni = avisos[0].profesor.dni if len(avisos) > 0 else ""
    dpto = session.profesor.departamento or ""
#    tutor = '%s, %s' % (avisos[0].amonestacion.id_grupo_alumno.id_curso_academico_grupo.id_tutor.apellidos,
#            avisos[0].amonestacion.id_grupo_alumno.id_curso_academico_grupo.id_tutor.nombre) \
#            if (len(avisos) > 0 and avisos[0].amonestacion.id_grupo_alumno.id_curso_academico_grupo.id_tutor) else ''
    logo = os.path.join(request.env.web2py_path,"applications",request.application,"uploads", session.logo_centro)      
    #cad = avisos[0].alumno.foto.split(".")
    #subpath = cad[:2]
    #subpath = os.path.join(".".join(subpath), cad[2][:2])
    #cad = ".".join(cad)
    #foto = os.path.join(request.folder,"uploads",subpath,cad)
    total = len(avisos)
    parte = 0
    comunicadas = 0
    cerradas = 0
    for aviso in avisos:
        if aviso.amonestacion.parte:
            parte+=1
        if aviso.amonestacion.comunicada:
            comunicadas+=1
        if aviso.amonestacion.cerrada:
            cerradas+=1        
    resumen = "Total de partes: "+str(total)+", con parte: "+str(parte)+" comunicadas: "+str(comunicadas)+" cerradas: "+str(cerradas)    
    
    titulo = "Partes del Profesor/a: "+nombreProfesor
    tnombre = "Profesor/a:"
    tdni = "D.N.I.:"
    tdpto = "Dpto.:"
    tcargos = "Funciones:"
    tcentro = session.codigo_centro+' '+session.nombre_centro
    tcurso = session.curso_academico_nombre
    funciones = []
    if session.esResponsable:
        funciones.append("Responsable de Centro")    
    if session.esInformatico:
        funciones.append("Informático")
    if session.esProfesor:
        funciones.append("Profesor")
    if session.profesor.esJefe:
        funciones.append("Jefe de departamento")
    if session.profesor.esTutor:
        funciones.append("Tutor/a "+session.profesor.tutor.curso)
    funciones = ", ".join(funciones)

    class WarningsFPDF(FPDF):
        def header(self): 
            #Arial bold 15
            self.set_font('Arial','B',15)
            #Poner código del centro y nombre el la parte izquierda superior
            self.cell(w=0,h=0,txt=parsestr(tcentro),border=0,ln=0,align='L',fill=0)
            #Ahora el curso académico en la parte derecha superior
            self.cell(w=0,h=0,txt="Curso: "+parsestr(tcurso),border=0,ln=1,align='R',fill=0)
            #Dibujamos una linea de separación
            #self.set_line_width(.5)
            self.line(5,13,205,13)
            #Calcular ancho del texto (titulo) y establecer posición
            w=self.get_string_width(titulo)+6
            self.set_x((210-w)/2)
            #Titulo
            self.cell(w=w,h=17,txt=parsestr(titulo),border=0,ln=1,align='C',fill=0)
            #Linea
            self.line(5,23,205,23)
            #Fuente más pequeña sin bold
            self.set_font('','',8)      
            #Nombre profesor      
            self.cell(w=20,h=0,txt=parsestr(tnombre),border=0,ln=0,align='R',fill=0)
            self.set_font('','B',10)                        
            self.cell(w=20,h=0,txt=parsestr(nombreProfesor),border=0,ln=1,align="L",fill=0)
            
            #Foto alumno
            #self.image(foto,180,25,17,22)
           
            #DNI profesor
            self.set_font('','',8)                        
            self.cell(w=20,h=9,txt=parsestr(tdni),border=0,ln=0,align='R',fill=0)            
            self.set_font('','B',10)                                    
            self.cell(w=20,h=9,txt=parsestr(dni),border=0,ln=1,align="L",fill=0)
            
            #Dpto
            self.set_font('','',8)                                                
            self.cell(w=20,h=0,txt=parsestr(tdpto),border=0,ln=0,align='R',fill=0)
            self.set_font('','B',10)                                                            
            self.cell(w=20,h=0,txt=parsestr(dpto),border=0,ln=1,align="L",fill=0)             

            #Funciones
            self.set_font('','',8)                                                            
            self.cell(w=20,h=9,txt=parsestr(tcargos),border=0,ln=0,align='R',fill=0)            
            self.set_font('','B',10)                                                                        
            self.cell(w=20,h=9,txt=parsestr(funciones),border=0,ln=1,align="L",fill=0)           
            self.line(5,43,205,43)
            self.set_font('','B',9)
            self.cell(w=10,h=1,txt=parsestr("Número"))
            self.cell(10)
            self.cell(w=10,h=1,txt=parsestr("Fecha"))
            self.cell(10)            
            self.cell(w=10,h=1,txt=parsestr("Alumno/a"))
            self.cell(80)            
            self.cell(w=10,h=1,txt=parsestr("Cerrada"))
            self.cell(12)            
            self.cell(w=10,h=1,txt=parsestr("Parte"))
            self.cell(10)           
            self.cell(w=10,h=1,txt=parsestr("Comunicada"))
            self.line(5,48,205,48)
            #Salto de línea
            self.ln(5)           
             
        def footer(self):
            "hook to draw custom page header (printing page numbers)"
            self.line(5,280,205,280)
            self.set_y(-19)
            self.set_font('Arial','I',8)
            self.cell(w=0,h=9,txt=parsestr(titulo),border=0,ln=0,align='L',fill=0)
            marcaid = parsestr(("Impreso por %s a las %s" % (session.auth.user.first_name+" "+session.auth.user.last_name,datetime.datetime.now().strftime("%H:%M:%S %d/%m/%Y"))))
            self.cell(w=0,h=9,txt=marcaid,border=0,ln=1,align='R',fill=0)
            #Resumen
            self.cell(w=0,h=0,txt=parsestr(resumen),ln=0)                        
            txt = parsestr('Página')+' %s de %s' % (self.page_no(), self.alias_nb_pages())
            self.cell(w=0,h=0,txt=txt,border=0,ln=0,align='R',fill=0)
                  
    pdf=WarningsFPDF()
    pdf.alias_nb_pages()
    pdf.add_page()
    pdf.set_font('Arial','',8)
    pdf.set_fill_color(230,230,230)    
    for aviso in avisos:
        pdf.cell(w=10,h=5,txt=parsestr(str(aviso.amonestacion.id)),border=0,ln=0,align="R",fill=0)
        pdf.cell(8)
        pdf.cell(w=10,h=5,txt=aviso.amonestacion.fecha.isoformat())
        pdf.cell(10)
        pdf.cell(w=10,h=5,txt=parsestr(aviso.alumno.apellidos+', '+aviso.alumno.nombre)+" ("+aviso.grupo.grupo+")")
        pdf.cell(85)            
        pdf.cell(w=10,h=5,txt=parsestr("Sí" if aviso.amonestacion.cerrada else "No"))
        pdf.cell(10)            
        pdf.cell(w=10,h=5,txt=parsestr("Sí" if aviso.amonestacion.parte else "No"))
        pdf.cell(15)           
        pdf.cell(w=10,h=5,txt=parsestr("Sí" if aviso.amonestacion.comunicada else "No"),ln=1)
        pdf.cell(19)
        pdf.multi_cell(w=0,h=5,txt=parsestr(aviso.amonestacion.amonestacion),border=0,align="J",fill=1)
        seguimientos = oaviso.dame_seguimientos(aviso.amonestacion.id)
        if len(seguimientos) > 0:
            # aquí debo imprimir los seguimientos del aviso
            pdf.ln(1)
            pdf.line(pdf.get_x()+30,pdf.get_y(),pdf.get_x()+190,pdf.get_y())            
            pdf.cell(30)       
            pdf.cell(w=10,h=5,txt=parsestr("Seguimientos"))
            pdf.cell(23)
            pdf.cell(w=10,h=5,txt=parsestr("Fecha"))
            pdf.cell(20)
            pdf.cell(w=10,h=5,txt=parsestr("Responsable"))        
            pdf.cell(40)            
            pdf.cell(w=10,h=5,txt=parsestr("Seguimiento"),ln=1)
            pdf.line(pdf.get_x()+30,pdf.get_y(),pdf.get_x()+190,pdf.get_y())
            pdf.ln(1)
            for seguimiento in seguimientos:
                pdf.cell(60)
                pdf.cell(w=10,h=4,txt=parsestr(seguimiento.seguimiento.fecha.isoformat()))       
                pdf.cell(10)
                pdf.cell(w=10,h=4,txt=parsestr(seguimiento.profesor.apellidos+", "+seguimiento.profesor.nombre))    
                pdf.cell(40)
                pdf.multi_cell(w=60,h=4,txt=parsestr(seguimiento.seguimiento.seguimiento),border=0,align="J",fill=1)    
                pdf.ln(1)
    
        pdf.line(pdf.get_x(),pdf.get_y(),pdf.get_x()+190,pdf.get_y())            
        
    
    response.headers['Content-Type']='application/pdf'
    return pdf.output(dest='S')


@auth.requires_login()
@auth.requires_membership(role='Responsables')
def absentismosTeacher():
    iddepartamentoprofesor = int(request.args[0]) or redirect('default', 'index')
    oaviso = Absentismo(db, session)
    avisos = oaviso.dame_absentismos_profesor(iddepartamentoprofesor)
    nombreProfesor = avisos[0].profesor.apellidos+', '+avisos[0].profesor.nombre if len(avisos) > 0 else ""
    dni = avisos[0].profesor.dni if len(avisos) > 0 else ""
    dpto = session.profesor.departamento or ""
#    tutor = '%s, %s' % (avisos[0].amonestacion.id_grupo_alumno.id_curso_academico_grupo.id_tutor.apellidos,
#            avisos[0].amonestacion.id_grupo_alumno.id_curso_academico_grupo.id_tutor.nombre) \
#            if (len(avisos) > 0 and avisos[0].amonestacion.id_grupo_alumno.id_curso_academico_grupo.id_tutor) else ''
    logo = os.path.join(request.env.web2py_path,"applications",request.application,"uploads", session.logo_centro)      
    #cad = avisos[0].alumno.foto.split(".")
    #subpath = cad[:2]
    #subpath = os.path.join(".".join(subpath), cad[2][:2])
    #cad = ".".join(cad)
    #foto = os.path.join(request.folder,"uploads",subpath,cad)
    total = len(avisos)
    comunicadas = 0
    for aviso in avisos:
        if aviso.amonestacion_absentismo.comunicada:
            comunicadas+=1
    resumen = "Total de partes: "+str(total)+", comunicadas: "+str(comunicadas)
    
    titulo = "Absentismos pasivos emitidos por el Profesor/a: "+nombreProfesor
    tnombre = "Profesor/a:"
    tdni = "D.N.I.:"
    tdpto = "Dpto.:"
    tcargos = "Funciones:"
    tcentro = session.codigo_centro+' '+session.nombre_centro
    tcurso = session.curso_academico_nombre
    funciones = []
    if session.esResponsable:
        funciones.append("Responsable de Centro")    
    if session.esInformatico:
        funciones.append("Informático")
    if session.esProfesor:
        funciones.append("Profesor")
    if session.profesor.esJefe:
        funciones.append("Jefe de departamento")
    if session.profesor.esTutor:
        funciones.append("Tutor/a "+session.profesor.tutor.curso)
    funciones = ", ".join(funciones)

    class AbsentismosFPDF(FPDF):
        def header(self): 
            #Arial bold 15
            self.set_font('Arial','B',15)
            #Poner código del centro y nombre el la parte izquierda superior
            self.cell(w=0,h=0,txt=parsestr(tcentro),border=0,ln=0,align='L',fill=0)
            #Ahora el curso académico en la parte derecha superior
            self.cell(w=0,h=0,txt="Curso: "+parsestr(tcurso),border=0,ln=1,align='R',fill=0)
            #Dibujamos una linea de separación
            #self.set_line_width(.5)
            self.line(5,13,205,13)
            #Calcular ancho del texto (titulo) y establecer posición
            w=self.get_string_width(titulo)+6
            self.set_x((210-w)/2)
            #Titulo
            self.cell(w=w,h=17,txt=parsestr(titulo),border=0,ln=1,align='C',fill=0)
            #Linea
            self.line(5,23,205,23)
            #Fuente más pequeña sin bold
            self.set_font('','',8)      
            #Nombre profesor      
            self.cell(w=20,h=0,txt=parsestr(tnombre),border=0,ln=0,align='R',fill=0)
            self.set_font('','B',10)                        
            self.cell(w=20,h=0,txt=parsestr(nombreProfesor),border=0,ln=1,align="L",fill=0)
            
            #Foto alumno
            #self.image(foto,180,25,17,22)
           
            #DNI profesor
            self.set_font('','',8)                        
            self.cell(w=20,h=9,txt=parsestr(tdni),border=0,ln=0,align='R',fill=0)            
            self.set_font('','B',10)                                    
            self.cell(w=20,h=9,txt=parsestr(dni),border=0,ln=1,align="L",fill=0)
            
            #Dpto
            self.set_font('','',8)                                                
            self.cell(w=20,h=0,txt=parsestr(tdpto),border=0,ln=0,align='R',fill=0)
            self.set_font('','B',10)                                                            
            self.cell(w=20,h=0,txt=parsestr(dpto),border=0,ln=1,align="L",fill=0)             

            #Funciones
            self.set_font('','',8)                                                            
            self.cell(w=20,h=9,txt=parsestr(tcargos),border=0,ln=0,align='R',fill=0)            
            self.set_font('','B',10)                                                                        
            self.cell(w=20,h=9,txt=parsestr(funciones),border=0,ln=1,align="L",fill=0)           
            self.line(5,43,205,43)
            self.set_font('','B',9)
            self.cell(w=10,h=1,txt=parsestr("Número"))
            self.cell(10)
            self.cell(w=10,h=1,txt=parsestr("Fecha"))
            self.cell(10)            
            self.cell(w=10,h=1,txt=parsestr("Alumno/a"))
            self.cell(45)            
            self.cell(w=10,h=1,txt=parsestr("Comunicada"))
            self.line(5,48,205,48)
            #Salto de línea
            self.ln(5)           
             
        def footer(self):
            "hook to draw custom page header (printing page numbers)"
            self.line(5,280,205,280)
            self.set_y(-19)
            self.set_font('Arial','I',8)
            self.cell(w=0,h=9,txt=parsestr(titulo),border=0,ln=0,align='L',fill=0)
            marcaid = parsestr(("Impreso por %s a las %s" % (session.auth.user.first_name+" "+session.auth.user.last_name,datetime.datetime.now().strftime("%H:%M:%S %d/%m/%Y"))))
            self.cell(w=0,h=9,txt=marcaid,border=0,ln=1,align='R',fill=0)
            #Resumen
            self.cell(w=0,h=0,txt=parsestr(resumen),ln=0)                        
            txt = parsestr('Página')+' %s de %s' % (self.page_no(), self.alias_nb_pages())
            self.cell(w=0,h=0,txt=txt,border=0,ln=0,align='R',fill=0)
                  
    pdf=AbsentismosFPDF()
    pdf.alias_nb_pages()
    pdf.add_page()
    pdf.set_font('Arial','',8)
    pdf.set_fill_color(230,230,230)    
    for aviso in avisos:
        pdf.cell(w=10,h=5,txt=parsestr(str(aviso.amonestacion_absentismo.id)),border=0,ln=0,align="R",fill=0)
        pdf.cell(8)
        pdf.cell(w=10,h=5,txt=aviso.amonestacion_absentismo.fecha.isoformat())
        pdf.cell(10)
        pdf.cell(w=10,h=5,txt=parsestr(aviso.alumno.apellidos+', '+aviso.alumno.nombre)+" ("+aviso.grupo.grupo+")")
        pdf.cell(50)            
        pdf.cell(w=10,h=5,txt=parsestr("Sí" if aviso.amonestacion_absentismo.comunicada else "No"))
        pdf.cell(10)
        pdf.multi_cell(w=0,h=5,txt=parsestr(aviso.amonestacion_absentismo.absentismo),border=0,align="J",fill=1)
        pdf.line(pdf.get_x(),pdf.get_y(),pdf.get_x()+190,pdf.get_y())            
    
    response.headers['Content-Type']='application/pdf'
    return pdf.output(dest='S')

@auth.requires_login()
@auth.requires_membership(role='Responsables')
def absentismosTeacher():
    iddepartamentoprofesor = int(request.args[0]) or redirect('default', 'index')
    oaviso = Absentismo(db, session)
    avisos = oaviso.dame_absentismos_profesor(iddepartamentoprofesor)
    nombreProfesor = avisos[0].profesor.apellidos+', '+avisos[0].profesor.nombre if len(avisos) > 0 else ""
    dni = avisos[0].profesor.dni if len(avisos) > 0 else ""
    dpto = session.profesor.departamento or ""
#    tutor = '%s, %s' % (avisos[0].amonestacion.id_grupo_alumno.id_curso_academico_grupo.id_tutor.apellidos,
#            avisos[0].amonestacion.id_grupo_alumno.id_curso_academico_grupo.id_tutor.nombre) \
#            if (len(avisos) > 0 and avisos[0].amonestacion.id_grupo_alumno.id_curso_academico_grupo.id_tutor) else ''
    logo = os.path.join(request.env.web2py_path,"applications",request.application,"uploads", session.logo_centro)      
    #cad = avisos[0].alumno.foto.split(".")
    #subpath = cad[:2]
    #subpath = os.path.join(".".join(subpath), cad[2][:2])
    #cad = ".".join(cad)
    #foto = os.path.join(request.folder,"uploads",subpath,cad)
    total = len(avisos)
    comunicadas = 0
    for aviso in avisos:
        if aviso.amonestacion_absentismo.comunicada:
            comunicadas+=1
    resumen = "Total de partes: "+str(total)+", comunicadas: "+str(comunicadas)
    
    titulo = "Absentismos pasivos emitidos por el Profesor/a: "+nombreProfesor
    tnombre = "Profesor/a:"
    tdni = "D.N.I.:"
    tdpto = "Dpto.:"
    tcargos = "Funciones:"
    tcentro = session.codigo_centro+' '+session.nombre_centro
    tcurso = session.curso_academico_nombre
    funciones = []
    if session.esResponsable:
        funciones.append("Responsable de Centro")    
    if session.esInformatico:
        funciones.append("Informático")
    if session.esProfesor:
        funciones.append("Profesor")
    if session.profesor.esJefe:
        funciones.append("Jefe de departamento")
    if session.profesor.esTutor:
        funciones.append("Tutor/a "+session.profesor.tutor.curso)
    funciones = ", ".join(funciones)

    class AbsentismosFPDF(FPDF):
        def header(self): 
            #Arial bold 15
            self.set_font('Arial','B',15)
            #Poner código del centro y nombre el la parte izquierda superior
            self.cell(w=0,h=0,txt=parsestr(tcentro),border=0,ln=0,align='L',fill=0)
            #Ahora el curso académico en la parte derecha superior
            self.cell(w=0,h=0,txt="Curso: "+parsestr(tcurso),border=0,ln=1,align='R',fill=0)
            #Dibujamos una linea de separación
            #self.set_line_width(.5)
            self.line(5,13,205,13)
            #Calcular ancho del texto (titulo) y establecer posición
            w=self.get_string_width(titulo)+6
            self.set_x((210-w)/2)
            #Titulo
            self.cell(w=w,h=17,txt=parsestr(titulo),border=0,ln=1,align='C',fill=0)
            #Linea
            self.line(5,23,205,23)
            #Fuente más pequeña sin bold
            self.set_font('','',8)      
            #Nombre profesor      
            self.cell(w=20,h=0,txt=parsestr(tnombre),border=0,ln=0,align='R',fill=0)
            self.set_font('','B',10)                        
            self.cell(w=20,h=0,txt=parsestr(nombreProfesor),border=0,ln=1,align="L",fill=0)
            
            #Foto alumno
            #self.image(foto,180,25,17,22)
           
            #DNI profesor
            self.set_font('','',8)                        
            self.cell(w=20,h=9,txt=parsestr(tdni),border=0,ln=0,align='R',fill=0)            
            self.set_font('','B',10)                                    
            self.cell(w=20,h=9,txt=parsestr(dni),border=0,ln=1,align="L",fill=0)
            
            #Dpto
            self.set_font('','',8)                                                
            self.cell(w=20,h=0,txt=parsestr(tdpto),border=0,ln=0,align='R',fill=0)
            self.set_font('','B',10)                                                            
            self.cell(w=20,h=0,txt=parsestr(dpto),border=0,ln=1,align="L",fill=0)             

            #Funciones
            self.set_font('','',8)                                                            
            self.cell(w=20,h=9,txt=parsestr(tcargos),border=0,ln=0,align='R',fill=0)            
            self.set_font('','B',10)                                                                        
            self.cell(w=20,h=9,txt=parsestr(funciones),border=0,ln=1,align="L",fill=0)           
            self.line(5,43,205,43)
            self.set_font('','B',9)
            self.cell(w=10,h=1,txt=parsestr("Número"))
            self.cell(10)
            self.cell(w=10,h=1,txt=parsestr("Fecha"))
            self.cell(10)            
            self.cell(w=10,h=1,txt=parsestr("Alumno/a"))
            self.cell(45)            
            self.cell(w=10,h=1,txt=parsestr("Comunicada"))
            self.line(5,48,205,48)
            #Salto de línea
            self.ln(5)           
             
        def footer(self):
            "hook to draw custom page header (printing page numbers)"
            self.line(5,280,205,280)
            self.set_y(-19)
            self.set_font('Arial','I',8)
            self.cell(w=0,h=9,txt=parsestr(titulo),border=0,ln=0,align='L',fill=0)
            marcaid = parsestr(("Impreso por %s a las %s" % (session.auth.user.first_name+" "+session.auth.user.last_name,datetime.datetime.now().strftime("%H:%M:%S %d/%m/%Y"))))
            self.cell(w=0,h=9,txt=marcaid,border=0,ln=1,align='R',fill=0)
            #Resumen
            self.cell(w=0,h=0,txt=parsestr(resumen),ln=0)                        
            txt = parsestr('Página')+' %s de %s' % (self.page_no(), self.alias_nb_pages())
            self.cell(w=0,h=0,txt=txt,border=0,ln=0,align='R',fill=0)
                  
    pdf=AbsentismosFPDF()
    pdf.alias_nb_pages()
    pdf.add_page()
    pdf.set_font('Arial','',8)
    pdf.set_fill_color(230,230,230)    
    for aviso in avisos:
        pdf.cell(w=10,h=5,txt=parsestr(str(aviso.amonestacion_absentismo.id)),border=0,ln=0,align="R",fill=0)
        pdf.cell(8)
        pdf.cell(w=10,h=5,txt=aviso.amonestacion_absentismo.fecha.isoformat())
        pdf.cell(10)
        pdf.cell(w=10,h=5,txt=parsestr(aviso.alumno.apellidos+', '+aviso.alumno.nombre)+" ("+aviso.grupo.grupo+")")
        pdf.cell(50)            
        pdf.cell(w=10,h=5,txt=parsestr("Sí" if aviso.amonestacion_absentismo.comunicada else "No"))
        pdf.cell(10)
        pdf.multi_cell(w=0,h=5,txt=parsestr(aviso.amonestacion_absentismo.absentismo),border=0,align="J",fill=1)
        pdf.line(pdf.get_x(),pdf.get_y(),pdf.get_x()+190,pdf.get_y())            
    
    response.headers['Content-Type']='application/pdf'
    return pdf.output(dest='S')


@auth.requires_login()
@auth.requires_membership(role='Profesores')
def hojasevaluacion():
    idevaluacion = int(request.args[-2]) or redirect('default', 'index')
    idgrupoprofesortutoria = int(request.args[-1]) or redirect('default', 'index')
    # comprobemos que somos reponsables o tutor del grupo
    if not session.esResponsable:
        if not session.profesor.esTutor or idgrupoprofesortutoria <> session.profesor.tutor.id_curso_academico_grupo:
            redirect(URL("default","index"))

    oevaluacion = Evaluacion(db, session)
    evaluaciones = oevaluacion.dame_evaluacion_alumnos_tutoria(idevaluacion, idgrupoprofesortutoria)
    if len(evaluaciones) == 0:
        return "No hay datos"
    #db.evaluacion_alumno.nivel.represent = lambda nivel:{100:"Sobresaliente 10",90:"Sobresaliente 9",
    #                                                 80:"Notable 8",70:"Notable 7",60:"Bien",
    #                                                 50:"Suficiente",40:"Insuficiente 4",
    #                                                 30:"Insuficiente 3",20:"Insuficiente 2",
    #                                                 10:"Insuficiente 1",0:"Abandono"}[nivel]
    db.evaluacion_alumno.trabajo_clase.represent = lambda trabajo_clase:{100:"Habitualmente",75:"A veces",
                                                     50:"Casi nunca",0:"Nunca"}[trabajo_clase]                                                     
    db.evaluacion_alumno.trabajo_casa.represent = lambda trabajo_casa:{100:"Habitualmente",75:"A veces",
                                                     50:"Casi nunca",0:"Nunca"}[trabajo_casa]                                                                                                          
    db.evaluacion_alumno.interes.represent = lambda interes:{100:"Mucho",75:"Normal",
                                                     50:"Poco",0:"Nada"}[interes]
    db.evaluacion_alumno.participa.represent = lambda participa:{100:"Mucho",75:"Normal",
                                                     50:"Poco",0:"Nada"}[participa]
    db.evaluacion_alumno.comportamiento.represent = lambda comportamiento:{100:"Muy bueno",75:"Bueno",
                                                     50:"Puede mejorar",0:"Disruptivo"}[comportamiento]      

    logo = os.path.join(request.env.web2py_path,"applications",request.application,"uploads", session.logo_centro)      
    titulo = "Hoja de evaluación individualizada ("+evaluaciones[0].curso_academico_evaluacion.evaluacion+")"
    tnombre = "Alumno/a:"
    tnie = "N.I.E.:"
    tgrupo = "Grupo:"
    ttutor = "Tutor:"
    tcentro = session.codigo_centro+' '+session.nombre_centro
    tcurso = session.curso_academico_nombre
    tutor = db.curso_academico_grupo(idgrupoprofesortutoria).id_tutor.apellidos+", "+db.curso_academico_grupo(idgrupoprofesortutoria).id_tutor.nombre
    class evaluacionalumnoPDF(FPDF):
        def header(self):
            self.set_font('Arial','B',15)
            #Logo del centro
            self.image(logo,5,5,20,20)
            #Poner código del centro y nombre el la parte izquierda superior
            self.cell(15)
            self.cell(w=0,h=0,txt=parsestr(tcentro),border=0,ln=0,align='L',fill=0)
            #Ahora el curso académico en la parte derecha superior
            self.cell(w=0,h=0,txt="Curso: "+parsestr(tcurso),border=0,ln=1,align='R',fill=0)
            #Dibujamos una linea de separación
            #self.set_line_width(.5)
            #pdf.line(5,13,205,13)
            #Calcular ancho del texto (titulo) y establecer posición
            w=self.get_string_width(titulo)+6
            self.set_x((297-w)/2)
            #Titulo
            self.cell(w=w,h=17,txt=parsestr(titulo),border=0,ln=1,align='C',fill=0)
            #Linea
            self.line(5,23,290,23)
    
    pdf=evaluacionalumnoPDF('L','mm','A4')
    pdf.alias_nb_pages()
    #pdf.add_page()
    pdf.set_font('Arial','',8)
    pdf.set_fill_color(230,230,230)    
    nie = None
    for evaluacion in evaluaciones:
        # es el primer alumno o bien se ha cambiado de alumno
        if nie <> evaluacion.alumno.nie:
            # ha cambiado el alumno y hay que imprimir las observaciones del anterior
            if nie <> None: 
                # imprime las estadísticas del alumno
                imprime_estadistica_alumno(pdf,nl,sumanivel,sumatrclase,sumatrcasa,sumainteres,sumaparticipa,sumacompor,sumaeval,grafico)
                # imprime las observaciones
                imprime_hoja_observaciones(pdf,tnombre,tnie,tgrupo,ttutor,observaciones,foto,nombreAlumno,nie,grupo,tutor)
            # contador de lineas
            nl = 1
            sumanivel = 0
            sumatrclase = 0
            sumatrcasa = 0
            sumainteres = 0
            sumaparticipa = 0
            sumacompor = 0
            sumaeval = 0      
            # inicializamos las observaciones
            observaciones = {}

            grafico = {}
            # ha cambiado el alumno, hemos de saltar la página
            pdf.add_page()
            nie = evaluacion.alumno.nie
            # imprimiremos la foto del alumno y su nombre
            #Fuente más pequeña sin bold
            pdf.set_font('','',8)      
            #Nombre alumno      
            nombreAlumno = evaluacion.alumno.apellidos+', '+evaluacion.alumno.nombre
            nie = evaluacion.alumno.nie
            grupo = evaluacion.grupo.grupo
            cad = evaluacion.alumno.foto.split(".")
            subpath = cad[:2]
            subpath = os.path.join(".".join(subpath), cad[2][:2])
            cad = ".".join(cad)
            foto = os.path.join(request.folder,"uploads",subpath,cad)
            
            pdf.cell(w=20,h=0,txt=parsestr(tnombre),border=0,ln=0,align='R',fill=0)
            pdf.set_font('','B',10)                        
            pdf.cell(w=20,h=0,txt=parsestr(nombreAlumno),border=0,ln=1,align="L",fill=0)
            
            #Foto alumno
            try:
                pdf.image(foto,260,24,17,20)
            except:
                pass
            
            #Nie alumno
            pdf.set_font('','',8)                        
            pdf.cell(w=20,h=9,txt=parsestr(tnie),border=0,ln=0,align='R',fill=0)            
            pdf.set_font('','B',10)                                    
            pdf.cell(w=20,h=9,txt=parsestr(nie),border=0,ln=1,align="L",fill=0)

            #Grupo
            pdf.set_font('','',8)                        
            pdf.cell(w=20,h=0,txt=parsestr(tgrupo),border=0,ln=0,align='R',fill=0)            
            pdf.set_font('','B',10)                                    
            pdf.cell(w=20,h=0,txt=parsestr(grupo),border=0,ln=1,align="L",fill=0)

            #Tutor
            pdf.set_font('','',8)                        
            pdf.cell(w=20,h=9,txt=parsestr(ttutor),border=0,ln=0,align='R',fill=0)            
            pdf.set_font('','B',10)                                    
            pdf.cell(w=20,h=9,txt=parsestr(tutor),border=0,ln=1,align="L",fill=0)
            
            pdf.line(5,45,290,45)
            pdf.set_font('','B',9)
            pdf.cell(w=10,h=9,txt=parsestr("Asignatura"))
            pdf.cell(75)
            pdf.line(75,50,160,50)
            pdf.cell(w=10,h=5,txt=parsestr("Aspectos académicos"))
            pdf.cell(85)            
            pdf.cell(w=10,h=5,txt=parsestr("Aspectos actitudinales"))
            pdf.line(170,50,250,50)
            pdf.cell(20)            
            pdf.cell(w=0,h=9,txt=parsestr("Total asignatura"),align="R")
            pdf.ln(7)
            pdf.cell(70)            
            pdf.cell(w=10,h=0,txt=parsestr("Nivel"))
            pdf.cell(8)           
            pdf.cell(w=10,h=0,txt=parsestr("Trabajo en clase"))
            pdf.cell(20)           
            pdf.cell(w=10,h=0,txt=parsestr("Trabajo en casa"))
            pdf.cell(40)           
            pdf.cell(w=10,h=0,txt=parsestr("Interés"))
            pdf.cell(10)           
            pdf.cell(w=10,h=0,txt=parsestr("Participa"))
            pdf.cell(10)           
            pdf.cell(w=10,h=0,txt=parsestr("Comportamiento"))
            pdf.line(5,54,290,54)
            
            
            
            #pdf.line(5,53,205,53)
            #Salto de línea
            pdf.ln(5)

        if nl % 2 <> 0:
            # imprimimos relleno de fondo
            fill = 1
        else:
            fill = 0

        pdf.set_fill_color(230,230,230)    
        pdf.set_font('','',8)                        
        #asignatura = evaluacion.asignatura.asignatura+" ("+evaluacion.asignatura.abreviatura+")"
        asignatura = evaluacion.asignatura.asignatura[:46-len(evaluacion.asignatura.abreviatura)]+" ("+evaluacion.asignatura.abreviatura+")"
        pdf.cell(w=50,h=5,txt=parsestr(str(asignatura)),border=0,ln=0,align="L",fill=fill)
        pdf.cell(10,h=5,fill=fill)
        if evaluacion.evaluacion_alumno.nivel < 5.0:
            nivel = T('Insuficiente')
        elif evaluacion.evaluacion_alumno.nivel >= 5 and evaluacion.evaluacion_alumno.nivel < 6.0:
            nivel = T('Suficiente')
        elif evaluacion.evaluacion_alumno.nivel >= 6 and evaluacion.evaluacion_alumno.nivel < 7.0:
            nivel = T('Bien')
        elif evaluacion.evaluacion_alumno.nivel >= 7 and evaluacion.evaluacion_alumno.nivel < 9.0:
            nivel = T('Notable')
        elif evaluacion.evaluacion_alumno.nivel >= 9 and evaluacion.evaluacion_alumno.nivel <= 10.0:
            nivel = T('Sobresaliente')
        else:
            nivel = T('No relación')
        #rep = db.evaluacion_alumno["nivel"].represent
        #if rep:
        #    nivel = rep(evaluacion.evaluacion_alumno.nivel)
        #else:
        #    nivel = evaluacion.evaluacion_alumno.nivel
        nivel += ' ('+str(evaluacion.evaluacion_alumno.nivel)+')'    
        pdf.cell(w=30,h=5,txt=parsestr(str(nivel)),align="C",fill=fill)
        rep = db.evaluacion_alumno["trabajo_clase"].represent
        if rep:
            trabajo_clase = rep(evaluacion.evaluacion_alumno.trabajo_clase)
        else:
            trabajo_clase = evaluacion.evaluacion_alumno.trabajo_clase       
        pdf.cell(w=25,h=5,txt=parsestr(str(trabajo_clase)),align="C",fill=fill)
        rep = db.evaluacion_alumno["trabajo_casa"].represent
        if rep:
            trabajo_casa = rep(evaluacion.evaluacion_alumno.trabajo_casa)
        else:
            trabajo_casa = evaluacion.evaluacion_alumno.trabajo_casa
        pdf.cell(w=30,h=5,txt=parsestr(str(trabajo_casa)),align="C",fill=fill)
        pdf.cell(20,h=5,fill=fill)
        rep = db.evaluacion_alumno["interes"].represent
        if rep:
            interes = rep(evaluacion.evaluacion_alumno.interes)
        else:
            interes = evaluacion.evaluacion_alumno.interes                    
        pdf.cell(w=20,h=5,txt=parsestr(str(interes)),align="C",fill=fill)
        #pdf.cell(10,fill=fill)
        rep = db.evaluacion_alumno["participa"].represent
        if rep:
            participa = rep(evaluacion.evaluacion_alumno.participa)
        else:
            participa = evaluacion.evaluacion_alumno.participa            
        pdf.cell(w=20,h=5,txt=parsestr(str(participa)),align="C",fill=fill)
        #pdf.cell(15,fill=fill)
        rep = db.evaluacion_alumno["comportamiento"].represent
        if rep:
            comportamiento = rep(evaluacion.evaluacion_alumno.comportamiento)
        else:
            comportamiento = evaluacion.evaluacion_alumno.comportamiento         
                   
        pdf.cell(w=30,h=5,txt=parsestr(str(comportamiento)),align="C",fill=fill)
        pdf.cell(w=10,h=5,fill=fill)
        pdf.set_fill_color(200,200,200)           
        pdf.set_font('','B',9)
        border = "TLR" if nl == 1 else "LR"                   
        pdf.cell(w=0,h=5,txt=parsestr(str(evaluacion.evaluacion_alumno.evaluacion)),border=border,align="R",fill=1,ln=1)
        
        # aumentamos el contador de linea
        nl += 1
        # aumentamos estadisticas alumno
        sumanivel += evaluacion.evaluacion_alumno.nivel
        sumatrclase += evaluacion.evaluacion_alumno.trabajo_clase
        sumatrcasa += evaluacion.evaluacion_alumno.trabajo_casa
        sumainteres += evaluacion.evaluacion_alumno.interes
        sumaparticipa += evaluacion.evaluacion_alumno.participa
        sumacompor += evaluacion.evaluacion_alumno.comportamiento
        sumaeval += evaluacion.evaluacion_alumno.evaluacion

        grafico[evaluacion.asignatura.abreviatura] = evaluacion.evaluacion_alumno.evaluacion

        # actualizamos las observaciones
        observaciones[evaluacion.asignatura.asignatura] = evaluacion.evaluacion_alumno.observaciones
    
    # estadistica del último alumno
    imprime_estadistica_alumno(pdf,nl,sumanivel,sumatrclase,sumatrcasa,sumainteres,sumaparticipa,sumacompor,sumaeval,grafico)
    # observaciones del último alumno
    imprime_hoja_observaciones(pdf,tnombre,tnie,tgrupo,ttutor,observaciones,foto,nombreAlumno,nie,grupo,tutor)
       
    response.headers['Content-Type']='application/pdf'
    return pdf.output(dest='S')

def imprime_hoja_observaciones(pdf,tnombre,tnie,tgrupo,ttutor,observaciones,foto,nombreAlumno,nie,grupo,tutor):
    pdf.add_page()
    #Fuente más pequeña sin bold
    pdf.set_font('','',8)      
    #Nombre alumno      
    pdf.cell(w=20,h=0,txt=parsestr(tnombre),border=0,ln=0,align='R',fill=0)
    pdf.set_font('','B',10)                        
    pdf.cell(w=20,h=0,txt=parsestr(nombreAlumno),border=0,ln=1,align="L",fill=0)
    #Foto alumno
    try:
        pdf.image(foto,260,24,17,20)
    except:
        pass
    #Nie alumno
    pdf.set_font('','',8)                        
    pdf.cell(w=20,h=9,txt=parsestr(tnie),border=0,ln=0,align='R',fill=0)            
    pdf.set_font('','B',10)                                    
    pdf.cell(w=20,h=9,txt=parsestr(nie),border=0,ln=1,align="L",fill=0)
    #Grupo
    pdf.set_font('','',8)                        
    pdf.cell(w=20,h=0,txt=parsestr(tgrupo),border=0,ln=0,align='R',fill=0)            
    pdf.set_font('','B',10)                                    
    pdf.cell(w=20,h=0,txt=parsestr(grupo),border=0,ln=1,align="L",fill=0)
    #Tutor
    pdf.set_font('','',8)                        
    pdf.cell(w=20,h=9,txt=parsestr(ttutor),border=0,ln=0,align='R',fill=0)            
    pdf.set_font('','B',10)                                    
    pdf.cell(w=20,h=9,txt=parsestr(tutor),border=0,ln=1,align="L",fill=0)

    pdf.line(5,45,290,45)
    pdf.set_font('','B',9)
    pdf.cell(w=10,h=9,txt=parsestr("Asignatura"))
    pdf.cell(75)
    pdf.cell(w=0,h=9,txt=parsestr("Observaciones"))
    pdf.ln(7)
    pdf.line(5,54,290,54)

    pdf.ln(5)

    pdf.set_fill_color(230,230,230)    
    
    nl = 1
    for observacion in observaciones.keys():
        if nl % 2 <> 0:
            # imprimimos relleno de fondo
            fill = 1
        else:
            fill = 0
        pdf.set_font('','',8)                        
        pdf.cell(w=50,h=5,txt=parsestr(str(observacion)),border=0,ln=0,align="L",fill=fill)
        pdf.cell(10,h=5,fill=fill)
        pdf.cell(w=0,h=5,txt=parsestr(str(observaciones[observacion])),ln=1,align="L",fill=fill)
        # aumentamos el contador de linea
        nl += 1
        
    pdf.ln(15)
    pdf.set_font('','',9)
    pdf.cell(180)
    import locale
    locale.setlocale(locale.LC_TIME, "es_ES.UTF8") # español
    fecha = parsestr(("En Monesterio a %s" % (datetime.datetime.now().strftime("%d de %B de %Y"))))    
    pdf.cell(w=0,h=5,txt=parsestr(str(fecha)),border=0,ln=0,align="L")
    pdf.ln(20)
    pdf.cell(190)
    pdf.cell(w=0,h=5,txt=parsestr(str("El tutor/a")),border=0,ln=0,align="L")

def genera_grafico_asignaturas_1(fichero, datos):
    chart = GroupedVerticalBarChart(75*len(datos.keys()), 150, y_range=(0, 10))
    chart.set_title(title="Por asignaturas")
    chart.set_grid(x_step = 0, y_step = 10)
    chart.set_bar_width(20)
    chart.set_colours(['dddddd'])
    chart.add_data([float(x) for x in datos.values()])
    chart.set_axis_labels(Axis.LEFT, xrange(0,11))
    chart.set_axis_labels(Axis.BOTTOM, [clave for clave in datos.keys()])
    chart.download(fichero)

def genera_grafico_asignaturas(fichero, datos):
    lista = [[k, datos[k]] for k in datos.keys()]
    lista.sort(key=lambda tup: tup[0])
    width = 75*len(lista)
    if width > 1000:
        width = 1000    
    chart = GroupedVerticalBarChart(width, 150, y_range=(0, 10))
    chart.set_title(title="Por asignaturas")
    chart.set_grid(x_step = 0, y_step = 10)
    chart.set_bar_width(20)
    chart.set_colours(['dddddd'])
    chart.add_data([float(x[1]) for x in lista])
    chart.set_axis_labels(Axis.LEFT, xrange(0,11))
    chart.set_axis_labels(Axis.BOTTOM, [k[0] for k in lista])
    chart.download(fichero)


def genera_grafico_aspectos_1(fichero, datos):
    chart = GroupedVerticalBarChart(75*len(datos.keys()), 150, y_range=(0, 10))
    chart.set_title(title="Por aspectos")        
    chart.set_grid(x_step = 0, y_step = 10)
    chart.set_bar_width(20)
    chart.set_colours(['dddddd'])
    chart.add_data([float(x) for x in datos.values()])
    chart.set_axis_labels(Axis.LEFT, xrange(0,11))
    chart.set_axis_labels(Axis.BOTTOM, [clave for clave in datos.keys()])
    chart.download(fichero)

def genera_grafico_aspectos(fichero, datos):
    lista = [["NIV", datos["NIV"]], ["TCL", datos["TCL"]], ["TCA", datos["TCA"]],
             ["INT", datos["INT"]], ["PAR", datos["PART"]], ["COM", datos["COMP"]]]
    chart = GroupedVerticalBarChart(75*len(lista), 150, y_range=(0, 10))
    chart.set_title(title="Por aspectos")        
    chart.set_grid(x_step = 0, y_step = 10)
    chart.set_bar_width(20)
    chart.set_colours(['dddddd'])
    chart.add_data([float(x[1]) for x in lista])
    chart.set_axis_labels(Axis.LEFT, xrange(0,11))
    chart.set_axis_labels(Axis.BOTTOM, [k[0] for k in lista])
    chart.download(fichero)


def imprime_estadistica_alumno(pdf,nl,sumanivel,sumatrclase,sumatrcasa,sumainteres,sumaparticipa,sumacompor,sumaeval,grafico):
    pdf.set_fill_color(200,200,200)    
    pdf.set_font('','B',9)                        
    pdf.cell(w=50,h=5,txt=parsestr(str("Estadísticas del alumno/a")),border="LTB",ln=0,align="L",fill=1)
    pdf.cell(10,h=5,border="TB",fill=1)
    nivel = float(sumanivel)/float(nl-1)
    pdf.cell(w=30,h=5,txt=parsestr(str('%.02f' % nivel)),border="TB",align="C",fill=1)
    trabajo_clase = (sumatrclase/float(nl-1))/float(10)       
    pdf.cell(w=25,h=5,txt=parsestr(str('%.02f' % trabajo_clase)),border="TB",align="C",fill=1)
    trabajo_casa = (sumatrcasa/float(nl-1))/float(10)
    pdf.cell(w=30,h=5,txt=parsestr(str('%.02f' % trabajo_casa)),border="TB",align="C",fill=1)
    pdf.cell(20,h=5,border="TB",fill=1)
    interes = (sumainteres/float(nl-1))/float(10)
    pdf.cell(w=20,h=5,txt=parsestr(str('%.02f' % interes)),border="TB",align="C",fill=1)
    participa = (sumaparticipa/float(nl-1))/float(10)
    pdf.cell(w=20,h=5,txt=parsestr(str('%.02f' % participa)),border="TB",align="C",fill=1)
    comportamiento = (sumacompor/float(nl-1))/float(10)
    pdf.cell(w=30,h=5,txt=parsestr(str('%.02f' % comportamiento)),border="TB",align="C",fill=1)
    pdf.cell(w=10,h=5,border="TB",fill=1)
    evaluacion = (sumaeval/(nl-1))
    pdf.set_font('','B',10)                            
    pdf.cell(w=0,h=5,txt=parsestr(str('%.02f' % evaluacion)),border=1,align="R",fill=1)
    fichero=os.path.join(request.folder,"uploads",str(uuid.uuid4())+".png") 
    genera_grafico_asignaturas(fichero, grafico)
    graf = os.path.join(fichero)
    pdf.image(graf,10,150)    
    os.unlink(graf)
    fichero=os.path.join(request.folder,"uploads",str(uuid.uuid4())+".png") 
    genera_grafico_aspectos(fichero, {"NIV":nivel, "TCL":trabajo_clase,
                                      "TCA":trabajo_casa, "INT":interes,
                                      "PART":participa, "COMP":comportamiento})
    graf = os.path.join(fichero)
    pdf.image(graf,200,150)    
    os.unlink(graf)
    
@auth.requires_login()
@auth.requires_membership(role='Profesores')
def informeevaluacion():
    idevaluacion = int(request.args[-2]) or redirect('default', 'index')    
    idgrupoprofesortutoria = int(request.args[-1]) or redirect('default', 'index')
    # comprobemos que somos reponsables o tutor del grupo
    if not session.esResponsable:
        if not session.profesor.esTutor or idgrupoprofesortutoria <> session.profesor.tutor.id_curso_academico_grupo:
            redirect(URL("default","index"))    
    oevaluacion = Evaluacion(db, session)
    evaluaciones = oevaluacion.dame_evaluacion_alumnos_tutoria(idevaluacion, idgrupoprofesortutoria)
    if len(evaluaciones) == 0:
        return "No hay datos"
    logo = os.path.join(request.env.web2py_path,"applications",request.application,"uploads", session.logo_centro)      
    titulo = "Hoja Resumen de Evaluación ("+evaluaciones[0].curso_academico_evaluacion.evaluacion+")"
    tgrupo = "Grupo:"
    grupo = evaluaciones[0].grupo.grupo    
    ttutor = "Tutor:"
    tcentro = session.codigo_centro+' '+session.nombre_centro
    tcurso = session.curso_academico_nombre
    tutor = db.curso_academico_grupo(idgrupoprofesortutoria).id_tutor.apellidos+", "+db.curso_academico_grupo(idgrupoprofesortutoria).id_tutor.nombre
    nevaluaciones = len(evaluaciones) or 1
    class evaluaciongrupoPDF(FPDF):
        def header(self):
            self.set_font('Arial','B',15)
            #Logo del centro
            self.image(logo,5,5,20,20)
            #Poner código del centro y nombre el la parte izquierda superior
            self.cell(15)
            self.cell(w=0,h=0,txt=parsestr(tcentro),border=0,ln=0,align='L',fill=0)
            #Ahora el curso académico en la parte derecha superior
            self.cell(w=0,h=0,txt="Curso: "+parsestr(tcurso),border=0,ln=1,align='R',fill=0)
            #Dibujamos una linea de separación
            #self.set_line_width(.5)
            #pdf.line(5,13,205,13)
            #Calcular ancho del texto (titulo) y establecer posición
            w=self.get_string_width(titulo)+6
            self.set_x((297-w)/2)
            #Titulo
            self.cell(w=w,h=17,txt=parsestr(titulo),border=0,ln=1,align='C',fill=0)
            #Linea
            self.line(5,23,290,23)

            pdf.set_font('','',8)      
            
            pdf.cell(w=20,h=0,txt=parsestr(tgrupo),border=0,ln=0,align='R',fill=0)
            pdf.set_font('','B',10)                        
            pdf.cell(w=20,h=0,txt=parsestr(grupo),border=0,ln=1,align="L",fill=0)
            
            pdf.set_font('','',8)                        
            pdf.cell(w=20,h=9,txt=parsestr(ttutor),border=0,ln=0,align='R',fill=0)            
            pdf.set_font('','B',10)                                    
            pdf.cell(w=20,h=9,txt=parsestr(tutor),border=0,ln=1,align="L",fill=0)
           
            pdf.line(5,35,290,35)
            
            pdf.set_font('','B',9)
            pdf.cell(w=10,h=9,txt=parsestr("Asignatura"))
            pdf.cell(75)
            pdf.line(75,40,160,40)
            pdf.cell(w=10,h=4,txt=parsestr("Aspectos académicos"))
            pdf.cell(85)            
            pdf.cell(w=10,h=4,txt=parsestr("Aspectos actitudinales"))
            pdf.line(170,40,250,40)
            pdf.cell(20)            
            pdf.cell(w=0,h=9,txt=parsestr("Medias asignaturas"),align="R")
            pdf.ln(7)
            pdf.cell(70)            
            pdf.cell(w=10,h=0,txt=parsestr("Nivel"))
            pdf.cell(8)           
            pdf.cell(w=10,h=0,txt=parsestr("Trabajo en clase"))
            pdf.cell(20)           
            pdf.cell(w=10,h=0,txt=parsestr("Trabajo en casa"))
            pdf.cell(40)           
            pdf.cell(w=10,h=0,txt=parsestr("Interés"))
            pdf.cell(10)           
            pdf.cell(w=10,h=0,txt=parsestr("Participa"))
            pdf.cell(10)           
            pdf.cell(w=10,h=0,txt=parsestr("Comportamiento"))
            pdf.line(5,45,290,45)
            #Salto de línea
            pdf.ln(5)            
            
            
    pdf=evaluaciongrupoPDF('L','mm','A4')
    pdf.alias_nb_pages()
    pdf.add_page()
    pdf.set_font('Arial','',8)
    pdf.set_fill_color(230,230,230)    
    datos = {}
    for evaluacion in evaluaciones:
        if evaluacion.asignatura.abreviatura not in datos.keys():
            datos[evaluacion.asignatura.abreviatura] = {"evaluacion":evaluacion.evaluacion_alumno.evaluacion,
                        "asignatura":evaluacion.asignatura.asignatura[:46-len(evaluacion.asignatura.abreviatura)]+" ("+evaluacion.asignatura.abreviatura+")",
                        "aspectos": {"NIV":evaluacion.evaluacion_alumno.nivel,
                                     "TCL":evaluacion.evaluacion_alumno.trabajo_clase,
                                     "TCA":evaluacion.evaluacion_alumno.trabajo_casa,
                                     "INT":evaluacion.evaluacion_alumno.interes,
                                     "PART":evaluacion.evaluacion_alumno.participa,
                                     "COMP":evaluacion.evaluacion_alumno.comportamiento},
                        "nalumnos":1}
                                     
        else:
            datos[evaluacion.asignatura.abreviatura]["evaluacion"] +=  evaluacion.evaluacion_alumno.evaluacion
            datos[evaluacion.asignatura.abreviatura]["aspectos"]["NIV"] += evaluacion.evaluacion_alumno.nivel
            datos[evaluacion.asignatura.abreviatura]["aspectos"]["TCL"] += evaluacion.evaluacion_alumno.trabajo_clase
            datos[evaluacion.asignatura.abreviatura]["aspectos"]["TCA"] += evaluacion.evaluacion_alumno.trabajo_casa
            datos[evaluacion.asignatura.abreviatura]["aspectos"]["INT"] += evaluacion.evaluacion_alumno.interes
            datos[evaluacion.asignatura.abreviatura]["aspectos"]["PART"] += evaluacion.evaluacion_alumno.participa
            datos[evaluacion.asignatura.abreviatura]["aspectos"]["COMP"] += evaluacion.evaluacion_alumno.comportamiento
            datos[evaluacion.asignatura.abreviatura]["nalumnos"] += 1
    
    for asignatura in datos.keys():
        datos[asignatura]["evaluacion"] = float(datos[asignatura]["evaluacion"])/datos[asignatura]["nalumnos"]
        datos[asignatura]["aspectos"]["NIV"] = (float(datos[asignatura]["aspectos"]["NIV"])/datos[asignatura]["nalumnos"])
        datos[asignatura]["aspectos"]["TCL"] = (float(datos[asignatura]["aspectos"]["TCL"])/datos[asignatura]["nalumnos"])/10
        datos[asignatura]["aspectos"]["TCA"] = (float(datos[asignatura]["aspectos"]["TCA"])/datos[asignatura]["nalumnos"])/10
        datos[asignatura]["aspectos"]["INT"] = (float(datos[asignatura]["aspectos"]["INT"])/datos[asignatura]["nalumnos"])/10
        datos[asignatura]["aspectos"]["PART"] = (float(datos[asignatura]["aspectos"]["PART"])/datos[asignatura]["nalumnos"])/10
        datos[asignatura]["aspectos"]["COMP"] = (float(datos[asignatura]["aspectos"]["COMP"])/datos[asignatura]["nalumnos"])/10
       
        
        #esto no es correcto, debemos tener en cuenta criterios de evaluación de asignatura->departamento->centro
        #miremos en la tabla de asignaturas si esa asignatura usa criterios
        (peso1,peso2,peso3,peso4,peso5,peso6) = (0.0,0.0,0.0,0.0,0.0,0.0)
        asignaturarow = db(db.asignatura.abreviatura==asignatura).select().first()
        if asignaturarow.usar_criterios_asignatura:
            (peso1,peso2,peso3,peso4,peso5,peso6) = (asignaturarow.peso_1,asignaturarow.peso_2,asignaturarow.peso_3,
                                                   asignaturarow.peso_4,asignaturarow.peso_5,asignaturarow.peso_6)            
        elif asignaturarow.id_departamento.usar_criterios_departamento:
            (peso1,peso2,peso3,peso4,peso5,peso6) = (asignaturarow.id_departamento.peso_1,asignaturarow.id_departamento.peso_2,
                                                   asignaturarow.id_departamento.peso_3,asignaturarow.id_departamento.peso_4,
                                                   asignaturarow.id_departamento.peso_5,asignaturarow.id_departamento.peso_6)
        else:                                                   
            (peso1,peso2,peso3,peso4,peso5,peso6) = (evaluaciones[0].curso_academico_evaluacion.id_curso_academico.peso_1,
                                                   evaluaciones[0].curso_academico_evaluacion.id_curso_academico.peso_2,
                                                   evaluaciones[0].curso_academico_evaluacion.id_curso_academico.peso_3,
                                                   evaluaciones[0].curso_academico_evaluacion.id_curso_academico.peso_4,
                                                   evaluaciones[0].curso_academico_evaluacion.id_curso_academico.peso_5,
                                                   evaluaciones[0].curso_academico_evaluacion.id_curso_academico.peso_6)                                                   
            
        datos[asignatura]["evaluacion"] = (datos[asignatura]["aspectos"]["NIV"]*float(peso1) +
                                           datos[asignatura]["aspectos"]["TCL"]*float(peso2) +
                                           datos[asignatura]["aspectos"]["TCA"]*float(peso3) +
                                           datos[asignatura]["aspectos"]["INT"]*float(peso4) +
                                           datos[asignatura]["aspectos"]["PART"]*float(peso5) +
                                           datos[asignatura]["aspectos"]["COMP"]*float(peso6))/100
           
    linea = 1
    for asignatura in sorted(datos.iterkeys()):
        # imprime resumen de asignatura
        if linea % 2 <> 0:
            # imprimimos relleno de fondo
            fill = 1
        else:
            fill = 0

        pdf.set_fill_color(230,230,230)    
        pdf.set_font('','',8)
        pdf.cell(w=50,h=5,txt=parsestr(datos[asignatura]["asignatura"]),border=0,ln=0,align="L",fill=fill)
        pdf.cell(10,h=5,fill=fill)
        nivel = datos[asignatura]["aspectos"]["NIV"]
        pdf.cell(w=30,h=5,txt=parsestr(str('%.02f' % nivel)),align="C",fill=fill)
        trabajo_clase = datos[asignatura]["aspectos"]["TCL"]
        pdf.cell(w=25,h=5,txt=parsestr(str('%.02f' %  trabajo_clase)),align="C",fill=fill)
        trabajo_casa = datos[asignatura]["aspectos"]["TCA"]
        pdf.cell(w=30,h=5,txt=parsestr(str('%.02f' % trabajo_casa)),align="C",fill=fill)
        pdf.cell(20,h=5,fill=fill)
        interes = datos[asignatura]["aspectos"]["INT"]
        pdf.cell(w=20,h=5,txt=parsestr(str('%.02f' % interes)),align="C",fill=fill)
        #pdf.cell(10,fill=fill)
        participa = datos[asignatura]["aspectos"]["PART"]
        pdf.cell(w=20,h=5,txt=parsestr(str('%.02f' % participa)),align="C",fill=fill)
        #pdf.cell(15,fill=fill)
        comportamiento = datos[asignatura]["aspectos"]["COMP"]
        pdf.cell(w=30,h=5,txt=parsestr(str('%.02f' % comportamiento)),align="C",fill=fill)
        pdf.cell(w=10,h=5,fill=fill)
        pdf.set_fill_color(200,200,200)           
        pdf.set_font('','B',9)
        border = "TLR" if linea == 1 else "LR"      
        evalua = datos[asignatura]["evaluacion"]             
        pdf.cell(w=0,h=5,txt=parsestr(str('%.02f' % evalua)),border=border,align="R",fill=1,ln=1)
        # aumentamos el contador de linea
        linea += 1

    # estadísticas generales
    sumanivel = 0
    sumatrclase = 0
    sumatrcasa = 0
    sumainteres = 0
    sumaparticipa = 0
    sumacomportamiento = 0
    sumaevaluacion = 0
    for asignatura in datos.keys():
        sumanivel += datos[asignatura]["aspectos"]["NIV"]
        sumatrclase += datos[asignatura]["aspectos"]["TCL"]
        sumatrcasa += datos[asignatura]["aspectos"]["TCA"]
        sumainteres += datos[asignatura]["aspectos"]["INT"]
        sumaparticipa += datos[asignatura]["aspectos"]["PART"]
        sumacomportamiento += datos[asignatura]["aspectos"]["COMP"]
        sumaevaluacion += datos[asignatura]["evaluacion"]
    
    nl = len(datos.keys())    
    pdf.set_fill_color(200,200,200)    
    pdf.set_font('','B',9)                        
    pdf.cell(w=50,h=5,txt=parsestr(str("Estadísticas de la evaluación")),border="LTB",ln=0,align="L",fill=1)
    pdf.cell(10,h=5,border="TB",fill=1)
    nivel = sumanivel/float(nl)
    pdf.cell(w=30,h=5,txt=parsestr(str('%.02f' % nivel)),border="TB",align="C",fill=1)
    trabajo_clase = sumatrclase/float(nl)       
    pdf.cell(w=25,h=5,txt=parsestr(str('%.02f' % trabajo_clase)),border="TB",align="C",fill=1)
    trabajo_casa = sumatrcasa/float(nl)
    pdf.cell(w=30,h=5,txt=parsestr(str('%.02f' % trabajo_casa)),border="TB",align="C",fill=1)
    pdf.cell(20,h=5,border="TB",fill=1)
    interes = sumainteres/float(nl)
    pdf.cell(w=20,h=5,txt=parsestr(str('%.02f' % interes)),border="TB",align="C",fill=1)
    participa = sumaparticipa/float(nl)
    pdf.cell(w=20,h=5,txt=parsestr(str('%.02f' % participa)),border="TB",align="C",fill=1)
    comportamiento = sumacomportamiento/float(nl)
    pdf.cell(w=30,h=5,txt=parsestr(str('%.02f' % comportamiento)),border="TB",align="C",fill=1)
    pdf.cell(w=10,h=5,border="TB",fill=1)
    evalua = (sumaevaluacion/(nl))
    pdf.set_font('','B',10)                            
    pdf.cell(w=0,h=5,txt=parsestr(str('%.02f' % evalua)),border=1,align="R",fill=1)
    fichero=os.path.join(request.folder,"uploads",str(uuid.uuid4())+".png")
    d = {}
    for asignatura in datos.keys():
        d[asignatura] = datos[asignatura]["evaluacion"] 
    genera_grafico_asignaturas(fichero, d)
    graf = os.path.join(fichero)
    pdf.image(graf,10,150)    
    os.unlink(graf)
    fichero=os.path.join(request.folder,"uploads",str(uuid.uuid4())+".png") 
    genera_grafico_aspectos(fichero, {"NIV":nivel, "TCL":trabajo_clase,
                                      "TCA":trabajo_casa, "INT":interes,
                                      "PART":participa, "COMP":comportamiento})
    graf = os.path.join(fichero)
    pdf.image(graf,200,150)    
    os.unlink(graf)
       
    response.headers['Content-Type']='application/pdf'
    return pdf.output(dest='S')
    
@auth.requires_login()
@auth.requires_membership(role='Profesores')
def informecurso():
    idgrupoprofesortutoria = int(request.args[-1]) or redirect('default', 'index')
    oevaluacion = Evaluacion(db, session)
    # comprobemos que somos reponsables o tutor del grupo
    if not session.esResponsable:
        if not session.profesor.esTutor or idgrupoprofesortutoria <> session.profesor.tutor.id_curso_academico_grupo:
            redirect(URL("default","index"))    
    evaluaciones = oevaluacion.dame_evaluacion_alumnos_tutoria(0, idgrupoprofesortutoria)
    if len(evaluaciones) == 0:
        return "No hay datos"
    logo = os.path.join(request.env.web2py_path,"applications",request.application,"uploads", session.logo_centro)      
    titulo = "Hoja Resumen de Evaluación del curso"
    tgrupo = "Grupo:"
    grupo = evaluaciones[0].grupo.grupo    
    ttutor = "Tutor:"
    tcentro = session.codigo_centro+' '+session.nombre_centro
    tcurso = session.curso_academico_nombre
    tutor = db.curso_academico_grupo(idgrupoprofesortutoria).id_tutor.apellidos+", "+db.curso_academico_grupo(idgrupoprofesortutoria).id_tutor.nombre
    nevaluaciones = len(evaluaciones) or 1
    class evaluaciongrupoPDF(FPDF):
        def header(self):
            self.set_font('Arial','B',15)
            #Logo del centro
            self.image(logo,5,5,20,20)
            #Poner código del centro y nombre el la parte izquierda superior
            self.cell(15)
            self.cell(w=0,h=0,txt=parsestr(tcentro),border=0,ln=0,align='L',fill=0)
            #Ahora el curso académico en la parte derecha superior
            self.cell(w=0,h=0,txt="Curso: "+parsestr(tcurso),border=0,ln=1,align='R',fill=0)
            #Dibujamos una linea de separación
            #self.set_line_width(.5)
            #pdf.line(5,13,205,13)
            #Calcular ancho del texto (titulo) y establecer posición
            w=self.get_string_width(titulo)+6
            self.set_x((297-w)/2)
            #Titulo
            self.cell(w=w,h=17,txt=parsestr(titulo),border=0,ln=1,align='C',fill=0)
            #Linea
            self.line(5,23,290,23)

            pdf.set_font('','',8)      
            
            pdf.cell(w=20,h=0,txt=parsestr(tgrupo),border=0,ln=0,align='R',fill=0)
            pdf.set_font('','B',10)                        
            pdf.cell(w=20,h=0,txt=parsestr(grupo),border=0,ln=1,align="L",fill=0)
            
            pdf.set_font('','',8)                        
            pdf.cell(w=20,h=9,txt=parsestr(ttutor),border=0,ln=0,align='R',fill=0)            
            pdf.set_font('','B',10)                                    
            pdf.cell(w=20,h=9,txt=parsestr(tutor),border=0,ln=1,align="L",fill=0)
           
            pdf.line(5,35,290,35)
            
            pdf.set_font('','B',9)
            pdf.cell(w=10,h=9,txt=parsestr("Asignatura"))
            pdf.cell(75)
            pdf.line(75,40,160,40)
            pdf.cell(w=10,h=4,txt=parsestr("Aspectos académicos"))
            pdf.cell(85)            
            pdf.cell(w=10,h=4,txt=parsestr("Aspectos actitudinales"))
            pdf.line(170,40,250,40)
            pdf.cell(20)            
            pdf.cell(w=0,h=9,txt=parsestr("Medias asignaturas"),align="R")
            pdf.ln(7)
            pdf.cell(70)            
            pdf.cell(w=10,h=0,txt=parsestr("Nivel"))
            pdf.cell(8)           
            pdf.cell(w=10,h=0,txt=parsestr("Trabajo en clase"))
            pdf.cell(20)           
            pdf.cell(w=10,h=0,txt=parsestr("Trabajo en casa"))
            pdf.cell(40)           
            pdf.cell(w=10,h=0,txt=parsestr("Interés"))
            pdf.cell(10)           
            pdf.cell(w=10,h=0,txt=parsestr("Participa"))
            pdf.cell(10)           
            pdf.cell(w=10,h=0,txt=parsestr("Comportamiento"))
            pdf.line(5,45,290,45)
            #Salto de línea
            pdf.ln(5)            
            
            
    pdf=evaluaciongrupoPDF('L','mm','A4')
    pdf.alias_nb_pages()
    pdf.add_page()
    pdf.set_font('Arial','',8)
    pdf.set_fill_color(230,230,230)    
    datos = {}
    for evaluacion in evaluaciones:
        if evaluacion.asignatura.abreviatura not in datos.keys():
            datos[evaluacion.asignatura.abreviatura] = {"evaluacion":evaluacion.evaluacion_alumno.evaluacion,
                        "asignatura":evaluacion.asignatura.asignatura[:46-len(evaluacion.asignatura.abreviatura)]+" ("+evaluacion.asignatura.abreviatura+")",                        
                        "aspectos": {"NIV":evaluacion.evaluacion_alumno.nivel,
                                     "TCL":evaluacion.evaluacion_alumno.trabajo_clase,
                                     "TCA":evaluacion.evaluacion_alumno.trabajo_casa,
                                     "INT":evaluacion.evaluacion_alumno.interes,
                                     "PART":evaluacion.evaluacion_alumno.participa,
                                     "COMP":evaluacion.evaluacion_alumno.comportamiento},
                        "nalumnos": 1 }
        else:
            datos[evaluacion.asignatura.abreviatura]["evaluacion"] +=  evaluacion.evaluacion_alumno.evaluacion
            datos[evaluacion.asignatura.abreviatura]["aspectos"]["NIV"] += evaluacion.evaluacion_alumno.nivel
            datos[evaluacion.asignatura.abreviatura]["aspectos"]["TCL"] += evaluacion.evaluacion_alumno.trabajo_clase
            datos[evaluacion.asignatura.abreviatura]["aspectos"]["TCA"] += evaluacion.evaluacion_alumno.trabajo_casa
            datos[evaluacion.asignatura.abreviatura]["aspectos"]["INT"] += evaluacion.evaluacion_alumno.interes
            datos[evaluacion.asignatura.abreviatura]["aspectos"]["PART"] += evaluacion.evaluacion_alumno.participa
            datos[evaluacion.asignatura.abreviatura]["aspectos"]["COMP"] += evaluacion.evaluacion_alumno.comportamiento
            datos[evaluacion.asignatura.abreviatura]["nalumnos"] += 1

    for asignatura in datos.keys():
        datos[asignatura]["evaluacion"] = (float(datos[asignatura]["evaluacion"])/datos[asignatura]["nalumnos"])/10
        datos[asignatura]["aspectos"]["NIV"] = float(datos[asignatura]["aspectos"]["NIV"])/datos[asignatura]["nalumnos"]
        datos[asignatura]["aspectos"]["TCL"] = (float(datos[asignatura]["aspectos"]["TCL"])/datos[asignatura]["nalumnos"])/10
        datos[asignatura]["aspectos"]["TCA"] = (float(datos[asignatura]["aspectos"]["TCA"])/datos[asignatura]["nalumnos"])/10
        datos[asignatura]["aspectos"]["INT"] = (float(datos[asignatura]["aspectos"]["INT"])/datos[asignatura]["nalumnos"])/10
        datos[asignatura]["aspectos"]["PART"] = (float(datos[asignatura]["aspectos"]["PART"])/datos[asignatura]["nalumnos"])/10
        datos[asignatura]["aspectos"]["COMP"] = (float(datos[asignatura]["aspectos"]["COMP"])/datos[asignatura]["nalumnos"])/10
        
        #esto no es correcto, debemos tener en cuenta criterios de evaluación de asignatura->departamento->centro
        #miremos en la tabla de asignaturas si esa asignatura usa criterios
        (peso1,peso2,peso3,peso4,peso5,peso6) = (0.0,0.0,0.0,0.0,0.0,0.0)
        asignaturarow = db(db.asignatura.abreviatura==asignatura).select().first()
        if asignaturarow.usar_criterios_asignatura:
            (peso1,peso2,peso3,peso4,peso5,peso6) = (asignaturarow.peso_1,asignaturarow.peso_2,asignaturarow.peso_3,
                                                   asignaturarow.peso_4,asignaturarow.peso_5,asignaturarow.peso_6)            
        elif asignaturarow.id_departamento.usar_criterios_departamento:
            (peso1,peso2,peso3,peso4,peso5,peso6) = (asignaturarow.id_departamento.peso_1,asignaturarow.id_departamento.peso_2,
                                                   asignaturarow.id_departamento.peso_3,asignaturarow.id_departamento.peso_4,
                                                   asignaturarow.id_departamento.peso_5,asignaturarow.id_departamento.peso_6)
        else:                                                   
            (peso1,peso2,peso3,peso4,peso5,peso6) = (evaluaciones[0].curso_academico_evaluacion.id_curso_academico.peso_1,
                                                   evaluaciones[0].curso_academico_evaluacion.id_curso_academico.peso_2,
                                                   evaluaciones[0].curso_academico_evaluacion.id_curso_academico.peso_3,
                                                   evaluaciones[0].curso_academico_evaluacion.id_curso_academico.peso_4,
                                                   evaluaciones[0].curso_academico_evaluacion.id_curso_academico.peso_5,
                                                   evaluaciones[0].curso_academico_evaluacion.id_curso_academico.peso_6)                                                   
            
        datos[asignatura]["evaluacion"] = (datos[asignatura]["aspectos"]["NIV"]*float(peso1) +
                                           datos[asignatura]["aspectos"]["TCL"]*float(peso2) +
                                           datos[asignatura]["aspectos"]["TCA"]*float(peso3) +
                                           datos[asignatura]["aspectos"]["INT"]*float(peso4) +
                                           datos[asignatura]["aspectos"]["PART"]*float(peso5) +
                                           datos[asignatura]["aspectos"]["COMP"]*float(peso6))/100          
                      
    linea = 1
    for asignatura in sorted(datos.iterkeys()):
        # imprime resumen de asignatura
        if linea % 2 <> 0:
            # imprimimos relleno de fondo
            fill = 1
        else:
            fill = 0

        pdf.set_fill_color(230,230,230)    
        pdf.set_font('','',8)
        pdf.cell(w=50,h=5,txt=parsestr(datos[asignatura]["asignatura"]),border=0,ln=0,align="L",fill=fill)
        pdf.cell(10,h=5,fill=fill)
        nivel = datos[asignatura]["aspectos"]["NIV"]
        pdf.cell(w=30,h=5,txt=parsestr(str('%.02f' % nivel)),align="C",fill=fill)
        trabajo_clase = datos[asignatura]["aspectos"]["TCL"]
        pdf.cell(w=25,h=5,txt=parsestr(str('%.02f' %  trabajo_clase)),align="C",fill=fill)
        trabajo_casa = datos[asignatura]["aspectos"]["TCA"]
        pdf.cell(w=30,h=5,txt=parsestr(str('%.02f' % trabajo_casa)),align="C",fill=fill)
        pdf.cell(20,h=5,fill=fill)
        interes = datos[asignatura]["aspectos"]["INT"]
        pdf.cell(w=20,h=5,txt=parsestr(str('%.02f' % interes)),align="C",fill=fill)
        #pdf.cell(10,fill=fill)
        participa = datos[asignatura]["aspectos"]["PART"]
        pdf.cell(w=20,h=5,txt=parsestr(str('%.02f' % participa)),align="C",fill=fill)
        #pdf.cell(15,fill=fill)
        comportamiento = datos[asignatura]["aspectos"]["COMP"]
        pdf.cell(w=30,h=5,txt=parsestr(str('%.02f' % comportamiento)),align="C",fill=fill)
        pdf.cell(w=10,h=5,fill=fill)
        pdf.set_fill_color(200,200,200)           
        pdf.set_font('','B',9)
        border = "TLR" if linea == 1 else "LR"      
        evalua = datos[asignatura]["evaluacion"]             
        pdf.cell(w=0,h=5,txt=parsestr(str('%.02f' % evalua)),border=border,align="R",fill=1,ln=1)
        # aumentamos el contador de linea
        linea += 1

    # estadísticas generales
    sumanivel = 0
    sumatrclase = 0
    sumatrcasa = 0
    sumainteres = 0
    sumaparticipa = 0
    sumacomportamiento = 0
    sumaevaluacion = 0
    for asignatura in datos.keys():
        sumanivel += datos[asignatura]["aspectos"]["NIV"]
        sumatrclase += datos[asignatura]["aspectos"]["TCL"]
        sumatrcasa += datos[asignatura]["aspectos"]["TCA"]
        sumainteres += datos[asignatura]["aspectos"]["INT"]
        sumaparticipa += datos[asignatura]["aspectos"]["PART"]
        sumacomportamiento += datos[asignatura]["aspectos"]["COMP"]
        sumaevaluacion += datos[asignatura]["evaluacion"]
    
    nl = len(datos.keys())    
    pdf.set_fill_color(200,200,200)    
    pdf.set_font('','B',9)                        
    pdf.cell(w=50,h=5,txt=parsestr(str("Estadísticas de la evaluación")),border="LTB",ln=0,align="L",fill=1)
    pdf.cell(10,h=5,border="TB",fill=1)
    nivel = sumanivel/float(nl)
    pdf.cell(w=30,h=5,txt=parsestr(str('%.02f' % nivel)),border="TB",align="C",fill=1)
    trabajo_clase = sumatrclase/float(nl)       
    pdf.cell(w=25,h=5,txt=parsestr(str('%.02f' % trabajo_clase)),border="TB",align="C",fill=1)
    trabajo_casa = sumatrcasa/float(nl)
    pdf.cell(w=30,h=5,txt=parsestr(str('%.02f' % trabajo_casa)),border="TB",align="C",fill=1)
    pdf.cell(20,h=5,border="TB",fill=1)
    interes = sumainteres/float(nl)
    pdf.cell(w=20,h=5,txt=parsestr(str('%.02f' % interes)),border="TB",align="C",fill=1)
    participa = sumaparticipa/float(nl)
    pdf.cell(w=20,h=5,txt=parsestr(str('%.02f' % participa)),border="TB",align="C",fill=1)
    comportamiento = sumacomportamiento/float(nl)
    pdf.cell(w=30,h=5,txt=parsestr(str('%.02f' % comportamiento)),border="TB",align="C",fill=1)
    pdf.cell(w=10,h=5,border="TB",fill=1)
    evalua = (sumaevaluacion/(nl))
    pdf.set_font('','B',10)                            
    pdf.cell(w=0,h=5,txt=parsestr(str('%.02f' % evalua)),border=1,align="R",fill=1)
    fichero=os.path.join(request.folder,"uploads",str(uuid.uuid4())+".png")
    d = {}
    for asignatura in datos.keys():
        d[asignatura] = datos[asignatura]["evaluacion"] 
    genera_grafico_asignaturas(fichero, d)
    graf = os.path.join(fichero)
    pdf.image(graf,10,150)    
    os.unlink(graf)
    fichero=os.path.join(request.folder,"uploads",str(uuid.uuid4())+".png") 
    genera_grafico_aspectos(fichero, {"NIV":nivel, "TCL":trabajo_clase,
                                      "TCA":trabajo_casa, "INT":interes,
                                      "PART":participa, "COMP":comportamiento})
    graf = os.path.join(fichero)
    pdf.image(graf,200,150)    
    os.unlink(graf)
       
    response.headers['Content-Type']='application/pdf'
    return pdf.output(dest='S')

@auth.requires_login()
@auth.requires_membership(role='Profesores')
def informefichas():
    idgrupoprofesortutoria = int(request.args[-2]) or redirect('default', 'index')
    idcurso = int(request.args[-1]) or redirect('default', 'index')

    # para que valga para todos los cursos queda implementar, el acceder al curso anterior y para ese grupo
    # obtener su id y cambiar el idgrupoprofesortutoria...

    # comprobemos que somos reponsables o tutor del grupo
    if not session.esResponsable:
        if not session.profesor.esTutor or idgrupoprofesortutoria <> session.profesor.tutor.id_curso_academico_grupo:
            redirect(URL("default","index"))

    idgrupo = db((db.curso_academico_grupo.id == idgrupoprofesortutoria)).select().first().id_grupo
    idgrupoprofesortutoria = db((db.curso_academico_grupo.id_grupo == idgrupo) & (db.curso_academico_grupo.id_curso_academico == idcurso)).select().first().id

    query = ((db.grupo_alumno.id_curso_academico_grupo == idgrupoprofesortutoria) &
             (db.grupo_alumno.id_alumno == db.alumno.id) &
             (db.grupo_alumno.id == db.seguimiento_alumno.id_grupo_alumno))
    alumnos_fichas = db(query).select(orderby=db.alumno.apellidos|db.alumno.nombre)
    if len(alumnos_fichas) == 0:
        return "No hay datos"

    logo = os.path.join(request.env.web2py_path,"applications",request.application,"uploads", session.logo_centro)
    titulo = "Ficha-Registro de Seguimiento del Alumnado"
    tnombre = "Alumno/a:"
    tnie = "N.I.E.:"
    tfecha = "Fec.Nac.:"
    tgrupo = "Grupo:"
    ttutor = "Tutor/a:"
    tcentro = session.codigo_centro+' '+session.nombre_centro
    tcurso = session.curso_academico_nombre
    tutor = db.curso_academico_grupo(idgrupoprofesortutoria).id_tutor.apellidos+", "+db.curso_academico_grupo(idgrupoprofesortutoria).id_tutor.nombre
    nombreAlumno = alumnos_fichas[0].grupo_alumno.id_alumno.apellidos+', '+alumnos_fichas[0].grupo_alumno.id_alumno.nombre
    nie = alumnos_fichas[0].grupo_alumno.id_alumno.nie
    fnac = alumnos_fichas[0].grupo_alumno.id_alumno.fecha_nacimiento
    grupo = alumnos_fichas[0].grupo_alumno.id_curso_academico_grupo.id_grupo.grupo
    tutor = '%s, %s' % (alumnos_fichas[0].grupo_alumno.id_curso_academico_grupo.id_tutor.apellidos,
            alumnos_fichas[0].grupo_alumno.id_curso_academico_grupo.id_tutor.nombre)
    cad = alumnos_fichas[0].grupo_alumno.id_alumno.foto.split(".")
    subpath = cad[:2]
    subpath = os.path.join(".".join(subpath), cad[2][:2])
    cad = ".".join(cad)
    foto = os.path.join(request.folder,"uploads",subpath,cad)

    class ficharegistroPDF(FPDF):
        def header(self):
            self.set_font('Arial','B',13)
            #Logo del centro
            self.image(logo,5,5,20,20)
            #Poner código del centro y nombre el la parte izquierda superior
            self.cell(15)
            self.cell(w=0,h=0,txt=parsestr(tcentro),border=0,ln=0,align='L',fill=0)
            #Ahora el curso académico en la parte derecha superior
            self.cell(w=0,h=0,txt="Curso: "+parsestr(tcurso),border=0,ln=1,align='R',fill=0)
            #Dibujamos una linea de separación
            #self.set_line_width(.5)
            #pdf.line(5,13,205,13)
            #Calcular ancho del texto (titulo) y establecer posición
            w=self.get_string_width(titulo)+6
            self.set_x((210-w)/2)
            #Titulo
            self.cell(w=w,h=17,txt=parsestr(titulo),border=0,ln=1,align='C',fill=0)
            #Linea
            self.line(5,23,205,23)
            #Fuente más pequeña sin bold
            self.set_font('','',8)
            #Nombre alumno
            self.cell(w=20,h=0,txt=parsestr(tnombre),border=0,ln=0,align='R',fill=0)
            self.set_font('','B',10)
            self.cell(w=20,h=0,txt=parsestr(nombreAlumno),border=0,ln=1,align="L",fill=0)

            #Foto alumno
            try:
                self.image(foto,180,25,17,22)
            except:
                pass

            #Nie alumno
            self.set_font('','',8)
            self.cell(w=20,h=9,txt=parsestr(tnie),border=0,ln=0,align='R',fill=0)
            self.set_font('','B',10)
            self.cell(w=20,h=9,txt=parsestr(nie),border=0,ln=1,align="L",fill=0)

            #Fecha nacimiento
            self.set_font('','',8)
            self.cell(w=20,h=0,txt=parsestr(tfecha),border=0,ln=0,align='R',fill=0)
            self.set_font('','B',10)
            self.cell(w=20,h=0,txt=fnac.isoformat(),border=0,ln=1,align="L",fill=0)

            #Grupo
            self.set_font('','',8)
            self.cell(w=20,h=9,txt=parsestr(tgrupo),border=0,ln=0,align='R',fill=0)
            self.set_font('','B',10)
            self.cell(w=20,h=9,txt=parsestr(grupo),border=0,ln=1,align="L",fill=0)

            #Tutor
            self.set_font('','',8)
            self.cell(w=20,h=0,txt=parsestr(ttutor),border=0,ln=0,align='R',fill=0)
            self.set_font('','B',10)
            self.cell(w=20,h=0,txt=parsestr(tutor),border=0,ln=1,align="L",fill=0)
            self.line(5,48,205,48)
            #Salto de línea
            self.ln(5)

        def footer(self):
            "hook to draw custom page header (printing page numbers)"
            self.line(5,280,205,280)
            self.set_y(-19)
            self.set_font('Arial','I',8)
            self.cell(w=0,h=9,txt=parsestr(titulo),border=0,ln=0,align='L',fill=0)
            marcaid = parsestr(("Impreso por %s a las %s" % (session.auth.user.first_name+" "+session.auth.user.last_name,datetime.datetime.now().strftime("%H:%M:%S %d/%m/%Y"))))
            self.cell(w=0,h=9,txt=marcaid,border=0,ln=1,align='R',fill=0)
            txt = parsestr('Página')+' %s de %s' % (self.page_no(), self.alias_nb_pages())
            self.cell(w=0,h=0,txt=txt,border=0,ln=0,align='R',fill=0)

    pdf=ficharegistroPDF('P','mm','A4')
    pdf.alias_nb_pages()
    pdf.add_page()
    pdf.set_font('Arial','',8)
    pdf.set_fill_color(230,230,230)
    for ficha in alumnos_fichas:
        if nie != ficha.grupo_alumno.id_alumno.nie:
            # cambiamos de alumno
            nombreAlumno = ficha.grupo_alumno.id_alumno.apellidos+', '+ficha.grupo_alumno.id_alumno.nombre
            nie = ficha.grupo_alumno.id_alumno.nie
            fnac = ficha.grupo_alumno.id_alumno.fecha_nacimiento
            cad = ficha.grupo_alumno.id_alumno.foto.split(".")
            subpath = cad[:2]
            subpath = os.path.join(".".join(subpath), cad[2][:2])
            cad = ".".join(cad)
            foto = os.path.join(request.folder,"uploads",subpath,cad)
            pdf.add_page()

        pdf.set_font('','B',12)
        #Calcular ancho del texto y establecer posición
        w=pdf.get_string_width("Evaluación Inicial")+6
        pdf.set_x((210-w)/2)
        pdf.cell(w=w,h=17,txt=parsestr("Evaluación Inicial"),border=0,ln=1,align='C',fill=0)
        pdf.line(10,62,200,62)
        pdf.set_font('','B',10)
        pdf.cell(w=10,h=5,txt=parsestr(str(db.seguimiento_alumno.inicial_ev_materias_pendientes.label)),border=0,ln=1,align="L",fill=0)
        pdf.cell(15)
        pdf.set_font('','',10)
        pdf.multi_cell(w=0,h=5,txt=parsestr(ficha.seguimiento_alumno.inicial_ev_materias_pendientes),border=0,align="J",fill=1)
        pdf.ln(1)
        pdf.set_font('','B',10)
        pdf.cell(w=10,h=5,txt=parsestr(str(db.seguimiento_alumno.inicial_ev_dificultades_detectadas.label)),border=0,ln=1,align="L",fill=0)
        pdf.set_font('','',10)
        pdf.cell(15)
        pdf.multi_cell(w=0,h=5,txt=parsestr(ficha.seguimiento_alumno.inicial_ev_dificultades_detectadas),border=0,align="J",fill=1)
        pdf.ln(1)
        if ficha.seguimiento_alumno.inicial_ev_refuerzo_indiv_aula:
            pdf.set_font('','B',10)
            pdf.cell(10)
            pdf.cell(w=10,h=5,txt=parsestr(str(db.seguimiento_alumno.inicial_ev_refuerzo_indiv_aula.label)),border=0,ln=1,align="L",fill=0)
        if ficha.seguimiento_alumno.inicial_ev_refuerzo_apoyo_pt:
            pdf.set_font('','B',10)
            pdf.cell(10)
            pdf.cell(w=10,h=5,txt=parsestr(str(db.seguimiento_alumno.inicial_ev_refuerzo_apoyo_pt.label)),border=0,ln=1,align="L",fill=0)
        if ficha.seguimiento_alumno.inicial_ev_refuerzo_apoyo_ec:
            pdf.set_font('','B',10)
            pdf.cell(10)
            pdf.cell(w=10,h=5,txt=parsestr(str(db.seguimiento_alumno.inicial_ev_refuerzo_apoyo_ec.label)),border=0,ln=1,align="L",fill=0)
        if ficha.seguimiento_alumno.inicial_ev_aci_no_significativa:
            pdf.set_font('','B',10)
            pdf.cell(10)
            pdf.cell(w=10,h=5,txt=parsestr(str(db.seguimiento_alumno.inicial_ev_aci_no_significativa.label)),border=0,ln=1,align="L",fill=0)
        if ficha.seguimiento_alumno.inicial_ev_aci_significativa:
            pdf.set_font('','B',10)
            pdf.cell(10)
            pdf.cell(w=10,h=5,txt=parsestr(str(db.seguimiento_alumno.inicial_ev_aci_significativa.label)),border=0,ln=1,align="L",fill=0)
        if ficha.seguimiento_alumno.inicial_ev_otras:
            pdf.set_font('','B',10)
            pdf.cell(10)
            pdf.cell(w=10,h=5,txt=parsestr(str(db.seguimiento_alumno.inicial_ev_otras.label)),border=0,ln=1,align="L",fill=0)
            pdf.set_font('','',10)
            pdf.cell(15)
            pdf.multi_cell(w=0,h=5,txt=parsestr(ficha.seguimiento_alumno.inicial_ev_otras_especificar),border=0,align="J",fill=1)
            pdf.ln(1)

        pdf.line(10,pdf.get_y(),200,pdf.get_y())
        pdf.set_font('','B',12)
        w=pdf.get_string_width("Primera Evaluación")+6
        pdf.set_x((210-w)/2)
        pdf.cell(w=w,h=17,txt=parsestr("Primera Evaluación"),border=0,ln=1,align='C',fill=0)
        pdf.line(10,pdf.get_y()-5,200,pdf.get_y()-5)
        pdf.set_font('','B',10)
        pdf.cell(w=10,h=5,txt=parsestr(str(db.seguimiento_alumno.primera_ev_dificultades.label)),border=0,ln=1,align="L",fill=0)
        pdf.cell(15)
        pdf.multi_cell(w=0,h=5,txt=parsestr(ficha.seguimiento_alumno.primera_ev_dificultades),border=0,align="J",fill=1)
        pdf.ln(1)
        pdf.set_font('','B',10)
        pdf.cell(w=10,h=5,txt=parsestr(str(db.seguimiento_alumno.primera_ev_evolucion.label)),border=0,ln=1,align="L",fill=0)
        pdf.cell(15)
        pdf.multi_cell(w=0,h=5,txt=parsestr(ficha.seguimiento_alumno.primera_ev_evolucion),border=0,align="J",fill=1)
        pdf.ln(1)
        pdf.set_font('','B',10)
        pdf.cell(w=10,h=5,txt=parsestr(str(db.seguimiento_alumno.primera_ev_decisiones.label)),border=0,ln=1,align="L",fill=0)
        pdf.cell(15)
        pdf.multi_cell(w=0,h=5,txt=parsestr(ficha.seguimiento_alumno.primera_ev_decisiones),border=0,align="J",fill=1)
        pdf.ln(1)

        pdf.line(10,pdf.get_y(),200,pdf.get_y())
        pdf.set_font('','B',12)
        w=pdf.get_string_width("Segunda Evaluación")+6
        pdf.set_x((210-w)/2)
        pdf.cell(w=w,h=17,txt=parsestr("Segunda Evaluación"),border=0,ln=1,align='C',fill=0)
        pdf.line(10,pdf.get_y()-5,200,pdf.get_y()-5)
        pdf.set_font('','B',10)
        pdf.cell(w=10,h=5,txt=parsestr(str(db.seguimiento_alumno.segunda_ev_dificultades.label)),border=0,ln=1,align="L",fill=0)
        pdf.cell(15)
        pdf.multi_cell(w=0,h=5,txt=parsestr(ficha.seguimiento_alumno.segunda_ev_dificultades),border=0,align="J",fill=1)
        pdf.ln(1)
        pdf.set_font('','B',10)
        pdf.cell(w=10,h=5,txt=parsestr(str(db.seguimiento_alumno.segunda_ev_evolucion.label)),border=0,ln=1,align="L",fill=0)
        pdf.cell(15)
        pdf.multi_cell(w=0,h=5,txt=parsestr(ficha.seguimiento_alumno.segunda_ev_evolucion),border=0,align="J",fill=1)
        pdf.ln(1)
        pdf.set_font('','B',10)
        pdf.cell(w=10,h=5,txt=parsestr(str(db.seguimiento_alumno.segunda_ev_decisiones.label)),border=0,ln=1,align="L",fill=0)
        pdf.cell(15)
        pdf.multi_cell(w=0,h=5,txt=parsestr(ficha.seguimiento_alumno.segunda_ev_decisiones),border=0,align="J",fill=1)
        pdf.ln(1)

        pdf.line(10,pdf.get_y(),200,pdf.get_y())
        pdf.set_font('','B',12)
        w=pdf.get_string_width("Evaluación Ordinaria-Extraordinaria")+6
        pdf.set_x((210-w)/2)
        pdf.cell(w=w,h=17,txt=parsestr("Evaluación Ordinaria-Extraordinaria"),border=0,ln=1,align='C',fill=0)
        pdf.line(10,pdf.get_y()-5,200,pdf.get_y()-5)
        pdf.set_font('','B',10)
        pdf.cell(w=10,h=5,txt=parsestr(str(T('Decisión adoptada:'))),border=0,ln=0,align="L",fill=0)
        if ficha.seguimiento_alumno.ord_extra_ev_promocion:
            pdf.cell(40)
            pdf.cell(w=10,h=5,txt=parsestr(str(db.seguimiento_alumno.ord_extra_ev_promocion.label)),border=0,ln=1,align="L",fill=0)
        elif ficha.seguimiento_alumno.ord_extra_ev_promocion_automatica:
            pdf.cell(40)
            pdf.cell(w=10,h=5,txt=parsestr(str(db.seguimiento_alumno.ord_extra_ev_promocion_automatica.label)),border=0,ln=1,align="L",fill=0)
        elif ficha.seguimiento_alumno.ord_extra_ev_repetir:
            pdf.cell(40)
            pdf.cell(w=10,h=5,txt=parsestr(str(db.seguimiento_alumno.ord_extra_ev_repetir.label)),border=0,ln=1,align="L",fill=0)
        else:
            pdf.cell(40)
            pdf.cell(w=10,h=5,txt=parsestr(str(T('Ninguna marcada'))),border=0,ln=1,align="L",fill=0)
        pdf.set_font('','B',10)
        pdf.cell(w=10,h=5,txt=parsestr(str(db.seguimiento_alumno.ord_extra_ev_asignatura_pendientes.label)),border=0,ln=1,align="L",fill=0)
        pdf.cell(15)
        pdf.multi_cell(w=0,h=5,txt=parsestr(ficha.seguimiento_alumno.ord_extra_ev_asignatura_pendientes),border=0,align="J",fill=1)
        pdf.ln(1)
        pdf.set_font('','B',10)
        pdf.cell(w=10,h=5,txt=parsestr(str(T('Medidas propuestas para el próximo curso:'))),border=0,ln=1,align="L",fill=0)

        if ficha.seguimiento_alumno.ord_extra_ev_frances:
            pdf.set_font('','B',10)
            pdf.cell(10)
            pdf.cell(w=10,h=5,txt=parsestr(str(db.seguimiento_alumno.ord_extra_ev_frances.label)),border=0,ln=1,align="L",fill=0)
        if ficha.seguimiento_alumno.ord_extra_ev_dbm:
            pdf.set_font('','B',10)
            pdf.cell(10)
            pdf.cell(w=10,h=5,txt=parsestr(str(db.seguimiento_alumno.ord_extra_ev_dbm.label)),border=0,ln=1,align="L",fill=0)
        if ficha.seguimiento_alumno.ord_extra_ev_lha:
            pdf.set_font('','B',10)
            pdf.cell(10)
            pdf.cell(w=10,h=5,txt=parsestr(str(db.seguimiento_alumno.ord_extra_ev_lha.label)),border=0,ln=1,align="L",fill=0)
        if ficha.seguimiento_alumno.ord_extra_ev_apoyo:
            pdf.set_font('','B',10)
            pdf.cell(10)
            pdf.cell(w=10,h=5,txt=parsestr(str(db.seguimiento_alumno.ord_extra_ev_apoyo.label)),border=0,ln=1,align="L",fill=0)
        if ficha.seguimiento_alumno.ord_extra_ev_compensatoria:
            pdf.set_font('','B',10)
            pdf.cell(10)
            pdf.cell(w=10,h=5,txt=parsestr(str(db.seguimiento_alumno.ord_extra_ev_compensatoria.label)),border=0,ln=1,align="L",fill=0)
        if ficha.seguimiento_alumno.ord_extra_ev_pdc:
            pdf.set_font('','B',10)
            pdf.cell(10)
            pdf.cell(w=10,h=5,txt=parsestr(str(db.seguimiento_alumno.ord_extra_ev_pdc.label)),border=0,ln=1,align="L",fill=0)
        if ficha.seguimiento_alumno.ord_extra_ev_pcpi:
            pdf.set_font('','B',10)
            pdf.cell(10)
            pdf.cell(w=10,h=5,txt=parsestr(str(db.seguimiento_alumno.ord_extra_ev_pcpi.label)),border=0,ln=1,align="L",fill=0)
        if ficha.seguimiento_alumno.ord_extra_ev_adaptaciones:
            pdf.set_font('','B',10)
            pdf.cell(10)
            pdf.cell(w=10,h=5,txt=parsestr(str(db.seguimiento_alumno.ord_extra_ev_adaptaciones.label)),border=0,ln=1,align="L",fill=0)
            pdf.set_font('','',10)
            pdf.cell(15)
            pdf.multi_cell(w=0,h=5,txt=parsestr(ficha.seguimiento_alumno.ord_extra_ev_adaptaciones_especificar),border=0,align="J",fill=1)
            pdf.ln(1)
        if ficha.seguimiento_alumno.ord_extra_ev_otras:
            pdf.set_font('','B',10)
            pdf.cell(10)
            pdf.cell(w=10,h=5,txt=parsestr(str(db.seguimiento_alumno.ord_extra_ev_otras.label)),border=0,ln=1,align="L",fill=0)
            pdf.set_font('','',10)
            pdf.cell(15)
            pdf.multi_cell(w=0,h=5,txt=parsestr(ficha.seguimiento_alumno.ord_extra_ev_otras_especificar),border=0,align="J",fill=1)
            pdf.ln(1)

        pdf.line(10,pdf.get_y(),200,pdf.get_y())
        pdf.set_font('','B',12)
        w=pdf.get_string_width("Competencias Básicas")+6
        pdf.set_x((210-w)/2)
        pdf.cell(w=w,h=17,txt=parsestr("Competencias Básicas"),border=0,ln=1,align='C',fill=0)
        pdf.line(10,pdf.get_y()-5,200,pdf.get_y()-5)
        pdf.set_font('','B',10)
        pdf.cell(w=10,h=5,txt=parsestr(str(T('Competencias básicas que ha adquirido suficientemente el/la'))),border=0,align="L",fill=0)
        pdf.cell(110)
        pdf.cell(w=10,h=5,txt=parsestr(str(T('Altamente'))),border=0,align="C",fill=0)
        pdf.cell(45)
        pdf.cell(w=10,h=5,txt=parsestr(str(T('No'))),border=0,align="C",ln=1,fill=0)
        pdf.cell(w=10,h=5,txt=parsestr(str(T('alumno/a en el proceso de enseñanza-aprendizaje:'))),border=0,align="L",fill=0)
        pdf.cell(110)
        pdf.cell(w=10,h=5,txt=parsestr(str(T('conseguida'))),border=0,align="C",fill=0)
        pdf.cell(17)
        pdf.cell(w=10,h=5,txt=parsestr(str(T('conseguida'))),border=0,align="C",fill=0)
        pdf.cell(17)
        pdf.cell(w=10,h=5,txt=parsestr(str(T('conseguida'))),border=0,align="C",ln=1,fill=0)
        pdf.line(10,pdf.get_y()-1,200,pdf.get_y()-1)
        pdf.ln(1)
        pdf.set_font('','',10)
        pdf.cell(w=115,h=5,txt=parsestr(str(T('Comunicación lingüística'))),border=0,align="L",ln=0,fill=1)
        pdf.cell(1)
        pdf.cell(w=20,h=5,txt=parsestr(str('X' if ficha.seguimiento_alumno.com_bas_com_len_alta else ' ')),align='C',ln=0,fill=1)
        pdf.cell(1)
        pdf.cell(w=30,h=5,txt=parsestr(str('X' if ficha.seguimiento_alumno.com_bas_com_len_cons else ' ')),align='C',ln=0,fill=1)
        pdf.cell(1)
        pdf.cell(w=20,h=5,txt=parsestr(str('X' if ficha.seguimiento_alumno.com_bas_com_len_no else ' ')),align='C',ln=1,fill=1)

        pdf.cell(w=115,h=5,txt=parsestr(str(T('Competencia matemática'))),border=0,align="L",ln=0,fill=0)
        pdf.cell(1)
        pdf.cell(w=20,h=5,txt=parsestr(str('X' if ficha.seguimiento_alumno.com_bas_com_mat_alta else ' ')),align='C',ln=0,fill=0)
        pdf.cell(1)
        pdf.cell(w=30,h=5,txt=parsestr(str('X' if ficha.seguimiento_alumno.com_bas_com_mat_cons else ' ')),align='C',ln=0,fill=0)
        pdf.cell(1)
        pdf.cell(w=20,h=5,txt=parsestr(str('X' if ficha.seguimiento_alumno.com_bas_com_mat_no else ' ')),align='C',ln=1,fill=0)

        pdf.cell(w=115,h=5,txt=parsestr(str(T('Conocicimiento e interacción con el mundo físico'))),border=0,align="L",ln=0,fill=1)
        pdf.cell(1)
        pdf.cell(w=20,h=5,txt=parsestr(str('X' if ficha.seguimiento_alumno.com_bas_con_alta else ' ')),align='C',ln=0,fill=1)
        pdf.cell(1)
        pdf.cell(w=30,h=5,txt=parsestr(str('X' if ficha.seguimiento_alumno.com_bas_con_cons else ' ')),align='C',ln=0,fill=1)
        pdf.cell(1)
        pdf.cell(w=20,h=5,txt=parsestr(str('X' if ficha.seguimiento_alumno.com_bas_con_no else ' ')),align='C',ln=1,fill=1)

        pdf.cell(w=115,h=5,txt=parsestr(str(T('Tratamiento de la información y competencia digital'))),border=0,align="L",ln=0,fill=0)
        pdf.cell(1)
        pdf.cell(w=20,h=5,txt=parsestr(str('X' if ficha.seguimiento_alumno.com_bas_ti_alta else ' ')),align='C',ln=0,fill=0)
        pdf.cell(1)
        pdf.cell(w=30,h=5,txt=parsestr(str('X' if ficha.seguimiento_alumno.com_bas_ti_cons else ' ')),align='C',ln=0,fill=0)
        pdf.cell(1)
        pdf.cell(w=20,h=5,txt=parsestr(str('X' if ficha.seguimiento_alumno.com_bas_ti_no else ' ')),align='C',ln=1,fill=0)

        pdf.cell(w=115,h=5,txt=parsestr(str(T('Competencia social y ciudadana'))),border=0,align="L",ln=0,fill=1)
        pdf.cell(1)
        pdf.cell(w=20,h=5,txt=parsestr(str('X' if ficha.seguimiento_alumno.com_bas_so_alta else ' ')),align='C',ln=0,fill=1)
        pdf.cell(1)
        pdf.cell(w=30,h=5,txt=parsestr(str('X' if ficha.seguimiento_alumno.com_bas_so_cons else ' ')),align='C',ln=0,fill=1)
        pdf.cell(1)
        pdf.cell(w=20,h=5,txt=parsestr(str('X' if ficha.seguimiento_alumno.com_bas_so_no else ' ')),align='C',ln=1,fill=1)

        pdf.cell(w=115,h=5,txt=parsestr(str(T('Competencia cultural y artística'))),border=0,align="L",ln=0,fill=0)
        pdf.cell(1)
        pdf.cell(w=20,h=5,txt=parsestr(str('X' if ficha.seguimiento_alumno.com_bas_cu_alta else ' ')),align='C',ln=0,fill=0)
        pdf.cell(1)
        pdf.cell(w=30,h=5,txt=parsestr(str('X' if ficha.seguimiento_alumno.com_bas_cu_cons else ' ')),align='C',ln=0,fill=0)
        pdf.cell(1)
        pdf.cell(w=20,h=5,txt=parsestr(str('X' if ficha.seguimiento_alumno.com_bas_cu_no else ' ')),align='C',ln=1,fill=0)

        pdf.cell(w=115,h=5,txt=parsestr(str(T('Aprender a aprender'))),border=0,align="L",ln=0,fill=1)
        pdf.cell(1)
        pdf.cell(w=20,h=5,txt=parsestr(str('X' if ficha.seguimiento_alumno.com_bas_ap_alta else ' ')),align='C',ln=0,fill=1)
        pdf.cell(1)
        pdf.cell(w=30,h=5,txt=parsestr(str('X' if ficha.seguimiento_alumno.com_bas_ap_cons else ' ')),align='C',ln=0,fill=1)
        pdf.cell(1)
        pdf.cell(w=20,h=5,txt=parsestr(str('X' if ficha.seguimiento_alumno.com_bas_ap_no else ' ')),align='C',ln=1,fill=1)

        pdf.cell(w=115,h=5,txt=parsestr(str(T('Autonomía e iniciativa personal'))),border=0,align="L",ln=0,fill=0)
        pdf.cell(1)
        pdf.cell(w=20,h=5,txt=parsestr(str('X' if ficha.seguimiento_alumno.com_bas_au_alta else ' ')),align='C',ln=0,fill=0)
        pdf.cell(1)
        pdf.cell(w=30,h=5,txt=parsestr(str('X' if ficha.seguimiento_alumno.com_bas_au_cons else ' ')),align='C',ln=0,fill=0)
        pdf.cell(1)
        pdf.cell(w=20,h=5,txt=parsestr(str('X' if ficha.seguimiento_alumno.com_bas_au_no else ' ')),align='C',ln=1,fill=0)

        pdf.line(10,pdf.get_y(),200,pdf.get_y())

        pdf.set_font('','B',12)
        w=pdf.get_string_width("Otras medidas y aspectos")+6
        pdf.set_x((210-w)/2)
        pdf.cell(w=w,h=17,txt=parsestr("Otras medidas y aspectos"),border=0,ln=1,align='C',fill=0)
        pdf.line(10,pdf.get_y()-5,200,pdf.get_y()-5)
        pdf.set_font('','B',10)
        pdf.cell(w=10,h=5,txt=parsestr(str(db.seguimiento_alumno.medidas_propuestas.label)),border=0,ln=1,align="L",fill=0)
        pdf.cell(15)
        pdf.multi_cell(w=0,h=5,txt=parsestr(ficha.seguimiento_alumno.medidas_propuestas),border=0,align="J",fill=1)
        pdf.ln(1)
        pdf.set_font('','B',10)
        pdf.cell(w=10,h=5,txt=parsestr(str(db.seguimiento_alumno.otros_aspectos.label)),border=0,ln=1,align="L",fill=0)
        pdf.cell(15)
        pdf.multi_cell(w=0,h=5,txt=parsestr(ficha.seguimiento_alumno.otros_aspectos),border=0,align="J",fill=1)
        pdf.ln(1)
        pdf.set_font('','B',10)
        pdf.cell(w=10,h=5,txt=parsestr(str(db.seguimiento_alumno.aspectos_proximo_curso.label)),border=0,ln=1,align="L",fill=0)
        pdf.cell(15)
        pdf.multi_cell(w=0,h=5,txt=parsestr(ficha.seguimiento_alumno.aspectos_proximo_curso),border=0,align="J",fill=1)
        pdf.ln(1)

    response.headers['Content-Type']='application/pdf'
    return pdf.output(dest='S')

@auth.requires_login()
@auth.requires_membership(role='Profesores')
def informefichasanterior():
    idgrupoprofesortutoria = int(request.args[-2]) or redirect('default', 'index')
    idcursoanterior = int(request.args[-1]) or redirect('default', 'index')
    cursoanterior = db(db.curso_academico.id == idcursoanterior).select().first().curso
    grupoactual = db(db.curso_academico_grupo.id == idgrupoprofesortutoria).select().first().id_grupo.grupo
    # comprobemos que somos reponsables o tutor del grupo
    if not session.esResponsable:
        if not session.profesor.esTutor or idgrupoprofesortutoria <> session.profesor.tutor.id_curso_academico_grupo:
            redirect(URL("default","index"))

    #Primero realizamos una lista de los alumnos que tengo en el grupo en cuestión
    query = ((db.grupo_alumno.id_curso_academico_grupo == idgrupoprofesortutoria) &
             (db.grupo_alumno.id_alumno == db.alumno.id))
    idsgrupoalumnosanterior = []
    alumnos = db(query).select()
    for alumno in alumnos:
        q = ((db.grupo_alumno.id_alumno == alumno.grupo_alumno.id_alumno) &
             (db.grupo_alumno.id_curso_academico_grupo == db.curso_academico_grupo.id) &
             (db.curso_academico_grupo.id_curso_academico == idcursoanterior))
        qq = db(q).select().first()
        if qq:
            idsgrupoalumnosanterior.append(qq.grupo_alumno.id)

    queries=[]
    for id in idsgrupoalumnosanterior:
        queries.append(db.seguimiento_alumno.id_grupo_alumno == id)

    query = reduce(lambda a,b:(a|b),queries)
    query &= db.seguimiento_alumno.id_grupo_alumno == db.grupo_alumno.id
    query &= db.grupo_alumno.id_alumno == db.alumno.id

    alumnos_fichas = db(query).select(orderby=db.alumno.apellidos|db.alumno.nombre)
    if len(alumnos_fichas) == 0:
        return "No hay datos"

    logo = os.path.join(request.env.web2py_path,"applications",request.application,"uploads", session.logo_centro)
    titulo = "Ficha del Alumno  del Grupo: "+grupoactual+" Curso "+ cursoanterior
    tnombre = "Alumno/a:"
    tnie = "N.I.E.:"
    tfecha = "Fec.Nac.:"
    tgrupo = "Grupo:"
    ttutor = "Tutor/a:"
    tcentro = session.codigo_centro+' '+session.nombre_centro
    tcurso = session.curso_academico_nombre
    tutor = db.curso_academico_grupo(idgrupoprofesortutoria).id_tutor.apellidos+", "+db.curso_academico_grupo(idgrupoprofesortutoria).id_tutor.nombre
    nombreAlumno = alumnos_fichas[0].grupo_alumno.id_alumno.apellidos+', '+alumnos_fichas[0].grupo_alumno.id_alumno.nombre
    nie = alumnos_fichas[0].grupo_alumno.id_alumno.nie
    fnac = alumnos_fichas[0].grupo_alumno.id_alumno.fecha_nacimiento
    grupo = alumnos_fichas[0].grupo_alumno.id_curso_academico_grupo.id_grupo.grupo
    tutor = '%s, %s' % (alumnos_fichas[0].grupo_alumno.id_curso_academico_grupo.id_tutor.apellidos,
            alumnos_fichas[0].grupo_alumno.id_curso_academico_grupo.id_tutor.nombre)
    cad = alumnos_fichas[0].grupo_alumno.id_alumno.foto.split(".")
    subpath = cad[:2]
    subpath = os.path.join(".".join(subpath), cad[2][:2])
    cad = ".".join(cad)
    foto = os.path.join(request.folder,"uploads",subpath,cad)

    class ficharegistroPDF(FPDF):
        def header(self):
            self.set_font('Arial','B',13)
            #Logo del centro
            self.image(logo,5,5,20,20)
            #Poner código del centro y nombre el la parte izquierda superior
            self.cell(15)
            self.cell(w=0,h=0,txt=parsestr(tcentro),border=0,ln=0,align='L',fill=0)
            #Ahora el curso académico en la parte derecha superior
            self.cell(w=0,h=0,txt="Curso: "+parsestr(tcurso),border=0,ln=1,align='R',fill=0)
            #Dibujamos una linea de separación
            #self.set_line_width(.5)
            #pdf.line(5,13,205,13)
            #Calcular ancho del texto (titulo) y establecer posición
            w=self.get_string_width(titulo)+6
            self.set_x((210-w)/2)
            #Titulo
            self.cell(w=w,h=17,txt=parsestr(titulo),border=0,ln=1,align='C',fill=0)
            #Linea
            self.line(5,23,205,23)
            #Fuente más pequeña sin bold
            self.set_font('','',8)
            #Nombre alumno
            self.cell(w=20,h=0,txt=parsestr(tnombre),border=0,ln=0,align='R',fill=0)
            self.set_font('','B',10)
            self.cell(w=20,h=0,txt=parsestr(nombreAlumno),border=0,ln=1,align="L",fill=0)

            #Foto alumno
            try:
                self.image(foto,180,25,17,22)
            except:
                pass

            #Nie alumno
            self.set_font('','',8)
            self.cell(w=20,h=9,txt=parsestr(tnie),border=0,ln=0,align='R',fill=0)
            self.set_font('','B',10)
            self.cell(w=20,h=9,txt=parsestr(nie),border=0,ln=1,align="L",fill=0)

            #Fecha nacimiento
            self.set_font('','',8)
            self.cell(w=20,h=0,txt=parsestr(tfecha),border=0,ln=0,align='R',fill=0)
            self.set_font('','B',10)
            self.cell(w=20,h=0,txt=fnac.isoformat(),border=0,ln=1,align="L",fill=0)

            #Grupo
            self.set_font('','',8)
            self.cell(w=20,h=9,txt=parsestr(tgrupo),border=0,ln=0,align='R',fill=0)
            self.set_font('','B',10)
            self.cell(w=20,h=9,txt=parsestr(grupo),border=0,ln=1,align="L",fill=0)

            #Tutor
            self.set_font('','',8)
            self.cell(w=20,h=0,txt=parsestr(ttutor),border=0,ln=0,align='R',fill=0)
            self.set_font('','B',10)
            self.cell(w=20,h=0,txt=parsestr(tutor),border=0,ln=1,align="L",fill=0)
            self.line(5,48,205,48)
            #Salto de línea
            self.ln(5)

        def footer(self):
            "hook to draw custom page header (printing page numbers)"
            self.line(5,280,205,280)
            self.set_y(-19)
            self.set_font('Arial','I',8)
            self.cell(w=0,h=9,txt=parsestr(titulo),border=0,ln=0,align='L',fill=0)
            marcaid = parsestr(("Impreso por %s a las %s" % (session.auth.user.first_name+" "+session.auth.user.last_name,datetime.datetime.now().strftime("%H:%M:%S %d/%m/%Y"))))
            self.cell(w=0,h=9,txt=marcaid,border=0,ln=1,align='R',fill=0)
            txt = parsestr('Página')+' %s de %s' % (self.page_no(), self.alias_nb_pages())
            self.cell(w=0,h=0,txt=txt,border=0,ln=0,align='R',fill=0)

    pdf=ficharegistroPDF('P','mm','A4')
    pdf.alias_nb_pages()
    pdf.add_page()
    pdf.set_font('Arial','',8)
    pdf.set_fill_color(230,230,230)
    for ficha in alumnos_fichas:
        if nie != ficha.grupo_alumno.id_alumno.nie:
            # cambiamos de alumno
            nombreAlumno = ficha.grupo_alumno.id_alumno.apellidos+', '+ficha.grupo_alumno.id_alumno.nombre
            nie = ficha.grupo_alumno.id_alumno.nie
            fnac = ficha.grupo_alumno.id_alumno.fecha_nacimiento
            cad = ficha.grupo_alumno.id_alumno.foto.split(".")
            subpath = cad[:2]
            subpath = os.path.join(".".join(subpath), cad[2][:2])
            cad = ".".join(cad)
            foto = os.path.join(request.folder,"uploads",subpath,cad)
            pdf.add_page()
            # habría que ver el grupo y el tutor anterior del nuevo alumno
            # y asignarlo en grupo y tutor
            grupo = ficha.grupo_alumno.id_curso_academico_grupo.id_grupo.grupo
            tutor = '%s, %s' % (ficha.grupo_alumno.id_curso_academico_grupo.id_tutor.apellidos,
                    ficha.grupo_alumno.id_curso_academico_grupo.id_tutor.nombre)

        pdf.set_font('','B',12)
        #Calcular ancho del texto y establecer posición
        w=pdf.get_string_width("Evaluación Inicial")+6
        pdf.set_x((210-w)/2)
        pdf.cell(w=w,h=17,txt=parsestr("Evaluación Inicial"),border=0,ln=1,align='C',fill=0)
        pdf.line(10,62,200,62)
        pdf.set_font('','B',10)
        pdf.cell(w=10,h=5,txt=parsestr(str(db.seguimiento_alumno.inicial_ev_materias_pendientes.label)),border=0,ln=1,align="L",fill=0)
        pdf.cell(15)
        pdf.set_font('','',10)
        pdf.multi_cell(w=0,h=5,txt=parsestr(ficha.seguimiento_alumno.inicial_ev_materias_pendientes),border=0,align="J",fill=1)
        pdf.ln(1)
        pdf.set_font('','B',10)
        pdf.cell(w=10,h=5,txt=parsestr(str(db.seguimiento_alumno.inicial_ev_dificultades_detectadas.label)),border=0,ln=1,align="L",fill=0)
        pdf.set_font('','',10)
        pdf.cell(15)
        pdf.multi_cell(w=0,h=5,txt=parsestr(ficha.seguimiento_alumno.inicial_ev_dificultades_detectadas),border=0,align="J",fill=1)
        pdf.ln(1)
        if ficha.seguimiento_alumno.inicial_ev_refuerzo_indiv_aula:
            pdf.set_font('','B',10)
            pdf.cell(10)
            pdf.cell(w=10,h=5,txt=parsestr(str(db.seguimiento_alumno.inicial_ev_refuerzo_indiv_aula.label)),border=0,ln=1,align="L",fill=0)
        if ficha.seguimiento_alumno.inicial_ev_refuerzo_apoyo_pt:
            pdf.set_font('','B',10)
            pdf.cell(10)
            pdf.cell(w=10,h=5,txt=parsestr(str(db.seguimiento_alumno.inicial_ev_refuerzo_apoyo_pt.label)),border=0,ln=1,align="L",fill=0)
        if ficha.seguimiento_alumno.inicial_ev_refuerzo_apoyo_ec:
            pdf.set_font('','B',10)
            pdf.cell(10)
            pdf.cell(w=10,h=5,txt=parsestr(str(db.seguimiento_alumno.inicial_ev_refuerzo_apoyo_ec.label)),border=0,ln=1,align="L",fill=0)
        if ficha.seguimiento_alumno.inicial_ev_aci_no_significativa:
            pdf.set_font('','B',10)
            pdf.cell(10)
            pdf.cell(w=10,h=5,txt=parsestr(str(db.seguimiento_alumno.inicial_ev_aci_no_significativa.label)),border=0,ln=1,align="L",fill=0)
        if ficha.seguimiento_alumno.inicial_ev_aci_significativa:
            pdf.set_font('','B',10)
            pdf.cell(10)
            pdf.cell(w=10,h=5,txt=parsestr(str(db.seguimiento_alumno.inicial_ev_aci_significativa.label)),border=0,ln=1,align="L",fill=0)
        if ficha.seguimiento_alumno.inicial_ev_otras:
            pdf.set_font('','B',10)
            pdf.cell(10)
            pdf.cell(w=10,h=5,txt=parsestr(str(db.seguimiento_alumno.inicial_ev_otras.label)),border=0,ln=1,align="L",fill=0)
            pdf.set_font('','',10)
            pdf.cell(15)
            pdf.multi_cell(w=0,h=5,txt=parsestr(ficha.seguimiento_alumno.inicial_ev_otras_especificar),border=0,align="J",fill=1)
            pdf.ln(1)

        pdf.line(10,pdf.get_y(),200,pdf.get_y())
        pdf.set_font('','B',12)
        w=pdf.get_string_width("Primera Evaluación")+6
        pdf.set_x((210-w)/2)
        pdf.cell(w=w,h=17,txt=parsestr("Primera Evaluación"),border=0,ln=1,align='C',fill=0)
        pdf.line(10,pdf.get_y()-5,200,pdf.get_y()-5)
        pdf.set_font('','B',10)
        pdf.cell(w=10,h=5,txt=parsestr(str(db.seguimiento_alumno.primera_ev_dificultades.label)),border=0,ln=1,align="L",fill=0)
        pdf.cell(15)
        pdf.multi_cell(w=0,h=5,txt=parsestr(ficha.seguimiento_alumno.primera_ev_dificultades),border=0,align="J",fill=1)
        pdf.ln(1)
        pdf.set_font('','B',10)
        pdf.cell(w=10,h=5,txt=parsestr(str(db.seguimiento_alumno.primera_ev_evolucion.label)),border=0,ln=1,align="L",fill=0)
        pdf.cell(15)
        pdf.multi_cell(w=0,h=5,txt=parsestr(ficha.seguimiento_alumno.primera_ev_evolucion),border=0,align="J",fill=1)
        pdf.ln(1)
        pdf.set_font('','B',10)
        pdf.cell(w=10,h=5,txt=parsestr(str(db.seguimiento_alumno.primera_ev_decisiones.label)),border=0,ln=1,align="L",fill=0)
        pdf.cell(15)
        pdf.multi_cell(w=0,h=5,txt=parsestr(ficha.seguimiento_alumno.primera_ev_decisiones),border=0,align="J",fill=1)
        pdf.ln(1)

        pdf.line(10,pdf.get_y(),200,pdf.get_y())
        pdf.set_font('','B',12)
        w=pdf.get_string_width("Segunda Evaluación")+6
        pdf.set_x((210-w)/2)
        pdf.cell(w=w,h=17,txt=parsestr("Segunda Evaluación"),border=0,ln=1,align='C',fill=0)
        pdf.line(10,pdf.get_y()-5,200,pdf.get_y()-5)
        pdf.set_font('','B',10)
        pdf.cell(w=10,h=5,txt=parsestr(str(db.seguimiento_alumno.segunda_ev_dificultades.label)),border=0,ln=1,align="L",fill=0)
        pdf.cell(15)
        pdf.multi_cell(w=0,h=5,txt=parsestr(ficha.seguimiento_alumno.segunda_ev_dificultades),border=0,align="J",fill=1)
        pdf.ln(1)
        pdf.set_font('','B',10)
        pdf.cell(w=10,h=5,txt=parsestr(str(db.seguimiento_alumno.segunda_ev_evolucion.label)),border=0,ln=1,align="L",fill=0)
        pdf.cell(15)
        pdf.multi_cell(w=0,h=5,txt=parsestr(ficha.seguimiento_alumno.segunda_ev_evolucion),border=0,align="J",fill=1)
        pdf.ln(1)
        pdf.set_font('','B',10)
        pdf.cell(w=10,h=5,txt=parsestr(str(db.seguimiento_alumno.segunda_ev_decisiones.label)),border=0,ln=1,align="L",fill=0)
        pdf.cell(15)
        pdf.multi_cell(w=0,h=5,txt=parsestr(ficha.seguimiento_alumno.segunda_ev_decisiones),border=0,align="J",fill=1)
        pdf.ln(1)

        pdf.line(10,pdf.get_y(),200,pdf.get_y())
        pdf.set_font('','B',12)
        w=pdf.get_string_width("Evaluación Ordinaria-Extraordinaria")+6
        pdf.set_x((210-w)/2)
        pdf.cell(w=w,h=17,txt=parsestr("Evaluación Ordinaria-Extraordinaria"),border=0,ln=1,align='C',fill=0)
        pdf.line(10,pdf.get_y()-5,200,pdf.get_y()-5)
        pdf.set_font('','B',10)
        pdf.cell(w=10,h=5,txt=parsestr(str(T('Decisión adoptada:'))),border=0,ln=0,align="L",fill=0)
        if ficha.seguimiento_alumno.ord_extra_ev_promocion:
            pdf.cell(40)
            pdf.cell(w=10,h=5,txt=parsestr(str(db.seguimiento_alumno.ord_extra_ev_promocion.label)),border=0,ln=1,align="L",fill=0)
        elif ficha.seguimiento_alumno.ord_extra_ev_promocion_automatica:
            pdf.cell(40)
            pdf.cell(w=10,h=5,txt=parsestr(str(db.seguimiento_alumno.ord_extra_ev_promocion_automatica.label)),border=0,ln=1,align="L",fill=0)
        elif ficha.seguimiento_alumno.ord_extra_ev_repetir:
            pdf.cell(40)
            pdf.cell(w=10,h=5,txt=parsestr(str(db.seguimiento_alumno.ord_extra_ev_repetir.label)),border=0,ln=1,align="L",fill=0)
        else:
            pdf.cell(40)
            pdf.cell(w=10,h=5,txt=parsestr(str(T('Ninguna marcada'))),border=0,ln=1,align="L",fill=0)
        pdf.set_font('','B',10)
        pdf.cell(w=10,h=5,txt=parsestr(str(db.seguimiento_alumno.ord_extra_ev_asignatura_pendientes.label)),border=0,ln=1,align="L",fill=0)
        pdf.cell(15)
        pdf.multi_cell(w=0,h=5,txt=parsestr(ficha.seguimiento_alumno.ord_extra_ev_asignatura_pendientes),border=0,align="J",fill=1)
        pdf.ln(1)
        pdf.set_font('','B',10)
        pdf.cell(w=10,h=5,txt=parsestr(str(T('Medidas propuestas para el próximo curso:'))),border=0,ln=1,align="L",fill=0)

        if ficha.seguimiento_alumno.ord_extra_ev_frances:
            pdf.set_font('','B',10)
            pdf.cell(10)
            pdf.cell(w=10,h=5,txt=parsestr(str(db.seguimiento_alumno.ord_extra_ev_frances.label)),border=0,ln=1,align="L",fill=0)
        if ficha.seguimiento_alumno.ord_extra_ev_dbm:
            pdf.set_font('','B',10)
            pdf.cell(10)
            pdf.cell(w=10,h=5,txt=parsestr(str(db.seguimiento_alumno.ord_extra_ev_dbm.label)),border=0,ln=1,align="L",fill=0)
        if ficha.seguimiento_alumno.ord_extra_ev_lha:
            pdf.set_font('','B',10)
            pdf.cell(10)
            pdf.cell(w=10,h=5,txt=parsestr(str(db.seguimiento_alumno.ord_extra_ev_lha.label)),border=0,ln=1,align="L",fill=0)
        if ficha.seguimiento_alumno.ord_extra_ev_apoyo:
            pdf.set_font('','B',10)
            pdf.cell(10)
            pdf.cell(w=10,h=5,txt=parsestr(str(db.seguimiento_alumno.ord_extra_ev_apoyo.label)),border=0,ln=1,align="L",fill=0)
        if ficha.seguimiento_alumno.ord_extra_ev_compensatoria:
            pdf.set_font('','B',10)
            pdf.cell(10)
            pdf.cell(w=10,h=5,txt=parsestr(str(db.seguimiento_alumno.ord_extra_ev_compensatoria.label)),border=0,ln=1,align="L",fill=0)
        if ficha.seguimiento_alumno.ord_extra_ev_pdc:
            pdf.set_font('','B',10)
            pdf.cell(10)
            pdf.cell(w=10,h=5,txt=parsestr(str(db.seguimiento_alumno.ord_extra_ev_pdc.label)),border=0,ln=1,align="L",fill=0)
        if ficha.seguimiento_alumno.ord_extra_ev_pcpi:
            pdf.set_font('','B',10)
            pdf.cell(10)
            pdf.cell(w=10,h=5,txt=parsestr(str(db.seguimiento_alumno.ord_extra_ev_pcpi.label)),border=0,ln=1,align="L",fill=0)
        if ficha.seguimiento_alumno.ord_extra_ev_adaptaciones:
            pdf.set_font('','B',10)
            pdf.cell(10)
            pdf.cell(w=10,h=5,txt=parsestr(str(db.seguimiento_alumno.ord_extra_ev_adaptaciones.label)),border=0,ln=1,align="L",fill=0)
            pdf.set_font('','',10)
            pdf.cell(15)
            pdf.multi_cell(w=0,h=5,txt=parsestr(ficha.seguimiento_alumno.ord_extra_ev_adaptaciones_especificar),border=0,align="J",fill=1)
            pdf.ln(1)
        if ficha.seguimiento_alumno.ord_extra_ev_otras:
            pdf.set_font('','B',10)
            pdf.cell(10)
            pdf.cell(w=10,h=5,txt=parsestr(str(db.seguimiento_alumno.ord_extra_ev_otras.label)),border=0,ln=1,align="L",fill=0)
            pdf.set_font('','',10)
            pdf.cell(15)
            pdf.multi_cell(w=0,h=5,txt=parsestr(ficha.seguimiento_alumno.ord_extra_ev_otras_especificar),border=0,align="J",fill=1)
            pdf.ln(1)

        pdf.line(10,pdf.get_y(),200,pdf.get_y())
        pdf.set_font('','B',12)
        w=pdf.get_string_width("Competencias Básicas")+6
        pdf.set_x((210-w)/2)
        pdf.cell(w=w,h=17,txt=parsestr("Competencias Básicas"),border=0,ln=1,align='C',fill=0)
        pdf.line(10,pdf.get_y()-5,200,pdf.get_y()-5)
        pdf.set_font('','B',10)
        pdf.cell(w=10,h=5,txt=parsestr(str(T('Competencias básicas que ha adquirido suficientemente el/la'))),border=0,align="L",fill=0)
        pdf.cell(110)
        pdf.cell(w=10,h=5,txt=parsestr(str(T('Altamente'))),border=0,align="C",fill=0)
        pdf.cell(45)
        pdf.cell(w=10,h=5,txt=parsestr(str(T('No'))),border=0,align="C",ln=1,fill=0)
        pdf.cell(w=10,h=5,txt=parsestr(str(T('alumno/a en el proceso de enseñanza-aprendizaje:'))),border=0,align="L",fill=0)
        pdf.cell(110)
        pdf.cell(w=10,h=5,txt=parsestr(str(T('conseguida'))),border=0,align="C",fill=0)
        pdf.cell(17)
        pdf.cell(w=10,h=5,txt=parsestr(str(T('conseguida'))),border=0,align="C",fill=0)
        pdf.cell(17)
        pdf.cell(w=10,h=5,txt=parsestr(str(T('conseguida'))),border=0,align="C",ln=1,fill=0)
        pdf.line(10,pdf.get_y()-1,200,pdf.get_y()-1)
        pdf.ln(1)
        pdf.set_font('','',10)
        pdf.cell(w=115,h=5,txt=parsestr(str(T('Comunicación lingüística'))),border=0,align="L",ln=0,fill=1)
        pdf.cell(1)
        pdf.cell(w=20,h=5,txt=parsestr(str('X' if ficha.seguimiento_alumno.com_bas_com_len_alta else ' ')),align='C',ln=0,fill=1)
        pdf.cell(1)
        pdf.cell(w=30,h=5,txt=parsestr(str('X' if ficha.seguimiento_alumno.com_bas_com_len_cons else ' ')),align='C',ln=0,fill=1)
        pdf.cell(1)
        pdf.cell(w=20,h=5,txt=parsestr(str('X' if ficha.seguimiento_alumno.com_bas_com_len_no else ' ')),align='C',ln=1,fill=1)

        pdf.cell(w=115,h=5,txt=parsestr(str(T('Competencia matemática'))),border=0,align="L",ln=0,fill=0)
        pdf.cell(1)
        pdf.cell(w=20,h=5,txt=parsestr(str('X' if ficha.seguimiento_alumno.com_bas_com_mat_alta else ' ')),align='C',ln=0,fill=0)
        pdf.cell(1)
        pdf.cell(w=30,h=5,txt=parsestr(str('X' if ficha.seguimiento_alumno.com_bas_com_mat_cons else ' ')),align='C',ln=0,fill=0)
        pdf.cell(1)
        pdf.cell(w=20,h=5,txt=parsestr(str('X' if ficha.seguimiento_alumno.com_bas_com_mat_no else ' ')),align='C',ln=1,fill=0)

        pdf.cell(w=115,h=5,txt=parsestr(str(T('Conocicimiento e interacción con el mundo físico'))),border=0,align="L",ln=0,fill=1)
        pdf.cell(1)
        pdf.cell(w=20,h=5,txt=parsestr(str('X' if ficha.seguimiento_alumno.com_bas_con_alta else ' ')),align='C',ln=0,fill=1)
        pdf.cell(1)
        pdf.cell(w=30,h=5,txt=parsestr(str('X' if ficha.seguimiento_alumno.com_bas_con_cons else ' ')),align='C',ln=0,fill=1)
        pdf.cell(1)
        pdf.cell(w=20,h=5,txt=parsestr(str('X' if ficha.seguimiento_alumno.com_bas_con_no else ' ')),align='C',ln=1,fill=1)

        pdf.cell(w=115,h=5,txt=parsestr(str(T('Tratamiento de la información y competencia digital'))),border=0,align="L",ln=0,fill=0)
        pdf.cell(1)
        pdf.cell(w=20,h=5,txt=parsestr(str('X' if ficha.seguimiento_alumno.com_bas_ti_alta else ' ')),align='C',ln=0,fill=0)
        pdf.cell(1)
        pdf.cell(w=30,h=5,txt=parsestr(str('X' if ficha.seguimiento_alumno.com_bas_ti_cons else ' ')),align='C',ln=0,fill=0)
        pdf.cell(1)
        pdf.cell(w=20,h=5,txt=parsestr(str('X' if ficha.seguimiento_alumno.com_bas_ti_no else ' ')),align='C',ln=1,fill=0)

        pdf.cell(w=115,h=5,txt=parsestr(str(T('Competencia social y ciudadana'))),border=0,align="L",ln=0,fill=1)
        pdf.cell(1)
        pdf.cell(w=20,h=5,txt=parsestr(str('X' if ficha.seguimiento_alumno.com_bas_so_alta else ' ')),align='C',ln=0,fill=1)
        pdf.cell(1)
        pdf.cell(w=30,h=5,txt=parsestr(str('X' if ficha.seguimiento_alumno.com_bas_so_cons else ' ')),align='C',ln=0,fill=1)
        pdf.cell(1)
        pdf.cell(w=20,h=5,txt=parsestr(str('X' if ficha.seguimiento_alumno.com_bas_so_no else ' ')),align='C',ln=1,fill=1)

        pdf.cell(w=115,h=5,txt=parsestr(str(T('Competencia cultural y artística'))),border=0,align="L",ln=0,fill=0)
        pdf.cell(1)
        pdf.cell(w=20,h=5,txt=parsestr(str('X' if ficha.seguimiento_alumno.com_bas_cu_alta else ' ')),align='C',ln=0,fill=0)
        pdf.cell(1)
        pdf.cell(w=30,h=5,txt=parsestr(str('X' if ficha.seguimiento_alumno.com_bas_cu_cons else ' ')),align='C',ln=0,fill=0)
        pdf.cell(1)
        pdf.cell(w=20,h=5,txt=parsestr(str('X' if ficha.seguimiento_alumno.com_bas_cu_no else ' ')),align='C',ln=1,fill=0)

        pdf.cell(w=115,h=5,txt=parsestr(str(T('Aprender a aprender'))),border=0,align="L",ln=0,fill=1)
        pdf.cell(1)
        pdf.cell(w=20,h=5,txt=parsestr(str('X' if ficha.seguimiento_alumno.com_bas_ap_alta else ' ')),align='C',ln=0,fill=1)
        pdf.cell(1)
        pdf.cell(w=30,h=5,txt=parsestr(str('X' if ficha.seguimiento_alumno.com_bas_ap_cons else ' ')),align='C',ln=0,fill=1)
        pdf.cell(1)
        pdf.cell(w=20,h=5,txt=parsestr(str('X' if ficha.seguimiento_alumno.com_bas_ap_no else ' ')),align='C',ln=1,fill=1)

        pdf.cell(w=115,h=5,txt=parsestr(str(T('Autonomía e iniciativa personal'))),border=0,align="L",ln=0,fill=0)
        pdf.cell(1)
        pdf.cell(w=20,h=5,txt=parsestr(str('X' if ficha.seguimiento_alumno.com_bas_au_alta else ' ')),align='C',ln=0,fill=0)
        pdf.cell(1)
        pdf.cell(w=30,h=5,txt=parsestr(str('X' if ficha.seguimiento_alumno.com_bas_au_cons else ' ')),align='C',ln=0,fill=0)
        pdf.cell(1)
        pdf.cell(w=20,h=5,txt=parsestr(str('X' if ficha.seguimiento_alumno.com_bas_au_no else ' ')),align='C',ln=1,fill=0)

        pdf.line(10,pdf.get_y(),200,pdf.get_y())

        pdf.set_font('','B',12)
        w=pdf.get_string_width("Otras medidas y aspectos")+6
        pdf.set_x((210-w)/2)
        pdf.cell(w=w,h=17,txt=parsestr("Otras medidas y aspectos"),border=0,ln=1,align='C',fill=0)
        pdf.line(10,pdf.get_y()-5,200,pdf.get_y()-5)
        pdf.set_font('','B',10)
        pdf.cell(w=10,h=5,txt=parsestr(str(db.seguimiento_alumno.medidas_propuestas.label)),border=0,ln=1,align="L",fill=0)
        pdf.cell(15)
        pdf.multi_cell(w=0,h=5,txt=parsestr(ficha.seguimiento_alumno.medidas_propuestas),border=0,align="J",fill=1)
        pdf.ln(1)
        pdf.set_font('','B',10)
        pdf.cell(w=10,h=5,txt=parsestr(str(db.seguimiento_alumno.otros_aspectos.label)),border=0,ln=1,align="L",fill=0)
        pdf.cell(15)
        pdf.multi_cell(w=0,h=5,txt=parsestr(ficha.seguimiento_alumno.otros_aspectos),border=0,align="J",fill=1)
        pdf.ln(1)
        pdf.set_font('','B',10)
        pdf.cell(w=10,h=5,txt=parsestr(str(db.seguimiento_alumno.aspectos_proximo_curso.label)),border=0,ln=1,align="L",fill=0)
        pdf.cell(15)
        pdf.multi_cell(w=0,h=5,txt=parsestr(ficha.seguimiento_alumno.aspectos_proximo_curso),border=0,align="J",fill=1)
        pdf.ln(1)

    response.headers['Content-Type']='application/pdf'
    return pdf.output(dest='S')








@auth.requires_login()
@auth.requires_membership(role='Profesores')
def informeagrupado():
    todoelcurso = True
    if request.vars["idevaluacion"]:
        todoelcurso = False
        idevaluacion = int(request.vars["idevaluacion"])

    if request.vars["idgrupos"]:
        idgrupos=request.vars["idgrupos"].split(',')
        idgrupos=[int(grupo) for grupo in idgrupos]
    else:
        redirect(URL("default","index"))    

    # comprobemos que somos reponsables o tutor del grupo
    if not session.esResponsable:
        redirect(URL("default","index"))    

    query = ((db.curso_academico_grupo.id.belongs(idgrupos)) &
             (db.curso_academico_grupo.id_grupo == db.grupo.id) &
             (db.grupo_profesor.id_curso_academico_grupo == db.curso_academico_grupo.id) &
             (db.grupo_profesor_asignatura.id_grupo_profesor == db.grupo_profesor.id) &
             (db.grupo_profesor_asignatura.id_asignatura == db.asignatura.id) &
             (db.grupo_profesor_asignatura.id_grupo_profesor == db.grupo_profesor.id) &
             (db.grupo_profesor.id_profesor == db.profesor.id) &
             (db.grupo_profesor_asignatura_alumno.id_grupo_profesor_asignatura == db.grupo_profesor_asignatura.id) &
             (db.grupo_profesor_asignatura_alumno.id_grupo_alumno == db.grupo_alumno.id) &
             (db.grupo_alumno.id_alumno == db.alumno.id) &
             (db.evaluacion_alumno.id_grupo_profesor_asignatura_alumno == db.grupo_profesor_asignatura_alumno.id) &
             (db.evaluacion_alumno.id_curso_academico_evaluacion == db.curso_academico_evaluacion.id))

    if not todoelcurso:
        query &= db.evaluacion_alumno.id_curso_academico_evaluacion == idevaluacion

    evaluaciones = db(query).select()

    if len(evaluaciones) == 0:
        return "No hay datos"
    logo = os.path.join(request.env.web2py_path,"applications",request.application,"uploads", session.logo_centro)
    if todoelcurso:
        titulo = "Hoja Resumen de Evaluación de Grupos Anual"
    else:
        titulo = "Hoja Resumen de Evaluación de Grupos para "+db.curso_academico_evaluacion(idevaluacion).evaluacion

    tgrupo = "Grupos:"
    grupo = ""
    tutor = ""
    for gr in idgrupos:
        grupo += db.curso_academico_grupo(gr).id_grupo.grupo+" "
        tutor += db.curso_academico_grupo(gr).id_grupo.grupo+": "+ \
            db.curso_academico_grupo(gr).id_tutor.apellidos+", "+db.curso_academico_grupo(gr).id_tutor.nombre+" "
    tcentro = session.codigo_centro+' '+session.nombre_centro
    tcurso = session.curso_academico_nombre
    ttutor = "Tutores:"
    nevaluaciones = len(evaluaciones) or 1
    class informeagrupadoPDF(FPDF):
        def header(self):
            self.set_font('Arial','B',15)
            #Logo del centro
            self.image(logo,5,5,20,20)
            #Poner código del centro y nombre el la parte izquierda superior
            self.cell(15)
            self.cell(w=0,h=0,txt=parsestr(tcentro),border=0,ln=0,align='L',fill=0)
            #Ahora el curso académico en la parte derecha superior
            self.cell(w=0,h=0,txt="Curso: "+parsestr(tcurso),border=0,ln=1,align='R',fill=0)
            #Dibujamos una linea de separación
            #self.set_line_width(.5)
            #pdf.line(5,13,205,13)
            #Calcular ancho del texto (titulo) y establecer posición
            w=self.get_string_width(titulo)+6
            self.set_x((297-w)/2)
            #Titulo
            self.cell(w=w,h=17,txt=parsestr(titulo),border=0,ln=1,align='C',fill=0)
            #Linea
            self.line(5,23,290,23)

            pdf.set_font('','',8)      
            
            pdf.cell(w=20,h=0,txt=parsestr(tgrupo),border=0,ln=0,align='R',fill=0)
            pdf.set_font('','B',10)                        
            pdf.cell(w=20,h=0,txt=parsestr(grupo),border=0,ln=1,align="L",fill=0)
            
            pdf.set_font('','',8)                        
            pdf.cell(w=20,h=9,txt=parsestr(ttutor),border=0,ln=0,align='R',fill=0)            
            pdf.set_font('','B',10)                                    
            pdf.cell(w=20,h=9,txt=parsestr(tutor),border=0,ln=1,align="L",fill=0)
           
            pdf.line(5,35,290,35)
            
            pdf.set_font('','B',9)
            pdf.cell(w=10,h=9,txt=parsestr("Asignatura"))
            pdf.cell(75)
            pdf.line(75,40,160,40)
            pdf.cell(w=10,h=4,txt=parsestr("Aspectos académicos"))
            pdf.cell(85)            
            pdf.cell(w=10,h=4,txt=parsestr("Aspectos actitudinales"))
            pdf.line(170,40,250,40)
            pdf.cell(20)            
            pdf.cell(w=0,h=9,txt=parsestr("Medias asignaturas"),align="R")
            pdf.ln(7)
            pdf.cell(70)            
            pdf.cell(w=10,h=0,txt=parsestr("Nivel"))
            pdf.cell(8)           
            pdf.cell(w=10,h=0,txt=parsestr("Trabajo en clase"))
            pdf.cell(20)           
            pdf.cell(w=10,h=0,txt=parsestr("Trabajo en casa"))
            pdf.cell(40)           
            pdf.cell(w=10,h=0,txt=parsestr("Interés"))
            pdf.cell(10)           
            pdf.cell(w=10,h=0,txt=parsestr("Participa"))
            pdf.cell(10)           
            pdf.cell(w=10,h=0,txt=parsestr("Comportamiento"))
            pdf.line(5,45,290,45)
            #Salto de línea
            pdf.ln(5)            
            
            
    pdf=informeagrupadoPDF('L','mm','A4')
    pdf.alias_nb_pages()
    pdf.add_page()
    pdf.set_font('Arial','',8)
    pdf.set_fill_color(230,230,230)    
    datos = {}
    for evaluacion in evaluaciones:
        if evaluacion.asignatura.abreviatura not in datos.keys():
            datos[evaluacion.asignatura.abreviatura] = {"evaluacion":evaluacion.evaluacion_alumno.evaluacion,
                        "asignatura":evaluacion.asignatura.asignatura[:46-len(evaluacion.asignatura.abreviatura)]+" ("+evaluacion.asignatura.abreviatura+")",
                        "aspectos": {"NIV":evaluacion.evaluacion_alumno.nivel,
                                     "TCL":evaluacion.evaluacion_alumno.trabajo_clase,
                                     "TCA":evaluacion.evaluacion_alumno.trabajo_casa,
                                     "INT":evaluacion.evaluacion_alumno.interes,
                                     "PART":evaluacion.evaluacion_alumno.participa,
                                     "COMP":evaluacion.evaluacion_alumno.comportamiento},
                        "nalumnos":1}
                                     
        else:
            datos[evaluacion.asignatura.abreviatura]["evaluacion"] +=  evaluacion.evaluacion_alumno.evaluacion
            datos[evaluacion.asignatura.abreviatura]["aspectos"]["NIV"] += evaluacion.evaluacion_alumno.nivel
            datos[evaluacion.asignatura.abreviatura]["aspectos"]["TCL"] += evaluacion.evaluacion_alumno.trabajo_clase
            datos[evaluacion.asignatura.abreviatura]["aspectos"]["TCA"] += evaluacion.evaluacion_alumno.trabajo_casa
            datos[evaluacion.asignatura.abreviatura]["aspectos"]["INT"] += evaluacion.evaluacion_alumno.interes
            datos[evaluacion.asignatura.abreviatura]["aspectos"]["PART"] += evaluacion.evaluacion_alumno.participa
            datos[evaluacion.asignatura.abreviatura]["aspectos"]["COMP"] += evaluacion.evaluacion_alumno.comportamiento
            datos[evaluacion.asignatura.abreviatura]["nalumnos"] += 1
    
    for asignatura in datos.keys():
        datos[asignatura]["evaluacion"] = float(datos[asignatura]["evaluacion"])/datos[asignatura]["nalumnos"]
        datos[asignatura]["aspectos"]["NIV"] = (float(datos[asignatura]["aspectos"]["NIV"])/datos[asignatura]["nalumnos"])
        datos[asignatura]["aspectos"]["TCL"] = (float(datos[asignatura]["aspectos"]["TCL"])/datos[asignatura]["nalumnos"])/10
        datos[asignatura]["aspectos"]["TCA"] = (float(datos[asignatura]["aspectos"]["TCA"])/datos[asignatura]["nalumnos"])/10
        datos[asignatura]["aspectos"]["INT"] = (float(datos[asignatura]["aspectos"]["INT"])/datos[asignatura]["nalumnos"])/10
        datos[asignatura]["aspectos"]["PART"] = (float(datos[asignatura]["aspectos"]["PART"])/datos[asignatura]["nalumnos"])/10
        datos[asignatura]["aspectos"]["COMP"] = (float(datos[asignatura]["aspectos"]["COMP"])/datos[asignatura]["nalumnos"])/10
       
        
        #esto no es correcto, debemos tener en cuenta criterios de evaluación de asignatura->departamento->centro
        #miremos en la tabla de asignaturas si esa asignatura usa criterios
        (peso1,peso2,peso3,peso4,peso5,peso6) = (0.0,0.0,0.0,0.0,0.0,0.0)
        asignaturarow = db(db.asignatura.abreviatura==asignatura).select().first()
        if asignaturarow.usar_criterios_asignatura:
            (peso1,peso2,peso3,peso4,peso5,peso6) = (asignaturarow.peso_1,asignaturarow.peso_2,asignaturarow.peso_3,
                                                   asignaturarow.peso_4,asignaturarow.peso_5,asignaturarow.peso_6)            
        elif asignaturarow.id_departamento.usar_criterios_departamento:
            (peso1,peso2,peso3,peso4,peso5,peso6) = (asignaturarow.id_departamento.peso_1,asignaturarow.id_departamento.peso_2,
                                                   asignaturarow.id_departamento.peso_3,asignaturarow.id_departamento.peso_4,
                                                   asignaturarow.id_departamento.peso_5,asignaturarow.id_departamento.peso_6)
        else:                                                   
            (peso1,peso2,peso3,peso4,peso5,peso6) = (evaluaciones[0].curso_academico_evaluacion.id_curso_academico.peso_1,
                                                   evaluaciones[0].curso_academico_evaluacion.id_curso_academico.peso_2,
                                                   evaluaciones[0].curso_academico_evaluacion.id_curso_academico.peso_3,
                                                   evaluaciones[0].curso_academico_evaluacion.id_curso_academico.peso_4,
                                                   evaluaciones[0].curso_academico_evaluacion.id_curso_academico.peso_5,
                                                   evaluaciones[0].curso_academico_evaluacion.id_curso_academico.peso_6)                                                   
            
        datos[asignatura]["evaluacion"] = (datos[asignatura]["aspectos"]["NIV"]*float(peso1) +
                                           datos[asignatura]["aspectos"]["TCL"]*float(peso2) +
                                           datos[asignatura]["aspectos"]["TCA"]*float(peso3) +
                                           datos[asignatura]["aspectos"]["INT"]*float(peso4) +
                                           datos[asignatura]["aspectos"]["PART"]*float(peso5) +
                                           datos[asignatura]["aspectos"]["COMP"]*float(peso6))/100
           
    linea = 1
    for asignatura in sorted(datos.iterkeys()):
        # imprime resumen de asignatura
        if linea % 2 <> 0:
            # imprimimos relleno de fondo
            fill = 1
        else:
            fill = 0

        pdf.set_fill_color(230,230,230)    
        pdf.set_font('','',8)
        pdf.cell(w=50,h=5,txt=parsestr(datos[asignatura]["asignatura"]),border=0,ln=0,align="L",fill=fill)
        pdf.cell(10,h=5,fill=fill)
        nivel = datos[asignatura]["aspectos"]["NIV"]
        pdf.cell(w=30,h=5,txt=parsestr(str('%.02f' % nivel)),align="C",fill=fill)
        trabajo_clase = datos[asignatura]["aspectos"]["TCL"]
        pdf.cell(w=25,h=5,txt=parsestr(str('%.02f' %  trabajo_clase)),align="C",fill=fill)
        trabajo_casa = datos[asignatura]["aspectos"]["TCA"]
        pdf.cell(w=30,h=5,txt=parsestr(str('%.02f' % trabajo_casa)),align="C",fill=fill)
        pdf.cell(20,h=5,fill=fill)
        interes = datos[asignatura]["aspectos"]["INT"]
        pdf.cell(w=20,h=5,txt=parsestr(str('%.02f' % interes)),align="C",fill=fill)
        #pdf.cell(10,fill=fill)
        participa = datos[asignatura]["aspectos"]["PART"]
        pdf.cell(w=20,h=5,txt=parsestr(str('%.02f' % participa)),align="C",fill=fill)
        #pdf.cell(15,fill=fill)
        comportamiento = datos[asignatura]["aspectos"]["COMP"]
        pdf.cell(w=30,h=5,txt=parsestr(str('%.02f' % comportamiento)),align="C",fill=fill)
        pdf.cell(w=10,h=5,fill=fill)
        pdf.set_fill_color(200,200,200)           
        pdf.set_font('','B',9)
        border = "TLR" if linea == 1 else "LR"      
        evalua = datos[asignatura]["evaluacion"]             
        pdf.cell(w=0,h=5,txt=parsestr(str('%.02f' % evalua)),border=border,align="R",fill=1,ln=1)
        # aumentamos el contador de linea
        linea += 1

    # estadísticas generales
    sumanivel = 0
    sumatrclase = 0
    sumatrcasa = 0
    sumainteres = 0
    sumaparticipa = 0
    sumacomportamiento = 0
    sumaevaluacion = 0
    for asignatura in datos.keys():
        sumanivel += datos[asignatura]["aspectos"]["NIV"]
        sumatrclase += datos[asignatura]["aspectos"]["TCL"]
        sumatrcasa += datos[asignatura]["aspectos"]["TCA"]
        sumainteres += datos[asignatura]["aspectos"]["INT"]
        sumaparticipa += datos[asignatura]["aspectos"]["PART"]
        sumacomportamiento += datos[asignatura]["aspectos"]["COMP"]
        sumaevaluacion += datos[asignatura]["evaluacion"]
    
    nl = len(datos.keys())    
    pdf.set_fill_color(200,200,200)    
    pdf.set_font('','B',9)                        
    pdf.cell(w=50,h=5,txt=parsestr(str("Estadísticas de la evaluación")),border="LTB",ln=0,align="L",fill=1)
    pdf.cell(10,h=5,border="TB",fill=1)
    nivel = sumanivel/float(nl)
    pdf.cell(w=30,h=5,txt=parsestr(str('%.02f' % nivel)),border="TB",align="C",fill=1)
    trabajo_clase = sumatrclase/float(nl)       
    pdf.cell(w=25,h=5,txt=parsestr(str('%.02f' % trabajo_clase)),border="TB",align="C",fill=1)
    trabajo_casa = sumatrcasa/float(nl)
    pdf.cell(w=30,h=5,txt=parsestr(str('%.02f' % trabajo_casa)),border="TB",align="C",fill=1)
    pdf.cell(20,h=5,border="TB",fill=1)
    interes = sumainteres/float(nl)
    pdf.cell(w=20,h=5,txt=parsestr(str('%.02f' % interes)),border="TB",align="C",fill=1)
    participa = sumaparticipa/float(nl)
    pdf.cell(w=20,h=5,txt=parsestr(str('%.02f' % participa)),border="TB",align="C",fill=1)
    comportamiento = sumacomportamiento/float(nl)
    pdf.cell(w=30,h=5,txt=parsestr(str('%.02f' % comportamiento)),border="TB",align="C",fill=1)
    pdf.cell(w=10,h=5,border="TB",fill=1)
    evalua = (sumaevaluacion/(nl))
    pdf.set_font('','B',10)                            
    pdf.cell(w=0,h=5,txt=parsestr(str('%.02f' % evalua)),border=1,align="R",fill=1)
    fichero=os.path.join(request.folder,"uploads",str(uuid.uuid4())+".png")
    d = {}
    for asignatura in datos.keys():
        d[asignatura] = datos[asignatura]["evaluacion"] 
    genera_grafico_asignaturas(fichero, d)
    graf = os.path.join(fichero)
    pdf.image(graf,10,150)    
    os.unlink(graf)
    fichero=os.path.join(request.folder,"uploads",str(uuid.uuid4())+".png") 
    genera_grafico_aspectos(fichero, {"NIV":nivel, "TCL":trabajo_clase,
                                      "TCA":trabajo_casa, "INT":interes,
                                      "PART":participa, "COMP":comportamiento})
    graf = os.path.join(fichero)
    pdf.image(graf,200,150)    
    os.unlink(graf)
    response.headers['Content-Type']='application/pdf'
    return pdf.output(dest='S')
