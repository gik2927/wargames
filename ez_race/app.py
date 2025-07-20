from flask import Flask, request
import random
import time

app = Flask(__name__)
FLAG = "4TH3N3{**redacted**}"
getflag = 0

key = random.randint(1, 100)

@app.route('/')
def home():
    return "3초 안에 키를 찾을 수 있나요?"

@app.route('/race')
def race():
    global getflag, key

    user_input_str = request.args.get('user')
    if user_input_str is None:
        return "Please use user parameter"

    try:
        userinput = int(user_input_str)
    except ValueError:
        return "ERROR"

    if userinput == key:
        getflag = 1
        return "WOW"
    else:
        time.sleep(3)
        key = random.randint(1, 100)
        return "NOPE"

@app.route('/flag')
def flag():
    global getflag   
    if getflag == 1:
        getflag = 0
        return f"FLAG IS {FLAG}"
    else:
        return "NOPE!!"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, threaded=True)