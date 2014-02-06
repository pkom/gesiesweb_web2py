# coding: utf8

from plugin_solidform import SOLIDFORM

crud.settings.controller = 'seguimiento' 

def index(): return dict(message="hello from seguimiento.py")

@auth.requires_login()
@auth.requires_membership(role='Profesores')    
def seguimiento_tutoria():
    # comprobemos que somos tutores, sino nada
    if not session.profesor.esTutor:
        redirect(URL("default","index"))
    query = ((db.grupo_alumno.id_curso_academico_grupo == session.profesor.tutor.id_curso_academico_grupo) &
             (db.grupo_alumno.id_alumno == db.alumno.id))
    alumnos_grupo = db(query).select()
    for alumno in alumnos_grupo:
    	db.seguimiento_alumno.update_or_insert(id_grupo_alumno = alumno.grupo_alumno.id)
    query = ((db.grupo_alumno.id_curso_academico_grupo == session.profesor.tutor.id_curso_academico_grupo) &
             (db.grupo_alumno.id_alumno == db.alumno.id) &
             (db.grupo_alumno.id == db.seguimiento_alumno.id_grupo_alumno))             

    db.seguimiento_alumno.id_grupo_alumno.readable = db.seguimiento_alumno.id_grupo_alumno.writable = False
    db.seguimiento_alumno.id.readable = db.seguimiento_alumno.id.writable = False
    grid = SQLFORM.grid(query,ui='jquery-ui',field_id=db.seguimiento_alumno.id,deletable=False,create=False,editable=True,csv=False,details=False,searchable=False,
                        paginate=0,sortable=False,fields=[db.alumno.apellidos,db.alumno.nombre,db.alumno.fecha_nacimiento,db.alumno.nie],formstyle='divs',
                        orderby=db.alumno.apellidos|db.alumno.nombre)
    if  len(request.args)>1 and (request.args[0]=='edit'):
        nombre_alumno = LABEL(db.seguimiento_alumno(request.args[2]).id_grupo_alumno.id_alumno.apellidos+', '+db.seguimiento_alumno(request.args[2]).id_grupo_alumno.id_alumno.nombre)
        grid[0].insert(-1,nombre_alumno)
        # a continuación el guardamos el fielset y lo envolvemos en un DIV
        div_fieldset = DIV(grid[1][0])
        # hacemos que sea scrollable
        div_fieldset['_style'] = 'overflow-y: scroll; height:400px;'
        div_fieldset['_id'] = 'informe'
        # copiamos el botón de enviar
        boton = grid[1].element("div#submit_record__row")
        # borramos del DOM el fieldset para procesarlo a nuestro gusto
        del grid[1][0]
        # debemos manipular el grid para agrupar campos según el formato de entrada de datos
        # recuperamos los divs de la evaluación inicial
        div_ini_mat = div_fieldset[0][0]
        div_ini_dif = div_fieldset[0][1]

        div_ini_refi = div_fieldset[0][2]
        div_ini_refapt = div_fieldset[0][3]
        div_ini_refec = div_fieldset[0][4]
        div_ini_acin= div_fieldset[0][5]
        div_ini_aci = div_fieldset[0][6]
        div_ini_otras = div_fieldset[0][7]
        div_ini_otrasespecificar = div_fieldset[0][8]

        # modelamos la tabla para la evaluación inicial
        div_ini_table = TABLE(TR(TD(div_ini_refi[1],_style='text-align: right;'),TD(div_ini_refi[0]),TD(div_ini_refi[2])),
                              TR(TD(div_ini_refapt[1],_style='text-align: right;'),TD(div_ini_refapt[0]),TD(div_ini_refapt[2])),
                              TR(TD(div_ini_refec[1],_style='text-align: right;'),TD(div_ini_refec[0]),TD(div_ini_refec[2])),
                              TR(TD(div_ini_acin[1],_style='text-align: right;'),TD(div_ini_acin[0]),TD(div_ini_acin[2])),
                              TR(TD(div_ini_aci[1],_style='text-align: right;'),TD(div_ini_aci[0]),TD(div_ini_aci[2])),
                              TR(TD(div_ini_otras[1],_style='text-align: right;'),TD(div_ini_otras[0]),TD(div_ini_otras[2])))


        # creamos un div nuevo para estos campos
#        div_ini = DIV(H4(T('Evaluación Inicial')),div_ini_mat,div_ini_dif,div_ini_refi,div_ini_refapt,
#            div_ini_refec,div_ini_acin,div_ini_aci,div_ini_otras,div_ini_otrasespecificar,_id='div_ini')
        div_ini = DIV(div_ini_mat,div_ini_dif,div_ini_table,div_ini_otrasespecificar,_id='div_ini')

        # ajustamos su estilo para aparezca una caja
        div_ini['_style'] =  'border: 2px solid #DEDEDE; padding: 6px;'
        # recuperamos los divs de la primera evaluación
        div_pri_dif = div_fieldset[0][9]
        div_pri_evo = div_fieldset[0][10]
        div_pri_dec = div_fieldset[0][11]
        # creamos un div nuevo para estos campos
        div_pri = DIV(div_pri_dif,div_pri_evo,div_pri_dec,_id='div_pri')
        # ajustamos su estilo para aparezca una caja
        div_pri['_style'] =  'border: 2px solid #DEDEDE; padding: 6px;'
        # recuperamos los divs de la segunda evaluación
        div_seg_dif = div_fieldset[0][12]
        div_seg_evo = div_fieldset[0][13]
        div_seg_dec = div_fieldset[0][14]
        # creamos un div nuevo para estos campos
        div_seg = DIV(div_seg_dif,div_seg_evo,div_seg_dec,_id='div_seg')
        # ajustamos su estilo para aparezca una caja
        div_seg['_style'] =  'border: 2px solid #DEDEDE; padding: 6px;'
        # recuperamos los divs de la evaluación ordinaria-extraordinaria
        div_ord_pro = div_fieldset[0][15]
        div_ord_proau = div_fieldset[0][16]
        div_ord_rep = div_fieldset[0][17]

        # modelamos la decisión adoptada en la evaluación ordinaria-extraordinaria
        div_ord_decision = DIV(H4(T('Decisión adoptada')),
                               TABLE(TR(TD(div_ord_pro[1],_style='text-align: right;'),TD(div_ord_pro[0]),
                                        TD(div_ord_proau[1],_style='text-align: right;'),TD(div_ord_proau[0]),
                                        TD(div_ord_rep[1],_style='text-align: right;'),TD(div_ord_rep[0]))))


        div_ord_pen = div_fieldset[0][18]

        div_ord_fra = div_fieldset[0][19]
        div_ord_dbm = div_fieldset[0][20]
        div_ord_lha = div_fieldset[0][21]
        div_ord_apo = div_fieldset[0][22]
        div_ord_com = div_fieldset[0][23]
        div_ord_pdc = div_fieldset[0][24]
        div_ord_ada = div_fieldset[0][25]
        div_ord_adaespecificar = div_fieldset[0][26]
        div_ord_pcpi = div_fieldset[0][27]
        div_ord_otr = div_fieldset[0][28]
        div_ord_otrespecificar = div_fieldset[0][29]

        div_ord_medidas_1 = TABLE(TR(TD(div_ord_fra[1],_style='text-align: right;'),TD(div_ord_fra[0]),
                                        TD(div_ord_dbm[1],_style='text-align: right;'),TD(div_ord_dbm[0]),
                                        TD(div_ord_lha[1],_style='text-align: right;'),TD(div_ord_lha[0])),
                                TR(TD(div_ord_apo[1],_style='text-align: right;'),TD(div_ord_apo[0]),
                                        TD(div_ord_com[1],_style='text-align: right;'),TD(div_ord_com[0]),
                                        TD(div_ord_pdc[1],_style='text-align: right;'),TD(div_ord_pdc[0])),
                                TR(TD(div_ord_pcpi[1],_style='text-align: right;'),TD(div_ord_pcpi[0]),
                                        TD(),
                                        TD()))

        div_ord_medidas_2 = TABLE(TR(TD(div_ord_ada[1],_style='text-align: right;'),TD(div_ord_ada[0])),
                                  TR(TD(div_ord_adaespecificar,_colspan="2")),
                                  TR(TD(div_ord_otr[1],_style='text-align: right;'),TD(div_ord_otr[0])),
                                  TR(TD(div_ord_otrespecificar,_colspan="2")))


        # div de medidas propuestas para el próximo curso
        #div_ord_medidas = DIV(H4(T('Medidas propuestas para el próximo curso')),div_ord_fra,div_ord_dbm,
        #    div_ord_lha,div_ord_apo,div_ord_com,div_ord_pdc,div_ord_ada,div_ord_adaespecificar,div_ord_pcpi,
        #    div_ord_otr,div_ord_otrespecificar,_id='div_ord_medidas')
        div_ord_medidas = DIV(H4(T('Medidas propuestas para el próximo curso')),div_ord_medidas_1,div_ord_medidas_2,_id='div_ord_medidas')

        div_ord_medidas['_style'] =  'border: 1px solid #DEDEDE; padding: 6px;'       
        # creamos un div nuevo para estos campos
#        div_ord = DIV(H4(T('Evaluación Ordinaria/Extraordinaria')),div_ord_pro,div_ord_proau,div_ord_rep,
#            div_ord_pen,div_ord_medidas,_id='div_ord')

        div_ord = DIV(div_ord_decision,div_ord_pen,div_ord_medidas,_id='div_ord')

        # ajustamos su estilo para aparezca una caja
        div_ord['_style'] =  'border: 2px solid #DEDEDE; padding: 6px;'
        # recuperamos los divs de las competencias básicas
        div_com_len_alta = div_fieldset[0][30]
        div_com_len_cons = div_fieldset[0][31]
        div_com_len_no = div_fieldset[0][32]
        div_com_mat_alta = div_fieldset[0][33]
        div_com_mat_cons = div_fieldset[0][34]
        div_com_mat_no = div_fieldset[0][35]
        div_com_con_alta = div_fieldset[0][36]
        div_com_con_cons = div_fieldset[0][37]
        div_com_con_no = div_fieldset[0][38]
        div_com_ti_alta = div_fieldset[0][39]
        div_com_ti_cons = div_fieldset[0][40]
        div_com_ti_no = div_fieldset[0][41]
        div_com_so_alta = div_fieldset[0][42]
        div_com_so_cons = div_fieldset[0][43]
        div_com_so_no = div_fieldset[0][44]
        div_com_cu_alta = div_fieldset[0][45]
        div_com_cu_cons = div_fieldset[0][46]
        div_com_cu_no = div_fieldset[0][47]
        div_com_ap_alta = div_fieldset[0][48]
        div_com_ap_cons = div_fieldset[0][49]
        div_com_ap_no = div_fieldset[0][50]
        div_com_au_alta = div_fieldset[0][51]
        div_com_au_cons = div_fieldset[0][52]
        div_com_au_no = div_fieldset[0][53]

        div_com_table = TABLE(TR(TH(T('Competencias básicas que ha adquirido suficientemente el alumno en el proceso de enseñanza-aprendizaje')),
                                    TH(T('Altamente conseguida')),TH(T('Conseguida')),TH(T('No conseguida'))),
                              TR(TD(T('Comunicación lingüística')),TD(div_com_len_alta[1],_style='text-align: center;'),
                                                                   TD(div_com_len_cons[1],_style='text-align: center;'),
                                                                   TD(div_com_len_no[1],_style='text-align: center;')),
                              TR(TD(T('Competencia matemática')),TD(div_com_mat_alta[1],_style='text-align: center;'),
                                                                 TD(div_com_mat_cons[1],_style='text-align: center;'),
                                                                 TD(div_com_mat_no[1],_style='text-align: center;')),
                              TR(TD(T('Conocimiento e interacción con el mundo físico')),TD(div_com_con_alta[1],_style='text-align: center;'),
                                                                                         TD(div_com_con_cons[1],_style='text-align: center;'),
                                                                                         TD(div_com_con_no[1],_style='text-align: center;')),
                              TR(TD(T('Tratamiento de la información y competencia digital')),TD(div_com_ti_alta[1],_style='text-align: center;'),
                                                                                              TD(div_com_ti_cons[1],_style='text-align: center;'),
                                                                                              TD(div_com_ti_no[1],_style='text-align: center;')),
                              TR(TD(T('Competencia social y ciudadana')),TD(div_com_so_alta[1],_style='text-align: center;'),
                                                                         TD(div_com_so_cons[1],_style='text-align: center;'),
                                                                         TD(div_com_so_no[1],_style='text-align: center;')),
                              TR(TD(T('Competencia cultural y artística')),TD(div_com_cu_alta[1],_style='text-align: center;'),
                                                                           TD(div_com_cu_cons[1],_style='text-align: center;'),
                                                                           TD(div_com_cu_no[1],_style='text-align: center;')),
                              TR(TD(T('Aprender a aprender')),TD(div_com_ap_alta[1],_style='text-align: center;'),
                                                              TD(div_com_ap_cons[1],_style='text-align: center;'),
                                                              TD(div_com_ap_no[1],_style='text-align: center;')),
                              TR(TD(T('Autonomía e iniciativa personal')),TD(div_com_au_alta[1],_style='text-align: center;'),
                                                                          TD(div_com_au_cons[1],_style='text-align: center;'),
                                                                          TD(div_com_au_no[1],_style='text-align: center;'))
                             )

        # div de competencias básicas
        div_com = DIV(div_com_table,_id='div_com')
        # ajustamos su estilo para aparezca una caja
        div_com['_style'] =  'border: 2px solid #DEDEDE; padding: 6px;'
        # borramos los elementos que ya hemos reordenado

        div_medidas = div_fieldset[0][54]
        div_otros = div_fieldset[0][55]
        div_aspectos = div_fieldset[0][56]
        # divs de resto de información
        div_resto = DIV(div_medidas,div_otros,div_aspectos,_id='div_resto')
        # ajustamos su estilo para aparezca una caja
        div_resto['_style'] =  'border: 2px solid #DEDEDE; padding: 6px;'


        for i in range(57):
            del div_fieldset[0][0]

        # introducimos los nuevos divs en el fieldset
        div_fieldset.insert(0, H3(A(T('Evaluación Inicial'))))
        div_fieldset.insert(1, div_ini)
        div_fieldset.insert(2, H3(A(T('Primera Evaluación'))))
        div_fieldset.insert(3, div_pri)
        div_fieldset.insert(4, H3(A(T('Segunda Evaluación'))))
        div_fieldset.insert(5, div_seg)
        div_fieldset.insert(6, H3(A(T('Evaluación Ordinaria-Extraordinaria'))))
        div_fieldset.insert(7, div_ord)
        div_fieldset.insert(8, H3(A(T('Competencias Básicas'))))
        div_fieldset.insert(9, div_com)
        div_fieldset.insert(10, H3(A(T('Otros Aspectos y Medidas'))))
        div_fieldset.insert(11, div_resto)

        del div_fieldset[12]
        
        # colocamos el DIV del fieldset en el grid
        grid[1].insert(0, div_fieldset)

        grid[1].insert(2,boton)
        grid[0].insert(1,DIV(IMG(_src=URL(c='default',f='download',args=db.seguimiento_alumno(request.args[2]).id_grupo_alumno.id_alumno.foto),
                                 _style="background-color: rgb(187, 187, 187); width: 80px; border: 1px solid; padding: 5px; display: inline;",
                                 _class="ui-corner-all"),
                             _style="float:right;padding-right:15px;", _width="20%"))

        grid[2].insert(-1,nombre_alumno)

    return dict(grid=grid)
