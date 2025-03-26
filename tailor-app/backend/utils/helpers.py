from flask import session
from uuid import uuid4

def get_user_id():
    if 'user_id' not in session:
        session['user_id'] = f"user_{uuid4().hex[:8]}"
    # return session['user_id']
    return "123" # temporary