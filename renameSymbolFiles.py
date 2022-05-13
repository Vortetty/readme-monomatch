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
from time import sleep
from tqdm import tqdm
import shutil

shutil.rmtree("symbols_tmp", ignore_errors=True)
shutil.copytree("symbols", "symbols_tmp")
shutil.rmtree("symbols", ignore_errors=True)
os.mkdir("symbols")

svgFiles = [f for f in os.listdir("symbols_tmp") if f.endswith(".svg")]

for i,file in tqdm(enumerate(svgFiles), total=len(svgFiles), unit="file(s)", desc="Renaming files", position=0):
    os.rename(f"symbols_tmp/{file}", f"symbols/{i}.svg")
    sleep(0.25)

shutil.rmtree("symbols_tmp", ignore_errors=True)
