# app/main.py - ПОЛНАЯ ВЕРСИЯ

import os
import uuid
import json
import threading
import datetime
import pymysql
from flask import Blueprint, request, jsonify, render_template, session, send_file, current_app, redirect, url_for
from werkzeug.utils import secure_filename
from app.audio_processor import AudioProcessor
from app.analyzer import analyze_audio_result, CRITERIA

main_bp = Blueprint('main', __name__)
audio_processor = AudioProcessor()
analysis_results_store = {}

ALLOWED_EXTENSIONS = {'mp3', 'wav', 'm4a', 'ogg', 'flac', 'aac', 'opus'}

# Конфигурация базы данных
DB_CONFIG = {
    'host': os.environ.get('DB_HOST', 'localhost'),
    'port': int(os.environ.get('DB_PORT', 3308)),
    'user': os.environ.get('DB_USER', 'root'),
    'password': os.environ.get('DB_PASSWORD', 'rootpassword'),
    'database': os.environ.get('DB_NAME', 'autosalon_analytics'),
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor,
    'connect_timeout': 10
}


def get_db_connection():
    """Получение соединения с базой данных"""
    try:
        if os.path.exists('/.dockerenv'):
            DB_CONFIG['host'] = 'host.docker.internal'
        
        connection = pymysql.connect(**DB_CONFIG)
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        return connection
    except Exception as e:
        print(f"❌ Ошибка подключения к БД: {e}")
        return None


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# ==================== МАРШРУТЫ ====================

@main_bp.route('/')
def index():
    return render_template('index.html', criteria=CRITERIA)


@main_bp.route('/dashboard')
def dashboard():
    if not session.get('user'):
        return redirect(url_for('auth.login'))
    return render_template('dashboard.html', user=session.get('user', {}))


@main_bp.route('/analysis-status/<file_id>')
def analysis_status(file_id):
    """Проверка статуса анализа (для фронтенда)"""
    if file_id in analysis_results_store:
        return jsonify(analysis_results_store[file_id])
    
    # Проверить в БД
    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT ar.*, uf.status 
                    FROM analysis_results ar
                    JOIN uploaded_files uf ON ar.file_id = uf.file_id
                    WHERE ar.file_id = %s
                """, (file_id,))
                result = cursor.fetchone()
                if result:
                    return jsonify({
                        'success': True,
                        'file_id': file_id,
                        'total_score': result.get('total_score', 0),
                        'grade': result.get('grade', ''),
                        'grade_class': result.get('grade_class', ''),
                        'word_count': result.get('word_count', 0),
                        'admin_word_count': result.get('admin_word_count', 0),
                        'client_word_count': result.get('client_word_count', 0),
                        'confidence': result.get('avg_confidence', 0)
                    })
        except Exception as e:
            print(f"Ошибка проверки статуса в БД: {e}")
        finally:
            conn.close()
    
    return jsonify({'success': False, 'status': 'processing'})


@main_bp.route('/upload', methods=['POST'])
def upload_file():
    """Загрузка файла с записью в БД"""
    if 'file' not in request.files:
        return jsonify({'error': 'Файл не найден'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'Файл не выбран'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': f'Неподдерживаемый формат. Разрешены: {", ".join(ALLOWED_EXTENSIONS)}'}), 400
    
    filename = secure_filename(file.filename)
    file_id = str(uuid.uuid4())
    file_ext = filename.rsplit('.', 1)[1].lower()
    saved_filename = f"{file_id}.{file_ext}"
    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], saved_filename)
    file.save(file_path)
    
    file_size = os.path.getsize(file_path)
    
    # СОХРАНЕНИЕ В БД СРАЗУ ПОСЛЕ ЗАГРУЗКИ
    save_uploaded_file_to_db(file_id, filename, saved_filename, file_size, file_ext, file_path)
    
    return jsonify({
        'success': True,
        'file_id': file_id,
        'filename': filename,
        'file_size': file_size,
        'file_size_formatted': f"{file_size / 1024 / 1024:.2f} МБ",
        'format': file_ext.upper()
    })


def save_uploaded_file_to_db(file_id, original_filename, stored_filename, file_size, file_format, file_path):
    """Сохранение информации о загруженном файле в БД"""
    conn = get_db_connection()
    if not conn:
        print("⚠️ Не удалось подключиться к БД для сохранения файла")
        return
    
    try:
        with conn.cursor() as cursor:
            # Проверяем существование таблиц
            cursor.execute("SHOW TABLES LIKE 'uploaded_files'")
            if not cursor.fetchone():
                init_database_tables(conn)
            
            # Вставляем запись о файле
            cursor.execute("""
                INSERT INTO uploaded_files (file_id, original_filename, stored_filename, file_size, file_format, status, upload_time)
                VALUES (%s, %s, %s, %s, %s, 'uploaded', %s)
            """, (file_id, original_filename, stored_filename, file_size, file_format, datetime.datetime.now()))
            
            conn.commit()
            print(f"✅ Файл сохранен в БД: {file_id}")
    except Exception as e:
        print(f"❌ Ошибка сохранения файла в БД: {e}")
        conn.rollback()
    finally:
        conn.close()


@main_bp.route('/analyze/<file_id>', methods=['POST'])
def analyze_file(file_id):
    """Запуск анализа с обновлением статуса в БД"""
    file_path = None
    for ext in ALLOWED_EXTENSIONS:
        test_path = os.path.join(current_app.config['UPLOAD_FOLDER'], f"{file_id}.{ext}")
        if os.path.exists(test_path):
            file_path = test_path
            break
    
    if not file_path:
        return jsonify({'error': 'Файл не найден'}), 404
    
    # Обновляем статус в БД на "processing"
    update_file_status(file_id, 'processing')
    
    def analyze_task():
        try:
            audio_result = audio_processor.process(file_path)
            analysis_result = analyze_audio_result(audio_result)
            analysis_result['analysis_time'] = datetime.datetime.now().isoformat()
            analysis_result['file_id'] = file_id
            analysis_results_store[file_id] = analysis_result
            
            # Сохранение результатов в базу данных
            save_to_database(file_id, analysis_result)
            
            # Обновляем статус на "completed"
            update_file_status(file_id, 'completed')
            
            if os.path.exists(file_path):
                os.remove(file_path)
                
        except Exception as e:
            import traceback
            error_msg = f"Ошибка анализа: {str(e)}\n{traceback.format_exc()}"
            print(error_msg)
            analysis_results_store[file_id] = {'success': False, 'error': str(e)}
            update_file_status(file_id, 'failed')
    
    thread = threading.Thread(target=analyze_task)
    thread.daemon = True
    thread.start()
    
    return jsonify({'success': True, 'message': 'Анализ запущен', 'file_id': file_id})


def update_file_status(file_id, status):
    """Обновление статуса файла в БД"""
    conn = get_db_connection()
    if not conn:
        return
    
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                UPDATE uploaded_files 
                SET status = %s 
                WHERE file_id = %s
            """, (status, file_id))
            conn.commit()
    except Exception as e:
        print(f"❌ Ошибка обновления статуса: {e}")
    finally:
        conn.close()


def save_to_database(file_id, analysis_result):
    """Сохранение результатов анализа в базу данных"""
    conn = get_db_connection()
    if not conn:
        print("⚠️ Не удалось подключиться к БД для сохранения")
        return
    
    try:
        with conn.cursor() as cursor:
            # Обновляем запись файла
            cursor.execute("""
                UPDATE uploaded_files 
                SET status = 'completed' 
                WHERE file_id = %s
            """, (file_id,))
            
            # Сохраняем результаты анализа
            cursor.execute("""
                INSERT INTO analysis_results (file_id, total_score, grade, grade_class, word_count, admin_word_count, client_word_count, avg_confidence, analysis_time)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                file_id,
                analysis_result.get('total_score', 0),
                analysis_result.get('grade', ''),
                analysis_result.get('grade_class', ''),
                analysis_result.get('word_count', 0),
                analysis_result.get('admin_word_count', 0),
                analysis_result.get('client_word_count', 0),
                analysis_result.get('confidence', 0),
                datetime.datetime.now()
            ))
            
            analysis_id = cursor.lastrowid
            
            # Сохраняем оценки критериев
            for criterion_id, score_data in analysis_result.get('criteria_scores', {}).items():
                cursor.execute("""
                    INSERT INTO criteria_scores (analysis_id, criterion_id, score, keyword_count, keywords_found)
                    VALUES (%s, %s, %s, %s, %s)
                """, (
                    analysis_id,
                    criterion_id,
                    score_data.get('score', 0),
                    score_data.get('keyword_count', 0),
                    ', '.join(score_data.get('found_keywords', []))
                ))
            
            # Сохраняем сегменты диалога
            for idx, segment in enumerate(analysis_result.get('segments', [])):
                cursor.execute("""
                    INSERT INTO dialogue_segments (analysis_id, segment_index, speaker, text, timestamp, confidence)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (
                    analysis_id,
                    idx,
                    segment.get('speaker', ''),
                    segment.get('text', ''),
                    segment.get('timestamp', ''),
                    segment.get('confidence', 0)
                ))
            
            conn.commit()
            print(f"✅ Результаты анализа сохранены в БД, analysis_id={analysis_id}")
            
    except Exception as e:
        print(f"❌ Ошибка сохранения в БД: {e}")
        conn.rollback()
    finally:
        conn.close()


def init_database_tables(conn):
    """Инициализация таблиц в базе данных"""
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INT PRIMARY KEY AUTO_INCREMENT,
                    username VARCHAR(50) UNIQUE NOT NULL,
                    email VARCHAR(100) UNIQUE NOT NULL,
                    password_hash VARCHAR(255) NOT NULL,
                    full_name VARCHAR(100),
                    role ENUM('admin', 'manager', 'analyst') DEFAULT 'analyst',
                    is_active BOOLEAN DEFAULT TRUE,
                    last_login TIMESTAMP NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS uploaded_files (
                    id INT PRIMARY KEY AUTO_INCREMENT,
                    file_id VARCHAR(36) UNIQUE NOT NULL,
                    user_id INT,
                    original_filename VARCHAR(255) NOT NULL,
                    stored_filename VARCHAR(255) NOT NULL,
                    file_size BIGINT NOT NULL,
                    file_format VARCHAR(10) NOT NULL,
                    upload_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    file_path VARCHAR(500),
                    status ENUM('uploaded', 'processing', 'completed', 'failed') DEFAULT 'uploaded'
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS analysis_results (
                    id INT PRIMARY KEY AUTO_INCREMENT,
                    file_id VARCHAR(36) UNIQUE NOT NULL,
                    analysis_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    total_score INT,
                    grade VARCHAR(50),
                    grade_class VARCHAR(50),
                    word_count INT DEFAULT 0,
                    admin_word_count INT DEFAULT 0,
                    client_word_count INT DEFAULT 0,
                    avg_confidence FLOAT,
                    FOREIGN KEY (file_id) REFERENCES uploaded_files(file_id) ON DELETE CASCADE
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS criteria_scores (
                    id INT PRIMARY KEY AUTO_INCREMENT,
                    analysis_id INT NOT NULL,
                    criterion_id VARCHAR(50) NOT NULL,
                    score INT,
                    keyword_count INT DEFAULT 0,
                    keywords_found TEXT,
                    FOREIGN KEY (analysis_id) REFERENCES analysis_results(id) ON DELETE CASCADE
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS dialogue_segments (
                    id INT PRIMARY KEY AUTO_INCREMENT,
                    analysis_id INT NOT NULL,
                    segment_index INT NOT NULL,
                    speaker ENUM('admin', 'client') NOT NULL,
                    text TEXT NOT NULL,
                    timestamp VARCHAR(20),
                    confidence FLOAT,
                    FOREIGN KEY (analysis_id) REFERENCES analysis_results(id) ON DELETE CASCADE
                )
            """)
            
            cursor.execute("""
                INSERT IGNORE INTO users (username, email, password_hash, full_name, role) 
                VALUES ('admin', 'admin@autosalon.local', 'admin123', 'Администратор', 'admin')
            """)
            
            conn.commit()
            print("✅ Таблицы успешно созданы")
            
    except Exception as e:
        print(f"❌ Ошибка создания таблиц: {e}")


# ==================== API ДЛЯ ПРОСМОТРА БАЗЫ ДАННЫХ ====================

@main_bp.route('/database-view')
def database_view():
    """Страница просмотра базы данных"""
    return render_template('database_view.html')


@main_bp.route('/api/database/stats')
def api_db_stats():
    """API для получения статистики"""
    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'error': 'Не удалось подключиться к БД'})
    
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) as total FROM uploaded_files")
            total_files = cursor.fetchone()['total']
            
            cursor.execute("SELECT COUNT(*) as total FROM analysis_results")
            completed_analyses = cursor.fetchone()['total']
            
            cursor.execute("SELECT AVG(total_score) as avg FROM analysis_results")
            avg_score = cursor.fetchone()['avg']
            
            cursor.execute("SELECT COUNT(*) as total FROM users")
            total_users = cursor.fetchone()['total']
            
            return jsonify({
                'success': True,
                'stats': {
                    'total_files': total_files,
                    'completed_analyses': completed_analyses,
                    'avg_score': round(avg_score, 2) if avg_score else 0,
                    'total_users': total_users
                }
            })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})
    finally:
        conn.close()


@main_bp.route('/api/database/files')
def api_db_files():
    """API для получения списка файлов"""
    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'error': 'Не удалось подключиться к БД'})
    
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT * FROM uploaded_files 
                ORDER BY upload_time DESC 
                LIMIT 100
            """)
            files = cursor.fetchall()
            
            for file in files:
                if file.get('upload_time'):
                    file['upload_time'] = file['upload_time'].isoformat() if hasattr(file['upload_time'], 'isoformat') else str(file['upload_time'])
            
            return jsonify({'success': True, 'files': files})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})
    finally:
        conn.close()


@main_bp.route('/api/database/analyses')
def api_db_analyses():
    """API для получения списка анализов"""
    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'error': 'Не удалось подключиться к БД'})
    
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT ar.*, uf.original_filename 
                FROM analysis_results ar
                LEFT JOIN uploaded_files uf ON ar.file_id = uf.file_id
                ORDER BY ar.analysis_time DESC 
                LIMIT 100
            """)
            analyses = cursor.fetchall()
            
            for analysis in analyses:
                if analysis.get('analysis_time'):
                    analysis['analysis_time'] = analysis['analysis_time'].isoformat() if hasattr(analysis['analysis_time'], 'isoformat') else str(analysis['analysis_time'])
            
            return jsonify({'success': True, 'analyses': analyses})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})
    finally:
        conn.close()


@main_bp.route('/api/database/criteria')
def api_db_criteria():
    """API для получения оценок критериев"""
    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'error': 'Не удалось подключиться к БД'})
    
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT cs.*, ar.file_id, uf.original_filename
                FROM criteria_scores cs
                LEFT JOIN analysis_results ar ON cs.analysis_id = ar.id
                LEFT JOIN uploaded_files uf ON ar.file_id = uf.file_id
                ORDER BY cs.analysis_id DESC, cs.id DESC 
                LIMIT 200
            """)
            criteria = cursor.fetchall()
            return jsonify({'success': True, 'criteria': criteria})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})
    finally:
        conn.close()


@main_bp.route('/api/database/segments')
def api_db_segments():
    """API для получения сегментов диалога"""
    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'error': 'Не удалось подключиться к БД'})
    
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT ds.*, ar.file_id, uf.original_filename
                FROM dialogue_segments ds
                LEFT JOIN analysis_results ar ON ds.analysis_id = ar.id
                LEFT JOIN uploaded_files uf ON ar.file_id = uf.file_id
                ORDER BY ds.analysis_id DESC, ds.segment_index 
                LIMIT 500
            """)
            segments = cursor.fetchall()
            return jsonify({'success': True, 'segments': segments})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})
    finally:
        conn.close()


@main_bp.route('/api/database/users')
def api_db_users():
    """API для получения списка пользователей"""
    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'error': 'Не удалось подключиться к БД'})
    
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT id, username, email, full_name, role, is_active, created_at 
                FROM users 
                ORDER BY id
            """)
            users = cursor.fetchall()
            
            for user in users:
                if user.get('created_at'):
                    user['created_at'] = user['created_at'].isoformat() if hasattr(user['created_at'], 'isoformat') else str(user['created_at'])
            
            return jsonify({'success': True, 'users': users})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})
    finally:
        conn.close()


@main_bp.route('/analysis-result/<file_id>')
def analysis_result_view(file_id):
    """Страница просмотра результата анализа"""
    result = analysis_results_store.get(file_id)
    if not result:
        return render_template('error.html', error='Анализ не найден')
    return render_template('analysis_result.html', result=result)


@main_bp.route('/analysis-details/<int:analysis_id>')
def analysis_details_view(analysis_id):
    """Страница деталей анализа по ID"""
    conn = get_db_connection()
    if not conn:
        return render_template('error.html', error='Не удалось подключиться к БД')
    
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT ar.*, uf.original_filename 
                FROM analysis_results ar
                LEFT JOIN uploaded_files uf ON ar.file_id = uf.file_id
                WHERE ar.id = %s
            """, (analysis_id,))
            analysis = cursor.fetchone()
            
            cursor.execute("""
                SELECT * FROM criteria_scores 
                WHERE analysis_id = %s
            """, (analysis_id,))
            criteria = cursor.fetchall()
            
            cursor.execute("""
                SELECT * FROM dialogue_segments 
                WHERE analysis_id = %s
                ORDER BY segment_index
            """, (analysis_id,))
            segments = cursor.fetchall()
            
            return render_template('analysis_details.html', 
                                 analysis=analysis, 
                                 criteria=criteria, 
                                 segments=segments)
    except Exception as e:
        return render_template('error.html', error=str(e))
    finally:
        conn.close()


# ==================== СТАТИСТИКА ДЛЯ ДАШБОРДА ====================

@main_bp.route('/stats')
def get_stats():
    """API для получения статистики для дашборда"""
    total_files = len(analysis_results_store)
    completed = sum(1 for r in analysis_results_store.values() if r.get('success', False))
    in_progress = total_files - completed
    
    avg_score = 0
    if completed > 0:
        scores = []
        for r in analysis_results_store.values():
            if r.get('success', False):
                score = r.get('total_score', 0)
                if score > 0:
                    scores.append(score)
        if scores:
            avg_score = round(sum(scores) / len(scores))
    
    return jsonify({
        'success': True,
        'stats': {
            'total_files': total_files,
            'completed': completed,
            'avg_score': avg_score,
            'in_progress': in_progress
        }
    })


@main_bp.route('/api/recent-analyses')
def get_recent_analyses():
    """API для получения последних анализов"""
    recent = []
    
    # Получить данные из хранилища результатов
    for file_id, result in list(analysis_results_store.items())[-10:]:
        if result.get('success', False):
            recent.append({
                'file_id': file_id,
                'total_score': result.get('total_score', 0),
                'grade': result.get('grade', ''),
                'analysis_time': result.get('analysis_time', ''),
                'word_count': result.get('word_count', 0)
            })
    
    # Если в хранилище нет, попробовать получить из БД
    if not recent:
        conn = get_db_connection()
        if conn:
            try:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        SELECT ar.*, uf.original_filename
                        FROM analysis_results ar
                        LEFT JOIN uploaded_files uf ON ar.file_id = uf.file_id
                        ORDER BY ar.analysis_time DESC
                        LIMIT 10
                    """)
                    db_recent = cursor.fetchall()
                    for item in db_recent:
                        recent.append({
                            'file_id': item.get('file_id', ''),
                            'total_score': item.get('total_score', 0),
                            'grade': item.get('grade', ''),
                            'analysis_time': str(item.get('analysis_time', '')),
                            'word_count': item.get('word_count', 0),
                            'original_filename': item.get('original_filename', '')
                        })
            except Exception as e:
                print(f"Ошибка получения последних анализов из БД: {e}")
            finally:
                conn.close()
    
    return jsonify({
        'success': True,
        'analyses': recent
    })


@main_bp.route('/criteria')
def get_criteria():
    """API для получения критериев оценки"""
    return jsonify({
        'success': True,
        'criteria': CRITERIA
    })
