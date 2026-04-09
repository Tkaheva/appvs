import os
import uuid
import speech_recognition as sr
from pydub import AudioSegment
from app.utils import format_duration, format_timestamp
import numpy as np

class AudioProcessor:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.recognizer.energy_threshold = 300
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = 0.8
        
    def preprocess(self, file_path):
        """Предобработка аудиофайла для улучшения распознавания"""
        try:
            audio = AudioSegment.from_file(file_path)
            
            if audio.channels > 1:
                audio = audio.set_channels(1)
            
            audio = audio.apply_gain(-audio.max_dBFS)
            audio = audio.low_pass_filter(8000)
            
            return audio
        except Exception as e:
            print(f"Ошибка предобработки: {e}")
            return AudioSegment.from_file(file_path)
    
    def split_into_chunks(self, audio, min_silence_len=500, silence_thresh=-40):
        """Умное разбиение аудио на чанки по тишине"""
        try:
            from pydub.silence import split_on_silence
            chunks = split_on_silence(
                audio,
                min_silence_len=min_silence_len,
                silence_thresh=silence_thresh,
                keep_silence=300
            )
            
            if not chunks:
                chunks = [audio]
            
            return chunks
        except:
            chunk_duration = 30 * 1000
            chunks = []
            for i in range(0, len(audio), chunk_duration):
                chunks.append(audio[i:i+chunk_duration])
            return chunks
    
    def recognize_chunk(self, chunk):
        """Распознавание речи в чанке"""
        chunk_path = f"{uuid.uuid4()}.wav"
        chunk.export(chunk_path, format='wav')
        
        try:
            with sr.AudioFile(chunk_path) as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
                audio_data = self.recognizer.record(source)
            
            text = self.recognizer.recognize_google(audio_data, language='ru-RU')
            confidence = 0.85
            
            return text, confidence
        except sr.UnknownValueError:
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
    
    def detect_speaker(self, text, previous_speaker='admin'):
        """Улучшенное определение роли говорящего"""
        text_lower = text.lower()
        words = text_lower.split()
        
        admin_markers = {
            'greeting': ['здравствуйте', 'добрый день', 'приветствую', 'добрый вечер'],
            'intro': ['меня зовут', 'автосалон', 'фреш авто', 'компания', 'представитель'],
            'professional': ['оформить', 'записать', 'предлагаю', 'рекомендую', 'сообщите'],
            'closing': ['до свидания', 'всего доброго', 'ждём вас', 'обращайтесь'],
            'offers': ['акция', 'скидка', 'рассрочка', 'кредит', 'спецпредложение', 'тест-драйв']
        }
        
        client_markers = {
            'questions': ['сколько', 'какой', 'почему', 'когда', 'где', 'что', 'как'],
            'interest': ['интересует', 'хочу', 'нужен', 'подскажите', 'узнать', 'посмотреть'],
            'personal': ['я', 'мне', 'меня', 'мой', 'моя', 'мое'],
            'agreement': ['да', 'хорошо', 'согласен', 'договорились', 'понятно'],
            'concerns': ['дорого', 'долго', 'сложно', 'проблема', 'неудобно']
        }
        
        admin_score = 0
        client_score = 0
        
        for category, markers in admin_markers.items():
            for marker in markers:
                if marker in text_lower:
                    admin_score += 2
                    if category == 'intro':
                        admin_score += 2
                    if category == 'professional':
                        admin_score += 1
        
        for category, markers in client_markers.items():
            for marker in markers:
                if marker in text_lower:
                    client_score += 2
                    if category == 'questions':
                        client_score += 2
                    if category == 'personal':
                        client_score += 1
        
        if len(words) > 15:
            admin_score += 2
        elif len(words) < 3:
            client_score += 1
        
        if '?' in text:
            client_score += 3
        
        if '!' in text:
            admin_score += 1
        
        if previous_speaker == 'admin':
            admin_score += 0.5
        else:
            client_score += 0.5
        
        if admin_score > client_score + 2:
            return 'admin'
        elif client_score > admin_score + 2:
            return 'client'
        else:
            return previous_speaker
    
    def process(self, file_path):
        """Полная обработка аудиофайла"""
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
                        time_offset = current_time + (j * 2)
                        all_segments.append({
                            'speaker': speaker,
                            'text': sentence,
                            'timestamp': format_timestamp(time_offset),
                            'confidence': confidence,
                            'duration': len(sentence.split()) * 0.3
                        })
            
            current_time += chunk_duration
        
        full_text = ' '.join([s['text'] for s in all_segments])
        
        return {
            'text': full_text,
            'segments': all_segments,
            'duration': duration,
            'duration_formatted': format_duration(duration),
            'segment_count': len(all_segments)
        }
    
    def split_into_sentences(self, text):
        """Разбиение текста на предложения"""
        import re
        sentences = re.split(r'(?<=[.!?])\s+', text)
        return [s.strip() for s in sentences if s.strip()]
