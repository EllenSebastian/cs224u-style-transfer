from nltk.tree import *
from nltk.corpus import stopwords
from stat_parser import Parser
from nltk.tokenize import RegexpTokenizer
import string

parser = Parser()

def recurse(t, phrases):
  for n in t:
    if type(n) is Tree:
      if (n.label() == 'VP' or n.label() == 'NP') and phrases:
        p = phrases[len(phrases) - 1]
        for i in range(len(p)):
          if p[i] == n.leaves()[0]:
            phrases[len(phrases) - 1] = p[:i]
      if n.label() == 'VP':
        phrases.append(n.leaves())
      elif n.label() == 'NP':
        phrases.append(n.leaves())
    for c in n:
      if type(c) is Tree:
        recurse(c, phrases)

def append_to_list(new_phrases, s):
  if s in string.punctuation:
    new_phrases[len(new_phrases)-1] += s
  else:
    new_phrases.append(s)

def extract_phrases_from_sentence(sentence):
  #Parse into phrases
  try:
    t = parser.parse(sentence)
  except:
    return []
  phrases = []
  recurse(t, phrases)
  phrases = [' '.join(p) for p in phrases]
  stop = stopwords.words('english')
  phrases = [p for p in phrases if p not in stop]
  new_phrases = []
  if phrases != [] and sentence.lower().startswith(phrases[0].lower()):
    phrases[0] = phrases[0].capitalize()
  s = sentence

  #Go through parse and construct list of fragments
  for i in range(len(phrases)):
    missing = ''
    p = phrases[i]
    while s != '':
      #If fragment was NP or VP, append to list
      if s.lower().startswith(p.lower()):
        s = s[len(p):]
        break
      missing += s[0]
      s = s[1:]
    if missing != '' and missing != ' ':
      if missing[0] == ' ':
        missing = missing[1:]
      if missing[len(missing) - 1] == ' ':
        missing = missing[:-1]
      #Append punctuation to end of previous fragment
      append_to_list(new_phrases, missing)
    new_phrases.append(p)
  if s != '':
    if s[0] == ' ':
      s = s[1:]
    append_to_list(new_phrases, s)
  if new_phrases:
    new_phrases[0] = new_phrases[0].capitalize()
  return new_phrases

def main():
    # Usage example
    sentence = "To prevent conflict through diplomacy and strive to end conflicts after they've begun."
    print extract_phrases_from_sentence(sentence)
    #Returns a list of phrases 

if __name__ == "__main__":
    main()

