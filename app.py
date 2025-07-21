from flask import Flask

app = Flask(__name__)

@app.route('/test')
def home():
    return 'Test, let's see if it works.'

if __name__ == '__main__':
    app.run()
