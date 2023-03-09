from flask import Flask

app = Flask(__name__)

#Application Endpoint
application = app

@app.route('/')
def home():
    return "Hello there :)"

if __name__ == "__main__":
    app.run()