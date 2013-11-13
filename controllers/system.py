# coding: utf8
# intente algo como

import datetime

def index(): return dict(message="hello from system.py")

@auth.requires_login()
def call():
    session.forget()
    return service()

@service.json
def getDate():
    fecha = datetime.date.today()
    return dict(fecha=fecha)
