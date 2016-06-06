#Usage: python baseline.py source_file target_dir
#python baseline.py data/shakespeare-aligned/enotes/hamlet_modern.snt.aligned data/trump/
from nltk.corpus import wordnet as wn
import argparse
import glob
import collections
import re

import sys  

reload(sys)  
sys.setdefaultencoding('utf8')

parser = argparse.ArgumentParser(description="""Counts word frequencies of 
  all files in targetdir. Finds synonyms of each word and substitutes with 
  most frequent synonym in the target style. """)
parser.add_argument('source', help='source file path to use')
parser.add_argument('targetdir', help='target directory to use')
args = parser.parse_args()

counts = collections.Counter()

translation = ''

with open(args.source) as source:
  for filename in glob.iglob(args.targetdir + '/train.txt'):
    with open(filename) as f:
      content = f.read().replace('\n', '').split(' ')
      counts += collections.Counter(content)
  source_words = source.read()
  #print source_words
  for word in source_words.split(' '):
    substitute = ''
    frequency = 0
    syns = wn.synsets(word)
    for syn in syns:
      syn_name = str(syn.name())
      syn_name = syn_name.split('.')[0]
      if counts[syn_name] > frequency:
        substitute = syn_name
        frequency = counts[syn_name]
    if substitute != '':
      print word, substitute
      translation += substitute + ' '
    else:
      translation += word + ' '

print translation



