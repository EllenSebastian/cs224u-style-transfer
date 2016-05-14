# Usage: python collect_data.py dirname

import glob
import argparse

parser = argparse.ArgumentParser(description="""Strips newlines from all text
	files in dirname and cats them together into dirname/train.txt. Overwrites
	train.txt if it already exists.""")
parser.add_argument('dirname', help='the directory to use')
args = parser.parse_args()

with open(args.dirname + '/train.txt', 'w') as t:
	for filename in glob.iglob(args.dirname + '/*.txt'):
		with open(filename) as f:
			for line in f:
				t.write(line.strip() + ' ')
