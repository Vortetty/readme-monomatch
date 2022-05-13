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
import sympy
from datetime import datetime

def generateCardDataByCards(targetCards: int):
    TARGET_CARDS = targetCards
    prevPrime = sympy.ntheory.generate.prevprime(sqrt(TARGET_CARDS))
    nextPrime = sympy.ntheory.generate.nextprime(sqrt(TARGET_CARDS))
    GRID_SIZE = min([[prevPrime**2+prevPrime, prevPrime], [nextPrime**2+nextPrime, nextPrime]], key=lambda x:abs(x[0]-TARGET_CARDS))[1]
    return generateCardDataByDimension(GRID_SIZE)

def generateCardDataByDimension(targetDimension: int):
    GRID_SIZE = targetDimension
    if not sympy.isprime(GRID_SIZE):
        prevPrime = sympy.ntheory.generate.prevprime(sqrt(GRID_SIZE))
        nextPrime = sympy.ntheory.generate.nextprime(sqrt(GRID_SIZE))
        GRID_SIZE = min([[prevPrime**2+prevPrime, prevPrime], [nextPrime**2+nextPrime, nextPrime]], key=lambda x:abs(x[0]-GRID_SIZE))[1]

    print(f"Grid size: {GRID_SIZE}x{GRID_SIZE}")
    print(f"Card count: {GRID_SIZE**2+GRID_SIZE+1}")

    # Pseudocode for generating monomatch:
    # // N*N first cards
    # for I = 0 to N-1
    #    for J = 0 to N-1
    #       for K = 0 to N-1
    #          print ((I*K + J) modulus N)*N + K
    #       end for
    #       print N*N + I
    #       new line
    #    end for
    # end for
    #
    # // N following cards
    # for I = 0 to N-1
    #    for J = 0 to N-1
    #       print J*N + I
    #    end for
    #    print N*N + N
    #    new line
    # end for
    #
    # // Last card
    # for I = 0 to N-1
    #    print N*N + I
    # end for

    print("Generating cards...")
    cards = []
    maxSymbols = GRID_SIZE * GRID_SIZE + GRID_SIZE + 1
    cardBuf = []

    for i in range(GRID_SIZE):
        for j in range(GRID_SIZE):
            for k in range(GRID_SIZE):
                cardBuf.append( ((i * k + j) % GRID_SIZE) * GRID_SIZE + k )
            cardBuf.append(GRID_SIZE * GRID_SIZE + i)
            cards.append(cardBuf)
            cardBuf = []

    for i in range(GRID_SIZE):
        for j in range(GRID_SIZE):
            cardBuf.append(j * GRID_SIZE + i)
        cardBuf.append(GRID_SIZE * GRID_SIZE + GRID_SIZE)
        cards.append(cardBuf)
        cardBuf = []

    for i in range(GRID_SIZE+1):
        cardBuf.append(GRID_SIZE * GRID_SIZE + i)
    cards.append(cardBuf)
    cardBuf = []

    print(f"Generated {len(cards)} cards using {maxSymbols} symbols at {len(cards[0])} symbols per card\nGenerating dict to write...")
    cardData = {
        "symbol_count": maxSymbols,
        "card_count": len(cards),
        "grid_size": GRID_SIZE,
        "card_data": cards
    }

    #with open("monomatch_card_data.cbor", "wb") as f:
    #    print("Generating cbor...")
    #    data = cbor2.dumps(cardData)
    #    print("Writing cbor...")
    #    f.write(data)

    #with open("monomatch_card_data.json", "w") as f:
    #    print("Generating json...")
    #    data = json.dumps(cardData)
    #    print("Writing json...")
    #    f.write(data)

    return cardData