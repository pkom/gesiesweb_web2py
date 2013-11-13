# coding: utf8

@auth.requires_login()
@auth.requires_membership(role='Responsables')    
def index(): 
    return dict(message="hello from statistics.py")

@auth.requires_login()
@auth.requires_membership(role='Responsables')    
def warnings(): 
    return dict(message="hello from warnings for responsibles")    

@auth.requires_login()
@auth.requires_membership(role='Responsables')    
def absentismo(): 
    return dict(message="hello from warnings for responsibles")          
        
@auth.requires_login()
@auth.requires_membership(role='Responsables')    
def delays(): 
    return dict(message="hello from delays for responsibles")

@auth.requires_login()
@auth.requires_membership(role='Responsables')    
def resumestudents(): 
    return dict(message="hello from students resume")
    
@auth.requires_login()
@auth.requires_membership(role='Responsables')    
def resumestudentsabsentismo(): 
    return dict(message="hello from students absentismo resume")    

@auth.requires_login()
@auth.requires_membership(role='Responsables')    
def resumestudentsdelays(): 
    return dict(message="hello from students delays resume")

@auth.requires_login()
@auth.requires_membership(role='Responsables')    
def resumeteachers(): 
    return dict(message="hello from teachers resume")


@auth.requires_login()
@auth.requires_membership(role='Responsables')    
def resumeteachersabsentismo(): 
    return dict(message="hello from teachers absentismo resume")
