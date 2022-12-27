import requests
from bs4 import BeautifulSoup
import re
import json

def convert_time(sec):
   sec = sec % (24 * 3600)
   hour = sec // 3600
   sec %= 3600
   min = sec // 60
   sec %= 60
   return "%02d:%02d:%02d" % (hour, min, sec)

class Scrape:
    def __init__(self) -> None:
        self.url = "https://www.youtube.com/results?search_query="
        self.video_url = "https://www.youtube.com/watch?v="
        
    def Url_Generator(self,query):
        splitted_query = query.split()
        res1 = ""
        for ele in splitted_query[:-1]:
            res1 += ele+"+"
        result = res1 + splitted_query[-1]
        query_url = self.url+result
        return query_url
    
    def Scraper(self,query):
        url = self.Url_Generator(query)
        response = requests.get(url).text
        soup = BeautifulSoup(response, "lxml")
        lol = soup.find_all("script")[33]
        html_text = re.search("var ytInitialData = (.+)[,;]{1}",lol.text).group(1)
        html_text.replace("true","True")
        json_data = json.loads(html_text)

        content = (
            json_data["contents"]["twoColumnSearchResultsRenderer"]["primaryContents"]
            ["sectionListRenderer"]["contents"][0]["itemSectionRenderer"]["contents"]
        )

        A = []
        for data in content:
            for value in data.values():
                if type(value) is dict:
                    D = {}
                    for k,v in value.items():
                        if k == "videoId" and len(v)== 11:
                            D["URL"] = self.video_url+v
                        elif k=='title' and 'runs' in v:
                            D["Title"] = v['runs'][0]['text']
                        elif k == "publishedTimeText" and "simpleText" in v:
                            D["Published"] = v["simpleText"]
                        elif k == "lengthText" and "simpleText" in v:
                            D["Duration"] = v["simpleText"]
                    if D : A.append(D)
        return A

    def data(self,query,Sort):

        try:
            doc = self.Scraper(query)
            result=[]
            if Sort:
                seconds,minutes,hours,days,weeks,months,years=([] for _ in range(7))
            for ele in doc:
                    duration = ele["Duration"]
                    time_arr = duration.split(":")
                    time = 0
                    if len(time_arr) == 2:
                        time = int(time_arr[1])*60 + int(time_arr[0])
                    elif len(time_arr) == 3:
                        time = int(time_arr[2])*3600+int(time_arr[1])*60 + int(time_arr[0])
                    ele["Duration"] = {
                        "0.25 x" : convert_time(time/0.25),
                        "0.5 x"  : convert_time(time/0.5),
                        "1.0 x"  : convert_time(time),
                        "1.25 x" : convert_time(time/1.25),
                        "1.5 x"  : convert_time(time/1.5),
                        "2.0 x"  : convert_time(time/2)
                    }
                    if Sort:
                        temp=ele['Published'].split(" ")
                        cursor=temp.index('ago')
                        match temp[cursor-1]:
                            case ('second'|'seconds'):
                                seconds.append({'t':temp[cursor-2],'vid':ele})
                            case ('minute'|'minutes'):
                                minutes.append({'t':temp[cursor-2],'vid':ele})
                            case ('hour'|'hours'):
                                hours.append({'t':temp[cursor-2],'vid':ele})
                            case ('day'|'days'):
                                days.append({'t':temp[cursor-2],'vid':ele})
                            case ('week'|'weeks'):
                                weeks.append({'t':temp[cursor-2],'vid':ele})
                            case ('month'|'months'):
                                months.append({'t':temp[cursor-2],'vid':ele})
                            case ('year'|'years'):
                                years.append({'t':temp[cursor-2],'vid':ele})
                    else:
                        result.append(ele)
                        
            if Sort:
                [ls.sort(key=lambda d: int(d['t'])) for ls in [seconds,minutes,hours,days,weeks,months,years]]
                [result.append(ele['vid']) for ele in seconds+minutes+hours+days+weeks+months+years]

            return result

        except Exception as e:
            raise e


