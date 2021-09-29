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


def create_wordlist() -> set:
    # CREATE ENGLISH LANGUAGE WORDLIST SET
    print("Creating wordlist...")
    with open("english-words-master/words.txt") as file:
        wordlist = {word.strip().lower() for word in file.readlines()}
    print("DONE.\n")

    return wordlist


async def get_html(s: ClientSession, link: str, server: str) -> dict:
    # TODO aiohttp module session
    # before = time.time()
    print("Fetching {}...".format(server))
    link = link.format(server.lower())
    # print(link)
    async with s.get(url=link, headers=headers) as r:
        html = await r.text()
        output = {
            "server": server,
            "html": html
        }
        # after = time.time()
        # result = round(after - before, 2)
        # print("Scraping of {} took: {}s".format(server, result))

        # await parse_html(html.decode(), server)
        print("Fetched {}".format(server))
        return output


def parse_html(wordlist: set, content: dict) -> None:
    # PROCESS THE RESPONSE WITH BEAUTIFUL SOUP
    html = content["html"]
    server = content["server"]
    print("Parsing {}...".format(server))
    soup = Bs(html, "html.parser")
    table = soup.select(css_selector)
    # print(f"Number of potential names: {len(table)}")
    assert len(table) != 0

    data = []
    # print("Fetching names...")
    for row in table:

        # GET EACH SUMMONER NAME AND IT's AVAILABILITY
        summoner_name = row.select_one("td > a").text.lower()
        availability = row.select("td")[1].select_one("span").text.strip()[0:-1]
        if summoner_name in wordlist:

            # ADD NAME, AVAILABILITY TUPLE TO OUTPUT LIST
            line = (availability, summoner_name)
            data.append(line)
    assert len(data) != 0
    # print(f"Number of {server} names fetched: {len(data)}")
    # after = time.time()
    # result = round(after - before, 2)
    # print("Parsing data for {} took: {}s".format(server, result))
    print("Parsed {}".format(server))

    save_data(data, server)


def save_data(data, server) -> None:
    # TRANSFORM OUTPUT LIST TO DICTIONARY
    d = defaultdict(list)
    for k, v in data:
        d[k].append(v)

    # WRITE OUTPUT TO JSON FILE
    # print("Saving as JSON file...")
    with open(f"{server}.json", "w") as f:
        json.dump(d, f, indent=4)


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
