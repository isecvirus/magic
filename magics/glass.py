"""
Copyright (c) 2024 Virus. All rights reserved.

Redistribution and use in source and binary forms, with or without modification,
are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice,
   this list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice,
   this list of conditions and the following disclaimer in the documentation
   and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""

import re
from PIL import Image
from time import time
from uuid import uuid4

"""
Basically giving every alpha channel a value
of 0, and before that we're making a map of
the original alpha channel values, the format
of the map file is:

flag alpha map = [255, 255, 255, 142, 90, 10, 24, 24, 0, 0, 5]
formatted alpha map = 255[3]142[1]90[1]10[1]24[2]0[2]5[1]

Example
    +-----------------------------------+
    | |R|G|B|A|   |R|G|B|A|   |R|G|B|A| |
    | |R|G|B|A|   |R|G|B|A|   |R|G|B|A| |  <--- This is the example image (:
    | |R|G|B|A|   |R|G|B|A|   |R|G|B|A| |
    +-----------------------------------+

Goes to be:
    +-----------------------------------+
    | |R|G|B|0|   |R|G|B|0|   |R|G|B|0| |
    | |R|G|B|0|   |R|G|B|0|   |R|G|B|0| |
    | |R|G|B|0|   |R|G|B|0|   |R|G|B|0| |
    +-----------------------------------+

A transparent image and a map file will be
produced.
"""

class Glass:
    def __init__(self, image: str, ):
        self.image = image
        self.start = 0
        self.id = str(uuid4())

    def glassify(self):
        self.start = time()

        in_image = Image.open(self.image)
        in_image = in_image.convert(mode="RGBA")
        width, height = in_image.width, in_image.height

        pixels = in_image.getdata()

        output = self.id + ".png"
        map_file = self.id

        array: list[tuple[int, int, int, int]] = []
        map = []

        for index, pixel in enumerate(pixels):
            r, g, b, a = pixel
            array.append((r, g, b, 0))
            map.append(a)

        with open(map_file, "w") as out_map:
            out_map.write(self.format(map))
        out_map.close()

        out_image = Image.new(mode="RGBA", size=(width, height))
        out_image.putdata(array)
        out_image.save(output, format="PNG")

    def clearify(self, map: list, output: str = None):
        self.start = time()

        in_image = Image.open(self.image)
        in_image = in_image.convert(mode="RGBA")
        width, height = in_image.width, in_image.height

        pixels = in_image.getdata()

        output = output if output else self.image

        array: list[tuple[int, int, int, int]] = []

        for index, pixel in enumerate(pixels):
            r, g, b, a = pixel
            array.append((r, g, b, int(map[index])))


        out_image = Image.new(mode="RGBA", size=(width, height))
        out_image.putdata(array)
        out_image.save(output, format="PNG")

    def format(self, map: list) -> str:
        if len(set(map)) == 1:
            return f"{map[0]}[{len(map)}]"

        count = 1
        formed = ""
        current = map[0]

        for i in range(1, len(map)):
            if map[i] == current:
                count += 1
            else:
                formed += f"{current}[{count}]"
                current = map[i]
                count = 1

        # add last item
        formed += f"{current}[{count}]"

        return formed

    def deformat(self, map: str) -> list:
        matches = re.findall("(\d+)\[(\d+)\]", map)
        array = []

        for match in matches:
            num, count = match

            array.append([int(num)] * int(count))

        return sum(array, [])

    def get_map(self, map_file: str):
        with open(map_file, "r") as map_fis:
            return self.deformat(map_fis.read())

    def get_elapsed(self):
        return round(time() - self.start, 3)

    def get_id(self):
        return self.id