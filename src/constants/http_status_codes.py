HTTP_200_OK = 200
HTTP_201_CREATED = 201
HTTP_204_NO_CONTENT = 204
HTTP_301_MOVED_PERMANENTLY = 301
HTTP_302_FOUND = 302
HTTP_400_BAD_REQUEST = 400
HTTP_401_UNAUTHORIZED = 401
HTTP_403_FORBIDDEN = 403
HTTP_404_NOT_FOUND = 404
HTTP_409_CONFLICT = 409
HTTP_500_INTERNAL_SERVER_ERROR = 500
HTTP_502_BAD_GATEWAY = 502
HTTP_503_SERVICE_UNAVAILABLE = 503

# Define functions to check the status code category
def is_informational(status):
    """Check if the status code is informational (1xx)."""
    return 100 <= status < 200

def is_success(status):
    """Check if the status code indicates success (2xx)."""
    return 200 <= status < 300

def is_redirect(status):
    """Check if the status code indicates a redirect (3xx)."""
    return 300 <= status < 400

def is_client_error(status):
    """Check if the status code indicates a client error (4xx)."""
    return 400 <= status < 500

def is_server_error(status):
    """Check if the status code indicates a server error (5xx)."""
    return 500 <= status < 600