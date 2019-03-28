from flask_wtf import Form
from wtforms import SubmitField, TextAreaField, StringField, IntegerField
from wtforms.validators import DataRequired, Length

class MessageForm(Form):
    message = TextAreaField(('Nachricht'), validators=[DataRequired(), Length(min=0, max=140)])
    submit = SubmitField('Senden')

class CreateExerciseForm(Form):
    title = StringField('Titel', validators=[DataRequired()])
    description = TextAreaField('Beschreibung', validators=[DataRequired()])
    submit = SubmitField('Hinzufügen')
