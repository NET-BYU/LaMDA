from flask import Flask, render_template
app = Flask(__name__)

@app.route("/", methods=['POST', 'GET'])
def deviceLookup():
    return render_template("register.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0.", port=1995, ssl_context=('cert.pem', 'key.pem'), debug=True)