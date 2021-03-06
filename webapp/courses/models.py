from webapp.db import db
from flask_login import current_user
from webapp.user.models import User_answer

"""Модели для базы данных, по части курсов
и входящих в них уроков, вопросов, тестов
и вариантов ответов на них
"""


lessons_to_courses = db.Table('lessons_to_courses',
                              db.Column('course_id', db.Integer, db.ForeignKey('Course.id')),
                              db.Column('lesson_id', db.Integer, db.ForeignKey('Lesson.id')),
                              db.Column('order', db.Integer))

questions_to_lessons = db.Table('questions_to_lessons',
                                db.Column('lesson_id', db.Integer, db.ForeignKey('Lesson.id')),
                                db.Column('question_id', db.Integer, db.ForeignKey('Question.id')))

answervariants_to_questions = db.Table('answervariants_to_questions',
                                       db.Column('question_id', db.Integer, db.ForeignKey('Question.id')),
                                       db.Column('answervariant_id', db.Integer, db.ForeignKey('AnswerVariant.id')))


class Course(db.Model):
    """Модель Курса, с условиями, инфой и входящими уроками"""
    __tablename__ = 'Course'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    lessons = db.relationship("Lesson", secondary=lessons_to_courses, backref='courses')
    info = db.Column(db.Text, nullable=True)
    conditions = db.Column(db.String(64))
    content = db.Column(db.Text, nullable=True)

    def __repr__(self):
        return f'Курс {self.id} {self.name}'


class Lesson(db.Model):
    """Модель урока, с типом материала, вопросами и необходимым кол-вом ответов"""
    __tablename__ = 'Lesson'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    material_type = db.Column(db.String, nullable=False)
    material = db.Column(db.Text, nullable=True)
    questions = db.relationship("Question", secondary=questions_to_lessons, backref='lessons')
    questions_to_pass = db.Column(db.Integer)

    def __repr__(self):
        return f'Урок {self.id} {self.name}'

    def passed(self, course_id):
        """Метод, позволяющий определить, пройден ли урок пользователем"""
        if self.questions_to_pass == User_answer.query.filter(
                                     User_answer.user_id == current_user.id,
                                     User_answer.answer_status == 'correct',
                                     User_answer.lesson_id == self.id,
                                     User_answer.course_id == course_id).count():
            return 'passed'
        else:
            return 'not passed'


class Slide(db.Model):
    """Содержит информацию о пути к изображеням для элемента slides-carousel"""
    __tablename__ = 'Slide'
    id = db.Column(db.Integer, primary_key=True)
    lesson_id = db.Column(db.Integer,
                          db.ForeignKey('Lesson.id',
                                        ondelete='CASCADE'),
                          index=True)
    lessons = db.relationship('Lesson', backref='slides')
    link = db.Column(db.String(128))

    def __repr__(self):
        return f'Слайд {self.id} {self.link}'


class Question(db.Model):
    """Модель вопроса для урока, с типом вопроса, вариантами овтета, правильным ответом"""
    __tablename__ = 'Question'
    id = db.Column(db.Integer, primary_key=True)
    correctanswer = db.Column(db.String(128))
    question_text = db.Column(db.String(128))
    question_type = db.Column(db.String(50))
    answervariants = db.relationship("AnswerVariant",
                                     secondary=answervariants_to_questions)

    def __repr__(self):
        return f'Вопрос {self.id} {self.question_text}, тип {self.question_type}'

    def answered(self, lesson_id, course_id):
        """Метод, определяющий, дал ли пользователь верный ответ на
        КОНКРЕТНЫЙ вопрос в КОНКРЕТНОМ уроке, в КОНКРЕТНОМ курсе
        """
        if User_answer.query.filter(User_answer.user_id == current_user.id,
                                    User_answer.answer_status == 'correct',
                                    User_answer.lesson_id == lesson_id,
                                    User_answer.question_id == self.id,
                                    User_answer.course_id == course_id).all():
            return 'answered'


class AnswerVariant(db.Model):
    """Модель для списка вариантов ответа на тестовые вопросы"""
    __tablename__ = 'AnswerVariant'
    id = db.Column(db.Integer, primary_key=True)
    answer_text = db.Column(db.String(128))

    def __repr__(self):
        return f'Ответ {self.id} {self.answer_text}'
