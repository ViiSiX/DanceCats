from flask import render_template, request, redirect, url_for
from app import app
from app.forms import RegisterForm


@app.route('/')
def index():
    jobs = [
        {
            "name": "Count Application Number",
            "connection": "FullDB",
            "scheduling": "Everyday at "
        }
    ]
    return render_template('index.html',
                           title='Dance Cat Reporting',
                           jobs=jobs)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        return redirect('/')
    return render_template('register.html', form=form)
