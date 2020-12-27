from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.ext.sqlalchemy.fields import QuerySelectMultipleField
from wtforms.validators import ValidationError, DataRequired, EqualTo, Length, Email, Regexp
from wtforms import TextAreaField
from wtforms.widgets import ListWidget, CheckboxInput
from wtforms import PasswordField
from app.models import User
from wtforms import BooleanField


# from app.models import Post

class PositionPostForm(FlaskForm):
    course = StringField('Course', validators=[DataRequired()])
    semester = StringField('Semester', validators=[DataRequired()])
    numbersOfTA = StringField('Numbers Of TA', validators=[DataRequired()])
    minGPA = StringField('Minimum GPA', validators=[DataRequired()])
    minGrade = StringField('Minimum Grade', validators=[DataRequired()])
    requirements = StringField('Requirements', validators=[DataRequired()])
    submit = SubmitField('Post')


class PositionApplyForm(FlaskForm):
    instructorname = StringField('Instructor Name', validators=[DataRequired()])
    course = StringField('Course', validators=[DataRequired()])
    grade = StringField('Grade', validators=[DataRequired()])
    takenTime = StringField('Year/Semester You Took The Class', validators=[DataRequired()])
    applyTime = StringField('Year/Semester You Want to Apply', validators=[DataRequired()])
    submit = SubmitField('Apply')


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Regexp('^[\w.+\-]+@wsu\.edu$',
                                                                          message='Usernaem should be WSU email')])
    email = StringField('Email', validators=[DataRequired(), Email(message='not valid')])
    wsuId = StringField('WSU ID', validators=[DataRequired(), Regexp('^\d+$', message='Please input WSU ID')])
    position = SelectField('Student or Instructor', choices=[(2, 'Student'), (1, 'Instructor')])
    password = PasswordField('Password',
                             validators=[DataRequired(), Length(6, 16, message='Password length should be 6-16')])
    password2 = PasswordField('Repeat Password', validators=[EqualTo('password', message='password not match')])

    submit = SubmitField('Register')


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class SortForm(FlaskForm):
    sort = SelectField('Sort by', choices=[(2, 'Date'), (1, 'Course')])
    checkbox = BooleanField('checkbox')
    submit = SubmitField('Refresh')

# 学生信息表格
class sForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    major = StringField('Major', validators=[DataRequired()])
    courseA = StringField('Course you have got A', validators=[DataRequired()])
    taExp = StringField('Course have been TA before', validators=[DataRequired()])
    submit = SubmitField('Submit')

# 老师信息表格
class insForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    course = StringField('Courses you are teaching', validators=[DataRequired()])
    semester = StringField('Semester', validators=[DataRequired()])
    phone = StringField('Phone Number', validators=[DataRequired()])
    submit = SubmitField('Submit')

#老师修改Post表格
class editForm(FlaskForm):
    numbersOfTA = StringField('Numbers Of TA', validators=[DataRequired()])
    minGPA = StringField('Minimum GPA', validators=[DataRequired()])
    minGrade = StringField('Minimum Grade', validators=[DataRequired()])
    requirements = StringField('Requirements', validators=[DataRequired()])
    submit = SubmitField('Post')