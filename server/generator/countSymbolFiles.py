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

import os

abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)

os.mkdir("symbols")

def sizeof_fmt(num, suffix="B"):
    for unit in ["", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"]:
        if abs(num) < 1024.0:
            return f"{num:3.1f}{unit}{suffix}"
        num /= 1024.0
    return f"{num:.1f}Yi{suffix}"

svgFiles = [f for f in os.listdir("symbols") if f.endswith(".svg")]
fileCount = len(svgFiles)
print(f"Found {fileCount} SVG files")

#
# Calculate the size of each file and display total
#
filesize = sum([os.path.getsize(os.path.join(dname, "symbols", f)) for f in svgFiles])
print(f"Size of all: {sizeof_fmt(filesize)}")

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
    sizeOnDisk = sum([disk_usage(os.path.join(dname, "symbols", f)) for f in svgFiles])
    print(f"Disk usage: {sizeof_fmt(sizeOnDisk)}")
else:
    print("Could not calculate disk usage")
