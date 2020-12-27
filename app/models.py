from datetime import datetime
from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import login

# ins_course = db.Table('ins_course',db.Column('instructor_id',db.Integer,db.ForeignKey('instructor.id')),db.Column('course_id',db.Integer,db.ForeignKey('course.id')))

#用户
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64))
    wsuId = db.Column(db.Integer)
    email = db.Column(db.String(120))
    password_hash = db.Column(db.String(128))
    position = db.Column(db.Integer, default=2)
    is_Active = db.Column(db.Boolean, default=False)
    student = db.relationship('Student', uselist=False, backref='user')
    instructor = db.relationship('Instructor', uselist=False, backref='user')

    def __repr__(self):
        return '{},{}'.format(self.id, self.username)

    def password(self):
        return self.password_hash

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def get_password(self, password):
        return check_password_hash(self.password_hash, password)

#老师发布
class PositionPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    phone = db.Column(db.String(64))
    course = db.Column(db.String(64))
    semester = db.Column(db.String(64))
    numbersOfTA = db.Column(db.Integer)
    minGPA = db.Column(db.Integer)
    minGrade = db.Column(db.Integer)
    requirements = db.Column(db.String(128))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    instructor_id = db.Column(db.Integer, db.ForeignKey('instructor.id'))
    # postCourse = db.relationship('Course', uselist=False, backref='post')
    # isSelect = db.Column(db.Boolean, default=False)
# def __repr__(self):
#     return '{},{},{}'.format(self.id, self.username)

#学生申请
class PositionApply(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    instructorname = db.Column(db.String(64))
    name = db.Column(db.String(64))
    course = db.Column(db.String(64))
    grade = db.Column(db.Integer)
    takenTime = db.Column(db.String(64))
    applyTime = db.Column(db.String(64))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    isPending = db.Column(db.Boolean, default=True)
    isSelect = db.Column(db.Boolean, default=False)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'))

# class Course(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     tas = db.Column(db.Integer)
#     isFull = db.Column(db.Boolean, unique=True, default=False)

@login.user_loader
def load_user(id):
    return User.query.get(int(id))

#学生
class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    major = db.Column(db.String(64))
    taExp = db.Column(db.String(64))
    courseA = db.Column(db.String(64))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    applies = db.relationship('PositionApply',backref='student')
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'))
    isSelect = db.Column(db.Boolean, default=False)
    # course_id=db.relationship('Course',secondary=tags)
    # talist_id = db.Column(db.Integer, db.ForeignKey('talist.id'))


#老师
class Instructor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    course = db.Column(db.String(64))
    phone = db.Column(db.String(64))
    semester = db.Column(db.String(64))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    posts = db.relationship('PositionPost',backref='instructor')
    courses = db.relationship('Course',backref='instructor')
    # courses = db.relationship('Course',secondary=ins_course,backref=db.backref('instructor',lazy='dynamic'),lazy='dynamic')
    # def __repr__(self):
    #     return '{},{},{},{},{}'.format(self.id,self.name, self.course,self.phone,self.semester)

#TAlist
# class TaList(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     students = db.relationship('Student',backref='talist')

class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    numbersOfTA = db.Column(db.Integer)
    currentTA = db.Column(db.Integer)
    students = db.relationship('Student',backref='student')
    instructor_id = db.Column(db.Integer, db.ForeignKey('instructor.id'))
    # post_id = db.Column(db.Integer, db.ForeignKey('post.id'))
    # instructors = db.relationship('instructor',secondary=ins_course,backref=db.backref('course',lazy='dynamic'),lazy='dynamic')



