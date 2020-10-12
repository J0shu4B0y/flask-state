import logging
from flask import current_app, _request_ctx_stack, request
from ..controller.response_methods import make_response_content
from ..exceptions import ErrorResponse
from ..exceptions.error_code import MsgCode
from werkzeug.local import LocalProxy


def auth_user(func):
    """
    Verify whether the user logs in through the flask-login package.
    If the user does not install flask-login, it will pass by default.
    :return: auth result
    :rtype: bool
    """

    def wrapper():
        try:
            cr = current_app.login_manager
        except Exception as e:
            logging.error(e)
            return func()
        current_user = LocalProxy(lambda: get_user())

        def get_user():
            if _request_ctx_stack.top is not None and not hasattr(_request_ctx_stack.top, 'user'):
                cr._load_user()
            return getattr(_request_ctx_stack.top, 'user', None)
        if not (current_user and current_user.is_authenticated):
            return make_response_content(ErrorResponse(MsgCode.AUTH_FAIL))
        return func()

    return wrapper


def auth_method(func):
    """
    Determine whether request methods is post
    :return: auth result
    :rtype: bool
    """

    def wrapper():
        if request.method != 'POST':
            return make_response_content(ErrorResponse(MsgCode.REQUEST_METHOD_ERROR))
        return func()

    return wrapper
