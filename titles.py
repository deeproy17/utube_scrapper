import os
import time
import requests
from selenium import webdriver
import snowflake.connector
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup as bs
videos_title={}
videos_links={}
videos_likes={}
videos_comments_count={}
commetators_comments={}
def snowflake_connnect(query,type=None):
    conn = snowflake.connector.connect(
                    user='karthik777',
                    password='Pavan@123',
                    account='px65781.ap-southeast-1',
                    database='YOUTUBE_DB',
                    warehouse='YOUTUBE',
                    schema='PUBLIC',
                    )
    cur=conn.cursor()
    cur.execute('USE ROLE ACCOUNTADMIN')
    cur.execute(query)
    if type=='select':
        return cur.fetchall()
    cur.close()
    conn.commit()
    return "task done"
def fetch_image_titles(search_term,max_links_to_fetch,wd,sleep_between_interactions):
    def scroll_to_end(wd):
        wd.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(sleep_between_interactions)
    wd.get(search_term)
    image_count = 0
    results_start = 0
    counter=0
    while image_count < max_links_to_fetch:
        print("Again")
        scroll_to_end(wd)
        thumbnail_results = wd.find_elements("css selector","ytd-grid-video-renderer.ytd-grid-renderer")
        number_results = len(thumbnail_results)
        print(f"Found: {number_results} search results. Extracting links from {results_start}:{number_results}")
        for each_thumb in thumbnail_results[results_start:number_results]:
            for each_title in each_thumb.find_elements("css selector","a.ytd-grid-video-renderer"):
                print(each_title.get_attribute('title'),image_count)
                if each_title.get_attribute('title') and image_count not in videos_title: 
                    videos_title[image_count]=each_title.get_attribute('title')
            for each_link in each_thumb.find_elements("css selector","a.ytd-thumbnail"):
                print(each_link.get_attribute('href'))
                if each_link.get_attribute('href') and image_count not in videos_links:
                    videos_links[image_count]=each_link.get_attribute('href')
                    with webdriver.Chrome(ChromeDriverManager().install()) as wd1:
                        wd1.get(each_link.get_attribute('href'))
                        time.sleep(sleep_between_interactions)
                        for each_like in wd1.find_elements('css selector','yt-formatted-string.style-text'):
                            print(each_like.get_attribute('aria-label'))
                            if each_like.get_attribute('aria-label') and image_count not in videos_likes:
                                videos_likes[image_count]=each_like.get_attribute('aria-label')
                        counter_comment=0
                        for each_comments_count in wd1.find_elements('css selector','span.yt-formatted-string'):
                                if each_comments_count.text.isdigit():
                                    videos_comments_count[image_count]=each_comments_count.text
                                    print(each_comments_count.text)
                        for each_like in wd1.find_elements('css selector','yt-formatted-string.style-text'):
                            print(each_like.get_attribute('aria-label'))
                            if each_like.get_attribute('aria-label') and image_count not in videos_likes:
                                videos_likes[image_count]=each_like.get_attribute('aria-label')
                        each_video_comments=set()
                        time.sleep(sleep_between_interactions)
                        try:
                            comment_section=wd1.find_element('css selector','ytd-item-section-renderer.ytd-comments')
                            for each_verified in comment_section.find_elements('tag name','div.ytd-comment-renderer'):
                                title=each_verified.find_elements('tag name','span.ytd-comment-renderer')
                                if title:
                                    for each in range(len(title)):
                                        title_name=[]
                                        if type(title[each].text==type(str())) and title[each].text!='Read more' and title[each].text!='':  
                                            if title[each].text not in title_name :
                                                title_name.append(title[each].text)
                                            comments=each_verified.find_elements('css selector','yt-formatted-string.ytd-comment-renderer')
                                            if comments:
                                                for each_cm in range(len(comments)):
                                                    if each_cm==1 and comments[each_cm].text!='Read more':  
                                                        data=":".join([title_name[0],comments[each_cm].text])
                                                        each_video_comments.add(data)
                        except Exception as exc:
                            print(Exception)
                        else:
                            commetators_comments[image_count]=each_video_comments
            image_count = len(videos_title)
            if len(videos_links)  >= max_links_to_fetch:
                print(f"Found: {len(videos_links)} title links, done!")
                break
        else:
            print("Found:", len(videos_links), "title links, looking for more ...")
            load_more_button = wd.find_elements("css selector", ".mye4qd")
            if load_more_button:
                wd.execute_script("document.querySelector('.mye4qd').click();")
        results_start = len(thumbnail_results)

def search_download(search_term,number_images,target_path='./images'):
    target_folder = os.path.join(target_path, '_'.join(search_term.lower().split(' ')))
    channel_name="".join(i for i in search_term.split("/")[4] if i.isalnum())
    drop_query='''DROP TABLE if exists {0} ;'''.format(channel_name)
    snowflake_connnect(drop_query)
    create_query="""create table {0} if not exists (s_no VARCHAR(250), title VARCHAR(250)  NULL,link VARCHAR(250)  NULL,likes VARCHAR(250)  NULL,comments VARCHAR(250) NULL);""".format(channel_name)
    print(snowflake_connnect(create_query))
    if not os.path.exists(target_folder):
        os.makedirs(target_folder)
    with webdriver.Chrome(ChromeDriverManager().install()) as wd:
        res = fetch_image_titles(search_term, number_images, wd=wd, sleep_between_interactions=2)
    print(videos_links,videos_title,videos_likes,videos_comments_count,commetators_comments)
    return "Selenium data extracted"
