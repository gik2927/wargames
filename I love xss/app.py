from flask import Flask, request
from selenium.webdriver.chrome.service import Service
from selenium import webdriver
import time
from sanitizer import sanitize_input

FLAG = "4TH3N3{**redacted**}"
banlist = ["`","'","alert(","fetch(","replace(","[","]","javascript","@","!","%","location","href","window","eval"]

app = Flask(__name__)

def read_url(url):
    driver = None
    try:
        service = Service(executable_path="/usr/local/bin/chromedriver")
        options = webdriver.ChromeOptions()
        for opt in [
            "headless",
            "window-size=1920x1080",
            "disable-gpu",
            "no-sandbox",
            "disable-dev-shm-usage",
        ]:
            options.add_argument(opt)
        driver = webdriver.Chrome(service=service, options=options)
        driver.implicitly_wait(3)
        driver.set_page_load_timeout(3)
        driver.get("http://127.0.0.1:5000/")
        driver.add_cookie({'name':'flag','value':FLAG, 'domain':'127.0.0.1'})
        driver.get(url)
        time.sleep(1)
    except Exception as e:
        if driver:
            driver.quit()
        return False
    if driver:
        driver.quit()
    return True

@app.route('/')
def home():
    return "I LOVE XSS!"

@app.route('/test', methods=['GET'])
def test():
    payload = request.args.get('payload')
    if payload is None:
        return "show your payload!"
    
    payload = payload.lower()

    if any(banned in payload for banned in banlist):
        payload = "Nope!"

    input = sanitize_input(payload)

    return f"{input}"

@app.route('/flag')
def report():
    uanswer = request.args.get('answer')
    result = read_url(f'http://127.0.0.1:5000/test?payload={uanswer}')
    message = "Success" if result else "Fail"
    return message

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)