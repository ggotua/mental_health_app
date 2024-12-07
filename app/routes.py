from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from datetime import datetime
from .models import DailyReflection

main = Blueprint('main', __name__)

@main.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return render_template('index.html')

@main.route('/dashboard')
@login_required
def dashboard():
    today = datetime.now().date()
    today_reflection = DailyReflection.get_by_user_and_date(current_user.id, today.strftime('%Y-%m-%d'))
    recent_reflections = DailyReflection.get_user_reflections(current_user.id)
    return render_template('dashboard.html', 
                         today_reflection=today_reflection,
                         recent_reflections=recent_reflections,
                         today=today.strftime('%Y-%m-%d'))

@main.route('/reflect', methods=['GET', 'POST'])
@login_required
def reflect():
    today = datetime.now().date()
    if request.method == 'POST':
        achievement_1 = request.form.get('achievement_1')
        achievement_2 = request.form.get('achievement_2')
        achievement_3 = request.form.get('achievement_3')
        
        if not all([achievement_1, achievement_2, achievement_3]):
            flash('Please fill in all three achievements.', 'error')
            return redirect(url_for('main.reflect'))
        
        existing_reflection = DailyReflection.get_by_user_and_date(
            current_user.id, 
            today.strftime('%Y-%m-%d')
        )
        
        if existing_reflection:
            existing_reflection.update(
                achievement_1=achievement_1,
                achievement_2=achievement_2,
                achievement_3=achievement_3
            )
            flash('Your reflection has been updated!', 'success')
        else:
            DailyReflection.create(
                current_user.id,
                today.strftime('%Y-%m-%d'),
                achievement_1,
                achievement_2,
                achievement_3
            )
            flash('Your reflection has been saved!', 'success')
        
        return redirect(url_for('main.dashboard'))
    
    existing_reflection = DailyReflection.get_by_user_and_date(
        current_user.id, 
        today.strftime('%Y-%m-%d')
    )
    return render_template('reflect.html', reflection=existing_reflection)

@main.route('/edit_reflection/<date>', methods=['GET', 'POST'])
@login_required
def edit_reflection(date):
    reflection = DailyReflection.get_by_user_and_date(current_user.id, date)
    if not reflection:
        flash('Reflection not found.', 'error')
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        achievement_1 = request.form.get('achievement_1')
        achievement_2 = request.form.get('achievement_2')
        achievement_3 = request.form.get('achievement_3')
        
        if not all([achievement_1, achievement_2, achievement_3]):
            flash('Please fill in all three achievements.', 'error')
            return redirect(url_for('main.edit_reflection', date=date))
        
        reflection.update(
            achievement_1=achievement_1,
            achievement_2=achievement_2,
            achievement_3=achievement_3
        )
        flash('Your reflection has been updated!', 'success')
        return redirect(url_for('main.dashboard'))
    
    return render_template('edit_reflection.html', reflection=reflection)

@main.route('/get_reflections')
@login_required
def get_reflections():
    reflections = DailyReflection.get_user_reflections(current_user.id)
    return jsonify([{
        'id': r.id,
        'date': r.date,
        'achievements': [r.achievement_1, r.achievement_2, r.achievement_3],
        'created_at': r.created_at,
        'updated_at': r.updated_at
    } for r in reflections])
