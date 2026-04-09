from flask import Blueprint, request, jsonify, render_template, session, redirect, url_for

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    
    data = request.get_json() if request.is_json else request.form
    username = data.get('username')
    password = data.get('password')
    
    if username == 'admin' and password == 'admin123':
        session['user_id'] = 1
        session['user'] = {'username': 'admin', 'full_name': 'Администратор', 'role': 'admin'}
        if request.is_json:
            return jsonify({'success': True, 'redirect': '/dashboard'})
        return redirect(url_for('main.dashboard'))
    
    if request.is_json:
        return jsonify({'success': False, 'error': 'Неверный логин или пароль'}), 401
    return render_template('login.html', error='Неверный логин или пароль')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    return jsonify({'success': True})

@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))
