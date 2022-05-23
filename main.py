import flask
import dangn
import naver
import bunjang
from flask import Flask

app = Flask(__name__)

@app.route('/search', methods=['GET'])
def startParsing():
    keywords = flask.request.args['value']
    keyword = str(keywords)
    print(keyword)
    dangn.get_dangn(keyword)
    naver.get_naver(keyword)
    bunjang.get_bunjang(keyword)
    return "success"

if __name__ == '__main__':
    app.run(debug=True)