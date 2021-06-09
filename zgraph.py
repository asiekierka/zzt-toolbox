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
import os
import queue
import sys

import zookeeper
import networkx as nx
import pygraphviz as viz

def main():
	world = zookeeper.Zookeeper(sys.argv[-1])
	board_graph = nx.DiGraph()
	board_names = {}
	backtracking_number = 1
	for idx in range(0, world.world.total_boards):
		board: zookeeper.Board = world.boards[idx]
		board_graph.add_node(idx, label=board.title)
		board_names[idx] = board.title
		if board.board_north > 0:
			board_graph.add_edge(idx, board.board_north)
		if board.board_south > 0:
			board_graph.add_edge(idx, board.board_south)
		if board.board_west > 0:
			board_graph.add_edge(idx, board.board_west)
		if board.board_east > 0:
			board_graph.add_edge(idx, board.board_east)
		for stat in board.stat_data:
			element: zookeeper.Element = board.get_element((stat.x, stat.y))
			if element.oop_name.casefold() == 'PASSAGE'.casefold():
				board_graph.add_edge(idx, stat.param3)
	for idx in range(0, world.world.total_boards):
		board: zookeeper.Board = world.boards[idx]
		results = {idx: True}
		for idx2 in range(0, world.world.total_boards):
			if idx2 != idx and nx.has_path(board_graph, idx, idx2) and nx.has_path(board_graph, idx2, idx):
				results[idx2] = True
		board_graph.add_node(idx, label=board.title + (" (%d)" % (len(results))))
		backtracking_number = max(backtracking_number, len(results))

	board_agraph = nx.drawing.nx_agraph.to_agraph(board_graph)
	board_agraph.layout('dot')
	board_agraph.draw("graph.png")

	print(f"Backtracking number: {backtracking_number}")

	return True


if __name__ == "__main__":
	main()
