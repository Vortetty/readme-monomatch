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

import gen_monomatch_data
import gen_image
import os, shutil
from tqdm import tqdm
import warnings

warnings.filterwarnings("ignore", module="tqdm")

if __name__ == "__main__":
    print("Generating cards...")
    data = gen_monomatch_data.CardData.generateCardDataByDimension(5)
    print("Generating images...")
    shutil.rmtree("cards", ignore_errors=True)
    os.mkdir("cards")
    cardBar = tqdm(total=1, unit="step(s)", desc=f"Generating card", position=1, unit_scale=True)
    for num,i in tqdm(enumerate(data.card_data), total=len(data.card_data), unit="card(s)", desc="Generating cards", position=0):
        cardBar.reset()
        card = gen_image.Card.generateImage(i, data.symbol_count, tqdmBar=cardBar)
        card.cardImage.save(f"./cards/{num}.png")
    print("Done!")
