from auth import authenticate_user
from database import connect_to_database

def run_application():
    if authenticate_user("admin", "secret"):
        return connect_to_database()
    return "Authentication failed"
