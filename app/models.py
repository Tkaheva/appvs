# Модели для работы с базой данных (используются для SQLAlchemy)
# Если не используете SQLAlchemy, этот файл опционален

class User:
    """Модель пользователя"""
    def __init__(self, id=None, username=None, email=None, full_name=None, role='analyst'):
        self.id = id
        self.username = username
        self.email = email
        self.full_name = full_name
        self.role = role
        self.is_active = True

class UploadedFile:
    """Модель загруженного файла"""
    def __init__(self, file_id=None, original_filename=None, file_size=None, file_format=None):
        self.file_id = file_id
        self.original_filename = original_filename
        self.file_size = file_size
        self.file_format = file_format
        self.status = 'uploaded'

class AnalysisResult:
    """Модель результата анализа"""
    def __init__(self, file_id=None, total_score=None, grade=None):
        self.file_id = file_id
        self.total_score = total_score
        self.grade = grade

class CriteriaScore:
    """Модель оценки критерия"""
    def __init__(self, analysis_id=None, criterion_id=None, score=None):
        self.analysis_id = analysis_id
        self.criterion_id = criterion_id
        self.score = score

class DialogueSegment:
    """Модель сегмента диалога"""
    def __init__(self, analysis_id=None, segment_index=None, speaker=None, text=None):
        self.analysis_id = analysis_id
        self.segment_index = segment_index
        self.speaker = speaker
        self.text = text
