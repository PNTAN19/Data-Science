import json

import requests
from selenium import webdriver
from bs4 import BeautifulSoup
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
import pandas as pd
from selenium.webdriver.common.by import By


# wait
def wait(driver, selector_name):
    while (True):
        try:
            myElem = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CLASS_NAME, selector_name)))
            if myElem is not None:
                break
        except TimeoutException:
            break


# scroll
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

# Drive the chrome to url link and return soup with html parser
def drive_to_url_page(driver, url):
    driver.get(url)
    #Scroll screen from page to get more data <li> </li>
    scroll(driver)
    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")
    return soup

def get_user_set_all_data(driver, set_link):
    #Get user id in SoundCloud/Discover by get meta tag in HEAD html
    set_data_user = []
    for link_user in set_link:
        one_data_user = []
        driver.get(link_user)
        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")

        #Get USER INFO
        id_user = soup.find("meta", property="twitter:app:url:googleplay")
        name_user = soup.find("meta", property="og:title")
        url_user = soup.find("meta", property="og:url")
        playlist_count = count_playlist_in_one_person(driver, link_user)
        users_city = soup.find("h3", {"class": "profileHeaderInfo__additional g-type-shrinkwrap-block theme-dark g-type-shrinkwrap-large-secondary sc-mt-1x"})
        info_start = soup.find_all("div", {"class":"infoStats__value sc-font-light"})

        #Add to one_data_user set
        one_data_user.append(id_user["content"].strip("soundcloud://users:"))
        one_data_user.append(name_user["content"])
        one_data_user.append(url_user["content"])
        one_data_user.append(playlist_count)
        one_data_user.append(users_city)
        for item in info_start:
            one_data_user.append(item)

        #Print to test by eye
        # print(id_user["content"].strip("soundcloud://users:") if id_user else "No meta title given")
        # print(name_user["content"] if name_user else "No meta url given")
        # print(url_user["content"] if url_user else "No meta url given")
        set_data_user.append(one_data_user)

    #Print all data user in 2D array
    # print(set_data_user[0])
    # print(set_data_user[0][0] + "\t" + set_data_user[0][1] + "\n")
    # print(set_data_user[10][0] + "\t" + set_data_user[10][1] + "\t" + set_data_user[10][2])

    # Print all data user we have:
    # for item in set_data_user:
    #     print(item)
    # print(len(set_data_user))
    return set_data_user

def get_user_name_id_and_url():
    main_url = "https://soundcloud.com/discover"
    driver = webdriver.Chrome()
    soup = drive_to_url_page(driver, main_url)
    links = soup.find_all("a", {"class": "sc-link-secondary sc-link-light playableTile__usernameHeading audibleTile__usernameHeading sc-truncate sc-text-h4"})
    set_link = []
    for item in links:
        user_url = "https://soundcloud.com" + item.get("href")
        if user_url not in set_link:
            set_link.append(user_url)

    #Get the all person in set_link with his/her following information
    for i in range(0, len(set_link) - 1):
        following_url = set_link[i] + "/following"
        soup = drive_to_url_page(driver, following_url)
        link_following_user = soup.find_all("a", {"class":"userBadgeListItem__heading sc-type-small sc-text-h4 sc-link-dark sc-link-primary sc-truncate"})
        for item in link_following_user:
            user_url = "https://soundcloud.com" + item.get("href")
            if user_url not in set_link:
                set_link.append(user_url)
        # print(len(link_following_user))
        print(len(set_link))
        if len(set_link) >= 38:
            break;

    set_data_user = get_all_user_data(driver, set_link)
    for item in set_data_user:
        print(item)
    print(len(set_data_user))
    return set_data_user

def get_all_user_data(driver, set_link):
    #Get user id in SoundCloud/Discover by get meta tag in HEAD html
    set_data_user = []
    for link_user in set_link:
        one_data_user = []
        driver.get(link_user)
        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")
        #Get user id & user name & user url
        id_user = soup.find("meta", property="twitter:app:url:googleplay")
        name_user = soup.find("meta", property="og:title")
        url_user = soup.find("meta", property="og:url")
        one_data_user.append(id_user["content"].strip("soundcloud://users:"))
        one_data_user.append(name_user["content"])
        one_data_user.append(url_user["content"])
        # print(id_user["content"].strip("soundcloud://users:") if id_user else "No meta title given")
        # print(name_user["content"] if name_user else "No meta url given")
        # print(url_user["content"] if url_user else "No meta url given")
        set_data_user.append(one_data_user)

    #Print all data user in 2D array
    # print(set_data_user[0])
    # print(set_data_user[0][0] + "\t" + set_data_user[0][1] + "\n")
    # print(set_data_user[10][0] + "\t" + set_data_user[10][1] + "\t" + set_data_user[10][2])

    #Print all data user we have:
    # for item in set_data_user:
    #     print(item)
    # print(len(set_data_user))
    return set_data_user

#============ using API to get USER.csv =================
#Get set_user API
def get_user_by_API(client_id):
    set_data_user = []
    #parse html to get <user id > in <HEAD> tag
    #MAYBE WE CAN FIND A BETTER WAY TO GET <USER_ID>
    main_url = "https://soundcloud.com/discover"
    driver = webdriver.Chrome()
    soup = drive_to_url_page(driver, main_url)
    links = soup.find_all("a", {
        "class": "sc-link-secondary sc-link-light playableTile__usernameHeading audibleTile__usernameHeading sc-truncate sc-text-h4"})
    set_link = []
    for item in links:
        user_url = "https://soundcloud.com" + item.get("href")
        if user_url not in set_link:
            set_link.append(user_url)
    set_data_user = get_user_set_all_data(driver, set_link)

    # USE THIS FUNCTION PARSER HTML TO GET MORE PEOPLE'S INFO
    #get_user_name_and_id()
    
    #This df to print out file <user.csv>
    df = pd.DataFrame(set_data_user,
                      columns=['User ID','User Name','User Link'])
    # Select first column of the dataframe as a series
    set_user_id = df.iloc[:, 0]
    for item in set_user_id:
        one_data_user = []
        user_id = item
        api_url = f'https://api-v2.soundcloud.com/users/{user_id}?client_id={client_id}'
        # get request
        r = requests.get(api_url)
        print(r)
        # check whether it get the url
        # or if it got request, does it have a string "incomplete_results":true in the response it recieved?
        while r.status_code != requests.codes.ok or '"incomplete_results":true' in r:
            print("wait")
            time.sleep(1)
            r = requests.get(api_url)
        #JSON processing
        json_str = json.loads(r.text)
        one_data_user.append(str(json_str['id']))
        one_data_user.append(str(json_str['username']))
        one_data_user.append(str(json_str['permalink_url']))
        set_data_user.append(one_data_user)
    #Print to test by eye
    # for item in set_data_user:
    #     print(item)
    return set_data_user


# Playlist - parse html func start
def getTracksFromPlaylists(playlist_url, optional):
    driver = webdriver.Chrome()
    driver.get(playlist_url)
    scroll(driver)
    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")

    user_name = soup.find("a", {"class": "userBadge__usernameLink"}).getText().strip()
    playlist_title = soup.find("h1", {"class": "soundTitle__title"}).getText().strip()
    num_of_track = soup.find("div", {"class": "genericTrackCount__title"}).getText()
    create_date = soup.find("time", {"class": "relativeTime"})["title"]
    datas = soup.find_all("span", {"aria-hidden": "true"})

    likes = datas[1].getText()
    reports = datas[2].getText()

    track_list = []
    track_str = []

    if optional == 0:
        track_items = soup.find_all("div", {"class": "trackItem__content"})

        for track_item in track_items:
            track_name = track_item.getText();
            track_list.append(track_name.strip().replace("\n", " "))
    elif optional == 1:
        track_items = soup.find_all("a", {"class": "trackItem__trackTitle"})
        track_urls = []

        for track_item in track_items:
            track_urls.append('https://soundcloud.com' + track_item['href'])

        for url in track_urls:
            driver = webdriver.Chrome()
            driver.get(url)
            html = driver.page_source
            soup = BeautifulSoup(html, "html.parser")

            meta = soup.find("meta", property="twitter:app:url:iphone")
            track_list.append(meta["content"].split(':')[-1])

    for track_item in track_list:
        track_str.append(track_item)
    track_str = ','.join(track_str)
    if track_str == '':
        track_str = 'None'

    return user_name, playlist_title, num_of_track, create_date, likes, reports, track_str


def getPlaylistURLs(user_playlist_url):
    url = user_playlist_url
    driver = webdriver.Chrome()
    driver.get(url)
    scroll(driver)
    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")

    contents = soup.find_all("a", {"class": "sound__coverArt"})
    urls = []

    for content in contents:
        urls.append('https://soundcloud.com' + content['href'])

    return urls


def getPlaylists(user_playlist_urls, optional):
    playlist_lst = []

    for user_url in user_playlist_urls:
        playlist_urls = getPlaylistURLs(user_url + '/sets')
        for playlist_url in playlist_urls:
            playlist_lst.append(getTracksFromPlaylists(playlist_url, optional))

    return playlist_lst
# Playlist - parse html func end

def getTracks(set_user):
    driver = webdriver.Chrome()
    set_tracks = set()
    set_link_tracks = set()
    for item in set_user:
        temp = item[2] + "/tracks"
        driver.get(temp)

        wait(driver, selector_name='sc-link-primary soundTitle__title sc-link-dark sc-text-h4')

        scroll(driver)

        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")
        link_tracks = soup.find_all('a', {'class': 'sc-link-primary soundTitle__title sc-link-dark sc-text-h4'})

        for link in link_tracks:
            string_temp = 'https://soundcloud.com'
            string_temp = string_temp + link['href']
            set_link_tracks.add(string_temp)
        for link in set_link_tracks:
            driver.get(link)
            wait(driver, selector_name='sc-ministats-item')
            soup = BeautifulSoup(driver.page_source, "html.parser")
            id_track = soup.find('meta', {'property': 'twitter:app:url:googleplay'})['content'].split(':')[-1]
            name_track = soup.find('h1', {'class': 'soundTitle__title sc-font g-type-shrinkwrap-inline g-type-shrinkwrap-large-primary theme-dark'}).getText().strip()
            time_release_track = soup.find('time', {'class': 'relativeTime'})['title']
            info_track = soup.find_all('span', {'aria-hidden': 'true'})
            plays = info_track[1].getText()
            likes = info_track[2].getText()
            reposts = info_track[3].getText()

            tup = (item[0], id_track, name_track, time_release_track, plays, likes, reposts)
            print(tup)
            set_tracks.add(tup)


    return set_tracks


def getTracksAPI(set_user):
    set_tracks = set()
    temp1 = 'https://api-v2.soundcloud.com/users/'
    temp2 = '/tracks?client_id=nGKlrpy2IotLQ0QGwBOmIgSFayis6H4e&limit=100'

    for item in set_user:
        string_tracks = ''
        api = temp1 + item[0] + temp2
        while True:
            r = requests.get(api)
            if r.status_code != 200:
                time.sleep(5.0)
            else:
                break
        for temp in r.json()['collection']:
            string_tracks = string_tracks + str(temp['id']) + ','
        tup = (item[0], string_tracks)
        set_tracks.add(tup)
    return set_tracks


# my_url = "https://soundcloud.com/discover"
# driver = webdriver.Chrome()
# driver.get(my_url)
# html = driver.page_source
# soup = BeautifulSoup(html, "html.parser")
# link = soup.find_all("a", {
#     "class": "sc-link-secondary sc-link-light playableTile__usernameHeading audibleTile__usernameHeading sc-truncate sc-text-h4"})
#
# set_link = []
# set_user = []
# for item in link:
#     user_url = "https://soundcloud.com" + item.get("href")
#     if user_url not in set_link:
#         set_link.append(user_url)
#
# for user_url in set_link:
#     if len(set_user) > 1:
#         break;
#     driver.get(user_url)
#     while (True):
#         myElem = WebDriverWait(driver, 30).until(
#             EC.presence_of_element_located((By.CLASS_NAME, 'profileHeaderInfo__userName')))
#         if myElem is not None:
#             break;
#     html = driver.page_source
#     soup = BeautifulSoup(html, "html.parser")
#     user_name = soup.find("h2", {"class": "profileHeaderInfo__userName"})
#     k = [p.getText(strip=True) for p in user_name]
#     set_user.append([k[0], user_url])
#
#     # Get followers
#     follower_url = user_url + "/following"
#     driver.get(follower_url)
#
#     #Wait
#     wait(driver, 'userBadgeListItem__heading')
#
#     html = driver.page_source
#     soup = BeautifulSoup(html, "html.parser")
#     followers = soup.find_all("a", {"class": "userBadgeListItem__heading"})
#     for follower in followers:
#         if follower not in set_link:
#             set_link.append("https://soundcloud.com" + follower.get("href"))
#
#
#
# url_lst = [];
# for i in set_user:
#     url_lst.append(i[1])
#
# playlist = getPlaylists(url_lst)
# for url in playlist:
#     print(url)
# f_out = pd.DataFrame(playlist, columns=['User', 'Playlist', 'Track'])
# f_out.to_csv('playlist.csv', index=False, sep='\t')
# tup = ('144468830', '...', 'https://soundcloud.com/pkvpro123')
# set_user = set()
# set_user.add(tup)
# print(getTracksAPI(set_user))
# getTracksAPI(set_user)
# print(getTracks(set_user))
# print(getTracks(set_user))
# getTracks(set_user)

def getPlaylist(user_id, client_id, limit=50):
    playlists = []
    url = f'https://api-v2.soundcloud.com/users/{user_id}/playlists?client_id={client_id}&limit={limit}'
    r = requests.get(url)

    while r.status_code != requests.codes.ok or '"incomplete_results":true' in r:
        time.sleep(1)
        print('wait')
        r = requests.get(url)

    y = json.loads(r.text)
    if len(y['collection']) == 0:
        playlists.append([user_id, 'None', 'None'])
    else:
        for playlist in y['collection']:
            trackIDs = []
            for track in playlist['tracks']:
                trackIDs.append(str(track['id']))
            allTrackIDs = ','.join(trackIDs)
            playlists.append([user_id, str(playlist['id']), allTrackIDs])

    return playlists

#example
#print(getPlaylist('42255333', 'nGKlrpy2IotLQ0QGwBOmIgSFayis6H4e', 50))


def main():
    #get_user_name_id_and_url()
    my_client_id = 'FjnXkiGFvyaVIYtXadMm9pqIDawoxzUW'
    get_user_by_API(my_client_id)


if __name__ == '__main__':
    main()
