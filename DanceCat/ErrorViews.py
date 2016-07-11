"""Render special page like 404 or 500."""

from flask import render_template
from DanceCat import app, Constants


@app.errorhandler(404)
def page_not_found(error):
    """404 Not Found Page for the application."""
    return render_template('error/404.html',
                           title=Constants.PROJECT_NAME,
                           error=error), 404


@app.errorhandler(500)
def page_error(error):
    """500 Error Page for the application"""
    return render_template('error/500.html',
                           title=Constants.PROJECT_NAME,
                           error=error), 500
