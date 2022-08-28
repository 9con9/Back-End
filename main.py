import flask
# import dangn
# import naver
import bunjang
import dangn_naver_chart
# import dangn_category
# import naver_category
# import bunjang_category
import numpy as np
import pandas as pd
from flask import Flask 
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
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
            # dangn_category.get_dangn(keyword)
            # naver_category.get_naver(keyword)
            # bunjang_category.get_bunjang(keyword)
            break
    else:
        # dangn.get_dangn(keyword)
        # naver.get_naver(naver_keyword)
        result = bunjang.get_bunjang(keyword)
        result_list = []
        for i in result:
            results = {"index":i[0], "platform":i[1], "name":i[2], "time":i[3], "place":i[4],
                          "price":i[5], "link":i[6], "img_link":i[7], "outlier":i[8]}
            result_list.append(results)
    return result_list

@app.route('/chart', methods=['GET'])
def startParsing_chart():
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
            # dangn_category.get_dangn(keyword)
            # naver_category.get_naver(keyword)
            # bunjang_category.get_bunjang(keyword)
            break
    else:
        # dangn.get_dangn(keyword)
        # naver.get_naver(naver_keyword)
        result = dangn_naver_chart.get_data(keyword)
        result_np = np.array(result)
        result_df = pd.DataFrame(result_np)
        result_df.columns = ['index', 'platform', 'name', 'time', 'place', 'price', 'link', 'img_link', 'outlier', 'keyword']
        # print(result_df.head())
        df = result_df.groupby('time')['price'].median()
        df = df.astype({'price':'int64'})
        list_col2 = df.drop(columns= ['time', 'price'])
        list_col2 = list_col2.to_dict()
        
        
        # result_list = []
        # for i in result:
        #     results = {"index":i[0], "platform":i[1], "name":i[2], "time":i[3], "place":i[4],
        #                   "price":i[5], "link":i[6], "img_link":i[7], "outlier":i[8]}
        #     result_list.append(results)
    return list_col2

if __name__ == '__main__':
    app.run(debug=True)

