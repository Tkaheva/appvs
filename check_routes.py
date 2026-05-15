from app import create_app
app = create_app()
print("Зарегистрированные маршруты:")
for rule in app.url_map.iter_rules():
    print(f"  {rule.endpoint}: {rule.rule}")
