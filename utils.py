import time
import re
import urllib.parse
import requests
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from gevent import monkey; monkey.patch_all()
import gevent

def get_subdomain(url, kw, name, page_count):
    #正则re="xxxxx"
    nuc_re = re.compile("<h3 class=\"t\"><a[\s\S]+?href=\"([^\"]+)\"")

    driver = webdriver.Chrome()
    driver.get(url)
    elem = driver.find_element_by_name(kw)
    elem.send_keys(name)
    elem.send_keys(Keys.RETURN)
    time.sleep(3)

    links = []

    for i in range(page_count):
        time.sleep(4)
        url = nuc_re.findall(driver.page_source)
        links.extend(url)
	#下一页为xxx
        a = driver.find_element_by_link_text('下一页>')
        a.click()

    driver.close()

    for i in links:
        res = requests.head(i)
        href = res.headers["Location"]
	#sudomain=xxx.xxx.cn
        if "xxx.edu.cn" in href:      
            with open("./subdomain","a") as f:
                f.write(urllib.parse.urlparse(href)[1]+"\n")


def check_is_alive(urls):
    links = []
    for url in urls:
        res=requests.get(url,headers=headers,timeout=2)
        if res.status_code == 200 and res.reason == OK:
            links.append(url)
    return links
        

def get_url(url):
    print("%s fetching..."%url)
    ext_names = [".rar", ".zip", ".doc", ".docx", ".xls",
                ".xlsx", ".ppt", ".pptx", ".pdf", ".jpg", ".png",
                ".bmp", ".gif", ".avi", ".3gp", ".mp4", ".mp3"]

    ua = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36"

    parses = urllib.parse.urlparse(url)
    href_re1 = "<a[\s\S]+?href=\"(https?://" + parses[1] + "[^\"]+?)\""
    href_re2 = "<a[\s\S]+?href=\"(?!http|https|mailto|javascript)([a-zA-Z0-9_./][^\"]+?)\""

    res = requests.get(url, headers={"User-Agent": ua})
    hrefs1 = re.findall(href_re1, res.text)
    hrefs2 = re.findall(href_re2, res.text)

    hrefs = []
    for i in hrefs1:
        switch = False
        for j in ext_names:
            if j in i:
                switch = True
        if switch == False:
            hrefs.append(i)

    for i in hrefs2:
        switch = False
        for j in ext_names:
            if j in i:
                switch = True
        if switch == False:
            hrefs.append(urllib.parse.urljoin(parses[0] + "://" + parses[1], i))

    return list(set(hrefs))

def get_all_url(url):
    print("%s fetching..."%url)
    results = []
    jobs = [url,]
    while True:

        if len(jobs) > 0:
            try:
                urls = get_url(jobs.pop())

                for i in urls:
                    if i not in results:
                        results.append(i)
                        jobs.append(i)
            except:
                pass

        else:
            break

    results.sort()
    return results

def get_all_url_async(url, max_cr):
    targets = [url,]
    results = []
    while True:
        jobs = []
        if len(targets) > max_cr:
            for i in range(max_cr):
                jobs.append(gevent.spawn(get_url, targets.pop()))
        elif max_cr >= len(targets) > 0:
            for i in range(len(targets)):
                jobs.append(gevent.spawn(get_url, targets.pop()))
        gevent.joinall(jobs)
        for job in jobs:
            for i in job.value:
                if i not in results:
                    targets.append(i)
                    results.append(i)

        if len(targets) == 0:
            break

    return list(set(results))

def form_check(url):
    print("%s form checking..."%url)

    ua = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36"
    res = requests.get(url, headers={"User-Agent": ua})

    if "<form" in res.text:
        return True
    else:
        return False

