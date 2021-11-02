from selenium import webdriver
from bs4 import BeautifulSoup
import requests
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
import time
import pandas as pd

url = "https://soundcloud.com/user-961145082/sets/new-indie-alternative-may-2016"
driver = webdriver.Chrome()
driver.get(url)
driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
time.sleep(2)
html = driver.page_source
soup = BeautifulSoup(html, "html.parser")
playlist_title = soup.find("h1", {"class": "soundTitle__title"}).getText().strip()
tracks = soup.find_all("div", {"class": "trackItem__content"})

playlist_lst = [];
track_lst = [];

for track in tracks:
    track_name = track.getText();
    track_lst.append(track_name.strip().replace("\n", " "))

lst = []

for track_item in track_lst:
    lst.append(track_item)
lst = ','.join(lst)

playlist_lst.append([playlist_title, lst])

f_out = pd.DataFrame(playlist_lst, columns=['name', 'Track'])
f_out.to_csv('playlist.csv', index=False, sep='\t')

