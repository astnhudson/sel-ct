import os
from time import sleep
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException

s = sleep
episode_code = ""
show_name_here = "" # Insert show name here
link = "" # Insert link to show here
series_links = []

# Set the default download directory
chrome_options = webdriver.ChromeOptions()
prefs = {'download.default_directory' : os.getcwd()}
chrome_options.add_experimental_option('prefs', prefs)

# Install the webdriver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

# Check to see if a button exists and continue clicking it until it disappears.
# This allows all episode links to be loaded.
def check_exists_button(button):
    try:
        driver.find_element(By.XPATH, button).click()
        s(2)
        check_exists_button(button)
    except NoSuchElementException:
        return False
    return True

driver.get(link)
s(2)
driver.find_element(By.ID, 'onetrust-reject-all-handler').click()

check_exists_button('/html/body/div[1]/div[2]/main/div[2]/div/div[2]/div[2]/div/div[2]/div[3]/button')

# Grid element which houses all the episode links we need for concatenation.
show_grid = driver.find_element(By.XPATH, "/html/body/div[1]/div[2]/main/div[2]/div/div[2]/div[2]/div/div[2]/div[2]")
soup = BeautifulSoup(show_grid.get_attribute('innerHTML'), features="html.parser")

# For each anchor in the HTML, we find the href text and concatenate it to make a fully functional link.
# We then save it to a file
for link in soup.find_all('a'):
    concat_link = "https://www.ceskatelevize.cz" + link.attrs['href'] + "\n"
    series_links.append(concat_link)

with open(show_name_here + ".txt", 'w', encoding='UTF8') as episode_links:
    episode_links.writelines(series_links)
    print("Successfully saved links here: " + os.getcwd() + "\\" + show_name_here + ".txt")

# Open a link to each subtitle file
# Rename the downloaded file to the episode name
# The sleep function is a terrible choice and this should be optimized with waiting for the element to load.
incident_count = 0
for i in series_links:
    driver.get(i)
    s(3)

    # Find the episode's title
    try:
        show_title = driver.find_element(By.XPATH,
                                         "/html/body/div[1]/div[2]/main/div[2]/div/div[1]/div/section[1]/div[1]/h1")
        title = show_title.text
    except NoSuchElementException:
        try:
            show_title = driver.find_element(By.XPATH,
                                             "/html/body/div[1]/div[2]/main/div[2]/div/div[1]/div/section[2]/div[1]/h1")
        except NoSuchElementException:
            print("No element exists. XPath is wrong.")
        except StaleElementReferenceException:
            print("Stale element here, not sure what to do.")
    episode_code = i.split('/')[-2]
    subtitle_file = "https://imgct.ceskatelevize.cz/cache/data/ivysilani/subtitles/{0}/{1}/sub.vtt".format(episode_code[
                                                                                                           0:3],
                                                                                                           episode_code)
    driver.get(subtitle_file)
    s(3)

    try:
        os.replace("sub.vtt", title + " - " + show_name_here + ".vtt")
    except FileNotFoundError:
        print("File doesn't exist.")
        with open(title + " - " + episode_code + ".txt", "x", encoding='UTF8'):
            incident_count += 1
    s(1)
print("All done. Incidents encountered = " + str(incident_count))
