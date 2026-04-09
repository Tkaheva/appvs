import re
import numpy as np

CRITERIA = [
    {'id': 'greeting', 'name': 'Приветствие и представление', 'weight': 12, 'maxScore': 100,
     'keywords': ['здравствуйте', 'добрый день', 'приветствую', 'добрый вечер', 'меня зовут', 'автосалон', 'фреш авто'],
     'description': 'Администратор должен представиться, назвать автосалон и поприветствовать клиента'},
    
    {'id': 'client_info', 'name': 'Сбор информации о клиенте', 'weight': 18, 'maxScore': 100,
     'keywords': ['имя', 'как к вам', 'телефон', 'почта', 'автомобиль', 'модель', 'бюджет', 'стоимость', 'сроки'],
     'description': 'Администратор должен узнать имя, контакт, интересующий автомобиль, бюджет'},
    
    {'id': 'communication_style', 'name': 'Стиль общения', 'weight': 12, 'maxScore': 100,
     'keywords': ['спасибо', 'пожалуйста', 'будьте добры', 'благодарю', 'извините'],
     'description': 'Вежливость, четкость речи, позитивный тон'},
    
    {'id': 'problem_identification', 'name': 'Выявление потребности', 'weight': 18, 'maxScore': 100,
     'keywords': ['ищете', 'хотите', 'интересует', 'цель', 'задача', 'для чего', 'какой автомобиль'],
     'description': 'Администратор должен выявить, зачем клиент обратился'},
    
    {'id': 'offers_promotions', 'name': 'Рассказ об акциях', 'weight': 10, 'maxScore': 100,
     'keywords': ['акция', 'скидка', 'рассрочка', 'кредит', 'тест-драйв', 'специальное предложение', 'выгода'],
     'description': 'Администратор должен рассказать о текущих акциях и спецпредложениях'},
    
    {'id': 'solution_proposal', 'name': 'Предложение решения', 'weight': 12, 'maxScore': 100,
     'keywords': ['предлагаю', 'рекомендую', 'записаться', 'приезжайте', 'записывайте', 'посмотреть'],
     'description': 'Администратор должен предложить конкретное решение или следующий шаг'},
    
    {'id': 'active_listening', 'name': 'Активное слушание', 'weight': 8, 'maxScore': 100,
     'keywords': ['правильно ли я понял', 'уточните', 'вы имеете в виду', 'другими словами', 'если я правильно понимаю'],
     'description': 'Администратор демонстрирует понимание, переспрашивает, уточняет'},
    
    {'id': 'closing_efficiency', 'name': 'Эффективность завершения', 'weight': 10, 'maxScore': 100,
     'keywords': ['до свидания', 'всего доброго', 'до встречи', 'договорились', 'ждем вас', 'свяжемся'],
     'description': 'Четкое завершение разговора, договоренность о следующих шагах'}
]

def analyze_criterion(text, criterion):
    """Анализ критерия с улучшенной логикой"""
    text_lower = text.lower()
    base_score = 0
    found_keywords = []
    keyword_positions = []
    
    for keyword in criterion['keywords']:
        if keyword in text_lower:
            found_keywords.append(keyword)
            base_score += 8
            try:
                pos = text_lower.find(keyword)
                keyword_positions.append(pos)
            except:
                pass
    
    if criterion['id'] == 'greeting':
        greeting_words = ['здравствуйте', 'добрый день', 'приветствую']
        if any(w in text_lower for w in greeting_words):
            base_score += 15
        if 'меня зовут' in text_lower:
            base_score += 20
        if 'автосалон' in text_lower or 'фреш авто' in text_lower:
            base_score += 15
    
    elif criterion['id'] == 'client_info':
        info_categories = {
            'name': ['имя', 'как к вам'],
            'contact': ['телефон', 'почта', 'звонок'],
            'car': ['автомобиль', 'модель', 'машина'],
            'budget': ['бюджет', 'стоимость', 'цена'],
            'timing': ['сроки', 'когда', 'сегодня', 'завтра']
        }
        categories_found = 0
        for category, markers in info_categories.items():
            if any(marker in text_lower for marker in markers):
                categories_found += 1
                base_score += 12
        if categories_found >= 3:
            base_score += 20
    
    elif criterion['id'] == 'communication_style':
        polite_words = ['спасибо', 'пожалуйста', 'будьте добры', 'благодарю']
        for word in polite_words:
            if word in text_lower:
                base_score += 12
        positive_words = ['отлично', 'хорошо', 'замечательно', 'прекрасно']
        for word in positive_words:
            if word in text_lower:
                base_score += 5
    
    elif criterion['id'] == 'problem_identification':
        question_words = ['какой', 'какая', 'какое', 'что', 'почему', 'зачем']
        for word in question_words:
            if word in text_lower:
                base_score += 8
        if '?' in text:
            base_score += 10
    
    elif criterion['id'] == 'offers_promotions':
        promo_words = ['акция', 'скидка', 'рассрочка', 'кредит', 'тест-драйв']
        found_promo = []
        for word in promo_words:
            if word in text_lower:
                found_promo.append(word)
                base_score += 12
        if 'специальное предложение' in text_lower:
            base_score += 20
        if len(found_promo) >= 2:
            base_score += 15
    
    elif criterion['id'] == 'solution_proposal':
        action_words = ['предлагаю', 'рекомендую', 'записаться', 'приезжайте', 'записывайте']
        for word in action_words:
            if word in text_lower:
                base_score += 15
        if any(word in text_lower for word in ['сегодня', 'завтра', 'время']):
            base_score += 10
    
    elif criterion['id'] == 'active_listening':
        listening_phrases = [
            'правильно ли я понял', 'уточните', 'вы имеете в виду',
            'другими словами', 'если я правильно понимаю', 'я правильно понял'
        ]
        for phrase in listening_phrases:
            if phrase in text_lower:
                base_score += 20
    
    elif criterion['id'] == 'closing_efficiency':
        closing_phrases = [
            'до свидания', 'всего доброго', 'до встречи',
            'договорились', 'ждем вас', 'свяжемся', 'жду звонка'
        ]
        for phrase in closing_phrases:
            if phrase in text_lower:
                base_score += 20
    
    normalized_score = min(100, base_score)
    
    return {
        'score': int(normalized_score),
        'found_keywords': found_keywords,
        'keyword_count': len(found_keywords),
        'keyword_positions': keyword_positions
    }

def analyze_sentiment(text):
    """Улучшенный анализ тональности"""
    positive_words = [
        'отлично', 'спасибо', 'хорошо', 'супер', 'отличный', 'доволен', 'рад', 
        'здорово', 'прекрасно', 'замечательно', 'понравилось', 'устраивает', 
        'подходит', 'нравится', 'класс', 'великолепно', 'благодарю'
    ]
    negative_words = [
        'проблема', 'дорого', 'долго', 'плохо', 'сложно', 'не нравится', 
        'ужасно', 'недоволен', 'разочарован', 'не подходит', 'слишком', 
        'жаль', 'обидно', 'не получается', 'невозможно'
    ]
    intensifiers = ['очень', 'слишком', 'крайне', 'чрезвычайно', 'совсем', 'абсолютно']
    
    text_lower = text.lower()
    words = text_lower.split()
    
    positive_score = 0
    negative_score = 0
    
    for i, word in enumerate(words):
        if word in positive_words:
            if i > 0 and words[i-1] in intensifiers:
                positive_score += 3
            else:
                positive_score += 2
        if word in negative_words:
            if i > 0 and words[i-1] in intensifiers:
                negative_score += 3
            else:
                negative_score += 2
    
    positive_score += text.count('!') * 0.5
    positive_score += text.count('😊') * 2
    negative_score += text.count('😞') * 2
    
    total_words = len(words)
    if total_words == 0:
        return 50
    
    sentiment = 50 + ((positive_score - negative_score) / total_words * 40)
    return int(max(0, min(100, sentiment)))

def calculate_text_complexity(text):
    """Расчет сложности текста"""
    words = text.split()
    if not words:
        return 0
    
    unique_words = len(set(words))
    total_words = len(words)
    uniqueness_ratio = (unique_words / total_words) * 100
    
    avg_word_length = sum(len(word) for word in words) / total_words
    
    long_words = sum(1 for w in words if len(w) > 6)
    long_word_ratio = (long_words / total_words) * 100
    
    complexity = (uniqueness_ratio * 0.4 + avg_word_length * 5 + long_word_ratio * 0.3)
    return min(100, int(complexity))

def generate_recommendations(criteria_scores):
    """Генерация персонализированных рекомендаций"""
    recommendations = []
    
    for criterion in CRITERIA:
        score_data = criteria_scores.get(criterion['id'], {'score': 0})
        score = score_data.get('score', 0)
        
        if score < 30:
            priority = 'high'
            recommendation = f"🔴 КРИТИЧЕСКИ ВАЖНО: {criterion['name']}. {criterion['description']}"
        elif score < 60:
            priority = 'medium'
            recommendation = f"🟡 РЕКОМЕНДУЕТСЯ УЛУЧШИТЬ: {criterion['name']}. {criterion['description']}"
        elif score < 80:
            priority = 'low'
            recommendation = f"🟢 ДЛЯ РАЗВИТИЯ: {criterion['name']}. Есть потенциал для улучшения."
        else:
            continue
        
        recommendations.append({
            'criterion_id': criterion['id'],
            'criterion_name': criterion['name'],
            'priority': priority,
            'recommendation_text': recommendation,
            'current_score': score,
            'target_score': min(100, score + 30)
        })
    
    return sorted(recommendations, key=lambda x: {'high': 0, 'medium': 1, 'low': 2}[x['priority']])

def generate_training_plan(criteria_scores):
    """Генерация плана обучения на основе результатов"""
    low_scores = []
    medium_scores = []
    
    for criterion in CRITERIA:
        score_data = criteria_scores.get(criterion['id'], {'score': 0})
        score = score_data.get('score', 0)
        
        if score < 40:
            low_scores.append({'name': criterion['name'], 'id': criterion['id'], 'score': score})
        elif score < 70:
            medium_scores.append({'name': criterion['name'], 'id': criterion['id'], 'score': score})
    
    plan = []
    
    if low_scores:
        plan.append({
            'week': 1,
            'title': 'Неделя 1: Интенсивный курс',
            'topics': [f"📌 {item['name']} (текущий балл: {item['score']}/100)" for item in low_scores],
            'color': '#f44336',
            'exercises': [
                'Прослушивание эталонных записей',
                'Ролевые игры с наставником',
                'Разбор ошибок и их исправление'
            ]
        })
    
    if medium_scores:
        plan.append({
            'week': 2,
            'title': 'Неделя 2: Закрепление навыков',
            'topics': [f"📌 {item['name']} (текущий балл: {item['score']}/100)" for item in medium_scores],
            'color': '#ff9800',
            'exercises': [
                'Практические задания',
                'Анализ собственных записей',
                'Обратная связь от руководителя'
            ]
        })
    
    if not plan:
        plan.append({
            'week': 1,
            'title': 'Поддержание высокого уровня',
            'topics': [
                'Продвинутые техники продаж',
                'Работа с возражениями',
                'Разбор сложных кейсов'
            ],
            'color': '#4caf50',
            'exercises': [
                'Участие в мастер-классах',
                'Наставничество для новых сотрудников',
                'Сертификация'
            ]
        })
    
    return plan

def analyze_audio_result(audio_result):
    """Полный анализ аудио с расширенной статистикой"""
    full_text = audio_result['text']
    segments = audio_result['segments']
    
    criteria_scores = {}
    for criterion in CRITERIA:
        criteria_scores[criterion['id']] = analyze_criterion(full_text, criterion)
    
    admin_segments = [s for s in segments if s['speaker'] == 'admin']
    client_segments = [s for s in segments if s['speaker'] == 'client']
    
    admin_word_count = sum(len(s['text'].split()) for s in admin_segments)
    client_word_count = sum(len(s['text'].split()) for s in client_segments)
    word_count = admin_word_count + client_word_count
    
    total_weight = sum(c['weight'] for c in CRITERIA)
    total_score = 0
    for criterion in CRITERIA:
        score = criteria_scores[criterion['id']]['score']
        total_score += score * (criterion['weight'] / total_weight)
    total_score = round(total_score)
    
    if total_score >= 90:
        grade, grade_class, grade_description = 'Отлично', 'grade-excellent', 'Высокий уровень обслуживания!'
    elif total_score >= 80:
        grade, grade_class, grade_description = 'Хорошо', 'grade-good', 'Хороший результат, есть потенциал'
    elif total_score >= 70:
        grade, grade_class, grade_description = 'Выше среднего', 'grade-good', 'Неплохо, но нужно доработать'
    elif total_score >= 60:
        grade, grade_class, grade_description = 'Средне', 'grade-average', 'Требуется улучшение'
    elif total_score >= 40:
        grade, grade_class, grade_description = 'Ниже среднего', 'grade-poor', 'Необходимо обучение'
    else:
        grade, grade_class, grade_description = 'Требуется обучение', 'grade-fail', 'Срочно требуется обучение!'
    
    sentiment = analyze_sentiment(full_text)
    complexity = calculate_text_complexity(full_text)
    
    avg_confidence = sum(s.get('confidence', 0.8) for s in segments) / len(segments) if segments else 0
    
    dialogue_analysis = {
        'total_turns': len(segments),
        'admin_turns': len(admin_segments),
        'client_turns': len(client_segments),
        'admin_words': admin_word_count,
        'client_words': client_word_count,
        'admin_percentage': round((admin_word_count / word_count * 100) if word_count > 0 else 0),
        'client_percentage': round((client_word_count / word_count * 100) if word_count > 0 else 0),
        'avg_admin_response': np.mean([len(s['text'].split()) for s in admin_segments]) if admin_segments else 0,
        'avg_client_response': np.mean([len(s['text'].split()) for s in client_segments]) if client_segments else 0,
        'longest_admin': max([len(s['text'].split()) for s in admin_segments]) if admin_segments else 0,
        'longest_client': max([len(s['text'].split()) for s in client_segments]) if client_segments else 0,
        'question_count': full_text.count('?'),
        'admin_question_count': sum(s['text'].count('?') for s in admin_segments),
        'client_question_count': sum(s['text'].count('?') for s in client_segments)
    }
    
    recommendations = generate_recommendations(criteria_scores)
    training_plan = generate_training_plan(criteria_scores)
    
    keyword_categories = {
        'Позитивные слова': ['отлично', 'хорошо', 'спасибо', 'рад', 'доволен'],
        'Проблемные слова': ['проблема', 'дорого', 'долго', 'сложно'],
        'Действия': ['записаться', 'приехать', 'посмотреть', 'оформить'],
        'Вопросы': ['сколько', 'какой', 'когда', 'где']
    }
    
    found_keywords_by_category = {}
    for category, keywords in keyword_categories.items():
        found = [kw for kw in keywords if kw in full_text.lower()]
        if found:
            found_keywords_by_category[category] = found
    
    return {
        'success': True,
        'text': full_text,
        'word_count': word_count,
        'admin_word_count': admin_word_count,
        'client_word_count': client_word_count,
        'duration': audio_result['duration'],
        'duration_formatted': audio_result['duration_formatted'],
        'confidence': avg_confidence,
        'confidence_percent': f"{int(avg_confidence * 100)}%",
        'criteria_scores': criteria_scores,
        'total_score': total_score,
        'grade': grade,
        'grade_class': grade_class,
        'grade_description': grade_description,
        'sentiment': sentiment,
        'sentiment_label': 'Позитивная' if sentiment > 60 else 'Нейтральная' if sentiment > 40 else 'Негативная',
        'complexity': complexity,
        'recommendations': recommendations,
        'training_plan': training_plan,
        'segments': segments,
        'segment_count': len(segments),
        'admin_segments': len(admin_segments),
        'client_segments': len(client_segments),
        'dialogue_analysis': dialogue_analysis,
        'keyword_categories': found_keywords_by_category,
        'analysis_time': '2026-03-25T00:00:00'
    }
