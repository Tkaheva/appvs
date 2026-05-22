import os
import uuid
import json
import datetime
from enum import Enum

class UserRole(Enum):
    ADMIN = 'admin'
    SUPERVISOR = 'supervisor'
    MANAGER = 'manager'

class User:
    """Модель пользователя с ролями"""
    def __init__(self, id=None, username=None, password_hash=None, full_name=None, role='manager', department=None, manager_id=None):
        self.id = id
        self.username = username
        self.password_hash = password_hash
        self.full_name = full_name
        self.role = role
        self.department = department
        self.manager_id = manager_id
        self.is_active = True
        self.created_at = datetime.datetime.now()
        self.last_login = None
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'full_name': self.full_name,
            'role': self.role,
            'department': self.department,
            'manager_id': self.manager_id,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }

class ExtendedTrainingCourse:
    """Расширенный курс обучения с детальным планом"""
    
    COURSE_STRUCTURE = {
        'greeting': {
            'name': 'Приветствие и представление',
            'icon': '👋',
            'modules': [
                {
                    'title': 'Стандарты приветствия в автосалоне',
                    'duration_hours': 2,
                    'content': [
                        'Правильное произношение названия компании "Фреш Авто"',
                        'Стандартная фраза приветствия: "Здравствуйте, автосалон Фреш Авто, меня зовут [Имя], чем могу помочь?"',
                        'Тон и интонация приветствия',
                        'Отработка приветствия в различных ситуациях'
                    ],
                    'deadline_days': 2,
                    'homework': 'Записать 5 вариантов приветствия и отправить на проверку'
                },
                {
                    'title': 'Активное слушание в начале разговора',
                    'duration_hours': 1.5,
                    'content': [
                        'Как правильно уточнить имя клиента',
                        'Техники запоминания имени',
                        'Использование имени клиента в разговоре'
                    ],
                    'deadline_days': 3,
                    'homework': 'Практика в 10 разговорах - использовать имя клиента не менее 3 раз'
                }
            ],
            'test_questions': [
                'Как правильно представиться при входящем звонке?',
                'Какие фразы приветствия запрещены?',
                'Почему важно назвать компанию в начале разговора?'
            ]
        },
        'client_info': {
            'name': 'Сбор информации о клиенте',
            'icon': '📝',
            'modules': [
                {
                    'title': 'Чек-лист сбора информации',
                    'duration_hours': 2,
                    'content': [
                        'Бюджет клиента (точный диапазон)',
                        'Предпочитаемая марка и модель',
                        'Тип кузова, цвет, комплектация',
                        'Сроки покупки',
                        'Способ оплаты (кредит, наличные, рассрочка)',
                        'Наличие автомобиля в трейд-ин'
                    ],
                    'deadline_days': 3,
                    'homework': 'Составить персональный чек-лист из 7 вопросов'
                },
                {
                    'title': 'Техника открытых вопросов',
                    'duration_hours': 2.5,
                    'content': [
                        'Чем открытые вопросы отличаются от закрытых',
                        'Примеры открытых вопросов для автосалона',
                        'Как переформулировать закрытый вопрос в открытый',
                        'Практика задавания вопросов без "да/нет" ответов'
                    ],
                    'deadline_days': 5,
                    'homework': 'Записать диалог, где задано минимум 5 открытых вопросов'
                },
                {
                    'title': 'Методика SPIN-продаж для автосалона',
                    'duration_hours': 3,
                    'content': [
                        'Ситуационные вопросы (Situation)',
                        'Проблемные вопросы (Problem)',
                        'Извлекающие вопросы (Implication)',
                        'Направляющие вопросы (Need-payoff)',
                        'Адаптация SPIN для телефонных продаж'
                    ],
                    'deadline_days': 7,
                    'homework': 'Применить SPIN в 3 диалогах и сдать расшифровку'
                }
            ],
            'test_questions': [
                'Назовите 5 обязательных вопросов для сбора информации о клиенте',
                'Чем отличается открытый вопрос от закрытого? Приведите примеры',
                'Что означает аббревиатура SPIN?'
            ]
        },
        'communication_style': {
            'name': 'Стиль общения',
            'icon': '💬',
            'modules': [
                {
                    'title': 'Профессиональная лексика',
                    'duration_hours': 1.5,
                    'content': [
                        'Слова-паразиты и как от них избавиться',
                        'Профессиональные термины автомобильной сферы',
                        'Вежливые формы обращения',
                        'Запрещенные фразы и выражения'
                    ],
                    'deadline_days': 2,
                    'homework': 'Анализ 5 своих разговоров на наличие слов-паразитов'
                },
                {
                    'title': 'Техники активного слушания',
                    'duration_hours': 2,
                    'content': [
                        'Эхо-техника (повтор последних слов)',
                        'Вербализация (пересказ своими словами)',
                        'Резюмирование (подведение итогов)',
                        'Эмпатия в диалоге'
                    ],
                    'deadline_days': 4,
                    'homework': 'В 5 разговорах применить 3 техники активного слушания'
                },
                {
                    'title': 'Тональность и голос',
                    'duration_hours': 1.5,
                    'content': [
                        'Темп речи (оптимальный для телефона)',
                        'Громкость и интонация',
                        'Улыбка в голосе',
                        'Паузы и их значение'
                    ],
                    'deadline_days': 3,
                    'homework': 'Записать голосовое сообщение с анализом темпа и интонации'
                }
            ],
            'test_questions': [
                'Какие слова являются словами-паразитами?',
                'Назовите 3 техники активного слушания',
                'Почему важна улыбка при телефонном разговоре?'
            ]
        },
        'problem_identification': {
            'name': 'Выявление потребности',
            'icon': '🎯',
            'modules': [
                {
                    'title': 'Типы клиентов и их потребности',
                    'duration_hours': 2,
                    'content': [
                        'Клиент-новичок (впервые покупает авто)',
                        'Опытный автовладелец',
                        'Корпоративный клиент',
                        'Клиент с конкретной моделью',
                        'Клиент в поиске выгодного предложения'
                    ],
                    'deadline_days': 3,
                    'homework': 'Определить типы 10 клиентов по их первым фразам'
                },
                {
                    'title': 'Техника выявления болевых точек',
                    'duration_hours': 2.5,
                    'content': [
                        'Вопросы о текущем автомобиле (проблемы, недовольство)',
                        'Вопросы о потребностях семьи',
                        'Вопросы о комфорте и безопасности',
                        'Вопросы об экономичности и обслуживании'
                    ],
                    'deadline_days': 5,
                    'homework': 'Составить список из 10 вопросов для выявления боли клиента'
                },
                {
                    'title': 'Работа с возражениями',
                    'duration_hours': 3,
                    'content': [
                        'Классификация возражений (цена, качество, сроки, конкуренты)',
                        'Методика "согласие-аргумент-предложение"',
                        'Техника "да, но..."',
                        'Превращение возражения в преимущество',
                        'Топ-10 возражений в автосалоне и ответы на них'
                    ],
                    'deadline_days': 7,
                    'homework': 'Отработать 10 возражений в ролевой игре с наставником'
                }
            ],
            'test_questions': [
                'Какие вопросы помогают выявить "боли" клиента?',
                'Назовите 4 типа клиентов по их потребностям',
                'Как правильно отработать возражение "дорого"?'
            ]
        },
        'offers_promotions': {
            'name': 'Рассказ об акциях',
            'icon': '🏷️',
            'modules': [
                {
                    'title': 'Актуальные акции и предложения',
                    'duration_hours': 1.5,
                    'content': [
                        'Изучение текущих акций автосалона',
                        'Сезонные предложения и скидки',
                        'Кредитные программы и рассрочки',
                        'Программа trade-in и её преимущества',
                        'Спецпредложения от дилеров (Haval, Chery, Exeed)'
                    ],
                    'deadline_days': 2,
                    'homework': 'Изучить и пересказать все текущие акции'
                },
                {
                    'title': 'Техника презентации выгоды',
                    'duration_hours': 2,
                    'content': [
                        'Перевод цены в выгоду (экономия в месяц, год)',
                        'Сравнение с конкурентами',
                        'Подсчёт экономии',
                        'Создание ощущения срочности (ограниченное предложение)'
                    ],
                    'deadline_days': 4,
                    'homework': 'Подготовить скрипт презентации кредита с подсчётом выгоды'
                },
                {
                    'title': 'Упоминание акций естественно',
                    'duration_hours': 1,
                    'content': [
                        'Как вписать акцию в диалог без навязывания',
                        'Временные маркеры для акций',
                        'Связь акции с потребностью клиента'
                    ],
                    'deadline_days': 3,
                    'homework': 'Записать диалог с упоминанием акции'
                }
            ],
            'test_questions': [
                'Назовите 3 текущие акции автосалона',
                'Как перевести ежемесячный платеж в выгоду для клиента?',
                'Почему важно упоминать ограниченность предложения?'
            ]
        },
        'solution_proposal': {
            'name': 'Предложение решения',
            'icon': '💡',
            'modules': [
                {
                    'title': 'Подбор автомобиля под потребности',
                    'duration_hours': 2,
                    'content': [
                        'Соотнесение бюджета и модели',
                        'Учет пожеланий клиента',
                        'Альтернативные варианты',
                        'Создание "пакета предложений"'
                    ],
                    'deadline_days': 3,
                    'homework': 'Подобрать 3 варианта авто под разные бюджеты'
                },
                {
                    'title': 'Техника приглашения в салон',
                    'duration_hours': 1.5,
                    'content': [
                        'Почему тест-драйв — ключевой этап',
                        'Аргументы для приглашения',
                        'Запись на конкретное время',
                        'Подтверждение записи (SMS, звонок)'
                    ],
                    'deadline_days': 2,
                    'homework': 'Отработать 5 приглашений на тест-драйв'
                },
                {
                    'title': 'Закрытие сделки по телефону',
                    'duration_hours': 2.5,
                    'content': [
                        'Альтернативный выбор (этот или тот?)',
                        'Предположение согласия',
                        'Снятие последних возражений',
                        'Оформление бронирования онлайн'
                    ],
                    'deadline_days': 5,
                    'homework': 'Записать диалог с бронированием автомобиля'
                }
            ],
            'test_questions': [
                'Какие аргументы убеждают клиента приехать на тест-драйв?',
                'Как предложить альтернативу, если авто нет в наличии?',
                'Что такое "предположение согласия"?'
            ]
        },
        'active_listening': {
            'name': 'Активное слушание',
            'icon': '👂',
            'modules': [
                {
                    'title': 'Базовые техники активного слушания',
                    'duration_hours': 2,
                    'content': [
                        'Эхо-техника (дословное повторение)',
                        'Уточняющие вопросы',
                        'Перефразирование',
                        'Поддерживающие фразы'
                    ],
                    'deadline_days': 3,
                    'homework': 'Анализ 3 диалогов с подсчётом техник слушания'
                },
                {
                    'title': 'Эмпатия в телефонных продажах',
                    'duration_hours': 1.5,
                    'content': [
                        'Фразы эмпатии («Я понимаю», «Мне жаль», «Согласен»)',
                        'Присоединение к эмоциям клиента',
                        'Снижение напряжения'
                    ],
                    'deadline_days': 3,
                    'homework': 'В 5 диалогах использовать эмпатические фразы'
                },
                {
                    'title': 'Резюмирование и подведение итогов',
                    'duration_hours': 1,
                    'content': [
                        'Формула резюмирования: "Если я правильно понял..."',
                        'Подведение итогов после сбора информации',
                        'Согласование следующих шагов'
                    ],
                    'deadline_days': 2,
                    'homework': 'В каждом диалоге резюмировать разговор'
                }
            ],
            'test_questions': [
                'Что такое эхо-техника? Приведите пример',
                'Какие фразы показывают клиенту, что его слышат?',
                'Как правильно резюмировать разговор?'
            ]
        },
        'closing_efficiency': {
            'name': 'Эффективность завершения',
            'icon': '✅',
            'modules': [
                {
                    'title': 'Правильное прощание',
                    'duration_hours': 1,
                    'content': [
                        'Стандартные фразы завершения',
                        'Благодарность за звонок',
                        'Пожелание хорошего дня',
                        'Незакрытые вопросы перед прощанием'
                    ],
                    'deadline_days': 2,
                    'homework': 'Отработать завершение 10 разговоров'
                },
                {
                    'title': 'Договорённость о следующих шагах',
                    'duration_hours': 1.5,
                    'content': [
                        'Чёткое определение действия (клиент приезжает, менеджер звонит)',
                        'Фиксация договорённостей в CRM',
                        'Отправка подтверждения (SMS, email)',
                        'Напоминание о встрече'
                    ],
                    'deadline_days': 3,
                    'homework': 'Создать шаблон подтверждения для клиента'
                },
                {
                    'title': 'Пост-разговорный анализ',
                    'duration_hours': 1,
                    'content': [
                        'Самооценка разговора по чек-листу',
                        'Фиксация ошибок для работы',
                        'План улучшения на следующий звонок'
                    ],
                    'deadline_days': 2,
                    'homework': 'Заполнить чек-лист самооценки для 5 звонков'
                }
            ],
            'test_questions': [
                'Что обязательно нужно сделать перед прощанием?',
                'Какие договорённости нужно зафиксировать?',
                'Как отправить клиенту подтверждение встречи?'
            ]
        }
    }
    
    def __init__(self, user_id=None, manager_name=None, total_score=0, weak_areas=None):
        self.user_id = user_id
        self.manager_name = manager_name
        self.total_score = total_score
        self.weak_areas = weak_areas or []
        self.created_at = datetime.datetime.now()
        self.start_date = None
        self.end_date = None
        self.status = 'active'
        self.progress = {}
        self.certificate_issued = False
    
    def generate_from_analysis(self, analysis_result, user_id, manager_name):
        """Генерация полного курса обучения на основе анализа"""
        self.user_id = user_id
        self.manager_name = manager_name
        self.total_score = analysis_result.get('total_score', 0)
        self.created_at = datetime.datetime.now()
        self.start_date = datetime.datetime.now()
        
        # Определяем слабые места (оценка ниже 60)
        criteria_scores = analysis_result.get('criteria_scores', {})
        weak_areas_raw = []
        
        for crit_id, score_data in criteria_scores.items():
            score = score_data.get('score', 0)
            if score < 60:
                weak_areas_raw.append({
                    'id': crit_id,
                    'score': score,
                    'required_score': 80,
                    'priority': 'high' if score < 40 else 'medium'
                })
        
        # Сортируем по приоритету
        weak_areas_raw.sort(key=lambda x: (x['score']))
        self.weak_areas = weak_areas_raw[:5]  # Берём топ-5 проблемных зон
        
        # Рассчитываем дату окончания (3 недели на курс)
        self.end_date = self.start_date + datetime.timedelta(days=21)
        
        # Инициализируем прогресс
        for area in self.weak_areas:
            course_data = self.COURSE_STRUCTURE.get(area['id'])
            if course_data:
                for module in course_data['modules']:
                    module_key = f"{area['id']}_{module['title']}"
                    self.progress[module_key] = {
                        'status': 'pending',
                        'completed_at': None,
                        'homework_submitted': False,
                        'homework_score': None,
                        'retake_count': 0
                    }
        
        return self
    
    def to_dict(self):
        """Преобразование курса в словарь для API"""
        return {
            'user_id': self.user_id,
            'manager_name': self.manager_name,
            'total_score': self.total_score,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'status': self.status,
            'weak_areas': self.weak_areas,
            'progress': self.progress,
            'certificate_issued': self.certificate_issued,
            'days_remaining': max(0, (self.end_date - datetime.datetime.now()).days) if self.end_date else 0,
            'total_modules': len(self.progress),
            'completed_modules': sum(1 for p in self.progress.values() if p['status'] == 'completed')
        }
    
    def get_detailed_schedule(self):
        """Получение детального расписания занятий"""
        schedule = []
        current_date = self.start_date or datetime.datetime.now()
        
        for area in self.weak_areas:
            course_data = self.COURSE_STRUCTURE.get(area['id'])
            if not course_data:
                continue
            
            for module in course_data['modules']:
                schedule.append({
                    'criterion_id': area['id'],
                    'criterion_name': course_data['name'],
                    'module_title': module['title'],
                    'duration_hours': module['duration_hours'],
                    'content': module['content'],
                    'deadline_days': module['deadline_days'],
                    'deadline_date': (current_date + datetime.timedelta(days=module['deadline_days'])).isoformat(),
                    'homework': module['homework']
                })
        
        return schedule
    
    def get_certificate_data(self):
        """Данные для сертификата об окончании курса"""
        return {
            'manager_name': self.manager_name,
            'total_score': self.total_score,
            'improvement_points': len(self.weak_areas),
            'completion_date': datetime.datetime.now().isoformat(),
            'total_hours': sum(
                module['duration_hours'] 
                for area in self.weak_areas 
                for module in self.COURSE_STRUCTURE.get(area['id'], {}).get('modules', [])
            ),
            'certificate_id': f"CERT-{self.user_id}-{int(datetime.datetime.now().timestamp())}"
        }


class TrainingPlan:
    """Модель плана обучения (базовая, для совместимости)"""
    def __init__(self, id=None, user_id=None, created_at=None, status='active'):
        self.id = id
        self.user_id = user_id
        self.created_at = created_at or datetime.datetime.now()
        self.status = status
        self.weeks = []
        self.total_score = 0
        self.criteria_scores = {}
    
    def generate_from_analysis(self, analysis_result, user_id):
        """Генерация плана обучения на основе анализа (упрощённая версия)"""
        self.user_id = user_id
        self.criteria_scores = analysis_result.get('criteria_scores', {})
        self.total_score = analysis_result.get('total_score', 0)
        
        # Анализ слабых мест
        weak_areas = []
        medium_areas = []
        strong_areas = []
        
        criteria_names = {
            'greeting': 'Приветствие и представление',
            'client_info': 'Сбор информации о клиенте',
            'communication_style': 'Стиль общения',
            'problem_identification': 'Выявление потребности',
            'offers_promotions': 'Рассказ об акциях',
            'solution_proposal': 'Предложение решения',
            'active_listening': 'Активное слушание',
            'closing_efficiency': 'Эффективность завершения'
        }
        
        for crit_id, score_data in self.criteria_scores.items():
            score = score_data.get('score', 0)
            name = criteria_names.get(crit_id, crit_id)
            if score < 40:
                weak_areas.append({'id': crit_id, 'name': name, 'score': score})
            elif score < 70:
                medium_areas.append({'id': crit_id, 'name': name, 'score': score})
            else:
                strong_areas.append({'id': crit_id, 'name': name, 'score': score})
        
        # Формирование недельных планов
        if weak_areas:
            week1 = {
                'week': 1,
                'title': 'Неделя 1: Интенсивный курс (Критические ошибки)',
                'color': '#f44336',
                'topics': [
                    {
                        'criterion': item['name'],
                        'current_score': item['score'],
                        'target_score': 70,
                        'exercises': self._get_exercises_for_criterion(item['id'])
                    } for item in weak_areas
                ],
                'total_hours': len(weak_areas) * 3,
                'status': 'pending'
            }
            self.weeks.append(week1)
        
        if medium_areas:
            week2 = {
                'week': 2,
                'title': 'Неделя 2: Закрепление и развитие навыков',
                'color': '#ff9800',
                'topics': [
                    {
                        'criterion': item['name'],
                        'current_score': item['score'],
                        'target_score': 85,
                        'exercises': self._get_exercises_for_criterion(item['id'])
                    } for item in medium_areas
                ],
                'total_hours': len(medium_areas) * 2,
                'status': 'pending'
            }
            self.weeks.append(week2)
        
        if strong_areas or not (weak_areas or medium_areas):
            week3 = {
                'week': 3,
                'title': 'Неделя 3: Продвинутый уровень и менторство',
                'color': '#4caf50',
                'topics': [
                    {
                        'criterion': item['name'],
                        'current_score': item['score'],
                        'target_score': 95,
                        'exercises': [
                            'Участие в ролевых играх как наставник',
                            'Разбор сложных кейсов с новыми сотрудниками',
                            'Сертификация и тестирование навыков'
                        ]
                    } for item in (strong_areas if strong_areas else [{'id': 'general', 'name': 'Поддержание высокого уровня', 'score': self.total_score}])
                ],
                'total_hours': 8,
                'status': 'pending'
            }
            self.weeks.append(week3)
        
        return self
    
    def _get_exercises_for_criterion(self, criterion_id):
        """Получение упражнений для конкретного критерия"""
        exercises_map = {
            'greeting': [
                'Прослушивание эталонных приветствий',
                'Отработка стандартного скрипта приветствия',
                'Ролевая игра "Первый контакт с клиентом"'
            ],
            'client_info': [
                'Составление чек-листа сбора информации',
                'Практика активных вопросов',
                'Анализ успешных диалогов коллег'
            ],
            'communication_style': [
                'Тренинг по вежливому общению',
                'Анализ тональности своих разговоров',
                'Практика позитивных формулировок'
            ],
            'problem_identification': [
                'Изучение методики SPIN-продаж',
                'Практика выявления скрытых потребностей',
                'Разбор кейсов с возражениями'
            ],
            'offers_promotions': [
                'Изучение актуального прайс-листа',
                'Отработка презентации спецпредложений',
                'Ролевая игра "Акции и скидки"'
            ],
            'solution_proposal': [
                'Составление шаблонов предложений',
                'Практика завершения сделки',
                'Анализ конверсии своих предложений'
            ],
            'active_listening': [
                'Упражнения на перефразирование',
                'Практика эмпатического слушания',
                'Тренинг "Слышу и понимаю"'
            ],
            'closing_efficiency': [
                'Отработка стандартных фраз завершения',
                'Практика договоренностей о следующих шагах',
                'Анализ завершенных диалогов'
            ]
        }
        return exercises_map.get(criterion_id, ['Индивидуальная работа с наставником', 'Повторение стандартов качества'])
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'status': self.status,
            'total_score': self.total_score,
            'criteria_scores': self.criteria_scores,
            'weeks': self.weeks
        }


class ReportGenerator:
    """Генератор отчётов"""
    
    @staticmethod
    def generate_html_report(analysis_result, user_info=None, training_plan=None, extended_course=None):
        """Генерация HTML отчёта с расширенным курсом"""
        html = f"""
        <!DOCTYPE html>
        <html lang="ru">
        <head>
            <meta charset="UTF-8">
            <title>Отчёт об анализе разговора - COFRESH Voice Analytics</title>
            <style>
                body {{ font-family: 'Segoe UI', Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }}
                .container {{ max-width: 1200px; margin: 0 auto; background: white; border-radius: 15px; box-shadow: 0 5px 20px rgba(0,0,0,0.1); overflow: hidden; }}
                .header {{ background: linear-gradient(135deg, #0a2a4a, #2a7bb0); color: white; padding: 30px; text-align: center; }}
                .header h1 {{ margin: 0; font-size: 28px; }}
                .header p {{ margin: 10px 0 0; opacity: 0.9; }}
                .content {{ padding: 30px; }}
                .score-section {{ text-align: center; padding: 20px; background: #f8f9fa; border-radius: 15px; margin-bottom: 30px; }}
                .score {{ font-size: 64px; font-weight: bold; color: #ff9800; }}
                .grade {{ display: inline-block; padding: 8px 24px; border-radius: 40px; font-weight: bold; margin-top: 10px; }}
                .grade-excellent {{ background: #2e7d32; color: white; }}
                .grade-good {{ background: #2a7bb0; color: white; }}
                .grade-average {{ background: #4a90b0; color: white; }}
                .criteria-grid {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 20px; margin-bottom: 30px; }}
                .criteria-item {{ background: #f8f9fa; border-radius: 12px; padding: 15px; }}
                .criteria-name {{ font-weight: bold; margin-bottom: 10px; }}
                .criteria-score {{ font-size: 24px; font-weight: bold; color: #ff9800; }}
                .progress-bar {{ height: 8px; background: #e0e0e0; border-radius: 4px; overflow: hidden; margin: 10px 0; }}
                .progress-fill {{ height: 100%; border-radius: 4px; transition: width 0.3s; }}
                .transcript {{ background: #f8f9fa; border-radius: 12px; padding: 20px; margin-top: 30px; }}
                .transcript-line {{ padding: 12px; border-left: 4px solid; margin-bottom: 10px; background: white; border-radius: 8px; }}
                .transcript-line.admin {{ border-left-color: #2a7bb0; }}
                .transcript-line.client {{ border-left-color: #4a90b0; }}
                .training-plan {{ background: #e8f5e9; border-radius: 12px; padding: 20px; margin-top: 30px; }}
                .week {{ background: white; border-radius: 10px; padding: 15px; margin-bottom: 15px; }}
                .week-title {{ font-weight: bold; font-size: 18px; margin-bottom: 10px; }}
                .extended-course {{ background: #e3f2fd; border-radius: 12px; padding: 20px; margin-top: 30px; }}
                .module-item {{ background: white; border-radius: 10px; padding: 15px; margin-bottom: 15px; border-left: 4px solid #ff9800; }}
                .module-deadline {{ background: #fff3e0; padding: 5px 10px; border-radius: 20px; font-size: 12px; display: inline-block; }}
                .footer {{ text-align: center; padding: 20px; background: #f8f9fa; color: #666; font-size: 12px; }}
                table {{ width: 100%; border-collapse: collapse; }}
                th, td {{ padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }}
                .homework-box {{ background: #f5f5f5; padding: 10px; border-radius: 8px; margin-top: 10px; font-size: 14px; }}
                @media (max-width: 768px) {{ .criteria-grid {{ grid-template-columns: 1fr; }} }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>COFRESH Voice Analytics Pro</h1>
                    <p>Отчёт об анализе качества телефонного разговора и план обучения</p>
                </div>
                <div class="content">
                    <div class="score-section">
                        <div class="score">{analysis_result.get('total_score', 0)}<span style="font-size: 24px;">/100</span></div>
                        <div class="grade grade-{analysis_result.get('grade_class', '')}">{analysis_result.get('grade', '')}</div>
                        <p>{analysis_result.get('grade_description', '')}</p>
                    </div>
                    
                    <h3>📊 Оценка по критериям</h3>
                    <div class="criteria-grid">
        """
        
        criteria_names = {
            'greeting': '👋 Приветствие и представление',
            'client_info': '📝 Сбор информации',
            'communication_style': '💬 Стиль общения',
            'problem_identification': '🎯 Выявление потребности',
            'offers_promotions': '🏷️ Рассказ об акциях',
            'solution_proposal': '💡 Предложение решения',
            'active_listening': '👂 Активное слушание',
            'closing_efficiency': '✅ Завершение разговора'
        }
        
        for crit_id, name in criteria_names.items():
            score_data = analysis_result.get('criteria_scores', {}).get(crit_id, {'score': 0})
            score = score_data.get('score', 0)
            percentage = (score / 100) * 100
            bar_color = '#2e7d32' if percentage >= 80 else '#ff9800' if percentage >= 60 else '#f44336'
            
            html += f"""
                        <div class="criteria-item">
                            <div class="criteria-name">{name}</div>
                            <div class="criteria-score">{score}/100</div>
                            <div class="progress-bar">
                                <div class="progress-fill" style="width: {percentage}%; background: {bar_color};"></div>
                            </div>
                            <div style="font-size: 12px; color: #666; margin-top: 8px;">
                                Найдено ключевых слов: {score_data.get('keyword_count', 0)}
                            </div>
                        </div>
            """
        
        html += """
                    </div>
                    
                    <h3>📈 Статистика разговора</h3>
                    <table>
        """
        
        html += f"""
                        <tr><th>Параметр</th><th>Значение</th></tr>
                        <tr><td>Длительность</td><td>{analysis_result.get('duration_formatted', '0:00')}</td></tr>
                        <tr><td>Всего слов</td><td>{analysis_result.get('word_count', 0)}</td></tr>
                        <tr><td>Слов администратора</td><td>{analysis_result.get('admin_word_count', 0)} ({analysis_result.get('dialogue_analysis', {}).get('admin_percentage', 0)}%)</td></tr>
                        <tr><td>Слов клиента</td><td>{analysis_result.get('client_word_count', 0)} ({analysis_result.get('dialogue_analysis', {}).get('client_percentage', 0)}%)</td></tr>
                        <tr><td>Количество вопросов</td><td>{analysis_result.get('dialogue_analysis', {}).get('question_count', 0)}</td></tr>
                        <tr><td>Тональность</td><td>{analysis_result.get('sentiment_label', 'Нейтральная')} (балл: {analysis_result.get('sentiment', 50)})</td></tr>
                    </table>
        """
        
        # Расширенный курс обучения
        if extended_course:
            html += f"""
                    <div class="extended-course">
                        <h3>🎓 ПЕРСОНАЛЬНЫЙ КУРС ОБУЧЕНИЯ</h3>
                        <p><strong>Сотрудник:</strong> {extended_course.get('manager_name', 'Не указано')}</p>
                        <p><strong>Дата начала:</strong> {extended_course.get('start_date', '')[:10] if extended_course.get('start_date') else 'Не указана'}</p>
                        <p><strong>Дата окончания курса:</strong> {extended_course.get('end_date', '')[:10] if extended_course.get('end_date') else 'Не указана'}</p>
                        <p><strong>Осталось дней:</strong> {extended_course.get('days_remaining', 0)}</p>
                        <p><strong>Прогресс:</strong> {extended_course.get('completed_modules', 0)}/{extended_course.get('total_modules', 0)} модулей завершено</p>
                        <div class="progress-bar" style="margin: 10px 0;">
                            <div class="progress-fill" style="width: {(extended_course.get('completed_modules', 0) / max(extended_course.get('total_modules', 1), 1) * 100)}%; background: #ff9800;"></div>
                        </div>
            """
            
            # Слабые места и модули для изучения
            weak_areas = extended_course.get('weak_areas', [])
            for area in weak_areas:
                course_data = ExtendedTrainingCourse.COURSE_STRUCTURE.get(area['id'])
                if course_data:
                    html += f"""
                        <div style="margin-top: 20px;">
                            <h4 style="color: #f44336;">⚠️ {course_data['icon']} {course_data['name']} (текущий балл: {area.get('score', 0)}/100, требуется: {area.get('required_score', 80)}/100)</h4>
                    """
                    for module in course_data['modules']:
                        module_key = f"{area['id']}_{module['title']}"
                        progress_status = extended_course.get('progress', {}).get(module_key, {}).get('status', 'pending')
                        status_icon = '✅' if progress_status == 'completed' else '🟡' if progress_status == 'in_progress' else '❌'
                        html += f"""
                            <div class="module-item">
                                <div style="display: flex; justify-content: space-between; align-items: center;">
                                    <strong>{status_icon} {module['title']}</strong>
                                    <span class="module-deadline">⏰ Дедлайн: {module['deadline_days']} дня</span>
                                </div>
                                <div style="margin-top: 10px;">
                                    <strong>Содержание модуля:</strong>
                                    <ul>
                                        {' '.join([f'<li>{item}</li>' for item in module['content']])}
                                    </ul>
                                </div>
                                <div class="homework-box">
                                    <strong>📝 Домашнее задание:</strong> {module['homework']}
                                </div>
                            </div>
                        """
                    html += "</div>"
            
            # Тесты для проверки знаний
            html += """
                    <div style="margin-top: 30px; background: #fff8e1; border-radius: 12px; padding: 20px;">
                        <h4>📋 ИТОГОВАЯ АТТЕСТАЦИЯ</h4>
                        <p>После завершения всех модулей необходимо сдать итоговый тест и выполнить практическое задание.</p>
                        <ul>
                            <li>Тестирование по всем критериям (30 вопросов)</li>
                            <li>Практический экзамен: 3 пробных звонка с наставником</li>
                            <li>Анализ результатов: средний балл должен быть не менее 85/100</li>
                        </ul>
                    </div>
            """
            
            if extended_course.get('certificate_issued'):
                cert_data = extended_course.get('certificate_data', {})
                html += f"""
                    <div style="margin-top: 20px; background: #e8f5e9; border-radius: 12px; padding: 20px; text-align: center;">
                        <h4>🏆 СЕРТИФИКАТ ОБ ОКОНЧАНИИ КУРСА</h4>
                        <p><strong>№{cert_data.get('certificate_id', '')}</strong></p>
                        <p>Выдан {cert_data.get('manager_name', '')} за успешное прохождение курса</p>
                        <p>Дата выдачи: {cert_data.get('completion_date', '')[:10] if cert_data.get('completion_date') else ''}</p>
                    </div>
                """
            
            html += "</div>"
        
        # Базовый план обучения
        if training_plan:
            html += f"""
                    <div class="training-plan">
                        <h3>📚 Базовый план обучения</h3>
                        <p>Итоговый балл: {training_plan.get('total_score', 0)}/100</p>
            """
            for week in training_plan.get('weeks', []):
                html += f"""
                        <div class="week">
                            <div class="week-title" style="color: {week.get('color', '#333')};">📅 {week.get('title', '')}</div>
                            <p><strong>Темы для изучения:</strong></p>
                            <ul>
                """
                for topic in week.get('topics', []):
                    html += f"<li><strong>{topic.get('criterion', '')}</strong> (текущий балл: {topic.get('current_score', 0)}/100 → цель: {topic.get('target_score', 0)}/100)"
                    if topic.get('exercises'):
                        html += "<ul>"
                        for ex in topic.get('exercises', []):
                            html += f"<li>{ex}</li>"
                        html += "</ul>"
                    html += "</li>"
                html += f"""
                            </ul>
                            <p>⏱️ Рекомендуемое время: {week.get('total_hours', 0)} часов</p>
                        </div>
                """
            html += "</div>"
        
        # Расшифровка диалога
        html += f"""
                    <div class="transcript">
                        <h3>💬 Расшифровка диалога</h3>
        """
        
        for segment in analysis_result.get('segments', []):
            speaker_name = 'Администратор' if segment.get('speaker') == 'admin' else 'Клиент'
            speaker_icon = '👨‍💼' if segment.get('speaker') == 'admin' else '👤'
            html += f"""
                        <div class="transcript-line {segment.get('speaker', 'client')}">
                            <strong>{speaker_icon} {speaker_name}</strong> <span style="color: #999;">⏱️ {segment.get('timestamp', '00:00')}</span>
                            <div style="margin-top: 8px;">{segment.get('text', '')}</div>
                        </div>
            """
        
        html += f"""
                    </div>
                </div>
                <div class="footer">
                    <p>COFRESH Voice Analytics Pro · Отчёт сгенерирован {datetime.datetime.now().strftime('%d.%m.%Y %H:%M')}</p>
                    <p>АВТО С ЗАБОТОЙ · ТОП-3 дилер РФ</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html
    
    @staticmethod
    def generate_pdf_report(analysis_result, user_info=None, training_plan=None, extended_course=None):
        """Генерация PDF отчёта"""
        html = ReportGenerator.generate_html_report(analysis_result, user_info, training_plan, extended_course)
        import io
        from weasyprint import HTML
        
        pdf_file = io.BytesIO()
        HTML(string=html).write_pdf(pdf_file)
        pdf_file.seek(0)
        return pdf_file.getvalue()
    
    @staticmethod
    def generate_excel_report(analysis_result, training_plan=None, extended_course=None):
        """Генерация Excel отчёта"""
        import io
        import pandas as pd
        
        output = io.BytesIO()
        
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            # Лист 1: Общая информация
            summary_data = {
                'Показатель': ['Дата анализа', 'Длительность', 'Общий балл', 'Оценка', 'Всего слов', 
                              'Слов администратора', 'Слов клиента', 'Тональность', 'Точность распознавания'],
                'Значение': [datetime.datetime.now().strftime('%d.%m.%Y %H:%M'),
                           analysis_result.get('duration_formatted', '0:00'),
                           analysis_result.get('total_score', 0),
                           analysis_result.get('grade', ''),
                           analysis_result.get('word_count', 0),
                           analysis_result.get('admin_word_count', 0),
                           analysis_result.get('client_word_count', 0),
                           analysis_result.get('sentiment_label', 'Нейтральная'),
                           analysis_result.get('confidence_percent', '0%')]
            }
            df_summary = pd.DataFrame(summary_data)
            df_summary.to_excel(writer, sheet_name='Общая информация', index=False)
            
            # Лист 2: Оценки критериев
            criteria_data = []
            criteria_names = {
                'greeting': 'Приветствие и представление',
                'client_info': 'Сбор информации',
                'communication_style': 'Стиль общения',
                'problem_identification': 'Выявление потребности',
                'offers_promotions': 'Рассказ об акциях',
                'solution_proposal': 'Предложение решения',
                'active_listening': 'Активное слушание',
                'closing_efficiency': 'Завершение разговора'
            }
            for crit_id, name in criteria_names.items():
                score_data = analysis_result.get('criteria_scores', {}).get(crit_id, {'score': 0, 'keyword_count': 0})
                criteria_data.append({
                    'Критерий': name,
                    'Балл': score_data.get('score', 0),
                    'Найдено ключевых слов': score_data.get('keyword_count', 0),
                    'Ключевые слова': ', '.join(score_data.get('found_keywords', [])) if score_data.get('found_keywords') else '-'
                })
            df_criteria = pd.DataFrame(criteria_data)
            df_criteria.to_excel(writer, sheet_name='Оценки критериев', index=False)
            
            # Лист 3: Расширенный курс обучения
            if extended_course:
                course_data = []
                for area in extended_course.get('weak_areas', []):
                    course_info = ExtendedTrainingCourse.COURSE_STRUCTURE.get(area['id'], {})
                    for module in course_info.get('modules', []):
                        course_data.append({
                            'Критерий': course_info.get('name', area['id']),
                            'Текущий балл': area.get('score', 0),
                            'Целевой балл': area.get('required_score', 80),
                            'Модуль': module['title'],
                            'Длительность (часов)': module['duration_hours'],
                            'Дедлайн (дней)': module['deadline_days'],
                            'Домашнее задание': module['homework'],
                            'Статус': extended_course.get('progress', {}).get(f"{area['id']}_{module['title']}", {}).get('status', 'pending')
                        })
                if course_data:
                    df_course = pd.DataFrame(course_data)
                    df_course.to_excel(writer, sheet_name='План обучения', index=False)
            
            # Лист 4: Расшифровка диалога
            transcript_data = []
            for idx, segment in enumerate(analysis_result.get('segments', [])):
                transcript_data.append({
                    '№': idx + 1,
                    'Говорящий': 'Администратор' if segment.get('speaker') == 'admin' else 'Клиент',
                    'Время': segment.get('timestamp', '00:00'),
                    'Текст': segment.get('text', ''),
                    'Точность': f"{int(segment.get('confidence', 0.8) * 100)}%"
                })
            df_transcript = pd.DataFrame(transcript_data)
            df_transcript.to_excel(writer, sheet_name='Расшифровка диалога', index=False)
        
        output.seek(0)
        return output.getvalue()
    
    @staticmethod
    def generate_word_report(analysis_result, user_info=None, training_plan=None, extended_course=None):
        """Генерация Word отчёта"""
        from docx import Document
        from docx.shared import Pt
        from docx.enum.text import WD_ALIGN_PARAGRAPH
        
        doc = Document()
        
        # Заголовок
        title = doc.add_heading('COFRESH Voice Analytics Pro', 0)
        title.alignment = WD_ALIGN_PARAGRAPH.CENTER
        doc.add_heading('Отчёт об анализе качества телефонного разговора', level=1)
        
        # Общая информация
        doc.add_heading('1. Общая информация', level=2)
        info_table = doc.add_table(rows=8, cols=2)
        info_table.style = 'Table Grid'
        info_data = [
            ('Дата анализа', datetime.datetime.now().strftime('%d.%m.%Y %H:%M')),
            ('Длительность', analysis_result.get('duration_formatted', '0:00')),
            ('Общий балл', f"{analysis_result.get('total_score', 0)}/100"),
            ('Оценка', analysis_result.get('grade', '')),
            ('Всего слов', str(analysis_result.get('word_count', 0))),
            ('Слов администратора', str(analysis_result.get('admin_word_count', 0))),
            ('Слов клиента', str(analysis_result.get('client_word_count', 0))),
            ('Тональность', analysis_result.get('sentiment_label', 'Нейтральная'))
        ]
        for i, (key, value) in enumerate(info_data):
            info_table.cell(i, 0).text = key
            info_table.cell(i, 1).text = value
        
        # Оценки критериев
        doc.add_heading('2. Оценка по критериям', level=2)
        criteria_names = {
            'greeting': 'Приветствие и представление',
            'client_info': 'Сбор информации',
            'communication_style': 'Стиль общения',
            'problem_identification': 'Выявление потребности',
            'offers_promotions': 'Рассказ об акциях',
            'solution_proposal': 'Предложение решения',
            'active_listening': 'Активное слушание',
            'closing_efficiency': 'Завершение разговора'
        }
        
        criteria_table = doc.add_table(rows=len(criteria_names) + 1, cols=3)
        criteria_table.style = 'Table Grid'
        headers = criteria_table.rows[0].cells
        headers[0].text = 'Критерий'
        headers[1].text = 'Балл'
        headers[2].text = 'Ключевые слова'
        
        for i, (crit_id, name) in enumerate(criteria_names.items()):
            score_data = analysis_result.get('criteria_scores', {}).get(crit_id, {'score': 0, 'found_keywords': []})
            row = criteria_table.rows[i + 1].cells
            row[0].text = name
            row[1].text = f"{score_data.get('score', 0)}/100"
            row[2].text = ', '.join(score_data.get('found_keywords', [])) if score_data.get('found_keywords') else '-'
        
        # Расширенный курс обучения
        if extended_course:
            doc.add_heading('3. Персональный курс обучения', level=2)
            doc.add_paragraph(f"Сотрудник: {extended_course.get('manager_name', 'Не указано')}")
            doc.add_paragraph(f"Дата начала курса: {extended_course.get('start_date', '')[:10] if extended_course.get('start_date') else 'Не указана'}")
            doc.add_paragraph(f"Дата окончания: {extended_course.get('end_date', '')[:10] if extended_course.get('end_date') else 'Не указана'}")
            doc.add_paragraph(f"Прогресс: {extended_course.get('completed_modules', 0)}/{extended_course.get('total_modules', 0)} модулей")
            
            for area in extended_course.get('weak_areas', []):
                course_data = ExtendedTrainingCourse.COURSE_STRUCTURE.get(area['id'])
                if course_data:
                    doc.add_heading(f"⚠️ {course_data['name']} (балл: {area.get('score', 0)}/100)", level=3)
                    for module in course_data['modules']:
                        doc.add_heading(f"Модуль: {module['title']}", level=4)
                        doc.add_paragraph(f"Длительность: {module['duration_hours']} часов")
                        doc.add_paragraph(f"Дедлайн: {module['deadline_days']} дня")
                        doc.add_paragraph("Содержание:", style='List Bullet')
                        for content in module['content']:
                            doc.add_paragraph(content, style='List Bullet 2')
                        doc.add_paragraph(f"Домашнее задание: {module['homework']}")
        
        # Базовый план
        if training_plan:
            doc.add_heading('4. Базовый план обучения', level=2)
            for week in training_plan.get('weeks', []):
                doc.add_heading(week.get('title', ''), level=3)
                for topic in week.get('topics', []):
                    p = doc.add_paragraph()
                    p.add_run(f"• {topic.get('criterion', '')}").bold = True
                    p.add_run(f" (текущий балл: {topic.get('current_score', 0)}/100 → цель: {topic.get('target_score', 0)}/100)")
                    if topic.get('exercises'):
                        doc.add_paragraph('Упражнения:', style='List Bullet')
                        for ex in topic.get('exercises', []):
                            doc.add_paragraph(ex, style='List Bullet 2')
        
        # Расшифровка
        doc.add_heading('5. Расшифровка диалога', level=2)
        for segment in analysis_result.get('segments', []):
            speaker = 'Администратор' if segment.get('speaker') == 'admin' else 'Клиент'
            p = doc.add_paragraph()
            p.add_run(f"[{segment.get('timestamp', '00:00')}] {speaker}: ").bold = True
            p.add_run(segment.get('text', ''))
        
        # Сохранение
        import io
        buffer = io.BytesIO()
        doc.save(buffer)
        buffer.seek(0)
        return buffer.getvalue()
