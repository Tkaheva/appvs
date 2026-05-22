import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.reports import reports_bp

app = create_app()

# Регистрация blueprints для отчётов
app.register_blueprint(reports_bp)

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 7000))
    print("\n" + "="*50)
    print("🚗 COFRESH Voice Analytics Pro v3.0")
    print("="*50)
    print(f"🌐 Сервер запущен: http://localhost:{port}")
    print("\n📋 Учётные записи:")
    print("   👑 admin / admin123 (полный доступ)")
    print("   👔 supervisor / super123 (доступ к команде)")
    print("   👨‍💼 manager / manager123 (только свои данные)")
    print("="*50 + "\n")
    app.run(host='0.0.0.0', port=port, debug=True)
