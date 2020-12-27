from __future__ import print_function
import sys
from datetime import datetime
from flask import render_template, flash, redirect, url_for, request, session
from flask_sqlalchemy import sqlalchemy
from sqlalchemy import desc
from app import app, db
from app.forms import RegistrationForm, PositionPostForm, PositionApplyForm, SortForm, sForm, insForm, editForm
from app.models import User, PositionPost, PositionApply, Student, Instructor, Course
from werkzeug.security import generate_password_hash
from flask_login import current_user, login_user, logout_user, login_required
from app.forms import LoginForm
# from app.models import ins_course
from app.forms import PositionPostForm
from flask_bootstrap import Bootstrap

bootstrap = Bootstrap(app)


@app.before_first_request
def initDB(*args, **kwargs):
    db.create_all()

#首页
@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    posts = PositionPost.query.all()
    return render_template('index.html', title="TA Application", posts=posts)

#注册
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data,
                    email=form.email.data,
                    position=form.position.data,
                    wsuId=form.wsuId.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('index'))
    return render_template('register.html', title='Register', form=form)




@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.add(current_user)
        db.session.commit()

#学生主页面
@app.route('/', methods=['GET', 'POST'])
@app.route('/student', methods=['GET', 'POST'])
@login_required
def student():
    sortform = SortForm()
    selected = dict(sortform.sort.choices).get(int(request.args.get('sort', 0)))
    values = {
        'Course': 'course',
        'Date': 'timestamp'
    }
    if request.args.get('checkbox') == 'y':
        posts = db.session.query(PositionPost).filter(PositionPost.course == current_user.student.taExp).all()
        return render_template('student.html', posts=posts, title="TA Position List", sortform=sortform)
    else:
        posts = PositionPost.query.order_by(getattr(PositionPost, values.get(selected, 'timestamp')).desc())
        return render_template('student.html', posts=posts.all(), title="TA Position List", sortform=sortform)
# PositionPost.course == current_user.student.courseA

#老师主页面
@app.route('/', methods=['GET', 'POST'])
@app.route('/instructor', methods=['GET', 'POST'])
@login_required
def instructor():
    posts = db.session.query(PositionApply).filter(PositionApply.instructorname == current_user.instructor.name).all()
    return render_template('instructor.html', title="TA Application List", posts=posts)

#发放TA
@app.route('/postTaPosition', methods=['GET', 'POST'])
@login_required
def postTaPosition():
    form = PositionPostForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            post = PositionPost(course=request.form['course'],
                                    semester=request.form['semester'],
                                    numbersOfTA=request.form['numbersOfTA'],
                                    minGPA=request.form['minGPA'],
                                    minGrade=request.form['minGrade'],
                                    requirements=request.form['requirements'],
                                    instructor_id=current_user.instructor.id)
            course = Course(name=post.course,numbersOfTA=post.numbersOfTA,instructor_id=current_user.instructor.id)
            course.currentTA = 0
            post.name = current_user.instructor.name
            post.phone = current_user.instructor.phone
            post.classes = course
            db.session.add(course)
            db.session.add(post)
            current_user.instructor.courses.append(course)
            current_user.instructor.posts.append(post)
            db.session.commit()
            flash('Posted')
            return redirect('/instructor')
    return render_template('create.html', title="Post TA-Positions", form=form)

#申请TA
@app.route('/applyTaPosition', methods=['GET', 'POST'])
@login_required
def applyTaPosition():
    form = PositionApplyForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            apply = PositionApply(instructorname=request.form['instructorname'],
                                    course=request.form['course'],
                                    grade=request.form['grade'],
                                    takenTime=request.form['takenTime'],
                                    applyTime=request.form['applyTime'],
                                    student_id=current_user.student.id)
            apply.name = current_user.student.name
            apply.isSelect = current_user.student.isSelect
            db.session.add(apply)
            current_user.student.applies.append(apply)
            db.session.commit()
            flash('Applyied')
            return redirect('/student')
    return render_template('apply.html', title="Apply TA-Positions", form=form)

#学生申请状态
@app.route('/status', methods=['GET', 'POST'])
@login_required
def status():
    posts = db.session.query(PositionApply).filter(PositionApply.name == current_user.student.name).all()
    return render_template('status.html', title="TA Application", posts=posts)

#老师看自己Post
@app.route('/instructorPost', methods=['GET', 'POST'])
@login_required
def instructorPost():
    posts = current_user.instructor.posts
    return render_template('instructorPost.html', title="My Posts", posts=posts)

#登录
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.get_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        session['logged_in'] = True
        login_user(user, remember=form.remember_me.data)
        if user.position == 1:
            session['instructor'] = True
            if current_user.is_Active:
                return redirect(url_for('instructor'))
            else:
                return redirect(url_for('insinformation'))
        else:
            session['student'] = True
            if current_user.is_Active:
                return redirect(url_for('student'))
            else:
                return redirect(url_for('sinformation'))
    return render_template('login.html', title='Sign In', form=form)

#登出
@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('instructor', None)
    session.pop('student', None)

    logout_user()
    return redirect(url_for('index'))

# 老师Info
@app.route('/insinformation', methods=['GET', 'POST'])
def insinformation():
    form = insForm()
    if form.validate_on_submit():
        instructor = Instructor(name=form.name.data,
                                course=form.course.data,
                                semester=form.semester.data,
                                phone=form.phone.data,
                                user_id=current_user.id)
        # instructor = Instructor(user_id=current_user.id)
        current_user.is_Active = True
        db.session.add(instructor)
        db.session.commit()
        return redirect(url_for('instructor'))
    return render_template('insinformation.html', title='Instructor Profile', form=form)


# 学生Info
@app.route('/sinformation', methods=['GET', 'POST'])
def sinformation():
    form = sForm()
    if form.validate_on_submit():
        student = Student(name=form.name.data,
                          taExp=form.taExp.data,
                          major=form.major.data,
                          courseA=form.courseA.data,
                          user_id=current_user.id)
        # student = Student(user_id=current_user.id)
        current_user.is_Active = True
        db.session.add(student)
        db.session.commit()
        return redirect(url_for('student'))
    return render_template('sinformation.html', title='extra information', form=form)

#老师修改Post
@app.route('/editPost/<postid>', methods=['GET', 'POST'])
@login_required
def editPost(postid):
    form = editForm()
    currentPost = PositionPost.query.filter_by(id=postid).first()
    if request.method == 'POST':
        if form.validate_on_submit():
            post = PositionPost(numbersOfTA=request.form['numbersOfTA'],
                                minGPA=request.form['minGPA'],
                                minGrade=request.form['minGrade'],
                                requirements=request.form['requirements'])
            currentPost.numbersOfTA = post.numbersOfTA
            currentPost.minGPA = post.minGPA
            currentPost.minGrade = post.minGrade
            currentPost.requirements = post.requirements
            db.session.commit()
        return redirect(url_for('instructorPost'))
    return render_template('edit.html', title='Edit TA Postition', form=form)


#老师删除Post
@app.route('/deltePost/<postid>', methods=['GET', 'POST'])
@login_required
def deletePost(postid):
    post = PositionPost.query.filter_by(id=postid).first()
    db.session.delete(post)
    db.session.commit()
    return redirect(url_for('instructorPost'))

#学生删除申请
@app.route('/withdraw/<postid>', methods=['GET', 'POST'])
@login_required
def withdraw(postid):
    post = PositionApply.query.filter_by(id=postid).first()
    student = Student.query.filter_by(id=post.student_id).first()
    student.isSelect = False
    db.session.delete(post)
    db.session.commit()
    return redirect(url_for('status'))

#老师选择学生
@app.route('/select/<postid>', methods=['GET', 'POST'])
@login_required
def select(postid):
    post = PositionApply.query.filter_by(id=postid).first()
    course = Course.query.filter_by(name=post.course).first()
    student = Student.query.filter_by(id=post.student_id).first()
    if student.isSelect or course.numbersOfTA <= course.currentTA:
        flash('Fail to select this student')
        return redirect(url_for('instructor')) 
    else:
        course.students.append(student)
        course.currentTA = course.currentTA + 1
        student.isSelect = True
        post.isSelect = True
        post.isPending = False
        # db.session.delete(post)
        db.session.commit()
        flash('Selected Successfully')
        return redirect(url_for('instructorPost')) 
         

#学生Profile
@app.route('/sProfile', methods=['GET', 'POST'])
@login_required
def sProfile():
    return render_template('sProfile.html', title="Student Profile")

#老师Profile
@app.route('/insProfile', methods=['GET', 'POST'])
@login_required
def insProfile():
    return render_template('insProfile.html', title="Instructor Profile")

# 学生Profile edit
@app.route('/sprofileedit', methods=['GET', 'POST'])
def sprofileedit():
    form = sForm()
    if form.validate_on_submit():
        student = Student(name=form.name.data,
                      taExp=form.taExp.data,
                      major=form.major.data,
                      courseA=form.courseA.data,
                      user_id=current_user.id)
        current_user.student.name = student.name
        current_user.student.major = student.major
        current_user.student.courseA = student.courseA
        current_user.student.taExp = student.taExp
        db.session.commit()
        return redirect(url_for('sProfile'))
    return render_template('sinformation.html', title='Student Profile', form=form)

# 老师Profile edit
@app.route('/insprofileedit', methods=['GET', 'POST'])
def insprofileedit():
    form = insForm()
    if form.validate_on_submit():
        instructor = Instructor(name=form.name.data,
                            course=form.course.data,
                            semester=form.semester.data,
                            phone=form.phone.data,
                            user_id=current_user.id)
        current_user.instructor.name = instructor.name
        current_user.instructor.course = instructor.course
        current_user.instructor.semester = instructor.semester
        current_user.instructor.phone = instructor.phone
        db.session.commit()
        return redirect(url_for('insProfile'))
    return render_template('insinformation.html', title='Instructor Profile', form=form)
