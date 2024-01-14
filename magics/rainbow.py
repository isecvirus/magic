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

import base64
import os
from time import time

from PIL import Image
import math

"""
file = virus.exe

basically every byte in the $file will be
added to a channel RGB.

R = byte1
G = byte2
B = byte3
...

Like this:
    +-----------------------------+
    | |1|2|3|   |4|5|6|   |7|8|9| |
    | |*|*|*|   |*|*|*|   |*|*|*| |  <--- This is the example image (:
    | |*|*|*|   |*|*|*|   |*|*|*| |
    +-----------------------------+

Not this:
    +-----------------------------+
    | |1|1|1|   |2|2|2|   |3|3|3| |
    | |4|4|4|   |5|5|5|   |6|6|6| |
    | |7|7|7|   |8|8|8|   |9|9|9| |
    +-----------------------------+

Rainbow process:
    if the total $pixels < $bytes then the
    rest of the pixels will be padded with zeros
    then the result pixel bytes will be base64
    encoded to avoid wrong bytes conversion.

Extract process:
     extracting image pixels and converting them
     to normal chars and they actually a base64
     string, and then decoding them to represent
     us a sequence of bytes each byte represent
     a byte of the injected file.
"""

class Rainbow:
    def __init__(self, file: str, output: str = None):
        self.file = file
        self.output = output
        """
        bitdepth:
            Red      Green    Blue
            00000000 00000000 00000000 = 24bit
            ^^^^^^^^ ^^^^^^^^ ^^^^^^^^
              8bit     8bit     8bit        
        """
        self.bitdepth = 24
        self.filesize = self.get_filesize()
        # RGB
        self.CHANNELS = 3
        self.start = 0


    def rainbow(self):
        self.start = time()

        width = self.get_width()
        height = self.get_height()
        output = self.output

        pixels = []

        with open(self.file, "rb") as fis:
            bytes = base64.b64encode(fis.read())

            padding = (len(bytes) % self.CHANNELS)
            if padding != 0:
                bytes += b'\x00' * (self.CHANNELS - padding)

            for i in range(0, len(bytes), self.CHANNELS):
                r, g, b = bytes[i:i + self.CHANNELS]
                pixels.append((r, g, b))

        image = Image.new("RGB", (width, height))
        image.putdata(pixels)

        if not self.output:
            output = self.file + ".png"
            if "." in self.file:
                output = os.path.splitext(self.file)[0] + ".png"

        image.save(output, format="PNG")

        return pixels

    def extract(self, output: str) -> int:
        self.start = time()

        image = Image.open(self.file)
        # get image pixels (r,g,b)
        data = image.getdata()

        # flat the array [(r,g,b), [(r,g,b), ...]
        # to be [r, g, b, r, g, b, ...]
        data = [pixel for rgb in data for pixel in rgb]

        # encode it's content in base64
        data = base64.b64decode(bytes(data))

        with open(output, "wb") as out:
            return out.write(data)

    def get_filesize(self) -> int:
        return len(base64.b64encode(open(self.file, "rb").read()))

    def get_pixel_size(self) -> float:
        return self.bitdepth / 8

    def pixel_num(self) -> float:
        return self.filesize / self.get_pixel_size()

    def get_width(self) -> int:
        return int(math.sqrt(self.pixel_num()))

    def get_height(self) -> int:
        width = self.get_width()
        height = math.ceil(self.pixel_num() / width)
        return int(height)

    def get_aspect_ratio(self) -> tuple[int, int]:
        width = self.get_width()
        height = self.get_height()

        # Greatest Common Divisor (using euclid algorithm)
        gcd = math.gcd(width, height)

        return ((width // gcd), (height // gcd))

    def get_elapsed(self):
        return round(time() - self.start, 3)
