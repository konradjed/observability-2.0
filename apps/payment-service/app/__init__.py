if __name__ == "__main__":
    # allow `python -m app.main` or `flask run` to work
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 8000)))