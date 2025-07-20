from flask import Flask, request, render_template, make_response, abort
import subprocess
import base64

FLAG = "4TH3N3{**redacted**}"

app = Flask(__name__)

user = {
    "guest": "guest",
    "user":"user@!"
}

banlist = ["'","\"","\\","@","-","?",".","%","[","]","o"," ","c","s","p","h","s","t","u","x",":"]

def str_xor_bytes(bytes_data, key_bytes):
    return bytes(b1 ^ b2 for b1, b2 in zip(bytes_data, key_bytes * (len(bytes_data) // len(key_bytes)) + key_bytes[:len(bytes_data) % len(key_bytes)]))

def setcookie(id_str):
    b_id = id_str.encode('utf-8')
    
    step1 = str_xor_bytes(b_id, "4THêNē".encode('utf-8'))
    step2 = bytes((byte - 142) % 256 for byte in step1)
    step3 = str_xor_bytes(step2, "4EGIS".encode('utf-8'))
    
    return base64.b64encode(step3).decode('utf-8')

def readcookie(cookie_str):
    step3 = base64.b64decode(cookie_str)
    step2 = str_xor_bytes(step3, "4EGIS".encode('utf-8'))
    step1 = bytes((byte + 142) % 256 for byte in step2)
    b_id = str_xor_bytes(step1, "4THêNē".encode('utf-8'))

    return b_id.decode('utf-8', errors='ignore')

@app.route("/")  
def hello():
    user_id = request.cookies.get("id")

    if user_id:
        id = readcookie(user_id)
        return f"HI {id}"
    
    return "HI"

@app.route("/logintest", methods=["GET", "POST"])  
def test():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if username in user and user[username] == password:
            return "login success!"
        else:
            errorcode = setcookie(username)
            return f"ERROR : errorcode {errorcode}"

    return render_template("logintest.html")

@app.route("/login", methods=["GET", "POST"])  
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if username in user and user[username] == password:
            response = make_response(f"""
                <script>
                    alert("login success!");
                    document.cookie = "id={setcookie(username)}";
                    window.location.href = "/";
                </script>
            """)
            return response
        else:
            return """
                <script>
                    alert("login fail!");
                    window.location.href = "/login";
                </script>
            """

    return render_template("login.html")

@app.route("/admin")
def curl():
    user_id = request.cookies.get("id")
    errorcode = request.cookies.get("errorcode")
    
    if errorcode:
        return f"ERROR : {errorcode}"

    if not user_id or readcookie(user_id) != "admin":
        return "only admin!", 403
    
    url = request.args.get('url')
    if not url:
        return "admin page", 400
    
    if any(bad in url.lower() for bad in banlist):
        return "blocked", 403

    try:
        result = subprocess.check_output(
            ['curl', url],
            stderr=subprocess.STDOUT,
            timeout=5
        )
        return result.decode('utf-8')
    except subprocess.CalledProcessError:
        return f"ERROR", 500
    except subprocess.TimeoutExpired:
        return "TIMEOUT", 504

@app.route("/flag")
def flag():
    if request.remote_addr not in ("127.0.0.1"):
        abort(403) 
    return f"{FLAG}"

if __name__ == '__main__': 
    app.run(host="0.0.0.0", port=80)