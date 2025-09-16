from flask import Flask

app = Flask(__name__)

@app.route('/')
def index():
    return '<h1>Chessaroo</h1><p>Multiplayer chess application coming soon!</p>'

if __name__ == '__main__':
    import os
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=False)