from google.appengine.api import users
from google.appengine.ext import vendor
vendor.add('lib')

from grow.server import main as grow_main
import os
import grow


ALLOWED_DOMAINS = [
    'google.com',
]

IS_DEV_SERVER = os.getenv('SERVER_SOFTWARE', '').startswith('Dev')


class AuthMiddleware(object):
    def __init__(self, app):
        self.app = app

    def has_access(self, email):
        domain = email.split('@')[-1]
        return domain in ALLOWED_DOMAINS

    def __call__(self, environ, start_response):
        email = os.getenv('USER_EMAIL', '')
        is_https = os.getenv('wsgi.url_scheme', '') == 'https'
        if not is_https and not IS_DEV_SERVER:
            status = '302 Found'
            url = os.getenv('HTTP_ORIGIN', '').replace('http://', 'https://')
            response_headers = [('Location', url)]
            start_response(status, response_headers)
            return []
        if not email:
            status = '302 Found'
            url = users.create_login_url(environ['PATH_INFO'])
            response_headers = [('Location', url)]
            start_response(status, response_headers)
            return []
        if not self.has_access(email):
            status = '403 Forbidden'
            response_headers = [('Content-Type', 'text/html')]
            start_response(status, response_headers)
            url = users.create_logout_url(environ['PATH_INFO'])
            message = '{} is forbidden. <a href="{}">Sign out</a>.'
            return [message.format(email, url)]
        return self.app(environ, start_response)


pod = grow.Pod('.')
pod.env.name = 'dev'
pod_app = grow_main.create_wsgi_app(pod)
app = AuthMiddleware(pod_app)
