# Copyright (c) 2020 Adrian Siekierka
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

# Usage: world_join.py [worlds...] [output world]

#!/usr/bin/env python3
import zookeeper
import sys

def main():
    worldMain = zookeeper.Zookeeper(sys.argv[1])

    for i in range(2, len(sys.argv) - 1):
        worldSub = zookeeper.Zookeeper(sys.argv[i])
        boardOffsetMain = worldMain.world.total_boards
        for idx in range(0, worldSub.world.total_boards):
            boardSub: zookeeper.Board = worldSub.boards[idx]
            # transpose board IDs
            if boardSub.board_north > 0:
                boardSub.board_north += boardOffsetMain
            if boardSub.board_south > 0:
                boardSub.board_south += boardOffsetMain
            if boardSub.board_west > 0:
                boardSub.board_west += boardOffsetMain
            if boardSub.board_east > 0:
                boardSub.board_east += boardOffsetMain
            for statIdx in range(0, boardSub.stat_count):
                stat: zookeeper.Stat = boardSub.stats[statIdx]
                element: zookeeper.Element = boardSub.elements[(stat.x - 1 + ((stat.y - 1) * 60))]
                # Passage
                if element.id == 11:
                    stat.param3 = stat.param3 + boardOffsetMain
            # append
            worldMain.boards.append(boardSub)
        worldMain.world._total_boards += worldSub.world._total_boards

    worldMain.save(sys.argv[-1])

if __name__ == "__main__":
    main()




