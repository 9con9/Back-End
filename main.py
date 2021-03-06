import flask
import dangn
import naver
import bunjang
import dangn_category
import naver_category
import bunjang_category
from flask import Flask

app = Flask(__name__)
categoly = ["디지털기기", "가구/인테리어", "유아용품", "스포츠/레저", "의류", "도서/티켓/문구", "악기", "반려동물", "미용", "콘솔게임"]


@app.route('/search', methods=['GET'])
def startParsing():
    keywords = flask.request.args['value']
    keyword = str(keywords)
    print(keyword)

    ###
    spl = keyword.split()
    list_spl = [k for k in spl]
    naver_keyword_list = list_spl[1:]
    naver_keyword = " ".join(naver_keyword_list)
    print(naver_keyword)
    ###

    for check in categoly:
        if keyword == check:
            dangn_category.get_dangn(keyword)
            naver_category.get_naver(keyword)
            bunjang_category.get_bunjang(keyword)
            break
    else:
        dangn.get_dangn(keyword)
        naver.get_naver(naver_keyword)
        bunjang.get_bunjang(keyword)
    return "success"

if __name__ == '__main__':
    app.run(debug=True)

