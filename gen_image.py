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

if __name__ == "__main__":
    print("This is a library. It should not be run directly.")
    exit(1)

from io import BytesIO
from itertools import combinations
from turtle import dot
from types import NoneType
from xmlrpc.client import Boolean
import poisson_disc as pd
import numpy as np
from PIL import Image, ImageDraw
import cairosvg as csvg
import colorsys
import smallestenclosingcircle as sec
from tqdm import tqdm

class dummyTqdm:
    def __init__(self, *args, **kwargs):
        pass

class Card:
    def __init__(self, cardData: list, cardSymbolCount: int, deckSymbolCount: int, cardImageDimensions: tuple, cardImage: Image.Image, cardFgImage: Image.Image, cardBgImage: Image.Image, givenDotSpacingMult: int):
        self.cardData = cardData
        self.cardSymbolCount = cardSymbolCount
        self.deckSymbolCount = deckSymbolCount
        self.cardImageDimensions = cardImageDimensions
        self.cardImage = cardImage
        self.cardFgImage = cardFgImage
        self.cardBgImage = cardBgImage
        self.givenDotSpacingMult = givenDotSpacingMult

    @classmethod
    def generateImage(cls, cardData: list, symbolCount: int, outDimension: int=4096, dotSpacingMult: int=128, enableDebugPrint: Boolean|int=False, tqdmBar: tqdm|NoneType=None):
        CARD_DATA = [
            [j, i]
            for i,j in enumerate(cardData)
        ]
        SYMBOL_COUNT = symbolCount
        RAINBOW_SIZE = 128
        SCRAMBLE_RAINBOW = False
        OUT_DIMENSION = outDimension
        #OUT_FILE = "monomatch.png"

        REQUIRED_DOTS = len(CARD_DATA)
        TMP_SEED = hash(tuple(map(lambda x:x[0], CARD_DATA))) % (2**32)
        np.random.seed(TMP_SEED)

        def dotDistance(a: np.array, b: np.array) -> float:
            return np.linalg.norm(a - b)
        def checkDotInCircle(dot: np.array, center: np.array, radius: float) -> bool:
            return dotDistance(dot, center) < radius
        def countDotsInCircle(dots: np.array, center: np.array, radius: float) -> int:
            count = 0
            for i in dots:
                count += checkDotInCircle(i, center, radius)
            return count
        def normalizePoints(data):
            return (data - np.min(data)) / (np.max(data) - np.min(data))
        tqdmBar.update(0.1)

        disks = sorted(list(pd.Bridson_sampling(
            radius = dotSpacingMult/OUT_DIMENSION,
            k = 100
        )), key=lambda x: dotDistance(x, (0.5, 0.5)))
        tqdmBar.update(0.2)

        circleSize = 128/OUT_DIMENSION
        circleIncreaseInterval = 128/(OUT_DIMENSION*2)

        while countDotsInCircle(disks, np.array([0.5, 0.5]), circleSize) < REQUIRED_DOTS:
            circleSize += circleIncreaseInterval

        while countDotsInCircle(disks, np.array([0.5, 0.5]), circleSize) > REQUIRED_DOTS:
            circleSize -= circleIncreaseInterval/8

        circleSize += circleIncreaseInterval/8

        goodDisks = []
        almostGoodDisks = []
        badDisks = []
        for i in disks:
            if checkDotInCircle(i, np.array([0.5, 0.5]), circleSize):
                if len(goodDisks) < REQUIRED_DOTS:
                    goodDisks.append(i)
                else:
                    almostGoodDisks.append(i)
            else:
                badDisks.append(i)
        tqdmBar.update(0.1)

        fg_im = Image.new('RGBA', (OUT_DIMENSION+10, OUT_DIMENSION+10), (0, 0, 0, 0))
        draw = ImageDraw.Draw(fg_im)
        normalGoodDisks = sorted(list(normalizePoints(goodDisks)), key=lambda x: dotDistance(x, (0.5, 0.5))) # Ensure sorted by distance(they should be but i want to be sure for reproducibility)
        idealDiskSize = min(map(
            lambda x:dotDistance(x[0], x[1]),
            combinations(normalGoodDisks, 2),
        ))*(OUT_DIMENSION/2)/2

        if (enableDebugPrint): print(f"Generated {len(disks)} dots and {len(goodDisks)+len(almostGoodDisks)}/{REQUIRED_DOTS} are in the circle with {len(almostGoodDisks)} pruned from the edge.")

        COLORS = [
            tuple(int(i) for i in colorsys.hsv_to_rgb(i/RAINBOW_SIZE*360, .5, 1)*np.array([255, 255, 255])) for i in range(RAINBOW_SIZE)
        ]
        if SCRAMBLE_RAINBOW:
            np.random.shuffle(COLORS)
        tqdmBar.update(0.1)

        def recolorImage(im: Image.Image, color: tuple):
            im = im.convert('RGBA')
            data = np.array(im)
            red, green, blue, alpha = data.T
            black_areas = (alpha != 0)
            data[..., :-1][black_areas.T] = color
            im = Image.fromarray(data)
            return im

        def importSvg(id: int):
            with BytesIO() as f:
                csvg.svg2png(url=f"./symbols/{id}.svg", write_to=f, output_height=idealDiskSize*4)
                im = Image.open(f)
                im = im.crop(im.getbbox())
                im = im.rotate(np.random.randint(0, 359), Image.BICUBIC, expand=True)
                tmpSize = max(64, np.random.randint(idealDiskSize/2+32, idealDiskSize*2-32))
                im = im.resize((tmpSize, tmpSize), Image.LANCZOS)
                im = recolorImage(im, COLORS[id%len(COLORS)])
                if (enableDebugPrint): print(f"Imported {id} with color {COLORS[id%len(COLORS)]}")
                return im

        CARD_IMAGES = {
            j: [importSvg(i), tqdmBar.update(0.3/len(CARD_DATA))][0] for i,j in CARD_DATA
        }

        cardIconPositions = [
            (
                int(disk[0]*(OUT_DIMENSION/2)+((OUT_DIMENSION/2)/2)-idealDiskSize),
                int(disk[1]*(OUT_DIMENSION/2)+((OUT_DIMENSION/2)/2)-idealDiskSize)
            ) for disk in normalGoodDisks
        ]

        #draw.ellipse((2048-(circleSize*2048+1024)-64, 2048-(circleSize*2048+1024)-64, 2048+(circleSize*2048+1024)+64, 2048+(circleSize*2048+1024)+64), outline=(128, 128, 128), fill=(64, 64, 64), width=16)
        for pos, image in zip(cardIconPositions, map(lambda x:x[1], CARD_DATA)):
            #draw.ellipse((disk[0]*2048+1024-idealDiskSize, disk[1]*2048+1024-idealDiskSize, disk[0]*2048+1024+idealDiskSize, disk[1]*2048+1024+idealDiskSize), fill=(0, 128, 0))
            fg_im.paste(CARD_IMAGES[image], pos, CARD_IMAGES[image])
        #for disk in almostGoodDisks:
        #    draw.ellipse((disk[0]*2048+1024-idealDiskSize, disk[1]*2048+1024-idealDiskSize, disk[0]*2048+1024+idealDiskSize, disk[1]*2048+1024+idealDiskSize), fill=(256, 256, 0, 255))
        #for disk in badDisks:
        #    draw.ellipse((disk[0]*2048+1024-idealDiskSize, disk[1]*2048+1024-idealDiskSize, disk[0]*2048+1024+idealDiskSize, disk[1]*2048+1024+idealDiskSize), fill=(128, 0, 0, 255))
        cropCircle = sec.make_circle(cardIconPositions)
        if (enableDebugPrint): print(cropCircle)
        tqdmBar.update(0.15)

        canvasCircleInnerDiam = (OUT_DIMENSION-int(128/4096*OUT_DIMENSION))
        canvasCircleCorrectedDiam = int(canvasCircleInnerDiam-int(128/4096*OUT_DIMENSION)/2)
        #circleInsideSize = int(canvasCircleInnerRadius*np.sqrt(2)) # Diameter not radius

        fg_im = fg_im.crop(
            (
                cropCircle[0]-(cropCircle[2]+(idealDiskSize*2-32)),
                cropCircle[1]-(cropCircle[2]+(idealDiskSize*2-32)),
                cropCircle[0]+(cropCircle[2]+(idealDiskSize*2-32)),
                cropCircle[1]+(cropCircle[2]+(idealDiskSize*2-32))
            )
        ).resize(
            (canvasCircleCorrectedDiam, canvasCircleCorrectedDiam),
            Image.LANCZOS
        )
        fg_im = fg_im.crop(
            fg_im.getbbox()
        )
        #fg_im_square_canvas = Image.new('RGBA', (max(fg_im.size), max(fg_im.size)), (0, 0, 0, 0))
        #fg_im_square_canvas.paste(fg_im, ((max(fg_im.size)-fg_im.size[0])//2, (max(fg_im.size)-fg_im.size[1])//2))
        #fg_im_square_canvas = fg_im_square_canvas.resize((circleInsideSize, circleInsideSize), Image.LANCZOS)
        finished_fg = Image.new('RGBA', (OUT_DIMENSION, OUT_DIMENSION), (0, 0, 0, 0))
        finished_fg.paste(fg_im, ((OUT_DIMENSION-fg_im.size[0])//2, (OUT_DIMENSION-fg_im.size[1])//2))
        #finished_fg.paste(fg_im_square_canvas, ((OUT_DIMENSION-circleInsideSize)//2, (OUT_DIMENSION-circleInsideSize)//2))
        #finished_fg = visual_center.visuallyCenter(finished_fg, (40, 42, 54))
        tqdmBar.update(0.05/3)

        bg_im = Image.new('RGBA', (OUT_DIMENSION, OUT_DIMENSION), (0, 0, 0, 0))
        bg_draw = ImageDraw.Draw(bg_im)
        bg_draw.ellipse((0, 0, OUT_DIMENSION, OUT_DIMENSION), fill=(40, 42, 54), outline=(30, 32, 44), width=int((128/4096*OUT_DIMENSION)/2))
        tqdmBar.update(0.05/3)

        fullImage = Image.new('RGBA', (OUT_DIMENSION, OUT_DIMENSION), (0, 0, 0, 0))
        fullImage.paste(bg_im, (0, 0))
        fullImage.paste(finished_fg, (0, 0), mask=finished_fg)
        tqdmBar.update(0.05/3)

        return Card(
            CARD_DATA,
            len(CARD_DATA),
            SYMBOL_COUNT,
            (OUT_DIMENSION, OUT_DIMENSION),
            fullImage,
            finished_fg,
            bg_im,
            dotSpacingMult
        )
