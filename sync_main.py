from constants import headers, url, css_selector, servers
from bs4 import BeautifulSoup as Bs
from collections import defaultdict
import requests
import json
import time


def create_wordlist(wl_path="english-words-master/words.txt") -> set:
    """Creates set of clean english words."""

    with open(wl_path) as file:
        wordlist = {word.strip().lower() for word in file.readlines()}
    print("Created wordlist.")

    return wordlist


def get_html(link: str, s: requests.Session, server: str) -> str:
    # GET THE TARGET SERVER UPCOMING NAMES PAGE
    print(f"Accessing {server} server page...")

    r = s.get(link, params=headers)
    r.raise_for_status()
    html = r.text
    print("Page loaded successfully.")

    return html


def parse_html(html: str, wordlist: set, server: str) -> list:
    # PROCESS THE RESPONSE WITH BEAUTIFUL SOUP
    soup = Bs(html, "html.parser")
    table = soup.select(css_selector)
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

    return data


def save_data(data: list, server: str) -> None:
    # TRANSFORM OUTPUT LIST TO DICTIONARY
    d = defaultdict(list)
    for k, v in data:
        d[k].append(v)

    # WRITE OUTPUT TO JSON FILE
    print("Saving as JSON file...")
    with open(f"{server}.json", "w") as file:
        json.dump(d, file, indent=4)


session = requests.Session()
wl = create_wordlist()

total_time = 0
for server in servers:
    before = time.time()

    # GET THE TARGET SERVER HTML PAGE
    html = get_html(link=url.format(server.lower()), s=session, server=server)

    # PROCESS THE RESPONSE WITH BEAUTIFUL SOUP
    data = parse_html(html, wl, server)

    # TRANSFORM OUTPUT LIST TO DICTIONARY
    save_data(data, server)

    # ADD TO TOTAL TIME
    after = time.time()
    time_spent = round(after - before, 2)
    total_time += time_spent
    print(f"DONE. (Time passed {time_spent}s)\n")

print(f"Finished in {round(total_time, 2)}s.")