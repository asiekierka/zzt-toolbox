# Copyright (c) 2021 Adrian Siekierka
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

#!/usr/bin/env python3
from struct import unpack
import sys

f = open(sys.argv[1], 'rb')
file_entry_count = unpack('<H', f.read(2))[0]
file_entries = []

for i in range(0, file_entry_count):
	f_index, f_offs, f_size = unpack('<HII', f.read(10))
	print(f"Asset {f_index}, offset = {f_offs}, size = {f_size} bytes")
	file_entries.append((f_index, f_offs, f_size))

for f_entry in file_entries:
	f.seek(f_entry[1])
	with open(f'asset{f_entry[0]}.dat', 'wb') as of:
		of.write(f.read(f_entry[2]))

f.close()
