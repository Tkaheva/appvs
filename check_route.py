from app import create_app
app = create_app()
print("Проверка маршрута /api/recent-analyses:")
for rule in app.url_map.iter_rules():
    if 'recent' in rule.rule:
        print(f"  {rule.rule} -> {rule.endpoint}")
