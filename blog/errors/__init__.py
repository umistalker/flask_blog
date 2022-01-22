from flask import Blueprint

bp = Blueprint('errors', __name__)

from blog.errors import handlers