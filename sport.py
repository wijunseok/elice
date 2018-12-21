# -*- coding: utf-8 -*-
import json
import os
import re
import urllib.request
from bs4 import BeautifulSoup
from slackclient import SlackClient
from flask import Flask, request, make_response, render_template
app = Flask(__name__)
slack_token = "xoxb-501387243681-507427613507-QWK0g4pLgE3TZIi8UoaKCdTx" #스트링으로 감싸야 한다! #자신의 토큰 값을 입력해줍니다.
slack_client_id = "501387243681.507730053797" #client_id 값을 입력합니다.
slack_client_secret = "c44a90103e4b570831e17481718a3ab1"  #client_secret 값을 입력합니다.
slack_verification = "dv79v8UkqCLQzZ4ekBOliIIJ" #verification 값을 입력합니다.
sc = SlackClient(slack_token)
#순위 테이블 함수
def _rank_table(soup):
    table=[]
    data=[]
    name=[]
    f_data=soup.find("tbody").find_all("td")
    for x in f_data:
        data.append(x.get_text())
    max=0
    for j in range(0,int(len(data)/10)):
        name.append(data[j*10+1])
        if len(name[j])>max:
            max=len(name[j])
    max+=5
    for j in range(len(name)):
        for a in range(0,max-len(name[j])):
            name[j]+=" "*2
    for i in range(0,int(len(data)/10)):
        s=data[i*10+0]+"\t\t"+name[i]
        d=data[i*10+2]+"\t\t"+data[i*10+4]+"\t\t"+data[i*10+5]+"\t\t"+data[i*10+6]+"\t\t"+data[i*10+7]
        #순위0, 클럽명1, 승점2, 경기수4, 승5/무6/패7
        table.append(s+d)
    # 한글 지원을 위해 앞에 unicode u를 붙혀준다.
    return "순위\t\t\t팀명\t\t\t\t\t\t\t\t   승점     경기수  승      무      패"+"\n"+u'\n'.join(table)
# 크롤링 함수 구현하기

def _crawl_naver_keywords(text):
    
    #여기에 함수를 구현해봅시다.
    url=["https://footballdatabase.com/league-scores-tables/england-premier-league-2018-19",
    "https://footballdatabase.com/league-scores-tables/germany-bundesliga-2018-19",
    "https://footballdatabase.com/league-scores-tables/spain-liga-bbva-2018-19"]
    sourcecode=[]
    soup=[]
    for x in range(len(url)):
        req=urllib.request.Request(url[x])
        sourcecode.append(urllib.request.urlopen(url[x]).read())
        soup.append(BeautifulSoup(sourcecode[x], "html.parser"))
    ################################################
    table=[]
    data=[]
    name=[]
    #################################################
    
    if "잉글랜드" in text or "영국" in text:
        return _rank_table(soup[0])
    #################################################################################################################
    elif "독일" in text:
        return _rank_table(soup[1])            
    #################################################################################################################
    elif "스페인" in text:
        return _rank_table(soup[2])
    elif "리그 종류" in text:
        return "현재는 잉글랜드, 독일, 스페인 경기를 보실 수 있습니다."
    else:
        return "나머지는 업데이트 예정입니다.\n 죄송하지만 기다려 주세요"
# 이벤트 핸들하는 함수
def _event_handler(event_type, slack_event):
    print(slack_event["event"])
    if event_type == "app_mention":
        channel = slack_event["event"]["channel"]
        text = slack_event["event"]["text"]
        keywords = _crawl_naver_keywords(text)
        sc.api_call(
            "chat.postMessage",
            channel=channel,
            text=keywords
        )
        return make_response("App mention message has been sent", 200,)
    # ============= Event Type Not Found! ============= #
    # If the event_type does not have a handler
    message = "You have not added an event handler for the %s" % event_type
    # Return a helpful error message
    return make_response(message, 200, {"X-Slack-No-Retry": 1})
@app.route("/listening", methods=["GET", "POST"])
def hears():
    slack_event = json.loads(request.data)
    if "challenge" in slack_event:
        return make_response(slack_event["challenge"], 200, {"content_type":
                                                             "application/json"
                                                            })
    if slack_verification != slack_event.get("token"):
        message = "Invalid Slack verification token: %s" % (slack_event["token"])
        make_response(message, 403, {"X-Slack-No-Retry": 1})
    
    if "event" in slack_event:
        event_type = slack_event["event"]["type"]
        return _event_handler(event_type, slack_event)
    # If our bot hears things that are not events we've subscribed to,
    # send a quirky but helpful error response
    return make_response("[NO EVENT IN SLACK REQUEST] These are not the droids\
                         you're looking for.", 404, {"X-Slack-No-Retry": 1})
@app.route("/", methods=["GET"])
def index():
    return "<h1>Server is ready.</h1>"
if __name__ == '__main__':
    app.run('0.0.0.0', port=8080)