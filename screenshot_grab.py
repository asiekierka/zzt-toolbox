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

# Usage: screenshot_grab.py [world]

#!/usr/bin/env python3
import zookeeper
import math, os, re, sys

rule_filename = "[^\w\-_\. ]"

def main():
    f = sys.argv[-1]
    dir = os.path.splitext(os.path.basename(f))[0]
    if not os.path.exists(dir):
        os.mkdir(dir)
    w = zookeeper.Zookeeper(f)
    for idx in range(0, w.world.total_boards):
        print("%d/%d" % (idx, w.world.total_boards))
        b = w.boards[idx]
        img_tsy = b.render(title_screen=True)
        img_tsn = b.render(title_screen=False)
        fn_tsy = os.path.join(dir, "%03dT %s.png" % (idx, re.sub(rule_filename, "_", b.title)))
        fn_tsn = os.path.join(dir, "%03dP %s.png" % (idx, re.sub(rule_filename, "_", b.title)))
        img_tsy.save(fn_tsy, "PNG")
        img_tsn.save(fn_tsn, "PNG")

if __name__ == "__main__":
    main()




