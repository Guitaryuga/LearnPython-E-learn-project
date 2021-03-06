import os
import os.path as op

from flask import Flask, render_template, request, url_for, send_from_directory
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_admin.contrib.fileadmin import FileAdmin
from flask_ckeditor import CKEditor, upload_fail, upload_success
from flask_login import LoginManager
from flask_migrate import Migrate

from webapp.model import db
from webapp.user.models import User, User_answer
from webapp.courses.models import Course, Lesson, Question, AnswerVariant
from webapp.admin.custom_views import MyAdminIndexView, UserView, LessonAdmin, CourseAdmin

from webapp.user.views import blueprint as user_blueprint
from webapp.courses.views import blueprint as courses_blueprint

path = op.join(op.dirname(__file__), 'uploads')


def create_app():
    app = Flask(__name__)
    app.config.from_pyfile('config.py')
    db.init_app(app)
    migrate = Migrate(app, db)
    ckeditor = CKEditor(app)

    admin = Admin(app, template_mode='bootstrap3',
                  index_view=MyAdminIndexView())
    admin.add_view(UserView(User, db.session))
    admin.add_view(CourseAdmin(Course, db.session))
    admin.add_view(LessonAdmin(Lesson, db.session))
    admin.add_view(ModelView(User_answer, db.session))
    admin.add_view(ModelView(Question, db.session))
    admin.add_view(ModelView(AnswerVariant, db.session))
    admin.add_view(FileAdmin(path, '/uploads/', name='Upload images'))

    app.register_blueprint(user_blueprint)
    app.register_blueprint(courses_blueprint)

    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'login'

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(user_id)

    @app.route("/test")  # тестовый роут
    def test():
        test_sample = "Welcome to the test-route!"
        test_sample2 = "Here goes test_sample2"
        test_sample3 = "Here goes test_sample3"
        return render_template('test_template.html', test_sample=test_sample,
                               test_sample2=test_sample2,
                               test_sample3=test_sample3)

    @app.route('/uploads/<filename>')
    def uploaded_files(filename):
        path = app.config['UPLOADED_PATH']
        return send_from_directory(path, filename)

    @app.route('/upload', methods=['POST'])
    def upload():
        f = request.files.get('upload')
        extension = f.filename.split('.')[-1].lower()
        if extension not in ['jpg', 'gif', 'png', 'jpeg']:
            return upload_fail(message='Image only!')
        f.save(os.path.join(app.config['UPLOADED_PATH'], f.filename))
        url = url_for('uploaded_files', filename=f.filename)
        return upload_success(url=url)

    return app
