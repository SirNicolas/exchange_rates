import base64
from aiohttp import web

from rates.handlers import routes
from rates.logic import check_user_auth


@web.middleware
async def auth_middleware(request, handler):
    if 'Authorization' in request.headers:
        auth_method, data = request.headers.get('Authorization').split()
        if auth_method == 'Basic':
            data = base64.b64decode(data.encode()).decode()
            name, password = data.split(':', 1)
            await check_user_auth(name, password)
            return await handler(request)
    return web.HTTPForbidden()


def make_app():
    app = web.Application(middlewares=[auth_middleware])
    app.add_routes(routes)
    return app
