# db.py
import sqlite3, pathlib, datetime as dt

SCHEMA = """
CREATE TABLE IF NOT EXISTS image (
    url           TEXT PRIMARY KEY,
    source_url    TEXT,          -- board or pin page where we found it
    added_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS pin (
    url           TEXT PRIMARY KEY,
    scanned       INTEGER DEFAULT 0   -- 0 = queued, 1 = done
);
"""

class DB:
    def __init__(self, path="pinterest.db"):
        self.path = pathlib.Path(path)
        self.cn = sqlite3.connect(self.path)
        self.cn.executescript(SCHEMA)

    def already_seen(self, table, url):
        cur = self.cn.execute(f"SELECT 1 FROM {table} WHERE url=? LIMIT 1", (url,))
        return cur.fetchone() is not None

    def queue_pin(self, url):
        self.cn.execute("INSERT OR IGNORE INTO pin(url) VALUES (?)", (url,))
        self.cn.commit()

    def mark_scanned(self, url):
        self.cn.execute("UPDATE pin SET scanned=1 WHERE url=?", (url,))
        self.cn.commit()

    def store_image(self, url, source):
        self.cn.execute(
            "INSERT OR IGNORE INTO image(url, source_url) VALUES (?,?)",
            (url, source),
        )
        self.cn.commit()

    def next_unscanned_pin(self):
        cur = self.cn.execute("SELECT url FROM pin WHERE scanned=0 LIMIT 1")
        row = cur.fetchone()
        return row[0] if row else None
