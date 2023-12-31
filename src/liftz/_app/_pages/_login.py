from typing import Optional

from fastapi import Request
from fastapi.responses import RedirectResponse
from starlette.middleware.base import BaseHTTPMiddleware

from liftz._app import _helpers

# copied from https://github.com/zauberzeug/nicegui/blob/main/examples/authentication/main.py


__all__ = (
    "register_login_page",
)


def register_login_page():
    from nicegui import Client, app, ui

    unrestricted_page_routes = {'/login'}

    class AuthMiddleware(BaseHTTPMiddleware):
        """This middleware restricts access to all NiceGUI pages.

        It redirects the user to the login page if they are not authenticated.
        """

        async def dispatch(self, request: Request, call_next):
            if not _helpers.user.get_authorization_status(app):

                # check if path is protected
                if (
                        request.url.path in Client.page_routes.values()
                        and request.url.path not in unrestricted_page_routes
                ):
                    # remember where the user wanted to go
                    app.storage.user['referrer_path'] = request.url.path
                    return RedirectResponse('/login')
            return await call_next(request)

    app.add_middleware(AuthMiddleware)

    @ui.page('/')
    def main_page() -> None:
        with ui.column().classes('absolute-center items-center'):
            user = _helpers.user.get_current_user(app)

            ui.label(f'Hello {user.name}!').classes('text-2xl')
            ui.button(
                on_click=lambda: (app.storage.user.clear(), ui.open('/login')), icon='logout'
            ).props('outline round')

    @ui.page('/subpage')
    def test_page() -> None:
        ui.label('This is a sub page.')

    @ui.page('/login')
    def login() -> Optional[RedirectResponse]:

        # local function to avoid passing username and password as arguments
        def try_login() -> None:
            user_obj = _helpers.user.user_creds_check(
                email=email.value,
                password=password.value
            )
            if user_obj:
                _helpers.user.set_current_user(user_obj, app)
                _helpers.user.set_authorization_status(app, status=True)
                # go back to where the user wanted to go
                ui.open(app.storage.user.get('referrer_path', '/'))
            else:
                ui.notify('Wrong email or password', color='negative')

        if _helpers.user.get_authorization_status(app):
            return RedirectResponse('/')
        with ui.card().classes('absolute-center'):
            email = ui.input('Email').on('keydown.enter', try_login)
            password = (
                ui.input('Password', password=True, password_toggle_button=True)
                .on('keydown.enter', try_login))
            ui.button('Log in', on_click=try_login)
