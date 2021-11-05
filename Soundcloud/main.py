from selenium import webdriver
from bs4 import BeautifulSoup
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
#import pandas as pd

#wait
def wait(driver, selector_name):
    while (True):
        try:
            myElem = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CLASS_NAME, selector_name)))
            if myElem is not None:
                break
        except TimeoutException:
            break
#scroll
def scroll(driver):
    # Get scroll height
    last_height = driver.execute_script("return document.body.scrollHeight")

    while True:
        # Scroll down to bottom
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        # Wait to load page
        time.sleep(2)

        # Calculate new scroll height and compare with last scroll height
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

def getTracks(playlist_url):
    driver = webdriver.Chrome()
    driver.get(playlist_url)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2)
    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")

    user_name = soup.find("a", {"class": "userBadge__usernameLink"}).getText().strip()
    playlist_title = soup.find("h1", {"class": "soundTitle__title"}).getText().strip()
    track_items = soup.find_all("div", {"class": "trackItem__content"})

    track_list = [];

    for track_item in track_items:
        track_name = track_item.getText();
        track_list.append(track_name.strip().replace("\n", " "))

    track_str = []
    for track_item in track_list:
        track_str.append(track_item)
    track_str = ','.join(track_str)
    if track_str == '':
        track_str = 'None'

    return user_name, playlist_title, track_str

def getPlaylistURLs(user_playlist_url):
    url = user_playlist_url
    driver = webdriver.Chrome()
    driver.get(url)

    # Get scroll height
    last_height = driver.execute_script("return document.body.scrollHeight")

    scroll(driver)

    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")
    contents = soup.find_all("a", {"class": "sound__coverArt"})
    urls = []

    for content in contents:
        urls.append('https://soundcloud.com' + content['href'])

    return urls

def getPlaylists(user_playlist_urls):
    playlist_lst = []

    for user_url in user_playlist_urls:
        playlist_urls = getPlaylistURLs(user_url + '/sets')
        for playlist_url in playlist_urls:
            playlist_lst.append(getTracks(playlist_url))

    return playlist_lst


my_url = "https://soundcloud.com/discover"
driver = webdriver.Chrome()
driver.get(my_url)
html = driver.page_source
soup = BeautifulSoup(html, "html.parser")
link = soup.find_all("a", {
    "class": "sc-link-secondary sc-link-light playableTile__usernameHeading audibleTile__usernameHeading sc-truncate sc-text-h4"})

set_link = []
set_user = []
for item in link:
    user_url = "https://soundcloud.com" + item.get("href")
    if user_url not in set_link:
        set_link.append(user_url)

for user_url in set_link:
    if len(set_user) > 1:
        break;
    driver.get(user_url)
    while (True):
        myElem = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'profileHeaderInfo__userName')))
        if myElem is not None:
            break;
    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")
    user_name = soup.find("h2", {"class": "profileHeaderInfo__userName"})
    k = [p.getText(strip=True) for p in user_name]
    set_user.append([k[0], user_url])

    # Get followers
    follower_url = user_url + "/following"
    driver.get(follower_url)

    #Wait
    wait(driver, 'userBadgeListItem__heading')

    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")
    followers = soup.find_all("a", {"class": "userBadgeListItem__heading"})
    for follower in followers:
        if follower not in set_link:
            set_link.append("https://soundcloud.com" + follower.get("href"))

# for item in set_user:
#     temp = item[1] + "/tracks"
#     driver.get(temp)
#     while (True):
#         try:
#             myElem = WebDriverWait(driver, 30).until(
#                 EC.presence_of_element_located((By.CLASS_NAME, 'profileHeaderInfo__userName')))
#             if myElem is not None:
#                 break
#         except TimeoutException:
#             break;
#
#     html = driver.page_source
#     soup = BeautifulSoup(html, "html.parser")
#     emptyTrack = soup.find("h3", {"class": "sc-type-large emptyNetworkPage__headline"})
#     if emptyTrack is None:
#         Track_list = soup.find_all("a", {"class": "sc-link-primary soundTitle__title sc-link-dark sc-text-h4"})
#         string_track = ""
#         for track in Track_list:
#             string_track = string_track + track.getText().strip() + "\t"
#         k = [p.getText(strip=True) for p in soup.find("h2", {"class": "profileHeaderInfo__userName"})]
#         print(k[0] + ':' + '\t' + string_track)
#     else:
#         k = [p.getText(strip=True) for p in soup.find("h2", {"class": "profileHeaderInfo__userName"})]
#         print(k[0] + ':' + '\t' + "None")

url_lst = [];
for i in set_user:
    url_lst.append(i[1])

playlist = getPlaylists(url_lst)
for url in playlist:
    print(url)
#f_out = pd.DataFrame(playlist, columns=['User', 'Playlist', 'Track'])
#f_out.to_csv('playlist.csv', index=False, sep='\t')
