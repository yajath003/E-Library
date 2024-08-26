from functools import wraps
from flask import request
from werkzeug.security import check_password_hash

from api.validation import BusinessValidationError
from author.models import Author

def auth_required(f):

    def check_auth(username_test, password_test):
        """This function is called to check if a username /
        password combination is valid.
        """
        author = Author.query.filter(Author.email == username_test).first()
        if author is None:
            raise BusinessValidationError(status_code=409, error_code="AUTH01", error_message="email does not exists")            
        else:    
            if not check_password_hash(author.password, password_test):
                raise BusinessValidationError(status_code=409, error_code="AUTH02", error_message="Incorrect password")                    
        return True    
    
    def authenticate():
        """Sends a 401 response that enables basic auth"""
        raise BusinessValidationError(status_code=409, error_code="AUTH03", error_message="Basic authentication required")                    
    
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated
    
    
