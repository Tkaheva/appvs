import os
import uuid
import speech_recognition as sr
from pydub import AudioSegment
from app.utils import format_duration, format_timestamp
import numpy as np

class AudioProcessor:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        # Улучшенные настройки распознавания
        self.recognizer.energy_threshold = 200  # Уменьшен порог чувствительности
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = 0.5  # Уменьшен порог паузы
        self.recognizer.phrase_threshold = 0.3  # Добавлен порог фразы
        self.recognizer.non_speaking_duration = 0.3  # Добавлена длительность неговорящего
        
    def preprocess(self, file_path):
        """Улучшенная предобработка аудиофайла"""
        try:
            audio = AudioSegment.from_file(file_path)
            
            # Конвертация в моно
            if audio.channels > 1:
                audio = audio.set_channels(1)
            
            # Нормализация громкости
            audio = audio.normalize()
            
            # Применение фильтра для уменьшения шума
            audio = audio.low_pass_filter(8000)
            audio = audio.high_pass_filter(80)
            
            # Увеличение громкости для лучшего распознавания
            audio = audio + 3
            
            # Конвертация частоты дискретизации для лучшего распознавания
            if audio.frame_rate != 16000:
                audio = audio.set_frame_rate(16000)
            
            return audio
        except Exception as e:
            print(f"Ошибка предобработки: {e}")
            return AudioSegment.from_file(file_path)
    
    def split_into_chunks(self, audio, min_silence_len=300, silence_thresh=-35):
        """Улучшенное разбиение аудио на чанки"""
        try:
            from pydub.silence import split_on_silence
            chunks = split_on_silence(
                audio,
                min_silence_len=min_silence_len,
                silence_thresh=silence_thresh,
                keep_silence=200
            )
            
            # Фильтрация пустых чанков
            chunks = [chunk for chunk in chunks if len(chunk) > 500]  # Минимум 0.5 секунды
            
            if not chunks:
                chunks = [audio]
            
            # Разбиваем слишком длинные чанки
            max_chunk_duration = 30000  # 30 секунд максимум
            processed_chunks = []
            for chunk in chunks:
                if len(chunk) > max_chunk_duration:
                    for i in range(0, len(chunk), max_chunk_duration):
                        processed_chunks.append(chunk[i:i+max_chunk_duration])
                else:
                    processed_chunks.append(chunk)
            
            return processed_chunks
        except Exception as e:
            print(f"Ошибка разбиения: {e}")
            chunk_duration = 15 * 1000  # 15 секунд
            chunks = []
            for i in range(0, len(audio), chunk_duration):
                chunks.append(audio[i:i+chunk_duration])
            return chunks
    
    def recognize_chunk(self, chunk):
        """Улучшенное распознавание речи в чанке"""
        chunk_path = f"{uuid.uuid4()}.wav"
        chunk.export(chunk_path, format='wav')
        
        try:
            with sr.AudioFile(chunk_path) as source:
                # Улучшенная настройка шума
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio_data = self.recognizer.record(source)
            
            # Попытка распознавания с Google
            text = self.recognizer.recognize_google(audio_data, language='ru-RU', show_all=False)
            confidence = 0.85
            
            # Постобработка текста
            text = self.postprocess_text(text)
            
            return text, confidence
        except sr.UnknownValueError:
            # Попытка с Sphinx для русских слов (более устойчив к шуму)
            try:
                text = self.recognizer.recognize_sphinx(audio_data, language='ru-RU')
                confidence = 0.65
                text = self.postprocess_text(text)
                return text, confidence
            except:
                return None, 0
        except sr.RequestError as e:
            print(f"Ошибка сервиса распознавания: {e}")
            return None, 0
        except Exception as e:
            print(f"Ошибка распознавания: {e}")
            return None, 0
        finally:
            if os.path.exists(chunk_path):
                os.remove(chunk_path)
    
    def postprocess_text(self, text):
        """Постобработка распознанного текста"""
        if not text:
            return text
        
        # Приведение к нижнему регистру для обработки
        text_original = text
        text = text.lower()
        
        # Исправление частых ошибок распознавания
        corrections = {
            'здраствуйте': 'здравствуйте',
            'здрасте': 'здравствуйте',
            'добрый ден': 'добрый день',
            'добрый вечер': 'добрый вечер',
            'до свидание': 'до свидания',
            'спасибо': 'спасибо',
            'пажалуйста': 'пожалуйста',
            'пажалуста': 'пожалуйста',
            'автомобил': 'автомобиль',
            'автосалон': 'автосалон',
            'тест драйв': 'тест-драйв',
            'тестдрайв': 'тест-драйв',
            'кредит': 'кредит',
            'рассрочка': 'рассрочка',
            'оформить': 'оформить',
            'записаться': 'записаться'
        }
        
        for wrong, correct in corrections.items():
            text = text.replace(wrong, correct)
        
        # Восстановление заглавных букв для имён и начала предложений
        sentences = text.split('. ')
        for i, sentence in enumerate(sentences):
            if sentence:
                sentences[i] = sentence[0].upper() + sentence[1:]
        text = '. '.join(sentences)
        
        return text
    
    def detect_speaker(self, text, previous_speaker='admin'):
        """Улучшенное определение роли говорящего"""
        text_lower = text.lower()
        words = text_lower.split()
        
        admin_markers = {
            'greeting': ['здравствуйте', 'добрый день', 'приветствую', 'добрый вечер', 'здрасте', 'доброе утро'],
            'intro': ['меня зовут', 'автосалон', 'фреш авто', 'компания', 'представитель', 'cоfresh', 'авто с заботой'],
            'professional': ['оформить', 'записать', 'предлагаю', 'рекомендую', 'сообщите', 'запишу', 'запишем'],
            'closing': ['до свидания', 'всего доброго', 'ждём вас', 'обращайтесь', 'до связи', 'до встречи'],
            'offers': ['акция', 'скидка', 'рассрочка', 'кредит', 'спецпредложение', 'тест-драйв'],
            'questions_admin': ['как я могу вам помочь', 'что вас интересует', 'какую машину', 'какой автомобиль']
        }
        
        client_markers = {
            'questions': ['сколько', 'какой', 'почему', 'когда', 'где', 'что', 'как', 'зачем', 'откуда'],
            'interest': ['интересует', 'хочу', 'нужен', 'подскажите', 'узнать', 'посмотреть', 'присмотреть'],
            'personal': ['я', 'мне', 'меня', 'мой', 'моя', 'мое', 'мне нужно', 'я хочу'],
            'agreement': ['да', 'хорошо', 'согласен', 'договорились', 'понятно', 'ладно', 'окей'],
            'concerns': ['дорого', 'долго', 'сложно', 'проблема', 'неудобно', 'слишком', 'жаль', 'обидно']
        }
        
        admin_score = 0
        client_score = 0
        
        for category, markers in admin_markers.items():
            for marker in markers:
                if marker in text_lower:
                    admin_score += 2
                    if category == 'intro':
                        admin_score += 3
                    if category == 'professional':
                        admin_score += 2
                    if category == 'offers':
                        admin_score += 1
        
        for category, markers in client_markers.items():
            for marker in markers:
                if marker in text_lower:
                    client_score += 2
                    if category == 'questions':
                        client_score += 2
                    if category == 'personal':
                        client_score += 2
        
        # Анализ длины фразы
        if len(words) > 20:
            admin_score += 2
        elif len(words) < 2:
            client_score += 1
        
        # Анализ вопросительных знаков
        question_count = text.count('?')
        if question_count > 0:
            client_score += question_count * 2
        
        # Анализ восклицательных знаков
        if text.count('!') > 0:
            admin_score += 1
        
        # Продолжение предыдущего говорящего
        if previous_speaker == 'admin':
            admin_score += 0.5
        else:
            client_score += 0.5
        
        # Принятие решения
        if admin_score > client_score + 1.5:
            return 'admin'
        elif client_score > admin_score + 1.5:
            return 'client'
        else:
            return previous_speaker
    
    def process(self, file_path):
        """Полная обработка аудиофайла с улучшенным распознаванием"""
        audio = self.preprocess(file_path)
        duration = len(audio) / 1000
        
        chunks = self.split_into_chunks(audio)
        
        all_segments = []
        current_time = 0
        previous_speaker = 'admin'
        
        for i, chunk in enumerate(chunks):
            chunk_duration = len(chunk) / 1000
            text, confidence = self.recognize_chunk(chunk)
            
            if text and text.strip():
                speaker = self.detect_speaker(text, previous_speaker)
                previous_speaker = speaker
                sentences = self.split_into_sentences(text)
                
                for j, sentence in enumerate(sentences):
                    if sentence.strip():
                        time_offset = current_time + (j * 1.5)
                        all_segments.append({
                            'speaker': speaker,
                            'text': sentence,
                            'timestamp': format_timestamp(time_offset),
                            'confidence': confidence,
                            'duration': len(sentence.split()) * 0.3
                        })
            else:
                # Если текст не распознан, добавляем маркер неразборчивой речи
                all_segments.append({
                    'speaker': 'unknown',
                    'text': '[неразборчиво]',
                    'timestamp': format_timestamp(current_time),
                    'confidence': 0,
                    'duration': chunk_duration
                })
            
            current_time += chunk_duration
        
        full_text = ' '.join([s['text'] for s in all_segments if s['speaker'] != 'unknown'])
        
        return {
            'text': full_text,
            'segments': all_segments,
            'duration': duration,
            'duration_formatted': format_duration(duration),
            'segment_count': len(all_segments)
        }
    
    def split_into_sentences(self, text):
        """Улучшенное разбиение текста на предложения"""
        import re
        
        # Разделение по знакам препинания
        sentences = re.split(r'(?<=[.!?;:])\s+', text)
        
        # Обработка аббревиатур и сокращений
        result = []
        for sentence in sentences:
            sentence = sentence.strip()
            if sentence:
                # Удаляем лишние пробелы
                sentence = re.sub(r'\s+', ' ', sentence)
                result.append(sentence)
        
        return result if result else [text]
