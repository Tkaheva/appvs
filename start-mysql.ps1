# start-mysql.ps1
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Запуск MySQL контейнера для AutoSalon Analytics" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# Остановка и удаление старого контейнера
docker stop mysql-db 2>$null
docker rm mysql-db 2>$null

# Запуск нового контейнера MySQL
Write-Host "Запуск MySQL 8.0 контейнера..." -ForegroundColor Green
docker run -d --name mysql-db -e MYSQL_ROOT_PASSWORD=rootpassword -e MYSQL_DATABASE=autosalon_analytics -p 3306:3306 mysql:8.0

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ MySQL контейнер успешно запущен!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Подключение к MySQL:" -ForegroundColor Cyan
    Write-Host "  docker exec -it mysql-db mysql -u root -p" -ForegroundColor White
    Write-Host "  Пароль: rootpassword" -ForegroundColor White
    
    # Ожидание запуска
    Start-Sleep -Seconds 10
    
    # Создание таблиц из существующего файла
    Write-Host "`nСоздание таблиц..." -ForegroundColor Green
    Get-Content database_schema.sql | docker exec -i mysql-db mysql -u root -prootpassword autosalon_analytics
    
    Write-Host "✅ База данных готова!" -ForegroundColor Green
    Write-Host ""
    Write-Host "🌐 Теперь запустите основное приложение:" -ForegroundColor Yellow
    Write-Host "  docker run -d --name autosalon-analytics -p 8080:8080 -v ${PWD}/uploads:/app/uploads -v ${PWD}/app:/app/app -v ${PWD}/templates:/app/templates -v ${PWD}/static:/app/static -e FLASK_ENV=development autosalon-analytics" -ForegroundColor White
}
