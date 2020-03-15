# handlers.py
from flask import Blueprint, render_template

error_pages = Blueprint('error_pages', __name__)

# for handling undefined pages
@error_pages.app_errorhandler(404)
def error_404(error):
    # (error) :-passing error we found
    return render_template('error_pages/404.html'), 404


@error_pages.app_errorhandler(403) # 403 is for forbidden access
def error_403(error):
    return render_template('error_pages/403.html'), 403
