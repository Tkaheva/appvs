import sqlite3
import os
import uuid
import json
import datetime
from flask import Flask, render_template_string, jsonify, request, session, redirect, url_for

app = Flask(__name__)
app.secret_key = 'voiceguard-secret-key-2024'

DB_PATH = 'voiceguard.db'

# ==================== БАЗА ДАННЫХ ====================

def init_db():
    """Инициализация SQLite базы данных"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Таблица пользователей
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            full_name TEXT,
            role TEXT DEFAULT 'manager',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Таблица звонков
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS calls (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            call_id TEXT UNIQUE NOT NULL,
            manager_name TEXT,
            client_phone TEXT,
            call_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            duration INTEGER,
            file_path TEXT,
            status TEXT DEFAULT 'uploaded'
        )
    ''')
    
    # Таблица результатов анализа
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS analysis_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            call_id TEXT UNIQUE NOT NULL,
            total_score INTEGER,
            grade TEXT,
            grade_class TEXT,
            word_count INTEGER DEFAULT 0,
            admin_word_count INTEGER DEFAULT 0,
            client_word_count INTEGER DEFAULT 0,
            avg_confidence REAL,
            sentiment_score INTEGER DEFAULT 50,
            analysis_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            result_data TEXT
        )
    ''')
    
    # Таблица оценок критериев
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS criteria_scores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            analysis_id INTEGER NOT NULL,
            criterion_id TEXT NOT NULL,
            score INTEGER,
            keywords_found TEXT
        )
    ''')
    
    # Таблица рекомендаций
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS recommendations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            call_id TEXT,
            recommendation_text TEXT,
            priority TEXT DEFAULT 'medium',
            is_viewed INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Добавление тестовых пользователей
    users = [
        ('admin', 'admin123', 'Главный администратор', 'admin'),
        ('supervisor', 'supervisor123', 'Руководитель отдела продаж', 'supervisor'),
        ('manager', 'manager123', 'Менеджер по продажам', 'manager'),
        ('analyst', 'analyst123', 'Аналитик', 'analyst')
    ]
    
    for username, password, full_name, role in users:
        cursor.execute('''
            INSERT OR IGNORE INTO users (username, password, full_name, role)
            VALUES (?, ?, ?, ?)
        ''', (username, password, full_name, role))
    
    conn.commit()
    conn.close()
    print(f"✅ База данных инициализирована: {DB_PATH}")

# Инициализация при запуске
if not os.path.exists(DB_PATH):
    init_db()

# ==================== КРИТЕРИИ ОЦЕНКИ ====================

CRITERIA = [
    {'id': 'greeting', 'name': 'Приветствие и представление', 'weight': 12, 
     'description': 'Представиться, назвать автосалон, поприветствовать клиента'},
    {'id': 'client_info', 'name': 'Сбор информации о клиенте', 'weight': 18,
     'description': 'Узнать имя, контакт, интересующий автомобиль, бюджет'},
    {'id': 'communication_style', 'name': 'Стиль общения', 'weight': 12,
     'description': 'Вежливость, четкость речи, позитивный тон'},
    {'id': 'problem_identification', 'name': 'Выявление потребности', 'weight': 18,
     'description': 'Выявить, зачем клиент обратился'},
    {'id': 'offers_promotions', 'name': 'Рассказ об акциях', 'weight': 10,
     'description': 'Рассказать о текущих акциях и спецпредложениях'},
    {'id': 'solution_proposal', 'name': 'Предложение решения', 'weight': 12,
     'description': 'Предложить конкретное решение или следующий шаг'},
    {'id': 'active_listening', 'name': 'Активное слушание', 'weight': 8,
     'description': 'Демонстрировать понимание, переспрашивать, уточнять'},
    {'id': 'closing_efficiency', 'name': 'Эффективность завершения', 'weight': 10,
     'description': 'Четкое завершение разговора, договоренность о следующих шагах'}
]

# ==================== HTML ШАБЛОНЫ ====================

LOGIN_HTML = '''
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Вход - VoiceGuard Analytics</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #0a2a4a 0%, #2a7bb0 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }
        .login-container {
            background: white;
            border-radius: 30px;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.2);
            overflow: hidden;
            max-width: 450px;
            width: 100%;
        }
        .login-header {
            background: linear-gradient(135deg, #0a2a4a, #2a7bb0);
            padding: 30px;
            text-align: center;
            color: white;
        }
        .login-header h1 { font-size: 1.8rem; margin-bottom: 10px; }
        .login-header p { opacity: 0.9; font-size: 0.9rem; }
        .login-body { padding: 30px; }
        .form-group { margin-bottom: 20px; }
        .form-group label {
            display: block;
            margin-bottom: 8px;
            color: #4a6070;
            font-weight: 500;
        }
        .form-group input {
            width: 100%;
            padding: 12px 15px;
            border: 2px solid #e0e8f0;
            border-radius: 25px;
            font-size: 1rem;
            transition: all 0.3s;
        }
        .form-group input:focus {
            outline: none;
            border-color: #2a7bb0;
            box-shadow: 0 0 0 3px rgba(42, 123, 176, 0.1);
        }
        .btn-login {
            width: 100%;
            padding: 12px;
            background: linear-gradient(135deg, #0a2a4a, #2a7bb0);
            color: white;
            border: none;
            border-radius: 25px;
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
        }
        .btn-login:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 20px rgba(42, 123, 176, 0.4);
        }
        .error-message {
            background: #f8d7da;
            color: #721c24;
            padding: 12px;
            border-radius: 25px;
            margin-bottom: 20px;
            text-align: center;
        }
        .users-info {
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #e0e8f0;
        }
        .users-info h3 {
            color: #0a2a4a;
            font-size: 1rem;
            margin-bottom: 15px;
            text-align: center;
        }
        .user-card {
            background: #f5f7fa;
            border-radius: 15px;
            padding: 12px;
            margin-bottom: 10px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 10px;
        }
        .user-role {
            display: inline-block;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.7rem;
            font-weight: bold;
        }
        .role-admin { background: #f44336; color: white; }
        .role-supervisor { background: #ff9800; color: white; }
        .role-manager { background: #4caf50; color: white; }
        .role-analyst { background: #2196f3; color: white; }
        .user-credentials {
            font-family: monospace;
            font-size: 0.8rem;
            color: #2a7bb0;
        }
        .footer {
            text-align: center;
            padding: 20px;
            background: #f5f7fa;
            font-size: 0.8rem;
            color: #4a6070;
        }
        .footer a { color: #2a7bb0; text-decoration: none; }
    </style>
</head>
<body>
    <div class="login-container">
        <div class="login-header">
            <h1>🎙️ VoiceGuard Analytics</h1>
            <p>Система анализа качества телефонных переговоров</p>
        </div>
        
        <div class="login-body">
            {% if error %}
            <div class="error-message">⚠️ {{ error }}</div>
            {% endif %}
            
            <form method="POST">
                <div class="form-group">
                    <label>👤 Логин</label>
                    <input type="text" name="username" placeholder="Введите логин" required autofocus>
                </div>
                <div class="form-group">
                    <label>🔑 Пароль</label>
                    <input type="password" name="password" placeholder="Введите пароль" required>
                </div>
                <button type="submit" class="btn-login">Войти в систему</button>
            </form>
            
            <div class="users-info">
                <h3>📋 Тестовые учётные записи</h3>
                <div class="user-card">
                    <div><strong>👑 Администратор</strong><div><span class="user-role role-admin">admin</span></div></div>
                    <div class="user-credentials">admin / admin123</div>
                </div>
                <div class="user-card">
                    <div><strong>👔 Руководитель</strong><div><span class="user-role role-supervisor">supervisor</span></div></div>
                    <div class="user-credentials">supervisor / supervisor123</div>
                </div>
                <div class="user-card">
                    <div><strong>💼 Менеджер</strong><div><span class="user-role role-manager">manager</span></div></div>
                    <div class="user-credentials">manager / manager123</div>
                </div>
                <div class="user-card">
                    <div><strong>📊 Аналитик</strong><div><span class="user-role role-analyst">analyst</span></div></div>
                    <div class="user-credentials">analyst / analyst123</div>
                </div>
            </div>
        </div>
        
        <div class="footer">
            <p>VoiceGuard Analytics Pro · 8 критериев оценки качества</p>
            <p><a href="/">На главную</a></p>
        </div>
    </div>
</body>
</html>
'''

REGISTER_HTML = '''
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <title>Регистрация - VoiceGuard Analytics</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', sans-serif;
            background: linear-gradient(135deg, #0a2a4a, #2a7bb0);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }
        .register-container {
            background: white;
            border-radius: 30px;
            padding: 35px;
            max-width: 500px;
            width: 100%;
        }
        .register-container h2 { text-align: center; color: #0a2a4a; margin-bottom: 25px; }
        .form-group { margin-bottom: 20px; }
        .form-group label {
            display: block;
            margin-bottom: 8px;
            color: #4a6070;
            font-weight: 500;
        }
        .form-group input, .form-group select {
            width: 100%;
            padding: 12px 15px;
            border: 2px solid #e0e8f0;
            border-radius: 25px;
            font-size: 1rem;
        }
        .form-group input:focus, .form-group select:focus {
            outline: none;
            border-color: #2a7bb0;
        }
        .btn-register {
            width: 100%;
            padding: 12px;
            background: linear-gradient(135deg, #0a2a4a, #2a7bb0);
            color: white;
            border: none;
            border-radius: 25px;
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
        }
        .success-message {
            background: #d4edda;
            color: #155724;
            padding: 12px;
            border-radius: 25px;
            margin-bottom: 20px;
            text-align: center;
        }
        .error-message {
            background: #f8d7da;
            color: #721c24;
            padding: 12px;
            border-radius: 25px;
            margin-bottom: 20px;
            text-align: center;
        }
        .back-link { text-align: center; margin-top: 20px; }
        .back-link a { color: #2a7bb0; text-decoration: none; }
    </style>
</head>
<body>
    <div class="register-container">
        <h2>📝 Регистрация</h2>
        {% if success %}<div class="success-message">✅ {{ success }}</div>{% endif %}
        {% if error %}<div class="error-message">⚠️ {{ error }}</div>{% endif %}
        <form method="POST">
            <div class="form-group">
                <label>👤 Логин</label>
                <input type="text" name="username" placeholder="Введите логин" required>
            </div>
            <div class="form-group">
                <label>📧 Email</label>
                <input type="email" name="email" placeholder="example@mail.ru" required>
            </div>
            <div class="form-group">
                <label>🔑 Пароль</label>
                <input type="password" name="password" placeholder="Введите пароль" required>
            </div>
            <div class="form-group">
                <label>👨‍💼 ФИО</label>
                <input type="text" name="full_name" placeholder="Иванов Иван Иванович">
            </div>
            <div class="form-group">
                <label>👔 Роль</label>
                <select name="role">
                    <option value="manager">💼 Менеджер по продажам</option>
                    <option value="analyst">📊 Аналитик</option>
                    <option value="supervisor">👔 Руководитель отдела</option>
                </select>
            </div>
            <button type="submit" class="btn-register">Зарегистрироваться</button>
        </form>
        <div class="back-link"><a href="/login">← Уже есть аккаунт? Войти</a></div>
    </div>
</body>
</html>
'''

MAIN_HTML = '''
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>VoiceGuard Analytics | ФРЭШ АВТО</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #f0f4f8 0%, #e0e8f0 100%);
            min-height: 100vh;
        }
        .container { max-width: 1400px; margin: 0 auto; padding: 20px; }
        
        .navbar {
            background: linear-gradient(135deg, #0a2a4a 0%, #0a2e5a 100%);
            border-radius: 50px;
            padding: 12px 25px;
            margin-bottom: 30px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 15px;
        }
        .logo {
            font-size: 1.3rem;
            font-weight: bold;
            color: white;
            text-decoration: none;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .nav-links {
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
        }
        .nav-links a {
            background: rgba(255,255,255,0.12);
            padding: 8px 18px;
            border-radius: 40px;
            color: white;
            text-decoration: none;
            transition: all 0.3s;
        }
        .nav-links a:hover { background: rgba(255,255,255,0.25); transform: translateY(-2px); }
        
        .header {
            text-align: center;
            padding: 40px;
            background: white;
            border-radius: 30px;
            margin-bottom: 30px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.08);
            position: relative;
            overflow: hidden;
        }
        .header::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 5px;
            background: linear-gradient(90deg, #0a2a4a, #2a7bb0, #0a2a4a);
        }
        .header h1 {
            font-size: 2.5rem;
            background: linear-gradient(135deg, #0a2a4a, #2a7bb0);
            -webkit-background-clip: text;
            background-clip: text;
            color: transparent;
        }
        .company-badge {
            display: inline-block;
            margin-top: 15px;
            padding: 8px 25px;
            background: linear-gradient(135deg, #0a2a4a, #2a7bb0);
            border-radius: 40px;
            color: white;
            font-weight: 500;
        }
        
        .main-grid {
            display: grid;
            grid-template-columns: 1fr 1.5fr;
            gap: 25px;
        }
        @media (max-width: 900px) { .main-grid { grid-template-columns: 1fr; } }
        
        .panel {
            background: white;
            border-radius: 30px;
            padding: 25px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        }
        .panel h2 {
            color: #0a2a4a;
            margin-bottom: 20px;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .upload-area {
            border: 2px dashed rgba(42, 123, 176, 0.4);
            border-radius: 25px;
            padding: 40px;
            text-align: center;
            cursor: pointer;
            transition: all 0.3s;
            background: rgba(42, 123, 176, 0.02);
        }
        .upload-area:hover {
            border-color: #2a7bb0;
            background: rgba(42, 123, 176, 0.05);
            transform: translateY(-2px);
        }
        
        .btn {
            padding: 12px 24px;
            border: none;
            border-radius: 40px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
            font-size: 1rem;
            margin-top: 20px;
        }
        .btn-primary {
            background: linear-gradient(135deg, #0a2a4a, #2a7bb0);
            color: white;
        }
        .btn-primary:hover:not(:disabled) {
            transform: translateY(-2px);
            box-shadow: 0 5px 20px rgba(42, 123, 176, 0.4);
        }
        .btn-primary:disabled { opacity: 0.5; cursor: not-allowed; }
        
        .status {
            margin-top: 20px;
            padding: 15px;
            border-radius: 15px;
            display: none;
        }
        .status.success { background: #d4edda; color: #155724; display: block; }
        .status.error { background: #f8d7da; color: #721c24; display: block; }
        .status.info { background: #d1ecf1; color: #0c5460; display: block; }
        
        .result-card {
            background: linear-gradient(135deg, #e8f5e9, #c8e6c9);
            border-radius: 20px;
            padding: 25px;
            text-align: center;
            margin-bottom: 20px;
        }
        .score { font-size: 48px; font-weight: bold; color: #2e7d32; }
        .grade-badge {
            display: inline-block;
            padding: 5px 20px;
            border-radius: 40px;
            font-weight: bold;
            margin-top: 10px;
        }
        .grade-excellent { background: #2e7d32; color: white; }
        .grade-good { background: #2a7bb0; color: white; }
        .grade-average { background: #ff9800; color: white; }
        .grade-poor { background: #f44336; color: white; }
        .grade-fail { background: #9e9e9e; color: white; }
        
        .criteria-list { margin-top: 20px; }
        .criteria-item {
            display: flex;
            justify-content: space-between;
            padding: 12px;
            border-bottom: 1px solid #eee;
        }
        .criteria-name { font-weight: 500; }
        .criteria-score { font-weight: bold; color: #2a7bb0; }
        
        .recommendations {
            margin-top: 20px;
            padding: 15px;
            background: #e3f2fd;
            border-radius: 15px;
        }
        .recommendations ul { margin-left: 20px; margin-top: 10px; }
        .recommendations li { margin: 8px 0; }
        
        .footer {
            text-align: center;
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid rgba(10, 42, 74, 0.1);
            color: #4a6070;
        }
        
        .loading-spinner {
            display: inline-block;
            width: 20px;
            height: 20px;
            border: 2px solid rgba(42, 123, 176, 0.2);
            border-top-color: #2a7bb0;
            border-radius: 50%;
            animation: spin 0.8s linear infinite;
        }
        @keyframes spin { to { transform: rotate(360deg); } }
        
        .role-badge {
            display: inline-block;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.7rem;
            font-weight: bold;
            margin-left: 10px;
        }
        .role-admin { background: #f44336; color: white; }
        .role-supervisor { background: #ff9800; color: white; }
        .role-manager { background: #4caf50; color: white; }
        .role-analyst { background: #2196f3; color: white; }
    </style>
</head>
<body>
    <div class="container">
        <nav class="navbar">
            <a href="/" class="logo">🎙️ VoiceGuard Analytics</a>
            <div class="nav-links">
                <a href="/dashboard">📊 Дашборд</a>
                {% if session.user %}
                <a href="/logout">🚪 Выход ({{ session.user.username }})</a>
                {% else %}
                <a href="/login">🔐 Вход</a>
                {% endif %}
            </div>
        </nav>
        
        <div class="header">
            <h1>AI-анализ качества телефонных разговоров</h1>
            <p>Автоматическая оценка по 8 критериям с рекомендациями по обучению</p>
            <div class="company-badge">⭐ ФРЭШ АВТО · ТОП-3 дилер РФ</div>
        </div>
        
        <div class="main-grid">
            <div class="panel">
                <h2>📁 Загрузить звонок</h2>
                <div class="upload-area" id="dropZone">
                    <p>📤 Перетащите запись разговора</p>
                    <p style="font-size: 12px; color: #666;">MP3, WAV, M4A, OGG (до 200 МБ)</p>
                    <input type="file" id="fileInput" accept=".mp3,.wav,.m4a,.ogg" style="display: none;">
                </div>
                
                <div id="fileInfo" style="margin-top: 20px; display: none;">
                    <strong>📄 Файл:</strong> <span id="fileName"></span><br>
                    <strong>📦 Размер:</strong> <span id="fileSize"></span>
                </div>
                
                <button class="btn btn-primary" id="analyzeBtn" disabled>🔍 Начать анализ</button>
                <div id="status" class="status"></div>
            </div>
            
            <div class="panel" id="resultsPanel" style="display: none;">
                <h2>📊 Результаты анализа</h2>
                <div id="results"></div>
            </div>
        </div>
        
        <div class="footer">
            <p>VoiceGuard Analytics Pro · 8 критериев оценки качества</p>
            <p style="font-size: 0.8rem;">Приветствие | Сбор информации | Стиль общения | Выявление потребности | Акции | Решение | Активное слушание | Завершение</p>
        </div>
    </div>
    
    <script>
        const dropZone = document.getElementById('dropZone');
        const fileInput = document.getElementById('fileInput');
        const analyzeBtn = document.getElementById('analyzeBtn');
        const fileInfo = document.getElementById('fileInfo');
        const fileName = document.getElementById('fileName');
        const fileSize = document.getElementById('fileSize');
        const statusDiv = document.getElementById('status');
        const resultsPanel = document.getElementById('resultsPanel');
        const resultsDiv = document.getElementById('results');
        let currentFile = null;
        
        dropZone.onclick = () => fileInput.click();
        dropZone.ondragover = (e) => { e.preventDefault(); dropZone.style.borderColor = '#ff9800'; };
        dropZone.ondragleave = () => dropZone.style.borderColor = '#2a7bb0';
        dropZone.ondrop = (e) => {
            e.preventDefault();
            dropZone.style.borderColor = '#2a7bb0';
            if (e.dataTransfer.files.length) handleFile(e.dataTransfer.files[0]);
        };
        fileInput.onchange = (e) => { if (e.target.files.length) handleFile(e.target.files[0]); };
        
        function handleFile(file) {
            currentFile = file;
            fileName.textContent = file.name;
            fileSize.textContent = (file.size / 1024 / 1024).toFixed(2) + ' МБ';
            fileInfo.style.display = 'block';
            analyzeBtn.disabled = false;
            showStatus('Файл загружен', 'info');
            resultsPanel.style.display = 'none';
        }
        
        analyzeBtn.onclick = () => {
            if (!currentFile) return;
            analyzeBtn.disabled = true;
            showStatus('<span class="loading-spinner"></span> Анализ запущен...', 'info');
            
            setTimeout(() => {
                const totalScore = Math.floor(Math.random() * 35) + 65;
                let grade, gradeClass;
                if (totalScore >= 85) { grade = 'Отлично'; gradeClass = 'grade-excellent'; }
                else if (totalScore >= 70) { grade = 'Хорошо'; gradeClass = 'grade-good'; }
                else if (totalScore >= 60) { grade = 'Средне'; gradeClass = 'grade-average'; }
                else if (totalScore >= 50) { grade = 'Ниже среднего'; gradeClass = 'grade-poor'; }
                else { grade = 'Требуется обучение'; gradeClass = 'grade-fail'; }
                
                const criteria = [
                    '👋 Приветствие и представление', '📝 Сбор информации о клиенте', '💬 Стиль общения',
                    '🎯 Выявление потребности', '🏷️ Рассказ об акциях', '💡 Предложение решения',
                    '👂 Активное слушание', '✅ Эффективность завершения'
                ];
                
                const recommendations = [];
                if (totalScore < 70) recommendations.push('⚠️ Общий балл ниже целевого. Требуется дополнительное обучение');
                recommendations.push('📌 Всегда представляйтесь и называйте автосалон');
                recommendations.push('📌 Обязательно выясняйте бюджет клиента');
                recommendations.push('📌 Предлагайте тест-драйв в каждом разговоре');
                
                resultsDiv.innerHTML = `
                    <div class="result-card">
                        <div class="score">${totalScore}/100</div>
                        <div class="grade-badge ${gradeClass}">${grade}</div>
                        <p style="margin-top: 10px;">${totalScore >= 80 ? 'Отличная работа!' : totalScore >= 60 ? 'Хороший результат, есть куда расти' : 'Требуется дополнительное обучение'}</p>
                    </div>
                    <div class="criteria-list">
                        <h3>📋 Оценка по критериям:</h3>
                        ${criteria.map(c => `<div class="criteria-item"><span class="criteria-name">${c}</span><span class="criteria-score">${Math.floor(Math.random() * 35) + 65}/100</span></div>`).join('')}
                    </div>
                    <div class="recommendations">
                        <h3>📌 Рекомендации по обучению:</h3>
                        <ul>${recommendations.map(r => `<li>${r}</li>`).join('')}</ul>
                    </div>
                    <div style="margin-top: 20px; padding: 15px; background: #f5f5f5; border-radius: 15px;">
                        <h3>📊 Статистика диалога:</h3>
                        <p>📝 Всего слов: ${Math.floor(Math.random() * 500) + 100}</p>
                        <p>👨‍💼 Администратор: ${Math.floor(Math.random() * 300) + 50} слов</p>
                        <p>👤 Клиент: ${Math.floor(Math.random() * 200) + 50} слов</p>
                        <p>🎯 Точность распознавания: ${Math.floor(Math.random() * 20) + 80}%</p>
                    </div>
                `;
                resultsPanel.style.display = 'block';
                showStatus('✅ Анализ завершен!', 'success');
                analyzeBtn.disabled = false;
            }, 2000);
        };
        
        function showStatus(message, type) {
            statusDiv.innerHTML = message;
            statusDiv.className = 'status ' + type;
            setTimeout(() => {
                if (statusDiv.className === 'status ' + type) statusDiv.style.display = 'none';
            }, 5000);
        }
    </script>
</body>
</html>
'''

DASHBOARD_HTML = '''
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Дашборд - VoiceGuard Analytics</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', sans-serif;
            background: linear-gradient(135deg, #f0f4f8, #e0e8f0);
            min-height: 100vh;
        }
        .container { max-width: 1400px; margin: 0 auto; padding: 20px; }
        
        .navbar {
            background: linear-gradient(135deg, #0a2a4a, #0a2e5a);
            border-radius: 50px;
            padding: 12px 25px;
            margin-bottom: 30px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 15px;
        }
        .logo { color: white; font-size: 1.3rem; font-weight: bold; text-decoration: none; }
        .nav-links {
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
        }
        .nav-links a {
            background: rgba(255,255,255,0.12);
            padding: 8px 18px;
            border-radius: 40px;
            color: white;
            text-decoration: none;
            transition: all 0.3s;
        }
        .nav-links a:hover { background: rgba(255,255,255,0.25); transform: translateY(-2px); }
        
        .welcome-section {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 30px;
            padding: 20px 30px;
            background: white;
            border-radius: 25px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.08);
        }
        .role-badge {
            padding: 8px 20px;
            border-radius: 40px;
            font-weight: bold;
        }
        .role-admin { background: #f44336; color: white; }
        .role-supervisor { background: #ff9800; color: white; }
        .role-manager { background: #4caf50; color: white; }
        .role-analyst { background: #2196f3; color: white; }
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 20px;
            margin-bottom: 30px;
        }
        .stat-card {
            background: white;
            border-radius: 25px;
            padding: 25px;
            text-align: center;
            box-shadow: 0 4px 15px rgba(0,0,0,0.08);
            transition: transform 0.3s;
        }
        .stat-card:hover { transform: translateY(-5px); }
        .stat-icon { font-size: 2rem; margin-bottom: 10px; }
        .stat-value { font-size: 2.5rem; font-weight: bold; color: #2a7bb0; }
        .stat-label { color: #4a6070; margin-top: 5px; }
        
        .panel {
            background: white;
            border-radius: 25px;
            padding: 25px;
            margin-bottom: 30px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.08);
        }
        .panel h3 {
            color: #0a2a4a;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid #e0e8f0;
        }
        
        .data-table {
            width: 100%;
            border-collapse: collapse;
        }
        .data-table th, .data-table td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #eee;
        }
        .data-table th {
            color: #2a7bb0;
            font-weight: 600;
        }
        .data-table tr:hover { background: #f5f7fa; }
        
        .rating-item {
            display: flex;
            align-items: center;
            gap: 15px;
            margin-bottom: 15px;
        }
        .rating-name { width: 150px; font-weight: 500; }
        .rating-bar {
            flex: 1;
            height: 10px;
            background: #e0e8f0;
            border-radius: 10px;
            overflow: hidden;
        }
        .rating-fill {
            height: 100%;
            background: linear-gradient(90deg, #2a7bb0, #4caf50);
            border-radius: 10px;
            transition: width 0.5s;
        }
        .rating-score { width: 45px; font-weight: bold; color: #2a7bb0; }
        
        .text-center { text-align: center; }
        .view-btn {
            background: #2a7bb0;
            color: white;
            padding: 5px 12px;
            border-radius: 20px;
            text-decoration: none;
            font-size: 0.8rem;
        }
        .view-btn:hover { background: #1a5a8a; }
        
        .footer {
            text-align: center;
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid rgba(10, 42, 74, 0.1);
            color: #4a6070;
        }
    </style>
</head>
<body>
    <div class="container">
        <nav class="navbar">
            <a href="/" class="logo">🎙️ VoiceGuard Analytics</a>
            <div class="nav-links">
                <a href="/">🏠 Главная</a>
                <a href="/logout">🚪 Выход ({{ user.username }})</a>
            </div>
        </nav>
        
        <div class="welcome-section">
            <div>
                <h2>Добро пожаловать, {{ user.full_name }}!</h2>
                <p style="color: #4a6070; margin-top: 5px;">Ваша роль: 
                    {% if user.role == 'admin' %}👑 Администратор
                    {% elif user.role == 'supervisor' %}👔 Руководитель отдела продаж
                    {% elif user.role == 'manager' %}💼 Менеджер по продажам
                    {% else %}📊 Аналитик
                    {% endif %}
                </p>
            </div>
            <div class="role-badge role-{{ user.role }}">
                {% if user.role == 'admin' %}👑 ADMIN
                {% elif user.role == 'supervisor' %}👔 SUPERVISOR
                {% elif user.role == 'manager' %}💼 MANAGER
                {% else %}📊 ANALYST
                {% endif %}
            </div>
        </div>
        
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-icon">📞</div>
                <div class="stat-value" id="totalCalls">24</div>
                <div class="stat-label">Всего звонков</div>
            </div>
            <div class="stat-card">
                <div class="stat-icon">⭐</div>
                <div class="stat-value" id="avgScore">78</div>
                <div class="stat-label">Средний балл</div>
            </div>
            <div class="stat-card">
                <div class="stat-icon">📈</div>
                <div class="stat-value" id="trend">+12%</div>
                <div class="stat-label">Динамика</div>
            </div>
            <div class="stat-card">
                <div class="stat-icon">🎯</div>
                <div class="stat-value" id="target">85</div>
                <div class="stat-label">Целевой показатель</div>
            </div>
        </div>
        
        {% if user.role in ['admin', 'supervisor'] %}
        <div class="panel">
            <h3>📊 Все звонки отдела</h3>
            <div class="table-container">
                <table class="data-table">
                    <thead>
                        <tr><th>Дата</th><th>Менеджер</th><th>Клиент</th><th>Балл</th><th>Оценка</th><th>Действия</th></tr>
                    </thead>
                    <tbody id="allCallsTable">
                        <tr><td colspan="6" class="text-center">Загрузка...</td></tr>
                    </tbody>
                </table>
            </div>
        </div>
        {% endif %}
        
        {% if user.role in ['admin', 'supervisor', 'manager'] %}
        <div class="panel">
            <h3>📞 Мои звонки</h3>
            <div class="table-container">
                <table class="data-table">
                    <thead>
                        <tr><th>Дата</th><th>Клиент</th><th>Балл</th><th>Оценка</th><th>Рекомендации</th><th>Действия</th></tr>
                    </thead>
                    <tbody id="myCallsTable">
                        <tr><td colspan="6" class="text-center">Загрузка...</td></tr>
                    </tbody>
                </table>
            </div>
        </div>
        {% endif %}
        
        <div class="panel">
            <h3>📈 Рейтинг менеджеров</h3>
            <div class="rating-container" id="ratingContainer">
                <div class="rating-item">
                    <div class="rating-name">Иванов И.И.</div>
                    <div class="rating-bar"><div class="rating-fill" style="width: 85%;"></div></div>
                    <div class="rating-score">85</div>
                </div>
                <div class="rating-item">
                    <div class="rating-name">Петров П.П.</div>
                    <div class="rating-bar"><div class="rating-fill" style="width: 78%;"></div></div>
                    <div class="rating-score">78</div>
                </div>
                <div class="rating-item">
                    <div class="rating-name">Сидоров С.С.</div>
                    <div class="rating-bar"><div class="rating-fill" style="width: 72%;"></div></div>
                    <div class="rating-score">72</div>
                </div>
                <div class="rating-item">
                    <div class="rating-name">Кузнецова А.В.</div>
                    <div class="rating-bar"><div class="rating-fill" style="width: 90%;"></div></div>
                    <div class="rating-score">90</div>
                </div>
            </div>
        </div>
        
        <div class="footer">
            <p>VoiceGuard Analytics Pro · 8 критериев оценки качества · Автоматические рекомендации</p>
        </div>
    </div>
    
    <script>
        function loadMyCalls() {
            const tbody = document.getElementById('myCallsTable');
            if (!tbody) return;
            
            const mockCalls = [
                { date: '2026-06-02 14:30', client: '+7 (999) 123-45-67', score: 85, grade: 'Отлично', recommendations: 3 },
                { date: '2026-06-02 11:15', client: '+7 (999) 234-56-78', score: 72, grade: 'Хорошо', recommendations: 2 },
                { date: '2026-06-01 16:45', client: '+7 (999) 345-67-89', score: 68, grade: 'Средне', recommendations: 4 },
                { date: '2026-06-01 10:00', client: '+7 (999) 456-78-90', score: 91, grade: 'Отлично', recommendations: 1 }
            ];
            
            tbody.innerHTML = mockCalls.map(call => `
                <tr>
                    <td>${call.date}</td>
                    <td>${call.client}</td>
                    <td><strong>${call.score}</strong></td>
                    <td>${call.grade}</td>
                    <td>${call.recommendations} рекомендаций</td>
                    <td><a href="/" class="view-btn">Детали</a></td>
                </tr>
            `).join('');
        }
        
        function loadAllCalls() {
            const tbody = document.getElementById('allCallsTable');
            if (!tbody) return;
            
            const mockCalls = [
                { date: '2026-06-02 14:30', manager: 'Иванов И.И.', client: '+7 (999) 123-45-67', score: 85, grade: 'Отлично' },
                { date: '2026-06-02 11:15', manager: 'Петров П.П.', client: '+7 (999) 234-56-78', score: 72, grade: 'Хорошо' },
                { date: '2026-06-01 16:45', manager: 'Сидоров С.С.', client: '+7 (999) 345-67-89', score: 68, grade: 'Средне' },
                { date: '2026-06-01 10:00', manager: 'Кузнецова А.В.', client: '+7 (999) 456-78-90', score: 91, grade: 'Отлично' }
            ];
            
            tbody.innerHTML = mockCalls.map(call => `
                <tr>
                    <td>${call.date}</td>
                    <td>${call.manager}</td>
                    <td>${call.client}</td>
                    <td><strong>${call.score}</strong></td>
                    <td>${call.grade}</td>
                    <td><a href="/" class="view-btn">Детали</a></td>
                </tr>
            `).join('');
        }
        
        document.addEventListener('DOMContentLoaded', function() {
            loadMyCalls();
            {% if user.role in ['admin', 'supervisor'] %}loadAllCalls();{% endif %}
        });
    </script>
</body>
</html>
'''

# ==================== МАРШРУТЫ ====================

@app.route('/')
def index():
    return render_template_string(MAIN_HTML)

@app.route('/dashboard')
def dashboard():
    if not session.get('user'):
        return redirect(url_for('login'))
    return render_template_string(DASHBOARD_HTML, user=session.get('user', {}))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password))
        user = cursor.fetchone()
        conn.close()
        
        if user:
            session['user'] = {
                'id': user[0],
                'username': user[1],
                'full_name': user[3],
                'role': user[4]
            }
            return redirect(url_for('dashboard'))
        
        return render_template_string(LOGIN_HTML, error='Неверный логин или пароль')
    
    return render_template_string(LOGIN_HTML)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        full_name = request.form.get('full_name', '')
        role = request.form.get('role', 'manager')
        
        if not username or not email or not password:
            return render_template_string(REGISTER_HTML, error='Заполните все поля')
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        try:
            cursor.execute('INSERT INTO users (username, password, full_name, role) VALUES (?, ?, ?, ?)',
                          (username, password, full_name, role))
            conn.commit()
            conn.close()
            return render_template_string(REGISTER_HTML, success='Регистрация успешна! Теперь войдите в систему.')
        except sqlite3.IntegrityError:
            conn.close()
            return render_template_string(REGISTER_HTML, error='Пользователь с таким логином уже существует')
    
    return render_template_string(REGISTER_HTML)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/health')
def health():
    return {'status': 'healthy', 'service': 'VoiceGuard Analytics', 'version': '3.0.0'}

# ==================== ЗАПУСК ====================

if __name__ == '__main__':
    print('\n' + '='*60)
    print('🚀 VoiceGuard Analytics успешно запущен!')
    print('='*60)
    print('\n🌐 Откройте в браузере: http://localhost:7000')
    print('\n📋 Тестовые учётные записи:')
    print('   ┌─────────────────┬──────────────────┬─────────────────┐')
    print('   │ Роль            │ Логин            │ Пароль          │')
    print('   ├─────────────────┼──────────────────┼─────────────────┤')
    print('   │ 👑 Администратор │ admin            │ admin123        │')
    print('   │ 👔 Руководитель   │ supervisor       │ supervisor123   │')
    print('   │ 💼 Менеджер      │ manager          │ manager123      │')
    print('   │ 📊 Аналитик      │ analyst          │ analyst123      │')
    print('   └─────────────────┴──────────────────┴─────────────────┘')
    print('\n📊 Доступные страницы:')
    print('   - Главная: http://localhost:7000')
    print('   - Дашборд: http://localhost:7000/dashboard')
    print('   - Вход: http://localhost:7000/login')
    print('   - Health: http://localhost:7000/health')
    print('\n' + '='*60 + '\n')
    
    app.run(host='0.0.0.0', port=7000, debug=True)
