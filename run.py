if __name__ == "__main__":
    port = int(os.environ.get('PORT', 8080))  # Измените 7000 на 8080
    app.run(host='0.0.0.0', port=port, debug=True)