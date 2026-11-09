import re
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, current_user
from . import db
from .models import User

auth_bp=Blueprint('auth',__name__)
@auth_bp.route('/register',methods=['GET','POST'])
def register():
    if current_user.is_authenticated: return redirect(url_for('main.dashboard'))
    if request.method=='POST':
        name=request.form.get('name','').strip(); email=request.form.get('email','').strip().lower(); password=request.form.get('password','')
        if not name or len(name)>100 or not re.fullmatch(r'[^@\s]+@[^@\s]+\.[^@\s]+',email): flash('Enter a valid name and email.','danger')
        elif len(password)<8: flash('Password must contain at least 8 characters.','danger')
        elif User.query.filter_by(email=email).first(): flash('Email is already registered.','danger')
        else:
            u=User(name=name,email=email); u.set_password(password); db.session.add(u); db.session.commit(); login_user(u); return redirect(url_for('main.dashboard'))
    return render_template('auth.html',mode='Register')
@auth_bp.route('/login',methods=['GET','POST'])
def login():
    if current_user.is_authenticated: return redirect(url_for('main.dashboard'))
    if request.method=='POST':
        u=User.query.filter_by(email=request.form.get('email','').strip().lower()).first()
        if u and u.check_password(request.form.get('password','')): login_user(u); return redirect(url_for('main.dashboard'))
        flash('Invalid email or password.','danger')
    return render_template('auth.html',mode='Login')
@auth_bp.route('/logout',methods=['POST'])
def logout(): logout_user(); return redirect(url_for('main.index'))
