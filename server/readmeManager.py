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

import asyncio
from datetime import date, datetime
from math import sqrt
import sched
import shutil
from generator.gen_monomatch_data import CardData
from xoshiro256ss import xoroshiro256ss
import numpy as np
import sympy
import os
import cbor2 as cbor # Using cbor to encode the data for the answers so people can't fudge it easily, has to be statically encoded so an issue can be opened even after the images refresh and still credit the user their points
import base64        # Base 64 encoding is used to make the data work with a gh issue
                     # Before the base64 it should be bit rotated by one fourth rounded down of the length of the cbor
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import warnings
warnings.filterwarnings("ignore", module="apscheduler") # Fix the warnings from the apscheduler's bad code
import generator.gen_image as genIm
from tqdm import tqdm
from PIL import Image

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

Just find the icon they share, and then scroll below the cards and click the correct icon. It will open a github issue with some text in the body, just submit it and it will be renamed+body changed to indicate your current score and if you got it correct. The bot can only make 5000 requests an hour due to ratelimits so it's only going to be able to handle ~4990 answers an hour.

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

def update_readme(rng: xoroshiro256ss, cardData: CardData, imageCount: int):
    print(f"[{datetime.now().strftime('%d.%b %Y %H:%M:%S')}] readme")

def update_cards(rng: xoroshiro256ss, cardData: CardData, imageCount: int):
    shutil.rmtree("cards", ignore_errors=True)
    os.mkdir("cards")

    card1_num = rng.next()%np.uint64(len(cardData.card_data))
    card2_num = rng.next()%np.uint64(len(cardData.card_data))

    print (f"card1: {card1_num}\ncard2: {card2_num}")

    print("Get data")
    card1 = cardData.card_data[card1_num]
    card2 = cardData.card_data[card2_num]

    print(f"card1: {card1}\ncard2: {card2}")

    print("Gen images")
    card1_im = genIm.Card.generateImage(card1, imageCount, outDimension=2048).cardImage.quantize(256)
    card2_im = genIm.Card.generateImage(card2, imageCount, outDimension=2048).cardImage.quantize(256)

    print("Save images")
    card1_im.save(f"cards/0.png", optimize=True)
    card1_im.save(f"cards/0.jpg", optimize=True)
    card2_im.save(f"cards/1.png", optimize=True)
    card2_im.save(f"cards/1.jpg", optimize=True)
    print(f"[{datetime.now().strftime('%d.%b %Y %H:%M:%S')}] cards")

def main(rng: xoroshiro256ss, cardData: CardData, imageCount: int):
    update_cards(rng, cardData, imageCount)

    scheduler = AsyncIOScheduler()
    scheduler.add_job(update_readme, 'cron', kwargs={"rng": rng, "cardData": cardData, "imageCount": imageCount}, minute="10-50/10")
    scheduler.add_job(update_cards, 'cron', kwargs={"rng": rng, "cardData": cardData, "imageCount": imageCount}, minute="0")
    scheduler.start()

    scheduler._eventloop.run_forever()


if __name__ == "__main__":
    main(xoroshiro256ss(), CardData.generateCardDataByCards(500), 0)
