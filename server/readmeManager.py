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

from math import sqrt
from generator.gen_monomatch_data import CardData
from xoshiro256ss import xoroshiro256ss
import numpy as np
import sympy
import os
import cbor2 as cbor # Using cbor to encode the data for the answers so people can't fudge it easily, has to be statically encoded so an issue can be opened even after the images refresh and still credit the user their points
import base64        # Base 64 encoding is used to make the data work with a gh issue
                     # Before the base64 it should be bit rotated by one fourth rounded down of the length of the cbor

# Cd to this dir for safety, ensure smooth running
abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)

def main(rng: xoroshiro256ss, cardData: CardData, imageCount: int):

