import flask

app = flask.Flask(__name__, static_url_path="/static")

@app.route('/')
def main():
    return flask.render_template('index.html')

if __name__ == '__main__':
    app.run()
