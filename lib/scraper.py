import sys
from dataclasses import dataclass

from bs4 import BeautifulSoup

from lib.utils import perform_request

BASE_URL = "https://psnprofiles.com"


@dataclass
class Trophies:
    trophy_count_level: int
    total: int
    platinum: int
    gold: int
    silver: int
    bronze: int


def scrape_trophies(content: str):
    soup = BeautifulSoup(content, "html.parser")

    user_bar = soup.find(id="user-bar")

    def find_count(class_):
        result = user_bar.find("li", class_=class_).text.strip()
        # '1,024' -> 1024
        return int(result.replace(",", ""))

    return Trophies(
        trophy_count_level=find_count("icon-sprite level"),
        total=find_count("total"),
        platinum=find_count("platinum"),
        gold=find_count("gold"),
        silver=find_count("silver"),
        bronze=find_count("bronze"),
    )


def fetch_trophies(user: str):
    content = perform_request(BASE_URL + f"/{user}")
    return scrape_trophies(content)


if __name__ == "__main__":
    print(fetch_trophies(sys.argv[1]))
