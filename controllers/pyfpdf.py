# coding: utf8

from reportlab.platypus import *
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.rl_config import defaultPageSize
from reportlab.lib.units import inch, mm
from reportlab.lib.enums import TA_LEFT, TA_RIGHT, TA_CENTER, TA_JUSTIFY
from reportlab.lib import colors
from uuid import uuid4
from cgi import escape
import os

from gluon.contrib.pyfpdf import Template

def get_me_a_pdf():
    title = "This The Doc Title"
    heading = "First Paragraph"
    text = 'bla '* 10000

    styles = getSampleStyleSheet()
    tmpfilename=os.path.join(request.folder,'private',str(uuid4()))
    doc = SimpleDocTemplate(tmpfilename)
    story = []
    story.append(Paragraph(escape(title),styles["Title"]))
    story.append(Paragraph(escape(heading),styles["Heading2"]))
    story.append(Paragraph(escape(text),styles["Normal"]))
    story.append(Spacer(1,2*inch))
    doc.build(story)
    data = open(tmpfilename,"rb").read()
    os.unlink(tmpfilename)
    response.headers['Content-Type']='application/pdf'
    return data

from gluon.contrib.pyfpdf import FPDF
import os

def get_me_a_pyfpdf():
    title = "This The Doc Title"
    heading = "First Paragraph"
    text = 'bla '* 10000

    pdf=FPDF()
    pdf.add_page()
    pdf.set_font('Times','B',15)
    pdf.cell(w=210,h=9,txt=title,border=0,ln=1,align='C',fill=0)
    pdf.set_font('Times','B',15)
    pdf.cell(w=0,h=6,txt=heading,border=0,ln=1,align='L',fill=0)
    pdf.set_font('Times','',12)
    pdf.multi_cell(w=0,h=5,txt=text)
    response.headers['Content-Type']='application/pdf'
    return pdf.output(dest='S')

def report():
    response.title = "web2py sample report"
    
    # include a google chart!
    url = "http://chart.apis.google.com/chart?cht=p3&chd=t:60,40&chs=250x100&chl=Hello|World&.png"
    chart = IMG(_src=url, _width="250",_height="100")

    # create a small table with some data:
    rows = [THEAD(TR(TH("Key",_width="70%"), TH("Value",_width="30%"))),
            TBODY(TR(TD("Hello"),TD("60")), 
                  TR(TD("World"),TD("40")))]
    table = TABLE(_border="0", _align="center", _width="50%", *rows)

    if request.extension=="pdf":
        from gluon.contrib.pyfpdf import FPDF, HTMLMixin

        # create a custom class with the required functionalities 
        class MyFPDF(FPDF, HTMLMixin):
            def header(self): 
                "hook to draw custom page header"
                logo=os.path.join(request.env.web2py_path,"applications",request.application,"static","images","logo.png")
                #self.image(logo,10,8,33)
                self.set_font('Arial','B',15)
                self.cell(65) # padding
                self.cell(60,10,response.title,1,0,'C')
                self.ln(20)
                
            def footer(self):
                "hook to draw custom page header (printing page numbers)"
                self.set_y(-15)
                self.set_font('Arial','I',8)
                txt = 'Page %s of %s' % (self.page_no(), self.alias_nb_pages())
                self.cell(0,10,txt,0,0,'C')
                    
        pdf=MyFPDF()
        # create a page and serialize/render HTML objects
        pdf.add_page()
        pdf.write_html(str(XML(table, sanitize=False)))
        pdf.write_html(str(XML(CENTER(chart), sanitize=False)))
        # prepare PDF to download:
        response.headers['Content-Type']='application/pdf'
        return pdf.output(dest='S')
    else:
        # normal html view:
        return dict(chart=chart, table=table)

def listing():
    response.title = "web2py sample listing"
    
    # define header and footers:
    head = THEAD(TR(TH("Header 1",_width="50%"), 
                    TH("Header 2",_width="30%"),
                    TH("Header 3",_width="20%"), 
                    _bgcolor="#A0A0A0"))
    foot = TFOOT(TR(TH("Footer 1",_width="50%"), 
                    TH("Footer 2",_width="30%"),
                    TH("Footer 3",_width="20%"),
                    _bgcolor="#E0E0E0"))
    
    # create several rows:
    rows = []
    for i in range(1000):
        col = i % 2 and "#F0F0F0" or "#FFFFFF"
        rows.append(TR(TD("Row %s" %i),
                       TD("something", _align="center"),
                       TD("%s" % i, _align="right"),
                       _bgcolor=col)) 

    # make the table object
    body = TBODY(*rows)
    table = TABLE(_border="1", _align="center", _width="100%", *[head,foot, body])

    if request.extension=="pdf":
        from gluon.contrib.pyfpdf import FPDF, HTMLMixin

        # define our FPDF class (move to modules if it is reused  frequently)
        class MyFPDF(FPDF, HTMLMixin):
            def header(self):
                self.set_font('Arial','B',15)
                self.cell(0,10, response.title ,1,0,'C')
                self.ln(20)
                
            def footer(self):
                self.set_y(-15)
                self.set_font('Arial','I',8)
                txt = 'Page %s of %s' % (self.page_no(), self.alias_nb_pages())
                self.cell(0,10,txt,0,0,'C')
                    
        pdf=MyFPDF()
        # first page:
        pdf.add_page()
        pdf.write_html(str(XML(table, sanitize=False)))
        response.headers['Content-Type']='application/pdf'
        return pdf.output(dest='S')
    else:
        # normal html view:
        return dict(table=table)
        

def create_label():
    pdf_template_id = db.pdf_template.insert(title="sample badge", format="A4")

    # configure optional background image and insert his element
    path_to_image = os.path.join(request.folder, 'static','badge_background.png')
    if path_to_image:
        db.pdf_element.insert(pdf_template_id=pdf_template_id, name='background', type='I', x1=0.0, y1=0.0, x2=85.23, y2=54.75, font='Arial', size=10.0, bold=False, italic=False, underline=False, foreground=0, background=16777215, align='L', text=path_to_image, priority=-1)
    # insert name, company_name, number and attendee type elements:
    db.pdf_element.insert(pdf_template_id=pdf_template_id, name='name', type='T', x1=4.0, y1=25.0, x2=62.0, y2=30.0, font='Arial', size=12.0, bold=True,       italic=False, underline=False, foreground=0, background=16777215, align='L', text='', priority=0)
    db.pdf_element.insert(pdf_template_id=pdf_template_id, name='company_name', type='T', x1=4.0, y1=30.0, x2=50.0, y2=34.0, font='Arial', size=10.0, bold=False, italic=False, underline=False, foreground=0, background=16777215, align='L', text='', priority=0)
    db.pdf_element.insert(pdf_template_id=pdf_template_id, name='no', type='T', x1=4.0, y1=34.0, x2=80.0, y2=38.0, font='Arial', size=10.0, bold=False, italic=False, underline=False, foreground=0, background=16777215, align='R', text='', priority=0)
    db.pdf_element.insert(pdf_template_id=pdf_template_id, name='attendee_type', type='T', x1=4.0, y1=38.0, x2=50.0, y2=42.0, font='Arial', size=10.0, bold=False, italic=False, underline=False, foreground=0, background=16777215, align='L', text='', priority=0)
    return dict(pdf_template_id=pdf_template_id)


def copy_labels():
    # read base label/badge elements from db 
    base_pdf_template_id = 1
    elements = db(db.pdf_element.pdf_template_id==base_pdf_template_id).select(orderby=db.pdf_element.priority)
    # setup initial offset and width and height:
    x0, y0 = 10, 10
    dx, dy = 85.5, 55
    # create new template to hold several labels/badges:
    rows, cols = 5,  2
    pdf_template_id = db.pdf_template.insert(title="sample badge %s rows %s cols" % (rows, cols), format="A4")
    # copy the base elements:
    k = 0
    for i in range(rows):
        for j in range(cols):
            k += 1
            for element in elements:
                e = dict(element)
                e['name'] = "%s%02d" % (e['name'], k)
                e['pdf_template_id'] = pdf_template_id
                e['x1'] = e['x1'] + x0 + dx*j
                e['x2'] = e['x2'] + x0 + dx*j
                e['y1'] = e['y1'] + y0 + dy*i
                e['y2'] = e['y2'] + y0 + dy*i
                del e['update_record']
                del e['delete_record']
                del e['id']
                db.pdf_element.insert(**e)
    return {'new_pdf_template_id': pdf_template_id}

def speakers_badges():
    # set template to use from the db:
    pdf_template_id = 2
    
    # query registered users and generate speaker labels
    speakers = db(db.auth_user.id>0).select(orderby=db.auth_user.last_name|db.auth_user.first_name)
    company_name = "web2conf"
    attendee_type = "Speaker"
    
    # read elements from db 
    elements = db(db.pdf_element.pdf_template_id==pdf_template_id).select(orderby=db.pdf_element.priority)

    f = Template(format="A4",
             elements = elements,
             title="Speaker Badges", author="web2conf",
             subject="", keywords="")
    
    # calculate pages:
    label_count = len(speakers)
    max_labels_per_page = 5*2
    pages = label_count / (max_labels_per_page - 1)
    if label_count % (max_labels_per_page - 1): pages = pages + 1

    # fill placeholders for each page
    for page in range(1, pages+1):
        f.add_page()
        k = 0
        li = 0
        for speaker in speakers:
            k = k + 1
            if k > page * (max_labels_per_page ):
                break
            if k > (page - 1) * (max_labels_per_page ):
                li += 1
                #f['item_quantity%02d' % li] = it['qty']
                f['name%02d' % li] = unicode("%s %s" % (speaker.first_name, speaker.last_name), "utf8")
                f['company_name%02d' % li] = unicode("%s %s" % (company_name, ""), "utf8")
                f['attendee_type%02d' % li] = attendee_type
                ##f['no%02d' % li] = li

    response.headers['Content-Type']='application/pdf'
    return f.render('badge.pdf', dest='S')

def import_csv():
    
    pdf_template_id = db.pdf_template.insert(title="invoice", format="A4")   

    cvs_file_path = os.path.join(request.folder,'static','stuff','invoice.csv')
    f = Template()
    f.parse_csv(infile=cvs_file_path, delimiter=";", decimal_sep=",")
#    for v in f.fields.elements():
    for campo in f.elements.keys():
        v = f.elements[campo]
        v['align']=  {'I':'L','D':'R','C':'C','':''}.get(v['align'], 'L')
        v['pdf_template_id'] = pdf_template_id
        db.pdf_element.insert(**v)

def invoice():
    import os.path
    
    # generate sample invoice (according Argentina's regulations)

    import random
    from decimal import Decimal

    # read elements from db 
    
    elements = db(db.pdf_element.pdf_template_id==3).select(orderby=db.pdf_element.priority)

    f = Template(format="A4",
             elements = elements,
             title="Sample Invoice", author="Sample Company",
             subject="Sample Customer", keywords="Electronic TAX Invoice")
    
    detail = "Lorem ipsum dolor sit amet, consectetur. " * 5
    items = []
    for i in range(1, 30):
        ds = "Sample product %s" % i
        qty = random.randint(1,10)
        price = round(random.random()*100,3)
        code = "%s%s%02d" % (chr(random.randint(65,90)), chr(random.randint(65,90)),i)
        items.append(dict(code=code, unit='u',
                          qty=qty, price=price, 
                          amount=qty*price,
                          ds="%s: %s" % (i,ds)))

    # divide and count lines
    lines = 0
    li_items = []
    for it in items:
        qty = it['qty']
        code = it['code']
        unit = it['unit']
        for ds in f.split_multicell(it['ds'], 'item_description01'):
            # add item description line (without price nor amount)
            li_items.append(dict(code=code, ds=ds, qty=qty, unit=unit, price=None, amount=None))
            # clean qty and code (show only at first)
            unit = qty = code = None
        # set last item line price and amount
        li_items[-1].update(amount = it['amount'],
                            price = it['price'])

    obs="\n<U>Detail:</U>\n\n" + detail
    for ds in f.split_multicell(obs, 'item_description01'):
        li_items.append(dict(code=code, ds=ds, qty=qty, unit=unit, price=None, amount=None))

    # calculate pages:
    lines = len(li_items)
    max_lines_per_page = 24
    pages = lines / (max_lines_per_page - 1)
    if lines % (max_lines_per_page - 1): pages = pages + 1

    # completo campos y hojas
    for page in range(1, pages+1):
        f.add_page()
        f['page'] = 'Page %s of %s' % (page, pages)
        if pages>1 and page<pages:
            s = 'Continues on page %s' % (page+1)
        else:
            s = ''
        f['item_description%02d' % (max_lines_per_page+1)] = s

        f["company_name"] = "Sample Company"
        f["company_logo"] = os.path.join(request.env.web2py_path,"applications",request.application,"private","tutorial","logo.png")
        f["company_header1"] = "Some Address - somewhere -"
        f["company_header2"] = "http://www.example.com"        
        f["company_footer1"] = "Tax Code ..."
        f["company_footer2"] = "Tax/VAT ID ..."
        f['number'] = '0001-00001234'
        f['issue_date'] = '2010-09-10'
        f['due_date'] = '2099-09-10'
        f['customer_name'] = "Sample Client"
        f['customer_address'] = "Siempreviva 1234"
       
        # print line item...
        li = 0 
        k = 0
        total = Decimal("0.00")
        for it in li_items:
            k = k + 1
            if k > page * (max_lines_per_page - 1):
                break
            if it['amount']:
                total += Decimal("%.6f" % it['amount'])
            if k > (page - 1) * (max_lines_per_page - 1):
                li += 1
                if it['qty'] is not None:
                    f['item_quantity%02d' % li] = it['qty']
                if it['code'] is not None:
                    f['item_code%02d' % li] = it['code']
                if it['unit'] is not None:
                    f['item_unit%02d' % li] = it['unit']
                f['item_description%02d' % li] = it['ds']
                if it['price'] is not None:
                    f['item_price%02d' % li] = "%0.3f" % it['price']
                if it['amount'] is not None:
                    f['item_amount%02d' % li] = "%0.2f" % it['amount']

        if pages == page:
            f['net'] = "%0.2f" % (total/Decimal("1.21"))
            f['vat'] = "%0.2f" % (total*(1-1/Decimal("1.21")))
            f['total_label'] = 'Total:'
        else:
            f['total_label'] = 'SubTotal:'
        f['total'] = "%0.2f" % total

    response.headers['Content-Type']='application/pdf'
    return f.render('invoice.pdf', dest='S')

def index():
    if request.extension == "pdf": response.view = "generic.pdf"
    """
    example action using the internationalization operator T and flash
    rendered by views/default/index.html or views/generic.html
    """
    response.flash = T('Welcome to web2py')
    return dict(message=T('Hello World'))
