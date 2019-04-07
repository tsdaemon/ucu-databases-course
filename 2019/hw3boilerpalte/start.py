from flask import Flask

from students.controller import students

app = Flask(__name__)
app.register_blueprint(students, url_prefix='/students')
# TODO: register your blueprints here

if __name__ == '__main__':
    app.run()
