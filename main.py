import flask
import dangn
import joongna
import bunjang
import dangn_naver_chart
import dangn_category
import joongna_category
import bunjang_category
import numpy as np
import pandas as pd
from flask import Flask 
from flask_cors import CORS
import time

app = Flask(__name__)
CORS(app)
categoly = ["디지털기기", "가구/인테리어", "유아용품", "스포츠/레저", "의류", "도서/티켓/문구", "악기", "반려동물", "미용", "콘솔게임"]


@app.route('/search', methods=['GET'])
def startParsing():
    
    start = time.time()  # 시작 시간 저장
    
    keywords = flask.request.args['value']
    keyword = str(keywords)

    ###
    spl = keyword.split()
    list_spl = [k for k in spl]
    naver_keyword_list = list_spl[1:]
    naver_keyword = " ".join(naver_keyword_list)
    ###

    for check in categoly:
        if keyword == check:
            parsing_list = []
            result_list = []
            result_dangn = dangn_category.get_dangn(keyword)
            result_bunjang = bunjang_category.get_bunjang(keyword)
            result_joongna = joongna_category.get_joongna(naver_keyword)
            all = np.concatenate((result_dangn, result_bunjang, result_joongna))
            all = pd.DataFrame(all)
            
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
                results = {"index":parsing[0], "platform":parsing[1], "name":parsing[2], "time":parsing[3], "place":parsing[4],
                            "price":parsing[5], "link":parsing[6], "img_link":parsing[7], "outlier":parsing[8]}
                result_list.append(results)
            break
    else:
        parsing_list = []
        result_list = []
        result_dangn = dangn.get_dangn(keyword)
        result_bunjang = bunjang.get_bunjang(keyword)
        result_joongna = joongna.get_joongna(naver_keyword)
        all = np.concatenate((result_dangn, result_bunjang, result_joongna))
        all = pd.DataFrame(all)
        
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
            results = {"index":parsing[0], "platform":parsing[1], "name":parsing[2], "time":parsing[3], "place":parsing[4],
                        "price":parsing[5], "link":parsing[6], "img_link":parsing[7], "outlier":parsing[8]}
            result_list.append(results)
            
    print("time :", time.time() - start)  # 현재시각 - 시작시간 = 실행 시간
    return result_list

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
    
    results = dangn_naver_chart.get_data(keyword)
    
    for result in results:
        result_np = np.array(result)
        result_df = pd.DataFrame(result_np)
        result_df.columns = ['index', 'platform', 'name', 'time', 'place', 'price', 'link', 'img_link', 'outlier']
        df = result_df.groupby('time')['price'].median()
        df = df.astype({'price':'int64'})
        list_col2 = df.drop(columns= ['time', 'price'])
        col2_index = list(list_col2.index)
        col2_list = list(list_col2)
        chart_result.append(col2_list)
        chart_result.append(col2_index)
            
    for chart_index in range(len(chart_result)):
        
        date_list = ['오늘', '1일 전', '2일 전', '3일 전', '4일 전', '5일 전', '6일 전', '7일 전']
        chart = chart_result[chart_index]
        s = set(chart)
        temp3 = [x for x in date_list if x not in s]
        
        if chart_index == 0:
            result_dict['joongna'] = chart
        elif chart_index == 1:
            chart.sort(reverse=True)
            if chart[0] == '오늘':
                chart.append(chart[0])
                del chart[0]
                result_dict['joongna_date'] = chart
            else:
                result_dict['joongna_date'] = chart
            result_dict['joongna_not_date'] = temp3
        elif chart_index == 2:
            result_dict['dangn'] = chart
        elif chart_index == 3:
            chart.sort(reverse=True)
            if chart[0] == '오늘':
                chart.append(chart[0])
                del chart[0]
                result_dict['dangn_date'] = chart
            else:
                result_dict['dangn_date'] = chart
            result_dict['dangn_not_date'] = temp3
        elif chart_index == 4:
            result_dict['bunjang'] = chart
        elif chart_index == 5:
            chart.sort(reverse=True)
            if chart[0] == '오늘':
                chart.append(chart[0])
                del chart[0]
                result_dict['bunjang_date'] = chart
            else:
                result_dict['bunjang_date'] = chart
            result_dict['bunjang_not_date'] = temp3
        elif chart_index == 6:
            result_dict['all'] = chart
        else:
            chart.sort(reverse=True)
            if chart[0] == '오늘':
                chart.append(chart[0])
                del chart[0]
                result_dict['date'] = chart
            else:
                result_dict['date'] = chart
                
    print("time :", time.time() - start)  # 현재시각 - 시작시간 = 실행 시간
    return result_dict

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000,debug=True)

