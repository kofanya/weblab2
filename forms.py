from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Email

class FeedbackForm(FlaskForm):
    name = StringField("Имя", validators=[DataRequired()])
    email = StringField("Почта", validators=[Email()])
    message = StringField("Сообщение", validators=[DataRequired()])
    submit = SubmitField("Отправить")
