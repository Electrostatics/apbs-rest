from flask import Flask

from views import workflow_app

'''Specifies location of static React files to deliver'''
app = Flask(
    __name__,
    static_folder="build/static",
    template_folder="build")

app.register_blueprint(workflow_app)

from . import views