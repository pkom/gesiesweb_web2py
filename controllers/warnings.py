# coding: utf8
# intente algo como
@auth.requires_login()
@auth.requires_membership(role='Profesores')
def index():
    return dict(message="hello from warnings")

@auth.requires_login()
@auth.requires_membership(role='Profesores')    
def warnings(): 
    return dict(message="hello from my warnings")    
    
@auth.requires_login()
@auth.requires_membership(role='Profesores')    
def warningstutor(): 
    return dict(message="hello from my tutor warnings")
    
@auth.requires_login()
@auth.requires_membership(role='Profesores')    
def form(): 
    return dict(message="hello from form")
