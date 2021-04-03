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

# Edit this variable with board IDs of boards you want to see fully decoded.
decode_full = []

f = open(sys.argv[1], 'rb')
f.seek(0x2)
board_count = unpack('<H', f.read(2))[0]

f.seek(0x200)
for i in range(0, board_count + 1):
	board_pos = f.tell()
	board_len = unpack('<H', f.read(2))[0]
	print(f"Board {i}, position = {board_pos} bytes, length = {board_len} bytes")
	if (board_len < 128) or (board_len >= 32768):
		print(f"Unusual board length!")
	board_next_pos = f.tell() + board_len

	f.seek(f.tell() + 51) # board name
	if i in decode_full:
		# decode RLE
		tile_to_find = 1500
		tile_id = 0
		while tile_to_find > 0:
			tile_pos = f.tell()
			tile_count, tile_element, tile_color = unpack('BBB', f.read(3))
			if tile_count == 0:
				tile_count = 256
			tile_to_find -= tile_count
			print(f"Tile {tile_id} at {tile_pos} bytes: {tile_count} x ({tile_element}, {tile_color})")
			if (tile_element >= 54):
				print(f"Unusual element!")
			tile_id += 1
		if tile_to_find < 0:
			tiles_too_many = -tile_to_find
			print(f"Invalid ending tile count ({tiles_too_many} tiles too many)!")
		else:
			tile_pos = f.tell()
			print(f"RLE ending found at {tile_pos} bytes.")
		f.seek(f.tell() + 86) # board info
		stat_count = unpack('<H', f.read(2))[0]
		print(f"stat count = {stat_count}")
		if stat_count > 151:
			print("Unusual stat count!")
		# decode stats
		for istat in range(0, stat_count + 1):
			stat_pos = f.tell()
			stat_x, stat_y, stat_stepx, stat_stepy, stat_cycle, \
			stat_p1, stat_p2, stat_p3, stat_follower, stat_leader, \
			stat_under_element, stat_under_color, stat_data, \
			stat_datapos, stat_datalen, stat_unk1, \
			stat_unk2 = unpack("<BBhhhBBBhhBBIhhII", f.read(33))
			print(f"stat {istat} @ {stat_pos} bytes, {stat_x}, {stat_y} pos")
			if (stat_x > 60) or (stat_y > 25) or (stat_x < 1) or (stat_y < 1):
				print("Unusual X/Y position!")
			if stat_datalen > 0:
				f.read(stat_datalen)

	f.seek(board_next_pos)

f.close()
