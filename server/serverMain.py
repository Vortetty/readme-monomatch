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

import server.githubIssueManager as server
import readmeManager as readme
import flaskImageProviderApp as fipa
import multiprocessing as mp

from generator.gen_monomatch_data import CardData
from xoshiro256ss import xoroshiro256ss
import sympy
from math import sqrt
import os

imageCount = len(filter(lambda x:x.endswith(".svg"), os.listdir("generator/symbols")))
rng = xoroshiro256ss()
cardData = CardData.generateCardDataByDimension(
    sympy.ntheory.generate.prevprime(sqrt(imageCount-sqrt(imageCount)-1)) # The symbol count has been consistently following approximately this pattern
)

if __name__ == "__main__": # Windows is dumb and mp needs a guard
    mp.freeze_support()    # Windows needs this too
    p1 = mp.Process(target=server.main, args=[rng, cardData, imageCount])
    p1.start()
    p2 = mp.Process(target=readme.main, args=[rng, cardData, imageCount])
    p2.start()
    p3 = mp.Process(target=fipa.main, args=[rng, cardData, imageCount])
    p3.start()