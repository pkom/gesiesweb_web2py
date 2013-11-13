# coding: utf8
# intente algo como
@auth.requires_login()
@auth.requires_membership(role='Profesores')
def index():
    return dict(message="hello from absentismo")

@auth.requires_login()
@auth.requires_membership(role='Profesores')    
def absentismo(): 
    return dict(message="hello from my absentismo")    
    
@auth.requires_login()
@auth.requires_membership(role='Profesores')    
def absentismotutor(): 
    return dict(message="hello from my tutor absentismo")
    
@auth.requires_login()
@auth.requires_membership(role='Profesores')    
def form(): 
    return dict(message="hello from form")
