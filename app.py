from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date, timezone
from forms import FeedbackForm
from models import db, User, Article, Comment
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash


def russian_date(value):
    if isinstance(value, (datetime, date)):
        months = [
    'января', 'февраля', 'марта', 'апреля', 'мая', 'июня',
    'июля', 'августа', 'сентября', 'октября', 'ноября', 'декабря'
    ]
        return f"{value.day} {months[value.month - 1]} {value.year}"
    return value

CATEGORIES = {
    'general': 'Общее',
    'tech': 'Технологии',
    'sports': 'Спорт',
    'culture': 'Культура',
    'politics': 'Политика',
    'science': 'Наука'
}

app = Flask(__name__)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login' 
login_manager.login_message = "Пожалуйста, войдите, чтобы получить доступ."

app.config['SECRET_KEY'] = 'my-secret-key-123456'
app.jinja_env.filters['russian_date'] = russian_date
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///newsweblab2.db'

db.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Регистрация
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name'].strip()
        email = request.form['email'].strip()
        password = request.form['password']

        if not name or not email or not password:
            return "Все поля обязательны", 400

        if User.query.filter_by(email=email).first():
            return "Пользователь с таким email уже существует", 400

        hashed = generate_password_hash(password, method='pbkdf2:sha256')
        new_user = User(name=name, email=email, hashed_password=hashed)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))

    return render_template('register.html')


# Вход
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.hashed_password, password):
            login_user(user)
            return redirect(url_for('index'))
        else:
            return render_template('not_user.html')

    return render_template('login.html')


# Выход
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route("/")
@app.route("/index")
def index():
    articles = Article.query.all()
    today_utc = datetime.now(timezone.utc).date()

    for article in articles:
        article.is_new = article.created_date.date() == today_utc
    return render_template('index.html', articles = articles, CATEGORIES=CATEGORIES)

@app.route("/articles")
def articles():
    articles = Article.query.all()
    today_utc = datetime.now(timezone.utc).date()
    for article in articles:
        article.is_new = article.created_date.date() == today_utc
    return render_template('articles.html', articles = articles, CATEGORIES=CATEGORIES)

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

@app.route("/news/<int:id>", methods=['GET', 'POST'])
def article_content(id):
    article = Article.query.get(id)
    if request.method == 'POST':
        if not current_user.is_authenticated:
            return "Только авторизированные пользователи могут оставлять комментарии"
        
        text = request.form.get('text', '').strip()

        comment = Comment(
            text=text,
            author_name=current_user.name,
            article_id=article.id
        )
        db.session.add(comment)
        db.session.commit()
        return redirect(url_for('article_content', id=id))

    comments = Comment.query.filter_by(article_id=id).order_by(Comment.created_date.desc()).all()
    return render_template('article_content.html', article=article, comments=comments, CATEGORIES=CATEGORIES)

    
@app.route("/create-articles", methods=['GET', 'POST'])
@login_required
def create():
    if request.method == 'POST':
        title = request.form.get('title')
        text = request.form.get('text')
        category = request.form.get('category', 'general')

        # Создание статьи
        article = Article(
            title=title,
            text=text,
            category=category,
            user_id=current_user.id  
        )

        try:
            db.session.add(article)
            db.session.commit()
            return redirect('/')
        except:
            db.session.rollback()
            return "При создании статьи произошла ошибка"

    else:
        return render_template('create.html', categories=CATEGORIES)
    
@app.route("/edit-article/<int:id>", methods=['GET', 'POST'])
@login_required
def edit_article(id):
    article = Article.query.get(id)

    if article.author != current_user:  
        return "вы не автор"

    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        text = request.form.get('text', '').strip()
        category = request.form.get('category', 'general')

        article.title = title
        article.text = text
        article.category = category

        try:
            db.session.commit()
            return redirect(url_for('article_content', id=article.id))
        except:
            db.session.rollback()
            return "При создании статьи произошла ошибка"

    return render_template('edit_article.html', article=article, categories=CATEGORIES)


@app.route("/delete-article/<int:id>", methods=['POST'])
@login_required
def delete_article(id):
    article = Article.query.get(id)

    if article.author != current_user:  
        return "вы не автор"

    db.session.delete(article)
    db.session.commit()
    return redirect(url_for('index'))

@app.route("/articles/<category>")
def articles_category(category):
    if category not in CATEGORIES:
        return "Категория не найдена"
    articles = Article.query.filter_by(category=category).all()
    today_utc = datetime.now(timezone.utc).date()
    for article in articles:
        article.is_new = article.created_date.date() == today_utc if article.created_date else False

    category_name = CATEGORIES[category]
    
    return render_template('articles.html', articles=articles, category_name=category_name, CATEGORIES=CATEGORIES)



if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        if not User.query.first():
            test_user = User(
                name="Админ",
                email="admin@example.com",
                hashed_password=generate_password_hash("123")
            )
            db.session.add(test_user)
            db.session.commit()
    app.run(debug = True)

