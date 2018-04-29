"""
Middleware to enable CORS requests from every domain
Works in DEGUG mode only
"""
from django.conf import settings


class CORSMiddleware(object):
    """
    Enable cors requests from all domains
    in debug mode
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if settings.DEBUG:
            response['Access-Control-Allow-Origin'] = "*"
            response['Access-Control-Allow-Credentials'] = 'true'
            response['Access-Control-Allow-Methods'] = \
                'GET,POST,OPTIONS,PUT,DELETE,PATCH'
        return response