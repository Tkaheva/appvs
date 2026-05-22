from flask import Blueprint, request, jsonify, render_template, session, redirect, url_for
from app.models import User, UserRole

auth_bp = Blueprint('auth', __name__)

# База пользователей (в реальном проекте - из БД)
USERS_DB = {
    'admin': {
        'id': 1,
        'username': 'admin',
        'password': 'admin123',
        'full_name': 'Администратор системы',
        'role': 'admin',
        'department': 'IT',
        'permissions': ['view_all', 'edit_all', 'delete_all', 'manage_users', 'view_reports', 'generate_reports']
    },
    'supervisor': {
        'id': 2,
        'username': 'supervisor',
        'password': 'super123',
        'full_name': 'Руководитель отдела продаж',
        'role': 'supervisor',
        'department': 'Sales',
        'permissions': ['view_team', 'edit_team', 'view_reports', 'generate_reports', 'assign_training']
    },
    'manager': {
        'id': 3,
        'username': 'manager',
        'password': 'manager123',
        'full_name': 'Менеджер по продажам',
        'role': 'manager',
        'department': 'Sales',
        'permissions': ['view_own', 'view_own_reports']
    }
}

def get_user_permissions(role):
    """Получение прав доступа по роли"""
    permissions_map = {
        'admin': ['view_all', 'edit_all', 'delete_all', 'manage_users', 'view_reports', 'generate_reports', 'view_training_plans', 'edit_training_plans'],
        'supervisor': ['view_team', 'edit_team', 'view_reports', 'generate_reports', 'assign_training', 'view_training_plans'],
        'manager': ['view_own', 'view_own_reports', 'view_own_training_plan']
    }
    return permissions_map.get(role, [])

def login_required(roles=None):
    """Декоратор для проверки прав доступа"""
    def decorator(f):
        from functools import wraps
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not session.get('user'):
                return redirect(url_for('auth.login'))
            
            if roles and session.get('user', {}).get('role') not in roles:
                return jsonify({'error': 'Доступ запрещён', 'required_roles': roles}), 403
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    
    data = request.get_json() if request.is_json else request.form
    username = data.get('username')
    password = data.get('password')
    
    user_data = USERS_DB.get(username)
    
    if user_data and user_data['password'] == password:
        session['user_id'] = user_data['id']
        session['user'] = {
            'id': user_data['id'],
            'username': user_data['username'],
            'full_name': user_data['full_name'],
            'role': user_data['role'],
            'department': user_data.get('department', ''),
            'permissions': get_user_permissions(user_data['role'])
        }
        
        if request.is_json:
            return jsonify({
                'success': True, 
                'redirect': '/dashboard',
                'user': session['user']
            })
        return redirect(url_for('main.dashboard'))
    
    if request.is_json:
        return jsonify({'success': False, 'error': 'Неверный логин или пароль'}), 401
    return render_template('login.html', error='Неверный логин или пароль')

@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@auth_bp.route('/api/user/permissions')
def get_permissions():
    """API для получения прав текущего пользователя"""
    if not session.get('user'):
        return jsonify({'error': 'Не авторизован'}), 401
    return jsonify({
        'success': True,
        'user': session['user']
    })
