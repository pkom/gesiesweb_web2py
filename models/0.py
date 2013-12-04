import logging
import logging.handlers
import os
from gluon.storage import Storage
from gluon.contrib.login_methods.ldap_auth import ldap_auth
from gluon.custom_import import track_changes

T.force('es-es')

settings = Storage()

settings.produccion = True

if settings.produccion == True:
    settings.expiracion = 60 * 60  # logout after 5 minutes of inactivity
else:
    settings.expiracion = 60 * 60

if settings.produccion:
    settings.db_uri = 'mysql://amonies:quemalosson@mysql/datosies'   
    settings.migrate = False
    settings.log_level = logging.ERROR
    
    track_changes(False)
else:
    settings.db_uri = 'mysql://amonies:quemalosson@mysql/datosiesdev'
    settings.migrate = True
    settings.log_level = logging.DEBUG

    track_changes(True)
    

#
# Logger
#
def get_configured_logger(name):
    logger = logging.getLogger(name)
    if (len(logger.handlers) == 0):
        # Create RotatingFileHandler
        import os
        formatter="%(asctime)s %(levelname)s %(process)s %(thread)s %(funcName)s():%(lineno)d %(message)s"
        handler = logging.handlers.RotatingFileHandler(os.path.join(request.folder,'private/app.log'),maxBytes=1024,backupCount=2)
        handler.setFormatter(logging.Formatter(formatter))
        # setting level
        handler.setLevel(settings.log_level)
        logger.addHandler(handler)
        logger.setLevel(settings.log_level)
        logger.debug(name + ' logger created')
        if settings.produccion == True:
            logger.debug('Server launched in production mode')
        else:
            logger.debug('Server launched in developpment mode')
    return logger
    
settings.logger = get_configured_logger(request.application)

settings.title = request.application
settings.subtitle = T('Gestión de Alumnado en Centros de Secundaria')
settings.author = 'Francisco Mora Sánchez'
settings.author_email = 'francisco.mora.sanchez@gmail.com'
settings.keywords = 'disciplina gestion prestamo libros alumnos enseñanza centros secundaria extremadura educacion eso bachillerato evaluación'
settings.description = T('Gestión de alumnado en Centros de Secundaria')
settings.layout_theme = 'Default'
settings.security_key = 'a098c897-724b-4e05-b2d8-8ee993385ae6'
settings.email_server = 'logging' or 'smtp.gmail.com:587'
settings.email_sender = 'francisco.mora.sanchez@gmail.com'
settings.email_login = ''
settings.login_method = [ldap_auth(server='ldap', base_dn='ou=People,dc=instituto,dc=extremadura,dc=es')]
settings.login_config = ''
