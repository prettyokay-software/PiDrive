from app.models import user_models as users
from functools import wraps
from flask import Blueprint, request, abort, current_app

import os
import json

api_blueprint = Blueprint('api', __name__ ,template_folder='templates')

def is_authorized_api_user(roles=False):
    """Verify API Token and its owners permission to use it"""
    if 'API_ID' not in request.headers:
        return False
    if 'API_KEY' not in request.headers:
        return False
    api_key = users.ApiKey.query.filter(users.ApiKey.id==request.headers['API_ID']).first()
    if not api_key:
        return False
    if not current_app.user_manager.verify_password(request.headers['API_KEY'], api_key.hash):
        return False
    if not roles:
        return True
    if api_key.user.has_role('admin'):
        return True
    for role in roles:
        if api_key.user.has_role(role):
            return True
    return False


def roles_accepted_api(*role_names):
    def wrapper(view_function):
        @wraps(view_function)
        def decorated_view_function(*args, **kwargs):
            if not is_authorized_api_user(role_names):
                return abort(403)
            return view_function(*args, **kwargs)
        return decorated_view_function
    return wrapper


def api_credentials_required():
    def wrapper(view_function):
        @wraps(view_function)
        def decorated_view_function(*args, **kwargs):
            if not is_authorized_api_user():
                return abort(403)
            return view_function(*args, **kwargs)
        return decorated_view_function
    return wrapper

@api_blueprint.route('/api/PathData', methods=['GET'])
def build_jstree_json():
    path = request.args.get("path")
    ajax_search = request.args.get("str")

    # If no path supplied in query, see if it's an ajax search to a valid dir. If not, quit
    if not path:
        if os.path.exists(ajax_search):
            path = ajax_search
        else:
            return json.dumps([])

    # Yes this is really the comparision that I want
    # string "false" is returned on first load
    if path =="false":
        path = "/"
        listing = get_current_directory_listing(path)
        return json.dumps(listing)  
    
    #Otherwise just get the subdirs of the folder we're in

    listing = get_allsubdirs(path)    
    
    return json.dumps(listing)    

def get_current_directory_listing(path):
    output = {}
    output["text"] = path #path.decode('latin1')
    output["type"] = "directory"
    output["children"] = get_allsubdirs(path)
    return output

def get_allsubdirs(path):
    result = []
    for item in os.scandir(path):
        # Check if we're looking at a directory, and ignore any hidden ones (.folder)
        if item.is_dir() and not item.name.startswith("."):
            item_json = {}
            item_json["text"] = item.name
            item_json["type"] = "directory"
            item_json["children"] = True
            result.append(item_json)
    return result