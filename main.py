import dangn
import naver
import bunjang

# keyword 만들기
keyword = input("검색어를 입력하세요 : ")
keyword = keyword.replace(" ", "%20")

dangn.get_dangn(keyword)
naver.get_naver(keyword)
bunjang.get_bunjang(keyword)