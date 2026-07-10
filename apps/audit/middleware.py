import threading

_state = threading.local()


class CurrentUserMiddleware:
    """Stashes the request's user so non-request code (signals, services)
    can attribute audit log entries without threading the user through
    every function call. Read-only convenience — never used for auth."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        _state.user = getattr(request, "user", None)
        try:
            return self.get_response(request)
        finally:
            _state.user = None


def get_current_user():
    return getattr(_state, "user", None)
