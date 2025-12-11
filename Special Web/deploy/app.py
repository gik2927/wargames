from flask import Flask, request, make_response, render_template

app = Flask(__name__)

@app.route('/')
def index():
    user_membership = request.cookies.get('membership', 'guest')

    response = make_response(render_template('index.html', membership=user_membership))

    if 'membership' not in request.cookies:
        response.set_cookie('membership', 'guest')

    return response

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000,debug=False)