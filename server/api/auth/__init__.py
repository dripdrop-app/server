from starlette.routing import Mount, Route
from server.utils.enums import RequestMethods
from server.api.auth.endpoints import create_account, admin_create_account, check_session, login, logout, google_oauth2

routes = [
    Mount('/auth', routes=[
        Route(
            '/create',
            endpoint=create_account,
            methods=[RequestMethods.POST.value]
        ),
        Route(
            '/admin/create',
            endpoint=admin_create_account,
            methods=[RequestMethods.POST.value]
        ),
        Route(
            '/checkSession',
            endpoint=check_session,
            methods=[RequestMethods.GET.value]
        ),
        Route(
            '/logout',
            endpoint=logout,
            methods=[RequestMethods.GET.value]
        ),
        Route(
            '/login',
            endpoint=login,
            methods=[RequestMethods.POST.value]
        ),
        Route(
            '/googleoauth2',
            endpoint=google_oauth2,
            methods=[RequestMethods.GET.value]
        )
    ])
]
