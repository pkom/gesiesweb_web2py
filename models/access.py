# ###########################################################
# ## session expiration
# ###########################################################
import time

t0 = time.time()
if session.last_time and session.last_time < t0 - settings.expiracion:
    session.flash = T('session expired')
    session.authorized = False
    session.clear()
else:
    session.last_time = t0
