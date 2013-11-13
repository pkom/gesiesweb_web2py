# coding: utf8
# intente algo como
@auth.requires_login()
@auth.requires_membership(role='Profesores')
def index(): 
    return dict(message="hello from delays")

@auth.requires_login()
@auth.requires_membership(role='Profesores')    
def delays(): 
    return dict(message="hello from delays")    
    
@auth.requires_login()
@auth.requires_membership(role='Profesores')    
def delaystutor(): 
    return dict(message="hello from my tutor delays")

@auth.requires_login()
@auth.requires_membership(role='Profesores')    
def form(): 
    return dict(message="hello from form")
