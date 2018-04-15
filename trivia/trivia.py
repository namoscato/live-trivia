import os

from flask import Flask, request, g, render_template, jsonify, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'postgres://localhost/trivia')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Question(db.Model):
    __tablename__ = 'question'

    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(100))
    options = db.Column(db.String(200))

    def __init__(self, text, options):
        self.text = text
        self.options = options


class Answer(db.Model):
    __tablename__ = 'answer'

    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer)
    user = db.Column(db.String(50))
    value = db.Column(db.String(50))
    is_correct = db.Column(db.Boolean)

    def __init__(self, question_id, user, value):
        self.question_id = question_id
        self.user = user
        self.value = value


@app.route('/')
def index_action():
    return render_template('question.html')


@app.route('/question', methods=['GET', 'POST'])
def question_action():
    if 'POST' == request.method:
        body = request.get_json()

        question = Question(
            body['text'],
            "|".join(body['options'])
        )
        db.session.add(question)
        db.session.commit()

        return jsonify({'id': question.id})
    else:
        question = db.session.query(Question).order_by(Question.id.desc()).first()

        if question is None:
            return '', 204

        return jsonify({
            'id': question.id,
            'text': question.text,
            'options': question.options.split("|")
        })


@app.route('/question/<int:question_id>/answer')
def get_question_answers_action(question_id):
    return jsonify(list(map(
        lambda answer: {
            'user': answer.user,
            'value': answer.value,
        },
        db.session.query(Answer).filter_by(question_id=question_id)
    )))


@app.route('/question/<int:question_id>/grade', methods=['POST'])
def post_question_grade_action(question_id):
    correct_users = request.get_json()['correct_users']
    answers = db.session.query(Answer).filter_by(question_id=question_id)

    for answer in answers:
        answer.is_correct = (answer.user in correct_users)

    db.session.commit()

    return '', 204


@app.route('/answer', methods=['POST'])
def post_answer_action():
    body = request.form

    answer = Answer(
        body['question_id'],
        body['user'],
        body['value']
    )
    db.session.add(answer)
    db.session.commit()

    return jsonify({'id': answer.id})


@app.route('/answer/<int:answer_id>')
def get_question_answer_action(answer_id):
    answer = db.session.query(Answer).filter_by(id=answer_id).first()
    return ('', 400) if answer is None else jsonify({'is_correct': answer.is_correct})


@app.cli.command('db:init')
def db_init_command():
    print('Initializing database')
    db.create_all()


@app.context_processor
def override_url_for():
    return dict(url_for=dated_url_for)


def dated_url_for(endpoint, **values):
    if endpoint == 'static':
        filename = values.get('filename', None)
        if filename:
            file_path = os.path.join(app.root_path, endpoint, filename)
            values['q'] = int(os.stat(file_path).st_mtime)
    return url_for(endpoint, **values)
