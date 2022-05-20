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

import numpy as np

class xoroshiro256ss:
    def __init__(self):
        self.state: np.ndarray[4, np.uint64] = np.random.randint(0, 2**64, 4, dtype=np.uint64)

    def next(self) -> np.uint64:
        result: np.uint64 = (self.state[0] + self.state[3]).astype(np.uint64)
        t: np.uint64 = (self.state[1] << np.uint64(17)).astype(np.uint64)

        self.state[2] = (self.state[2] ^ self.state[0]).astype(np.uint64)
        self.state[3] = (self.state[3] ^ self.state[1]).astype(np.uint64)
        self.state[1] = (self.state[1] ^ self.state[2]).astype(np.uint64)
        self.state[0] = (self.state[0] ^ self.state[3]).astype(np.uint64)

        self.state[2] = (self.state[2] ^ t).astype(np.uint64)
        self.state[3] = self.rol64(self.state[3], 45).astype(np.uint64)

        return result.astype(np.uint64)

    def rol64(self, x: np.uint64, k: np.uint64) -> np.uint64:
        x = np.uint64(x)
        k = np.uint64(k)
        return ((x << k).astype(np.uint64) | (x >> (np.uint64(64) - k).astype(np.uint64))).astype(np.uint64)
