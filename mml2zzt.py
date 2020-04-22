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

#!/usr/bin/env python3
import argparse, copy, sys
import pprint

DEFAULT_MML_QUIRK = "mabi"
ZZT_LINE_LENGTH = 36
ZZT_OBJECT_CYCLE = 1
MIN_VOLUME = 0

pp = pprint.PrettyPrinter(indent=4)

zzt_note_lengths = {
	1: "t",
	2: "s",
	3: "s.",
	4: "i",
	6: "i.",
	8: "q",
	12: "q.",
	16: "h",
	24: "h.",
	32: "w",
	48: "w."
}

zzt_note_notes = {
	0: "c",
	1: "c#",
	2: "d",
	3: "d#",
	4: "e",
	5: "f",
	6: "f#",
	7: "g",
	8: "g#",
	9: "a",
	10: "a#",
	11: "b"
}

def p_next_char(text):
	return text[0:1], text[1:]

def p_next_number(text, defval):
	i = 0
	while (text[0:(i+1)].isnumeric()) and (i < len(text)):
		i += 1
	if i > 0:
		return int(text[0:i]), text[i:]
	else:
		return defval, text

def p_next_length(text, defval):
	i = 0
	while text[i:(i+1)].isnumeric() and (i < len(text)):
		i += 1
	if i > 0:
		if text[(i):(i+1)] == '.':
			return (64.0 / int(text[0:i])) * 1.5, text[(i+1):]
		else:
			return (64.0 / int(text[0:i])), text[i:]
	else:
		if text[0:1] == '.':
			return defval * 1.5, text[1:]
		else:
			return defval, text

def _parse_mml_to_single_ir(text, quirk):
	cmds = []
	cmd_chr_notes = {"a": 9, "b": 11, "c": 0, "d": 2, "e": 4, "f": 5, "g": 7}
	cmd_chr_note_modifiers = {"+": 1, "#": 1, "-": -1}
	state = {
		"tempo": 120,
		"note_length": 16,
		"octave": 4,
		"volume": 8,
		"tie": False
	}
	while len(text) > 0:
		cmd = {}
		cmd_chr, text = p_next_char(text)
		cmd_chr = cmd_chr.lower()
		if cmd_chr == "t":
			state["tempo"], text = p_next_number(text, 120)
			cmd["name"] = "set_tempo"
			cmd["tempo"] = state["tempo"]
			cmd["length"] = 0
			cmds.append(cmd)
		elif cmd_chr == "l":
			state["note_length"], text = p_next_length(text, 16)
		elif cmd_chr == "v":
			state["volume"], text = p_next_number(text, 8)
		elif cmd_chr == "o":
			state["octave"], text = p_next_number(text, 4)
		elif cmd_chr == "<":
			if state["octave"] > 1:
				state["octave"] -= 1
		elif cmd_chr == ">":
			if state["octave"] < 8:
				state["octave"] += 1
		elif cmd_chr in cmd_chr_notes:
			cmd["name"] = "note"
			cmd["volume"] = state["volume"]
			cmd["octave"] = state["octave"]
			cmd["note"] = cmd_chr_notes[cmd_chr]
			if text[0:1] in cmd_chr_note_modifiers:
				cmd["note"] += cmd_chr_note_modifiers[text[0:1]]
				if cmd["note"] < 0:
					cmd["note"] += 12
				if cmd["note"] >= 12:
					cmd["note"] -= 12
				text = text[1:]
			cmd["tempo"] = state["tempo"]
			cmd["length"], text = p_next_length(text, state["note_length"])
			if state["tie"] and (
				(cmds[-1]["name"] == "note")
				and (cmds[-1]["volume"] == cmd["volume"])
				and (cmds[-1]["octave"] == cmd["octave"])
				and (cmds[-1]["note"] == cmd["note"])
			):
				cmds[-1]["length"] += cmd["length"]
			else:
				if (cmd["volume"] < MIN_VOLUME):
					cmd["name"] = "pause"
				cmds.append(cmd)
			state["tie"] = False
		elif cmd_chr == "&":
			state["tie"] = True
		elif (cmd_chr == "r") or (cmd_chr == "p"):
			cmd["name"] = "pause"
			cmd["volume"] = state["volume"]
			cmd["tempo"] = state["tempo"]
			cmd["length"], text = p_next_length(text, state["note_length"])
			# pauses make no sound, so ignore tie
			if state["tie"] and (len(cmds) > 0) and (cmds[-1]["name"] == "pause"):
				cmds[-1]["length"] += cmd["length"]
			else:
				cmds.append(cmd)
			state["tie"] = False
		elif cmd_chr == "n":
			midi_number, text = p_next_number(text, -1)
			if midi_number >= 0:
				midi_number = midi_number - 12
				cmd["name"] = "note"
				cmd["octave"] = int(midi_number / 12)
				cmd["volume"] = state["volume"]
				cmd["tempo"] = state["tempo"]
				cmd["note"] = midi_number % 12
				cmd["length"] = state["note_length"]
				if (cmd["volume"] < MIN_VOLUME):
					cmd["name"] = "pause"
				cmds.append(cmd)
		else:
			print("warning: unknown command %s" % cmd_chr)
	total_length = sum(map(lambda x: x["length"], cmds))
	print("total length (channel): %d" % total_length, file=sys.stderr)
	return cmds

def join_multi_ir(multi_ir):
	multi_ir = copy.deepcopy(multi_ir)
	ir = []
	tempo = 120
	total_length = 0
	while len(multi_ir) > 0:
		# remove all empty blocks
		for ir_part in multi_ir:
			if (len(ir_part) > 0) and ("length" in ir_part[0]) and (ir_part[0]["length"] <= 0):
				ir_part.pop(0)
		# handle set_tempo
		for ir_part in multi_ir:
			while (len(ir_part) > 0) and (ir_part[0]["name"] == "set_tempo"):
				tempo = ir_part[0]["tempo"]
				ir_part.pop(0)
		# remove all empty lists
		multi_ir = list(filter(lambda x: len(x) > 0, multi_ir))
		if len(multi_ir) > 0:
			# let's add a new block!
			block_len = min(map(lambda x: x[0]["length"], multi_ir))
			# create block
			joined_ir = {
				"length": block_len,
				"tempo": tempo,
				"notes": []
			}
			has_note = False
			for ir_part in multi_ir:
				note = copy.deepcopy(ir_part[0])
				if note["name"] == "note":
					has_note = True
				del note["length"]
				del note["tempo"]
				joined_ir["notes"].append(note)
			# cleanup 1: remove doubled-up pauses and unnecessary pauses
			if has_note:
				joined_ir["notes"] = list(filter(lambda x: x["name"] == "note", joined_ir["notes"]))
			else:
				joined_ir["notes"] = joined_ir["notes"][0:1]
			# cleanup 2: remove doubled notes
			if len(joined_ir["notes"]) > 1:
				old_notes = joined_ir["notes"]
				note_keys = {}
				joined_ir["notes"] = []
				# find min/max note key
				note_keys_allowed = {}
				min_note_key = 1000
				max_note_key = -1000
				for i in old_notes:
					note_key = i["octave"] * 16 + i["note"]
					if min_note_key > note_key:
						min_note_key = note_key
					if max_note_key < note_key:
						max_note_key = note_key
				note_keys_allowed[min_note_key] = True
				note_keys_allowed[max_note_key] = True
				for i in old_notes:
					note_key = i["octave"] * 16 + i["note"]
					if note_key not in note_keys:
						if (len(note_keys_allowed) <= 0) or (note_key in note_keys_allowed):
							joined_ir["notes"].append(i)
							note_keys[note_key] = True
			ir.append(joined_ir)
			total_length += block_len
			# subtract lengths
			for ir_part in multi_ir:
				ir_part[0]["length"] -= block_len
	print("total length (joined): %d" % total_length, file=sys.stderr)
	return ir

def parse_mml_to_multi_ir(text, quirk=DEFAULT_MML_QUIRK):
	text = text.strip()
	# if MML@ is found, clean up
	if text.startswith("MML@"):
		text = text[4:(text.rindex(";") or len(text))]
	# split text into tracks
	return list(map(lambda x: _parse_mml_to_single_ir(x, quirk), text.split(",")))

def zzt_append_new_line(state):
	text = state["text"]
	s = "#play "
	ticks_per_cycle = ZZT_OBJECT_CYCLE * 2
	while (state["ticks"] >= ticks_per_cycle) and ((len(s) * 2) < ZZT_LINE_LENGTH):
		s = "/i" + s
		state["ticks"] -= ticks_per_cycle
	text.append(s)
	state["octave"] = 3
	state["length"] = 1

def zzt_append_play(state, cmd, ticks):
	text = state["text"]
	if (len(text) <= 0):
		text.append("#play ")
	text[-1] += cmd
	state["ticks"] += ticks
	if ((len(text[-1]) + len(cmd)) >= ZZT_LINE_LENGTH):
		zzt_append_new_line(state)

def zzt_adjust_octave(state, note):
	z_cmd = ""
	if "octave" in note:
		z_note_octave = note["octave"] - 1
		if z_note_octave < 1:
			z_note_octave = 1
		if z_note_octave > 6:
			z_note_octave = 6
		while state["octave"] < z_note_octave:
			z_cmd += "+"
			state["octave"] += 1
		while state["octave"] > z_note_octave:
			z_cmd += "-"
			state["octave"] -= 1
	return z_cmd

def parse_joined_ir_to_zzt(ir):
	state = {
		"text": [],
		"octave": 3,
		"length": 1,
		"modulate_counter": 0,
		"length_diff": 0,
		"ticks": 0
	}
	duration = 0
	for note_group in ir:
		# note["length"] = 2 - 1/32, 64 - whole note
		# zzt length = 1 - 1/32 32 - whole note
		# 120 BPM = whole note
		# all of this is HACKS
		z_note_length = int(note_group["length"] / 2.0) + state["length_diff"]
		state["length_diff"] = 0
		if z_note_length < 1:
			state["length_diff"] += 1 - z_note_length
			z_note_length = 1
		if len(note_group["notes"]) > 1:
			# time to modulate up the wazoo
			duration += z_note_length
			while z_note_length > 0:
				state["modulate_counter"] = int(state["modulate_counter"] % len(note_group["notes"]))
				#
				note = note_group["notes"][state["modulate_counter"]]
				if note["name"] == "note":
					z_cmd = ""
					if state["length"] != 1:
						z_cmd += zzt_note_lengths[1]
						state["length"] = 1
					z_cmd += zzt_adjust_octave(state, note)
					z_cmd += zzt_note_notes[note["note"]]
					zzt_append_play(state, z_cmd, 1)
					z_note_length -= 1
				#
				state["modulate_counter"] += 1
		else:
			# just the one
			z_cmd = ""
			while z_note_length not in zzt_note_lengths:
				z_note_length -= 1
				state["length_diff"] += 1
			if state["length"] != z_note_length:
				z_cmd += zzt_note_lengths[z_note_length]
				state["length"] = z_note_length
			# note
			note = note_group["notes"][0]
			if note["name"] == "pause":
				z_cmd += "x"
				duration += z_note_length
				zzt_append_play(state, z_cmd, z_note_length)
			elif note["name"] == "note":
				z_cmd += zzt_adjust_octave(state, note)
				z_cmd += zzt_note_notes[note["note"]]
				duration += z_note_length
				zzt_append_play(state, z_cmd, z_note_length)
			else:
				print("warning: unknown notecmd %s" % note["name"], file=sys.stderr)
	print("duration: %.2f seconds" % (duration / 18.2), file=sys.stderr)
	return "\n".join(state["text"])

parser = argparse.ArgumentParser(description="Convert MML scripts to ZZT sound code.")
parser.add_argument("-q", "--quirk", default=DEFAULT_MML_QUIRK)
parser.add_argument("-l", "--line-length", type=int, default=ZZT_LINE_LENGTH)
parser.add_argument("-c", "--object-cycle", type=int, default=ZZT_OBJECT_CYCLE)
parser.add_argument("file")
args = parser.parse_args()

ZZT_LINE_LENGTH = args.line_length
ZZT_OBJECT_CYCLE = args.object_cycle

f = open(args.file, "r")
mml_text = f.read()
f.close()

multi_ir = parse_mml_to_multi_ir(mml_text, args.quirk)
joined_ir = join_multi_ir(multi_ir)
text = parse_joined_ir_to_zzt(joined_ir)

print(text)
