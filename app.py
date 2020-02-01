from flask import Flask, render_template, request, url_for, redirect


app = Flask(__name__)


comments = []


@app.route('/', methods=["GET", "POST"])
def render_template1():
    if request.method == "GET":
        return render_template("template1.html", comments=comments)

    comments.append(request.form["contents"])
    return redirect(url_for('render_template1'))


if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True)
