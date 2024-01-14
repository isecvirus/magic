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

import glob
import math
import os.path
import random
from hashlib import md5
from time import time

from PIL import Image


"""
Uniquely and randomly transparent a number of
pixels based on pieces.

pixels / pieces = number of transparent pixels

disassemble example:
    seed = by default is null but when static value
           the pixel randomness will be the same.
    pieces = 4 (example value)

    + 2d8aa42a0347c2d66cc86a0138dc9664
        | 1.png    <-- piece 1
        | 2.png    <-- piece 2
        | 3.png    <-- piece 3
        | 4.png    <-- piece 4

assemble example:
    path = 2d8aa42a0347c2d66cc86a0138dc9664
        | 1.png
        | 2.png
        | 3.png
        | 4.png
    output = 2d8aa42a0347c2d66cc86a0138dc9664.png
"""

class Puzzle:
    def __init__(self, path:str):
        """
        :param path: path for the image/folder
               the folder of the disassembled image.
        """
        self.image = path

        self.id = md5(str(random.randint(0, 9999999999)).encode()).hexdigest()
        self.CHANNELS = "RGBA"
        self.start = 0

    def assemble(self):
        self.start = time()

        pieces = glob.glob(f"{self.image}/*.png")

        init = Image.open(pieces[0])
        width, height = init.size

        reassembled_image = Image.new(init.mode, (width, height))

        for index, piece_image in enumerate(pieces):
            piece = Image.open(piece_image)

            reassembled_image.alpha_composite(piece)

        reassembled_image.save(self.id + ".png", format="PNG")

    def disassemble(self, pieces:int, seed:int=None):
        """
        :param pieces:
            Less means more transparent pixels
        :param seed:
            The shuffle seed
        :return:
        """
        self.start = time()

        dest_path = os.path.dirname(self.image)
        dest_path = os.path.join(dest_path, self.id)
        os.makedirs(dest_path, exist_ok=True)

        image = Image.open(self.image)
        image = image.convert(self.CHANNELS)
        width, height = image.size
        pixels: list[tuple[int, int, int]] = image.getdata()

        pixel_num = width * height
        ppp = math.ceil(pixel_num / pieces)  # pixel per piece

        pixels_index = list(range(pixel_num))
        random.seed(seed)
        random.shuffle(pixels_index)

        for m in range(pieces):  # multiplier
            start = ppp * m
            end = ppp * (m + 1)

            pixels_copy = list(pixels.copy())

            for index in pixels_index[start:end]:
                pixels_copy[index] = (0, 0, 0, 0)

            new_image = Image.new(self.CHANNELS, (width, height))
            new_image.putdata(pixels_copy)

            filename = f"{str(m + 1)}.png"
            path = os.path.join(dest_path, filename)

            new_image.save(path, format="PNG")

    def get_id(self):
        return self.id

    def get_elapsed(self):
        return round(time() - self.start, 3)
