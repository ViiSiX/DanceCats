from flask import render_template
from DanceCat import app, Constants


@app.errorhandler(404)
def page_not_found(e):
    return render_template('error/404.html',
                           title=Constants.PROJECT_NAME), 404


@app.errorhandler(500)
def page_error(e):
    return render_template('error/500.html',
                           title=Constants.PROJECT_NAME), 500
