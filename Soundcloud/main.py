from selenium import webdriver
from bs4 import BeautifulSoup
import requests
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException

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
    if len(set_user) > 20:
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
    while (True):
        try:
            myElem = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CLASS_NAME, 'userBadgeListItem__heading')))
            if myElem is not None:
                break
        except TimeoutException:
            break

    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")
    followers = soup.find_all("a", {"class": "userBadgeListItem__heading"})
    for follower in followers:
        if follower not in set_link:
            set_link.append("https://soundcloud.com" + follower.get("href"))

for item in set_user:
    temp = item[1] + "/tracks"
    driver.get(temp)
    while (True):
        try:
            myElem = WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'profileHeaderInfo__userName')))
            if myElem is not None:
                break
        except TimeoutException:
            break;

    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")
    emptyTrack = soup.find("h3", {"class": "sc-type-large emptyNetworkPage__headline"})
    if emptyTrack is None:
        Track_list = soup.find_all("a", {"class": "sc-link-primary soundTitle__title sc-link-dark sc-text-h4"})
        string_track = ""
        for track in Track_list:
            string_track = string_track + track.getText().strip() + "\t"
        k = [p.getText(strip=True) for p in soup.find("h2", {"class": "profileHeaderInfo__userName"})]
        print(k[0] + ':' + '\t' + string_track)
    else:
        k = [p.getText(strip=True) for p in soup.find("h2", {"class": "profileHeaderInfo__userName"})]
        print(k[0] + ':' + '\t' + "None")