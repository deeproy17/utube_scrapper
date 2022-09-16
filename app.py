from flask import Flask, render_template, request,jsonify
from flask_cors import CORS,cross_origin
import requests
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen as uReq
import titles
from titles import search_download,snowflake_connnect
from titles import videos_comments_count,videos_likes,videos_links,videos_title
app = Flask(__name__)
@app.route('/',methods=['GET'])  # route to display the home page
@cross_origin()
def homePage():
    print("hello")
    return render_template("index.html")

@app.route('/data',methods=['POST','GET']) # route to show the review comments in a web UI
@cross_origin()
def index():
    if request.method == 'POST':
        try:
            channel_link=request.form['content']
            print(search_download(channel_link,10))
            channel_title="".join(i for i in channel_link.split("/")[4] if i.isalnum())
            counter=0
            print(counter)
            for each_row in range(len(videos_links)):
                print(each_row)
                if each_row in videos_title:
                    title=videos_title[each_row]
                else:
                    title=""
                if each_row in videos_links:
                    link=videos_links[each_row]
                else:
                    link=""
                if each_row in videos_likes:
                    likes=videos_likes[each_row]
                else:
                    likes=""
                if each_row in videos_comments_count:
                    comments_count=videos_comments_count[each_row]
                else:
                    comments_count=""
                insert_query='''INSERT INTO {0} VALUES('{1}','{2}','{3}','{4}','{5}')'''.format(channel_title,counter,title,link,likes,comments_count)
                snowflake_connnect(insert_query)
                counter+=1
            print(channel_title)
            select_query=''' select * from {0}'''.format(channel_title)
            query_result=snowflake_connnect(select_query,'select')    
        except Exception as exc:
            print(exc)
            return render_template('index.html')
        else:
            return render_template('results.html',query_results=query_result)
    else:
        return render_template('index.html')


if __name__ == "__main__":
	app.run(debug=True)
