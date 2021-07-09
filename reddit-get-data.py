#### Analysis: Reddit banned accounts ####
""" In 2018 Reddit banned 944 accounts on suspicion of interference by the Russian government:
    https://www.reddit.com/r/announcements/comments/8bb85p/reddits_2017_transparency_report_and_suspect/
    The published list as of december 2019 has 939 usernames instead of 944
    A year later, it again banned 61 accounts however this time the target of the suspicious accounts was the UK Election of December 2019:
    https://www.reddit.com/r/redditsecurity/comments/e74nml
    In total 1,001 users were banned in these two banwaves
    This script scrapes the user accounts linked in these two posts in order to do a data analysis.  """

import json
import requests
import re
from datetime import datetime
import time
import os # used to get to the home directory cross platforms, "create data-files" directory

#global variables : url of posts, user-agent
# grab user-agent line from local file, see rules: https://github.com/reddit-archive/reddit/wiki/API
API_FILE = os.path.expanduser("~") + r"/.secrets/api/reddit-api.json"

# url of the posts
LINK_2018 = r"https://www.reddit.com/wiki/suspiciousaccounts" 
LINK_2019 = r"https://www.reddit.com/r/redditsecurity/comments/e74nml/"

# what data we want from reddit i.e the about page, submitted posts, comments etc.
user_data_attributes = ("about", "submitted", "comments", "gilded", "trophies")


# opening the credential files to get custom user-agent for the requests
# otherwise use a more generic line mentioning python
try:
    with open(API_FILE) as f:
        USER_AGENT = {"user-agent": json.load(f)["user_agent"]} 
except FileNotFoundError:
        USER_AGENT = {"user-agent": "python/praw6:someapi:v0.0.1"}



class get_users_data:
    """ class that takes url of the reddit posts and  creates a json file """
    def __init__(self, url):
        self.url = url
        
    def save_reddit_posts(self, filename):
        """ function that fetches reddit post  and returns a json file """
        response = requests.get(self.url + ".json?raw_json=1", headers=USER_AGENT)
        response_data = response.json()
        if not os.path.isdir("data-files"):
            os.mkdir("data-files")
        with open("data-files/" + filename, "w") as f:
            f.write(json.dumps(response_data, indent=2))


def extract_users_list(*args ):
    """ extracts a python list of reddit usernames from the json file of a reddit post 
    (listing or wikipage) """
    users_list = dict()
    for filename in args:
        try:
            with open(filename) as f:
                filedata = json.load(f)
                try:
                    # check if post is a reddit listing (2019 banwave)
                    if type(filedata) == list and filedata[0]["kind"].casefold() == "Listing".casefold():
                        # Adding the text of the post under an entry names after date of banning
                        banwave_date = datetime.fromtimestamp(filedata[0]["data"]["children"][0]["data"]["edited"]).strftime("%Y-%b-%d")
                        content = filedata[0]["data"]["children"][0]["data"]["selftext"]
                        # regex pattern to catch username only from the post, filter special chars at the end
                        pattern = r"(?<=user/).*?[^?/!\\)]*" \
                    
                    # check if it's a reddit "wikipage" (2018 banwave)
                    elif type(filedata) == dict and filedata["kind"].casefold() == "wikipage".casefold():
                        banwave_date = datetime.fromtimestamp(filedata["data"]["revision_date"]).strftime("%Y-%b-%d")
                        content = filedata["data"]["content_md"]
                        pattern = r"(?<=u/).*?[^\|]*"

                    # build the set of unique usernames using regex pattern
                    temp_users_list = sorted(set(re.findall(pattern, content)), key=str.casefold)
                    users_list[banwave_date] = temp_users_list

                except AttributeError:
                    print("Try another file with reddit json structure")

            # writing to the file
            if not os.path.isdir("data-files"):
                os.mkdir("data-files")
            with open("data-files/reddit-list-banned-users.json", "w") as f:
                f.write(json.dumps(users_list, indent=2))

        except FileNotFoundError:
            print(filename, "file not found")

def build_users_database(filename, *args):
    """ requests json files for all the users in the reddit-all-banned-users.json file 
        and saves all the data in a new file for analysis with pandas """
    
    all_users = []
    with open(filename) as f:
        data = json.load(f)
        for k,v in data.items():
            for e in v:
                # creates a tuple ("username", "banwave year") for each user
                all_users.append((e, k))

    # sorts through the tuples in a case insensitive manner
    all_users.sort(key=lambda x: x[0].casefold() )   
    
    # do requests based on the list
    start_time = datetime.now()
    print(f"Starting scraping data from {len(all_users)} Reddit users at {start_time}")
    user_data = {}

    for user, ban_year in all_users:
        # first fetch the json file corresponding to the username and the attribute in the list i.e "about", "submitted" pages
        for attr in args:
            response = requests.get("https://www.reddit.com/user/" + user + "/" + attr +  ".json?raw_json=1", headers = USER_AGENT) # using headers to avoid error 429 https://stackoverflow.com/questions/34539129/parsing-reddit-json-into-python-array-and-print-items-from-array

            if user not in user_data: #initialize the dictionary with first json data
                try:
                    user_data[user] = {attr:json.loads(response.text)["data"]} #filter to the level with desired data
                except KeyError:
                    print("Key Error:", user)

            else: # or update the dictionary entry 
                try:
                    user_data[user].update({attr:json.loads(response.text)["data"]})
                except KeyError:
                    print(f"Key Error: {user}. Maybe user was suspended.")

        # finally, add banwave year for later analysis
        user_data[user].update({"banwave_year": ban_year})

        # wait 10 seconds between API calls for each user: 
        # 60s / 10s delay * 5 requests for each users -> 30 rq/minute, reddit limit
        time.sleep(10.1) 
    
    # writing to the final file used for analysis
    if not os.path.isdir("data-files"):
        os.mkdir("data-files")

    with open("data-files/reddit-banned-users-DATA.json", "w") as f:
        f.write(json.dumps(user_data, indent=2))

    stop_time = datetime.now()
    print(f"Process finished at {stop_time}. It took {(stop_time - start_time)}")

""" getting the json data of the two reddit posts listing the banned users in 2018 and 2019,
    uncomment to execute """
# reddit_2018 = get_users_data(LINK_2018)
# reddit_2019 = get_users_data(LINK_2019)

#reddit_2018.save_reddit_posts("reddit-post-banning-users-2018.json")
#reddit_2019.save_reddit_posts("reddit-post-banning-users-2019.json")

""" extracting the 1000+ users from the json data of the two reddit posts, uncomment to execute"""
# extract_users_list("data-files/reddit-post-banning-users-2018.json","data-files/reddit-post-banning-users-2019.json")

""" fetching the data from all users in the list, takes 2hrs+ with delay between requests. Uncomment to execute"""
#build_users_database("data-files/reddit-list-banned-users.json", *user_data_attributes)