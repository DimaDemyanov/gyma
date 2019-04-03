from waitress import serve

from vdv.app import runWSGIApp, getWSGIPortFromConfig


if __name__ == '__main__':
    wsgi_app = runWSGIApp()

    WSGI_PORT = getWSGIPortFromConfig()
    if not WSGI_PORT:
        WSGI_PORT = 80

    serve(wsgi_app, host='0.0.0.0', port='%d' % WSGI_PORT)
