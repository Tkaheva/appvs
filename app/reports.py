import os
import uuid
import datetime
import json
from flask import Blueprint, request, jsonify, send_file, session, current_app
from app.models import ReportGenerator, TrainingPlan
from app.auth import login_required

reports_bp = Blueprint('reports', __name__)

# Хранилище планов обучения
training_plans_store = {}

@reports_bp.route('/api/reports/generate/<file_id>')
@login_required(roles=['admin', 'supervisor'])
def generate_report(file_id):
    """Генерация отчёта по результатам анализа"""
    from app.main import analysis_results_store, get_db_connection
    
    result = analysis_results_store.get(file_id)
    
    if not result:
        conn = get_db_connection()
        if conn:
            try:
                import pymysql
                with conn.cursor(pymysql.cursors.DictCursor) as cursor:
                    cursor.execute("""
                        SELECT ar.*, uf.original_filename 
                        FROM analysis_results ar
                        LEFT JOIN uploaded_files uf ON ar.file_id = uf.file_id
                        WHERE ar.file_id = %s
                    """, (file_id,))
                    db_result = cursor.fetchone()
                    if db_result:
                        result = {
                            'file_id': file_id,
                            'total_score': db_result.get('total_score', 0),
                            'grade': db_result.get('grade', ''),
                            'grade_class': db_result.get('grade_class', ''),
                            'word_count': db_result.get('word_count', 0),
                            'admin_word_count': db_result.get('admin_word_count', 0),
                            'client_word_count': db_result.get('client_word_count', 0),
                            'confidence': db_result.get('avg_confidence', 0),
                            'duration_formatted': '0:00',
                            'sentiment_label': 'Нейтральная',
                            'sentiment': 50,
                            'segments': []
                        }
                        cursor.execute("""
                            SELECT * FROM criteria_scores WHERE analysis_id = %s
                        """, (db_result.get('id'),))
                        criteria = cursor.fetchall()
                        result['criteria_scores'] = {}
                        for c in criteria:
                            result['criteria_scores'][c['criterion_id']] = {
                                'score': c.get('score', 0),
                                'keyword_count': c.get('keyword_count', 0),
                                'found_keywords': c.get('keywords_found', '').split(', ') if c.get('keywords_found') else []
                            }
                        cursor.execute("""
                            SELECT * FROM dialogue_segments WHERE analysis_id = %s ORDER BY segment_index
                        """, (db_result.get('id'),))
                        segments = cursor.fetchall()
                        result['segments'] = [
                            {
                                'speaker': s.get('speaker', 'client'),
                                'text': s.get('text', ''),
                                'timestamp': s.get('timestamp', '00:00'),
                                'confidence': s.get('confidence', 0.8)
                            } for s in segments
                        ]
            except Exception as e:
                print(f"Ошибка загрузки из БД: {e}")
            finally:
                conn.close()
    
    if not result:
        return jsonify({'error': 'Результат анализа не найден'}), 404
    
    report_format = request.args.get('format', 'html')
    user_info = session.get('user', {})
    
    # Получение или генерация плана обучения
    training_plan = None
    user_id = user_info.get('id')
    if user_id:
        plan_key = f"plan_{user_id}_{file_id}"
        if plan_key not in training_plans_store:
            training_plan_obj = TrainingPlan().generate_from_analysis(result, user_id)
            training_plans_store[plan_key] = training_plan_obj.to_dict()
        training_plan = training_plans_store.get(plan_key)
    
    if report_format == 'pdf':
        pdf_data = ReportGenerator.generate_pdf_report(result, user_info, training_plan)
        return send_file(
            io.BytesIO(pdf_data),
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f'voice_analysis_report_{file_id}.pdf'
        )
    elif report_format == 'excel':
        excel_data = ReportGenerator.generate_excel_report(result, training_plan)
        return send_file(
            io.BytesIO(excel_data),
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=f'voice_analysis_report_{file_id}.xlsx'
        )
    elif report_format == 'word':
        word_data = ReportGenerator.generate_word_report(result, user_info, training_plan)
        return send_file(
            io.BytesIO(word_data),
            mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            as_attachment=True,
            download_name=f'voice_analysis_report_{file_id}.docx'
        )
    else:
        html = ReportGenerator.generate_html_report(result, user_info, training_plan)
        return html

@reports_bp.route('/api/training-plan/<user_id>')
@login_required(roles=['admin', 'supervisor'])
def get_training_plan(user_id):
    """Получение плана обучения для менеджера"""
    plans = []
    for key, plan in training_plans_store.items():
        if plan.get('user_id') == int(user_id):
            plans.append(plan)
    
    if not plans:
        return jsonify({'success': True, 'plans': []})
    
    return jsonify({'success': True, 'plans': plans})

@reports_bp.route('/api/training-plan/assign', methods=['POST'])
@login_required(roles=['admin', 'supervisor'])
def assign_training_plan():
    """Назначение плана обучения менеджеру"""
    data = request.get_json()
    user_id = data.get('user_id')
    file_id = data.get('file_id')
    analysis_result = data.get('analysis_result')
    
    if not user_id or not analysis_result:
        return jsonify({'error': 'Недостаточно данных'}), 400
    
    training_plan_obj = TrainingPlan().generate_from_analysis(analysis_result, user_id)
    plan_key = f"plan_{user_id}_{file_id or str(uuid.uuid4())}"
    training_plans_store[plan_key] = training_plan_obj.to_dict()
    
    return jsonify({'success': True, 'plan': training_plan_obj.to_dict()})

@reports_bp.route('/api/training-plan/update-status', methods=['POST'])
@login_required(roles=['admin', 'supervisor', 'manager'])
def update_training_status():
    """Обновление статуса выполнения плана обучения"""
    data = request.get_json()
    plan_id = data.get('plan_id')
    week_index = data.get('week_index')
    status = data.get('status')  # completed, in_progress, pending
    
    for key, plan in training_plans_store.items():
        if key == plan_id or plan.get('id') == plan_id:
            if week_index is not None and 0 <= week_index < len(plan.get('weeks', [])):
                plan['weeks'][week_index]['status'] = status
            return jsonify({'success': True, 'plan': plan})
    
    return jsonify({'error': 'План не найден'}), 404

@reports_bp.route('/api/my-training-plan')
@login_required(roles=['admin', 'supervisor', 'manager'])
def my_training_plan():
    """Получение плана обучения для текущего пользователя"""
    user_id = session.get('user', {}).get('id')
    if not user_id:
        return jsonify({'error': 'Пользователь не найден'}), 404
    
    plans = []
    for key, plan in training_plans_store.items():
        if plan.get('user_id') == user_id:
            plans.append(plan)
    
    return jsonify({'success': True, 'plans': plans})

import io
