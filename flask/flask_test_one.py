from flask import Flask

app = Flask(__name__)


# @app.route("/<name>")
# def name(name):
#     return "Hello {}!".format(name)

# @app.route("/")
# def helloworld():
#     return "Hello World!"

@app.route("/")
@app.route("/<name>")
def test(name=None):
    if name == None:
        return "Hello World!"
    else:
        return "Hello {}!".format(name)


if __name__ == "__main__":
    app.run(port=4999, debug=True)
