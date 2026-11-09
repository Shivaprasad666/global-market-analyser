from flask import Blueprint, render_template
from flask_login import login_required
from .models import Product, AnalysisHistory
main_bp=Blueprint('main',__name__)
@main_bp.route('/')
def index(): return render_template('index.html')
@main_bp.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html',products=Product.query.order_by(Product.name).all(),history=AnalysisHistory.query.filter_by(user_id=__import__('flask_login').current_user.id).order_by(AnalysisHistory.created_at.desc()).limit(8).all())
