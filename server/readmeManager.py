# Copyright 2022 Winter/Vortetty
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#     http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from datetime import date, datetime
from math import sqrt
import sched
from generator.gen_monomatch_data import CardData
from xoshiro256ss import xoroshiro256ss
import numpy as np
import sympy
import os
import cbor2 as cbor # Using cbor to encode the data for the answers so people can't fudge it easily, has to be statically encoded so an issue can be opened even after the images refresh and still credit the user their points
import base64        # Base 64 encoding is used to make the data work with a gh issue
                     # Before the base64 it should be bit rotated by one fourth rounded down of the length of the cbor
from apscheduler.schedulers.background import BackgroundScheduler
import signal

# Cd to this dir for safety, ensure smooth running
abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)

readmeData = """# Hey, i'm Kali!

Just a trans girl programming in my free time

## Directory

1. [About me](#a-bit-more-about-me)
2. [Summary](#summary)
3. [Monomatch Game](#monomatch)

## A bit more about me

```python
class basicPronoun():
    def __init__(self, sub, obj):
        self.subjective = sub
        self.objective = obj

kali = {{
    "pronouns": [
        basicPronoun("it", "its"),
        basicPronoun("she", "her"),
        basicPronoun("they", "them"),
    ],
    "names": [ "Kali", "Winter", "Tæmt modʒiɹæ", "Vortetty" ]
    "languages": {{
        "natural": [ "english" ],
        "computer": [ "python", "c++", "kotlin", "java", "javascript", "c#", "html", "css" ]
    }},
    "current_focus": "Random projects for fun",
    "fun_fact": "Knowing what to search is half of the battle"
}}
```

## Summary

![trophy](https://github-profile-trophy.vercel.app/?username=vortetty&theme=dracula)

![Winter's GitHub stats](https://github-readme-stats.vercel.app/api?username=vortetty&theme=dracula&show_icons=true)

![Winter's Top Langs](https://github-readme-stats.vercel.app/api/top-langs/?username=vortetty&layout=compact&langs_count=10&theme=dracula)

![Winter's wakatime stats](https://github-readme-stats.vercel.app/api/wakatime?username=vortetty&theme=dracula)

## Monomatch

Keep in mind this is a WIP, still in testing.

### How to play

Each card has {icon_count} icons, and only shares one symbol with the other card.

Symbols may be a different size, may be rotated differently, but the color and shape are the same.

Just find the icon they share, and then scroll below the cards and click the correct icon. It will open a github issue with some text in the body, just submit it and it will be given a tag.

top 100 scores update every 10 minutes, and the cards change hourly. If you don't finish the card set within the hour you can still finish it as long as you don't reload the page, it will still be scored properly (card metadata is stored in the link).

| Card 1       | Card 2       |
| :----------: | :----------: |
| {card1_link} | {card2_link} |

{answer_table}

### Top 25

{top_score_table}

### Recent scores

{recent_score_table}
"""

def update_readme():
    print(f"[{datetime.now().strftime('%d.%b %Y %H:%M:%S')}] readme")

def update_cards():
    print(f"[{datetime.now().strftime('%d.%b %Y %H:%M:%S')}] cards")

def main(rng: xoroshiro256ss, cardData: CardData, imageCount: int):
    scheduler = BackgroundScheduler()
    signal.signal(signal.SIGINT, lambda: scheduler.shutdown())
    signal.signal(signal.SIGTERM, lambda: scheduler.shutdown())
    scheduler.add_job(update_readme, 'cron', minute="10-50/10")
    scheduler.add_job(update_cards, 'cron', minute="0")
    scheduler.start()


if __name__ == "__main__":
    main(xoroshiro256ss(), CardData(0, 0, [], 0), 0)
