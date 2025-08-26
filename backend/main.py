from app import create_app
from app.config import PORT

app = create_app()

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False, port=PORT)
