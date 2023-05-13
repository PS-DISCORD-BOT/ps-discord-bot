from dataclasses import dataclass

from psnawp_api import PSNAWP


@dataclass
class Trophies:
    trophy_count_level: int
    total: int
    platinum: int
    gold: int
    silver: int
    bronze: int


def trophy_fetcher(token: str):
    psnawp = PSNAWP(token)

    def fetch_trophy(user: str):
        user = psnawp.user(online_id=user)
        summary = user.trophy_summary()

        return Trophies(
            trophy_count_level=summary.trophy_level,
            total=sum(
                [
                    summary.earned_trophies.platinum,
                    summary.earned_trophies.gold,
                    summary.earned_trophies.silver,
                    summary.earned_trophies.bronze,
                ]
            ),
            platinum=summary.earned_trophies.platinum,
            gold=summary.earned_trophies.gold,
            silver=summary.earned_trophies.silver,
            bronze=summary.earned_trophies.bronze,
        )

    return fetch_trophy
