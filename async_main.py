import json
from collections import defaultdict
from bs4 import BeautifulSoup as Bs
from constants import headers, url, css_selector
from functools import partial
import multiprocessing
from aiohttp import ClientSession
import time
import asyncio

servers = ["EUW", "EUNE"]
wl_path = "english-words-master/words.txt"


def create_wordlist() -> set:
    """Creates set of clean english words."""

    with open(wl_path) as file:
        wordlist = {word.strip().lower() for word in file.readlines()}
    print("Created wordlist.")

    return wordlist


async def get_html(s: ClientSession, link: str, server: str) -> dict:
    """Fetches raw html from target server url."""
    print("Fetching {}...".format(server))
    link = link.format(server.lower())

    async with s.get(url=link, headers=headers) as r:
        html = await r.text()
        output = {
            "server": server,
            "html": html
        }

        print("Fetched {}".format(server))
        return output


def parse_html(wordlist: set, content: dict) -> None:
    """Processes raw html with BeautifulSoup."""
    html = content["html"]
    server = content["server"]

    soup = Bs(html, "html.parser")
    table = soup.select(css_selector)
    assert len(table) != 0

    print(f"Number of potential names: {len(table)}")

    data = []
    for row in table:

        # Get each summoner name and it's availability
        summoner_name = row.select_one("td > a").text.lower()
        availability = row.select("td")[1].select_one("span").text.strip()[0:-1]
        if summoner_name in wordlist:

            # Add (name, availability) to output list
            line = (availability, summoner_name)
            data.append(line)

    assert len(data) != 0

    print("Parsed {}".format(server))

    save_data(data, server)


def save_data(data, server) -> None:
    """Outputs data to json file."""
    # Transform data to dictionary {'days': [name, name...], ...}
    d = defaultdict(list)
    for k, v in data:
        d[k].append(v)

    with open(f"{server}.json", "w") as f:
        json.dump(d, f, indent=4)
    print("Saved {} json file.".format(server))


async def main():
    tasks = []
    async with ClientSession() as session:
        for server in servers:
            link = url.format(server)
            tasks.append(asyncio.create_task(get_html(session, link, server)))
        content = await asyncio.gather(*tasks)

    return content


if __name__ == '__main__':
    before = time.time()
    wl = create_wordlist()

    content = asyncio.get_event_loop().run_until_complete(main())

    pool = multiprocessing.Pool(4)
    func = partial(parse_html, wl)
    pool.map(func, content)
    pool.close()

    after = time.time()
    result = round(after - before, 2)
    print("Runtime: {}s".format(result))
