def authenticate_user(username, password):
    """
    Authenticates a user using username and password.
    """
    if username == "admin" and password == "secret":
        return True
    return False
