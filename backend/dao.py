import sqlite3
from threading import Lock


# Commit the transaction on success, rollback on failure + thread safety
class Ensure:
    def __init__(self, conn, lock):
        self.conn = conn
        self.lock = lock

        self.lock.acquire()

    def close(self):
        self.conn.close()

    def __enter__(self):
        return self.conn

    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            if exc_type:
                self.conn.rollback()
            else:
                self.conn.commit()
        except Exception:
            self.lock.release()
            raise


class Database:
    def __init__(self, db_path):
        conn = sqlite3.connect(db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row

        self.ensure = Ensure(conn, Lock())
        self.cur = conn.cursor()

        self._create()

    def _create(self):
        with self.ensure:
            self.cur.execute(
                "CREATE TABLE IF NOT EXISTS Users"
                "(discord_id TEXT UNIQUE NOT NULL PRIMARY KEY, psn_id TEXT NOT NULL,"
                "total INT, platinum INT, gold INT, silver INT, bronze INT)"
            )

    def set_id_to_psn(self, discord_id, psn_id):
        with self.ensure:
            self.cur.execute(
                "INSERT OR REPLACE INTO Users (discord_id, psn_id) VALUES((?), (?))",
                (
                    discord_id,
                    psn_id,
                ),
            )

    def get_id_to_psn_batch(self):
        with self.ensure:
            self.cur.execute("SELECT discord_id, psn_id FROM Users")

            return {
                result["discord_id"]: result["psn_id"]
                for result in self.cur.fetchall()
            }

    def set_id_to_trophies_batch(self, id_to_trophies):
        with self.ensure:
            for id, trophies in id_to_trophies.items():
                self.cur.execute(
                    "UPDATE Users SET total = (?), platinum = (?), gold = (?), silver = (?), bronze = (?)"
                    "WHERE discord_id = (?)",
                    (
                        trophies["total"],
                        trophies["platinum"],
                        trophies["gold"],
                        trophies["silver"],
                        trophies["bronze"],
                        id,
                    ),
                )

    def get_leaderboard(self):
        with self.ensure:
            self.cur.execute(
                "SELECT discord_id, total, platinum, gold, silver, bronze FROM Users ORDER BY total"
            )

            results = []

            for result in self.cur.fetchall():
                results.append({k: result[k] for k in result.keys()})

            return results

    def close(self):
        self.ensure.close()
