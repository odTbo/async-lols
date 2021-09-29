import requests
import json
from collections import defaultdict
from bs4 import BeautifulSoup as Bs
from constants import headers, servers
import time

# CREATE ENGLISH LANGUAGE WORDLIST SET
print("Creating wordlist...")
with open("english-words-master/words.txt") as file:
    wordlist = {word.strip().lower() for word in file.readlines()}
print("DONE.\n")
# HEADERS FOR "lols.gg" HTTP REQUEST


session = requests.Session()

# SERVERS YOU WANT TO TARGET
servers = ["EUW", "EUNE", "NA", "TR"]
total_time = 0
for server in servers:
    before = time.time()
    print(f"Accessing {server} server page...")
    url = f"https://lols.gg/en/name/lists/{server.lower()}/All%20Upcoming%20Names/Only%20letters/"

    # GET THE TARGET SERVER UPCOMING NAMES PAGE
    response = session.get(url, params=headers)
    response.raise_for_status()
    website = response.text
    print("Page loaded successfully.")

    # PROCESS THE RESPONSE WITH BEAUTIFUL SOUP
    soup = Bs(website, "html.parser")
    table = soup.select("#kt_content > div > div > div > div > div > div > div > table > tbody > tr")
    print(f"Number of potential names: {len(table)}")

    data = []
    print("Fetching names...")
    for row in table:

        # GET EACH SUMMONER NAME AND IT's AVAILABILITY
        summoner_name = row.select_one("td > a").text.lower()
        availability = row.select("td")[1].select_one("span").text.strip()[0:-1]

        if summoner_name in wordlist:

            # ADD NAME, AVAILABILITY TUPLE TO OUTPUT LIST
            line = (availability, summoner_name)
            data.append(line)
    print(f"Number of {server} names fetched: {len(data)}")

    # TRANSFORM OUTPUT LIST TO DICTIONARY
    d = defaultdict(list)
    for k, v in data:
        d[k].append(v)

    # WRITE OUTPUT TO JSON FILE
    print("Saving as JSON file...")
    with open(f"{server}.json", "w") as file:
        json.dump(d, file, indent=4)

    # ADD TO TOTAL TIME
    after = time.time()
    time_spent = round(after - before, 2)
    total_time += time_spent
    print(f"DONE. (Time passed {time_spent}s)\n")
print(f"Finished in {round(total_time, 2)}s.")