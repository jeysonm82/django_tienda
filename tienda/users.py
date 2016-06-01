import time
from django.conf import settings
from django.contrib import auth

class UserMiddleware:

    def process_request(self, request):
        now = time.time()
        if not request.user.is_authenticated() :
          request.session['last_touch'] = now
          return
        try:
            if now - request.session['last_touch'] > (settings.AUTO_LOGOUT_DELAY * 60):
                auth.logout(request)
                del request.session['last_touch']
                return
        except KeyError:
          pass

        request.session['last_touch'] = now
