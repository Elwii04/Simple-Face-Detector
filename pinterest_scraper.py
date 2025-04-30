# pinterest_scraper.py
import re, time, argparse, sys, json
from pathlib import Path
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from db import DB

PIN_RE   = re.compile(r"^/pin/\d+/?$")
BOARD_RE = re.compile(r"^https?://[^/]+/[^/]+/.+")

def load_cookies(netscape_file: Path):
    """Return a RequestsCookieJar from a Netscape export (like cookies.txt)."""
    jar = requests.cookies.RequestsCookieJar()
    with netscape_file.open() as fh:
        for line in fh:
            if line.startswith("#") or not line.strip():
                continue
            domain, flag, path, secure, expiry, name, value = line.strip().split('\t')
            jar.set(name, value, domain=domain, path=path, secure=secure.upper()=="TRUE")
    return jar

class PinterestScraper:
    def __init__(self, cookies_file, db_path, rps=1, depth=1):
        self.db      = DB(db_path)
        self.session = requests.Session()
        self.session.cookies.update(load_cookies(Path(cookies_file)))
        self.delay   = 1.0 / max(rps, 0.1)
        self.depth   = depth
        self.host    = "https://de.pinterest.com"

    # ---------- helpers ----------
    def get(self, url):
        time.sleep(self.delay)
        r = self.session.get(url, timeout=15)
        r.raise_for_status()
        return r.text

    def pin_links_on_board(self, html):
        soup = BeautifulSoup(html, "lxml")
        for a in soup.select('div[data-test-id="pin"] a[href^="/pin/"]'):
            href = a.get("href")
            if href and PIN_RE.match(href):
                yield urljoin(self.host, href)

    def image_and_rec_links_on_pin(self, html):
        soup = BeautifulSoup(html, "lxml")
        # Main pin image via <meta property="og:image" …>
        og = soup.find("meta", property="og:image")
        if og and og.get("content"):
            yield "img", og["content"]

        # Recommendation area contains more /pin/ links
        for a in soup.select('a[href^="/pin/"]'):
            href = a.get("href")
            if href and PIN_RE.match(href):
                yield "rec", urljoin(self.host, href)

    # ---------- crawl ----------
    def crawl(self, start_url):
        # If user pasted a board URL, push all contained pins to the queue
        if BOARD_RE.match(start_url):
            board_html = self.get(start_url)
            for pin in self.pin_links_on_board(board_html):
                self.db.queue_pin(pin)
        elif PIN_RE.search(start_url):
            self.db.queue_pin(start_url)
        else:
            print("Unsupported start URL:", start_url)
            return

        # BFS up to self.depth
        level = 0
        while level <= self.depth:
            pin_url = self.db.next_unscanned_pin()
            if not pin_url:
                break

            try:
                html = self.get(pin_url)
            except Exception as e:
                print("Fetch error", pin_url, e, file=sys.stderr)
                self.db.mark_scanned(pin_url)
                continue

            for kind, link in self.image_and_rec_links_on_pin(html):
                if kind == "img":
                    self.db.store_image(link, pin_url)
                elif kind == "rec" and level < self.depth:
                    self.db.queue_pin(link)

            self.db.mark_scanned(pin_url)
            level += 1


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--url", required=True, help="Board or pin URL to start with")
    p.add_argument("--cookies", default="cookies.txt", help="Netscape cookie file")
    p.add_argument("--db", default="pinterest.db", help="SQLite output file")
    p.add_argument("--rps", type=float, default=1, help="Max requests per second")
    p.add_argument("--depth", type=int, default=1, help="Recursion depth (≥1)")
    args = p.parse_args()

    PinterestScraper(args.cookies, args.db, args.rps, args.depth).crawl(args.url)
