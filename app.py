from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date
from datetime import datetime
from forms import FeedbackForm


def russian_date(value):
    if isinstance(value, (datetime, date)):
        months = [
    'января', 'февраля', 'марта', 'апреля', 'мая', 'июня',
    'июля', 'августа', 'сентября', 'октября', 'ноября', 'декабря'
    ]
        return f"{value.day} {months[value.month - 1]} {value.year}"
    return value

app = Flask(__name__)
app.config['SECRET_KEY'] = 'my-secret-key-123456'
app.jinja_env.filters['russian_date'] = russian_date

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///newsweblab2.db'
db = SQLAlchemy(app)


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200),nullable=False )
    date = db.Column(db.Date)



@app.route("/")
@app.route("/index")
def index():
    posts = Post.query.all()
    today = date.today()
    return render_template('index.html', posts = posts, today = today)

@app.route("/about")
def about():
    return render_template('about.html')

@app.route("/contact")
def contact():
    return render_template('contact.html')

@app.route("/feedback", methods=['POST', 'GET'])
def feedback():
    form = FeedbackForm()
    if form.validate_on_submit():
        name = form.name.data
        email = form.email.data
        message = form.message.data
        return render_template('feedback_success.html', name=name, email=email, message=message)
    return render_template('feedback.html', form=form)
    # if request.method == 'POST':    
    # return render_template('feedback.html')

@app.route("/create", methods=['POST', 'GET'])
def create():
    if request.method == 'POST':
        try:
            title = request.form['title']
            date_str = request.form['date']
            # Дата приходит в формате 'YYYY-MM-DD'
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except:
            return "Неверный формат даты"


        post = Post(title = title, date = date)

        try:
            db.session.add(post)
            db.session.commit()
            return redirect('/')
        except:
            return "При создании статьи произошла ошибка"
    else:
        return render_template('create.html')

if __name__ == '__main__':
    app.run(debug = True)