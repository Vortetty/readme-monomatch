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

# Single threaded, could be improved with multiprocessing but until I need it, I'll stick to this.

from io import BytesIO
import os
import colorsys
from pickletools import optimize
from tqdm import tqdm
import shutil
import numpy as np
from PIL import Image
import cairosvg as csvg
import multiprocessing as mp

def sizeof_fmt(num, suffix="B"):
    for unit in ["", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"]:
        if abs(num) < 1024.0:
            return f"{num:3.1f}{unit}{suffix}"
        num /= 1024.0
    return f"{num:.1f}Yi{suffix}"
COLORS = [
    tuple(int(i) for i in colorsys.hsv_to_rgb(i/128*360, .5, 1)*np.array([255, 255, 255])) for i in range(128)
]
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
        csvg.svg2png(url=f"./symbols/{id}.svg", write_to=f, output_height=512)
        im = Image.open(f)
        im = im.crop(im.getbbox())
        im = recolorImage(im, COLORS[id%len(COLORS)])
        return im
def genImages(fileList: list, threadNum: int, offset: int):
    for i,file in tqdm(enumerate(fileList), total=len(fileList), unit="file(s)", desc=f"Generating files (T-{hex(threadNum+1).upper().replace('X', 'x')})", position=threadNum, leave=False):
        shutil.copyfile(f"in_symbols/{file}", f"symbols/{i+offset}.svg")
        im = importSvg(i+offset)
        im.save(f"symbols/png/{i+offset}.png", optimize=True)
        im.convert("RGBA").save(f"symbols/webp/{i+offset}.webp", lossless=True, method=6, quality=100)

def genImagesMP(j):
    genImages(*j)

if __name__ == "__main__": # Windows is dumb and mp needs a guard
    mp.freeze_support()    # Windows needs this too
    tqdm.set_lock(mp.RLock()) # Output contention fix
    abspath = os.path.abspath(__file__)
    dname = os.path.dirname(abspath)
    os.chdir(dname)

    shutil.rmtree("symbols", ignore_errors=True)
    os.mkdir("symbols")
    os.mkdir("symbols/png")
    os.mkdir("symbols/webp")

    svgFiles = [f for f in os.listdir("in_symbols") if f.endswith(".svg")]
    fileCount = len(svgFiles)
    fullSvgFiles = [list(i) for i in np.reshape(svgFiles[:-(fileCount%10)], (10, -1))]
    lastSvgFiles = svgFiles[-(fileCount%10):]

    for i,j in enumerate(lastSvgFiles):
        fullSvgFiles[i%10].append(j)

    k = 0
    def getThing(i):
        global k
        l = [i[1], i[0], k]
        k += len(i[1])
        return l

    #processes = []

    #for i in reversed(list(enumerate(fullSvgFiles))):
    #    p = mp.Process(target=genImages, args=getThing(i))
    #    p.start()
    #    processes.append(p)

    #for i in processes:
    #    i.join()

    pool = mp.Pool(processes=10, initializer=tqdm.set_lock, initargs=(tqdm.get_lock(),))
    pool.map(genImagesMP, [getThing(i) for i in enumerate(fullSvgFiles)])



    fileCount = len(svgFiles)
    print(f"Processed {fileCount} SVG files")

    #
    # Calculate the size of each file and display total
    #
    svgFiles = [f for f in os.listdir("symbols") if f.endswith(".svg")]
    pngFiles = [f for f in os.listdir("symbols/png") if f.endswith(".png")]
    webpFiles = [f for f in os.listdir("symbols/webp") if f.endswith(".webp")]
    svgFilesize = sum([os.path.getsize(os.path.join(dname, "symbols", f)) for f in svgFiles])
    pngFilesize = sum([os.path.getsize(os.path.join(dname, "symbols/png", f)) for f in pngFiles])
    webpFilesize = sum([os.path.getsize(os.path.join(dname, "symbols/webp", f)) for f in webpFiles])
    print("\nFilesizes:")
    print(f"  Size of SVGs: {sizeof_fmt(svgFilesize)}")
    print(f"  Size of PNGs: {sizeof_fmt(pngFilesize)}")
    print(f"  Size of WebPs: {sizeof_fmt(webpFilesize)}")
    print(f"  Total size: {sizeof_fmt(svgFilesize+pngFilesize+webpFilesize)}")

    if hasattr(os, 'statvfs'):  # POSIX
        def disk_usage(path):
            if path == True: return True
            st = os.stat(path)
            # it seems like you *should* use st_blksize right? nope. it returns it in 512 byte blocks regardless of the filesystem's preferred block size.
            return st.st_blocks * 512 # st.st_blksize
    else:
        def disk_usage(path):
            return False

    if disk_usage(True) == True:
        svgSizeOnDisk = sum([disk_usage(os.path.join(dname, "symbols", f)) for f in svgFiles])
        pngSizeOnDisk = sum([disk_usage(os.path.join(dname, "symbols/png", f)) for f in pngFiles])
        webpSizeOnDisk = sum([disk_usage(os.path.join(dname, "symbols/webp", f)) for f in webpFiles])
        print("\nDisk space used:")
        print(f"  Size of SVGs on disk: {sizeof_fmt(svgSizeOnDisk)}")
        print(f"  Size of PNGs on disk: {sizeof_fmt(pngSizeOnDisk)}")
        print(f"  Size of WebPs on disk: {sizeof_fmt(webpSizeOnDisk)}")
        print(f"  Total size on disk: {sizeof_fmt(svgSizeOnDisk+pngSizeOnDisk+webpSizeOnDisk)}")
    else:
        print("Could not calculate disk usage")
