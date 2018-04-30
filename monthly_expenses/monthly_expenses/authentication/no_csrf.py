from rest_framework.authentication import SessionAuthentication


class CsrfExemptSessionAuthentication(SessionAuthentication):
    """
    Do not enforce csrf in requests
    """

    def enforce_csrf(self, request):
        return