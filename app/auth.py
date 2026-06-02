from flask import Blueprint, request, jsonify, render_template, session, redirect, url_for

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    
    data = request.get_json() if request.is_json else request.form
    username = data.get('username')
    password = data.get('password')
    
    # Тестовые учётные данные
    if username == 'admin' and password == 'admin123':
        session['user_id'] = 1
        session['user'] = {'username': 'admin', 'full_name': 'Администратор', 'role': 'admin'}
        if request.is_json:
            return jsonify({'success': True, 'redirect': '/dashboard'})
        return redirect(url_for('main.dashboard'))
    
    # Менеджер тестовый
    if username == 'manager' and password == 'manager123':
        session['user_id'] = 2
        session['user'] = {'username': 'manager', 'full_name': 'Менеджер', 'role': 'manager'}
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
    
    data = request.get_json() if request.is_json else request.form
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    full_name = data.get('full_name', '')
    
    if not username or not email or not password:
        if request.is_json:
            return jsonify({'success': False, 'error': 'Заполните все поля'}), 400
        return render_template('register.html', error='Заполните все поля')
    
    # В реальной системе здесь было бы сохранение в БД
    # Для демо просто показываем успех
    if request.is_json:
        return jsonify({'success': True, 'message': 'Регистрация успешна', 'redirect': '/login'})
    
    return render_template('register.html', success='Регистрация успешна! Теперь войдите в систему.')


@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))
