import flask
import numpy as np
import pandas as pd
from flask import Flask 
from flask_cors import CORS
import time
import firebase_test
from firebase_admin import db
from firebase_admin import credentials
from firebase_admin import firestore
import firebase_admin
import firebase_category

cred = credentials.Certificate("./test-3ab4e-firebase-adminsdk-pof1a-0c12bc8c6c.json")
firebase_admin.initialize_app(cred)
db = firestore.client()
app = Flask(__name__)
CORS(app)
categoly = ["디지털기기", "가구/인테리어", "유아용품", "스포츠/레저", "의류", "도서/티켓/문구", "반려동물", "미용", "콘솔게임"]


@app.route('/search', methods=['GET'])
def startParsing():
    start = time.time()  # 시작 시간 저장

    keywords = flask.request.args['value']
    keyword = str(keywords)

    for check in categoly:
        if keyword == check:
            parsing_list = []
            result_list = []
            # result_dangn = dangn_category.get_dangn(keyword)
            # result_bunjang = bunjang_category.get_bunjang(keyword)
            # result_joongna = joongna_category.get_joongna(keyword)
            all = firebase_category.shut(keyword,db)
            for i in range(len(all)):
                all[i][5] = format(int(all[i][5]), ',')
            all = np.array(all)
            all = pd.DataFrame(all)
            try:
                second = all[all[3].str.contains('초')]
                second[3] = second[3].replace(r'[^0-9]', '', regex=True)
                second[3] = pd.to_numeric(second[3])
                second.sort_values(by=[3], ascending=True, inplace=True)
                second[3] = second[3].map('{}초 전'.format)
                second = second.to_numpy()

                minute = all[all[3].str.contains('분')]
                minute[3] = minute[3].replace(r'[^0-9]', '', regex=True)
                minute[3] = pd.to_numeric(minute[3])
                minute.sort_values(by=[3], ascending=True, inplace=True)
                minute[3] = minute[3].map('{}분 전'.format)
                minute = minute.to_numpy()

                hour = all[all[3].str.contains('시간')]
                hour[3] = hour[3].replace(r'[^0-9]', '', regex=True)
                hour[3] = pd.to_numeric(hour[3])
                hour.sort_values(by=[3], ascending=True, inplace=True)
                hour[3] = hour[3].map('{}시간 전'.format)
                hour = hour.to_numpy()

                day = all[all[3].str.contains('일')]
                day[3] = day[3].replace(r'[^0-9]', '', regex=True)
                day[3] = pd.to_numeric(day[3])
                day.sort_values(by=[3], ascending=True, inplace=True)
                day[3] = day[3].map('{}일 전'.format)
                day = day.to_numpy()

                month = all[all[3].str.contains('달')]
                month[3] = month[3].replace(r'[^0-9]', '', regex=True)
                month[3] = pd.to_numeric(month[3])
                month.sort_values(by=[3], ascending=True, inplace=True)
                month[3] = month[3].map('{}달 전'.format)
                month = month.to_numpy()

                all = np.concatenate((second, minute, hour, day, month))
                parsing_list = list(all)

                for parsing in parsing_list:
                    results = {"index": parsing[0], "platform": parsing[1], "name": parsing[2], "time": parsing[3], "place": parsing[4], "price": parsing[5], "link": parsing[6], "img_link": parsing[7]}
                    result_list.append(results)
                break
            except:
                print("category main except")
    else:
        # cred = credentials.Certificate("../../con-635db-firebase-adminsdk-ki86d-a3e7d8b4ac.json")
        # firebase_admin.initialize_app(cred)
        # db = firestore.client()
        parsing_list = []
        result_list = []
        # result_dangn = dangn_category.get_dangn(keyword)
        # result_bunjang = bunjang_category.get_bunjang(keyword)
        # result_joongna = joongna_category.get_joongna(keyword)
        all = firebase_test.shut(keyword,db)
        for i in range(len(all)):
            all[i][5] = format(int(all[i][5]), ',')
        all = np.array(all)
        all = pd.DataFrame(all)

        try:
            minute = all[all[3].str.contains('분')]
            minute[3] = minute[3].replace(r'[^0-9]', '', regex=True)
            minute[3] = pd.to_numeric(minute[3])
            minute.sort_values(by=[3], ascending=True, inplace=True)
            minute[3] = minute[3].map('{}분 전'.format)
            minute = minute.to_numpy()

            hour = all[all[3].str.contains('시간')]
            hour[3] = hour[3].replace(r'[^0-9]', '', regex=True)
            hour[3] = pd.to_numeric(hour[3])
            hour.sort_values(by=[3], ascending=True, inplace=True)
            hour[3] = hour[3].map('{}시간 전'.format)
            hour = hour.to_numpy()

            day = all[all[3].str.contains('일')]
            day[3] = day[3].replace(r'[^0-9]', '', regex=True)
            day[3] = pd.to_numeric(day[3])
            day.sort_values(by=[3], ascending=True, inplace=True)
            day[3] = day[3].map('{}일 전'.format)
            day = day.to_numpy()

            month = all[all[3].str.contains('달')]
            month[3] = month[3].replace(r'[^0-9]', '', regex=True)
            month[3] = pd.to_numeric(month[3])
            month.sort_values(by=[3], ascending=True, inplace=True)
            month[3] = month[3].map('{}달 전'.format)
            month = month.to_numpy()

            all = np.concatenate((minute, hour, day, month))
            parsing_list = list(all)

            for parsing in parsing_list:
                results = {"index": parsing[0], "platform": parsing[1], "name": parsing[2], "time": parsing[3],
                           "place": parsing[4],
                           "price": parsing[5], "link": parsing[6], "img_link": parsing[7], "outlier": parsing[8]}
                result_list.append(results)
        except:
            print("search main except")
    try:
        print("time :", time.time() - start)  # 현재시각 - 시작시간 = 실행 시간
        return str(result_list)
    except:
        return None


@app.route('/chart', methods=['GET'])
def startParsing_chart():
    start = time.time()  # 시작 시간 저장

    keywords = flask.request.args['value']
    keyword = str(keywords)

    ###
    spl = keyword.split()
    list_spl = [k for k in spl]
    naver_keyword_list = list_spl[1:]
    naver_keyword = " ".join(naver_keyword_list)
    ###

    chart_result = []
    result_dict = {}

    # results = dangn_naver_chart.get_data(keyword)
    results = firebase_test.shut_chart(keyword,db)

    # for result in results:
    try:
        result_np = np.array(results)
        result_df = pd.DataFrame(result_np)
        result_df.columns = ['index', 'platform', 'name', 'time', 'place', 'price', 'link', 'img_link', 'outlier']
        result_group_df = result_df.groupby('time')['price'].median()
        result_group_df = result_group_df.astype({'price':'int64'})
        result_group_df_index = list(result_group_df.index)
        result_group_df_list = list(result_group_df)
        chart_result.append(result_group_df_list)
        chart_result.append(result_group_df_index)

        median = int(result_df['price'].median())

        joongna_df = result_df[result_df['platform'].str.contains('중고나라')]
        dangn_df = result_df[result_df['platform'].str.contains('당근마켓')]
        bunjang_df = result_df[result_df['platform'].str.contains('번개장터')]

        joongna_df.columns = ['index', 'platform', 'name', 'time', 'place', 'price', 'link', 'img_link', 'outlier']
        joongna_group_df = joongna_df.groupby('time')['price'].median()
        joongna_group_df = joongna_group_df.astype({'price': 'int64'})
        joongna_group_df_index = list(joongna_group_df.index)
        joongna_group_df_list = list(joongna_group_df)
        chart_result.append(joongna_group_df_list)
        chart_result.append(joongna_group_df_index)

        dangn_df.columns = ['index', 'platform', 'name', 'time', 'place', 'price', 'link', 'img_link', 'outlier']
        dangn_group_df = dangn_df.groupby('time')['price'].median()
        dangn_group_df = dangn_group_df.astype({'price': 'int64'})
        dangn_group_df_index = list(dangn_group_df.index)
        dangn_group_df_list = list(dangn_group_df)
        chart_result.append(dangn_group_df_list)
        chart_result.append(dangn_group_df_index)

        bunjang_df.columns = ['index', 'platform', 'name', 'time', 'place', 'price', 'link', 'img_link', 'outlier']
        bunjang_group_df = bunjang_df.groupby('time')['price'].median()
        bunjang_group_df = bunjang_group_df.astype({'price': 'int64'})
        bunjang_group_df_index = list(bunjang_group_df.index)
        bunjang_group_df_list = list(bunjang_group_df)
        chart_result.append(bunjang_group_df_list)
        chart_result.append(bunjang_group_df_index)

        for chart_index in range(len(chart_result)):
            date_list = ['오늘', '1일 전', '2일 전', '3일 전', '4일 전', '5일 전', '6일 전', '7일 전']
            chart = chart_result[chart_index]
            s = set(chart)
            temp3 = [x for x in date_list if x not in s]

            if len(chart) == 0:
                if chart_index == 0:
                    result_dict['all'] = chart
                elif chart_index == 1:
                    result_dict['date'] = chart
                    result_dict['all_not_date'] = temp3
                elif chart_index == 2:
                    result_dict['joongna'] = chart
                elif chart_index == 3:
                    result_dict['joongna_date'] = chart
                    result_dict['joongna_not_date'] = temp3
                elif chart_index == 4:
                    result_dict['dangn'] = chart
                elif chart_index == 5:
                    result_dict['dangn_date'] = chart
                    result_dict['dangn_not_date'] = temp3
                elif chart_index == 6:
                    result_dict['bunjang'] = chart
                else:
                    result_dict['bunjang_date'] = chart
                    result_dict['bunjang_not_date'] = temp3
            else:
                if chart_index == 2:
                    result_dict['joongna'] = chart
                elif chart_index == 3:
                    chart.sort(reverse=True)
                    if chart[0] == '오늘':
                        chart.append(chart[0])
                        del chart[0]
                        result_dict['joongna_date'] = chart
                    else:
                        result_dict['joongna_date'] = chart
                    result_dict['joongna_not_date'] = temp3
                elif chart_index == 4:
                    result_dict['dangn'] = chart
                elif chart_index == 5:
                    chart.sort(reverse=True)
                    if chart[0] == '오늘':
                        chart.append(chart[0])
                        del chart[0]
                        result_dict['dangn_date'] = chart
                    else:
                        result_dict['dangn_date'] = chart
                    result_dict['dangn_not_date'] = temp3
                elif chart_index == 6:
                    result_dict['bunjang'] = chart
                elif chart_index == 7:
                    chart.sort(reverse=True)
                    if chart[0] == '오늘':
                        chart.append(chart[0])
                        del chart[0]
                        result_dict['bunjang_date'] = chart
                    else:
                        result_dict['bunjang_date'] = chart
                    result_dict['bunjang_not_date'] = temp3
                elif chart_index == 0:
                    result_dict['all'] = chart
                elif chart_index == 1:
                    chart.sort(reverse=True)
                    if chart[0] == '오늘':
                        chart.append(chart[0])
                        del chart[0]
                        result_dict['date'] = chart
                    else:
                        result_dict['date'] = chart
                    result_dict['all_not_date'] = temp3

        print(result_dict)
        # for result in results:
        #     print(result)
        #     if len(result) == 0:
        #         continue
        #     result_np = np.array(result)
        #     result_df = pd.DataFrame(result_np)

        #     result_df.columns = ['index', 'platform', 'name', 'time', 'place', 'price', 'link', 'img_link', 'outlier']
        #     df = result_df.groupby('time')['price'].median()
        #     df = df.astype({'price': 'int64'})
        #     list_col2 = df.drop(columns=['time', 'price'])
        #     col2_index = list(list_col2.index)
        #     col2_list = list(list_col2)
        #     chart_result.append(col2_list)
        #     chart_result.append(col2_index)
        #     print(chart_result)

        # for chart_index in range(len(chart_result)):

        #     date_list = ['오늘', '1일 전', '2일 전', '3일 전', '4일 전', '5일 전', '6일 전', '7일 전']
        #     chart = chart_result[chart_index]
        #     s = set(chart)
        #     temp3 = [x for x in date_list if x not in s]
        #     if chart_index == 0:
        #         result_dict['joongna'] = chart
        #     elif chart_index == 1:
        #         chart.sort(reverse=True)
        #         if chart[0] == '오늘':
        #             chart.append(chart[0])
        #             del chart[0]
        #             result_dict['joongna_date'] = chart
        #         else:
        #             result_dict['joongna_date'] = chart
        #         result_dict['joongna_not_date'] = temp3
        #     elif chart_index == 2:
        #         result_dict['dangn'] = chart
        #     elif chart_index == 3:
        #         chart.sort(reverse=True)
        #         if chart[0] == '오늘':
        #             chart.append(chart[0])
        #             del chart[0]
        #             result_dict['dangn_date'] = chart
        #         else:
        #             result_dict['dangn_date'] = chart
        #         result_dict['dangn_not_date'] = temp3
        #     elif chart_index == 4:
        #         result_dict['bunjang'] = chart
        #     elif chart_index == 5:
        #         chart.sort(reverse=True)
        #         if chart[0] == '오늘':
        #             chart.append(chart[0])
        #             del chart[0]
        #             result_dict['bunjang_date'] = chart
        #         else:
        #             result_dict['bunjang_date'] = chart
        #         result_dict['bunjang_not_date'] = temp3
        #     elif chart_index == 6:
        #         result_dict['all'] = chart
        #     else:
        #         chart.sort(reverse=True)
        #         if chart[0] == '오늘':
        #             chart.append(chart[0])
        #             del chart[0]
        #             result_dict['date'] = chart
        #         else:
        #             result_dict['date'] = chart

        for i in result_dict['all_not_date']:
            if i == "7일 전":
                result_dict['all'].insert(0, median)
            elif i == '6일 전':
                result_dict['all'].insert(1, median)
            elif i == '5일 전':
                result_dict['all'].insert(2, median)
            elif i == '4일 전':
                result_dict['all'].insert(3, median)
            elif i == '3일 전':
                result_dict['all'].insert(4, median)
            elif i == '2일 전':
                result_dict['all'].insert(5, median)
            elif i == '1일 전':
                result_dict['all'].insert(6, median)
            else:
                result_dict['all'].insert(7, median)

        for i in result_dict['bunjang_not_date']:
            if i == "7일 전":
                result_dict['bunjang'].insert(0, result_dict['all'][0])
            elif i == '6일 전':
                result_dict['bunjang'].insert(1, result_dict['all'][1])
            elif i == '5일 전':
                result_dict['bunjang'].insert(2, result_dict['all'][2])
            elif i == '4일 전':
                result_dict['bunjang'].insert(3, result_dict['all'][3])
            elif i == '3일 전':
                result_dict['bunjang'].insert(4, result_dict['all'][4])
            elif i == '2일 전':
                result_dict['bunjang'].insert(5, result_dict['all'][5])
            elif i == '1일 전':
                result_dict['bunjang'].insert(6, result_dict['all'][6])
            else:
                result_dict['bunjang'].insert(7, result_dict['all'][7])

        for i in result_dict['dangn_not_date']:
            if i == "7일 전":
                result_dict['dangn'].insert(0, result_dict['all'][0])
            elif i == '6일 전':
                result_dict['dangn'].insert(1, result_dict['all'][1])
            elif i == '5일 전':
                result_dict['dangn'].insert(2, result_dict['all'][2])
            elif i == '4일 전':
                result_dict['dangn'].insert(3, result_dict['all'][3])
            elif i == '3일 전':
                result_dict['dangn'].insert(4, result_dict['all'][4])
            elif i == '2일 전':
                result_dict['dangn'].insert(5, result_dict['all'][5])
            elif i == '1일 전':
                result_dict['dangn'].insert(6, result_dict['all'][6])
            else:
                result_dict['dangn'].insert(7, result_dict['all'][7])

        for i in result_dict['joongna_not_date']:
            if i == "7일 전":
                result_dict['joongna'].insert(0, result_dict['all'][0])
            elif i == '6일 전':
                result_dict['joongna'].insert(1, result_dict['all'][1])
            elif i == '5일 전':
                result_dict['joongna'].insert(2, result_dict['all'][2])
            elif i == '4일 전':
                result_dict['joongna'].insert(3, result_dict['all'][3])
            elif i == '3일 전':
                result_dict['joongna'].insert(4, result_dict['all'][4])
            elif i == '2일 전':
                result_dict['joongna'].insert(5, result_dict['all'][5])
            elif i == '1일 전':
                result_dict['joongna'].insert(6, result_dict['all'][6])
            else:
                result_dict['joongna'].insert(7, result_dict['all'][7])

        print("time :", time.time() - start)  # 현재시각 - 시작시간 = 실행 시간
        return result_dict
    except:
        return None


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
