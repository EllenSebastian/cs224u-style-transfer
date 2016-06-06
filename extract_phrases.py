from nltk.tree import *
from nltk.corpus import stopwords
from stat_parser import Parser
from nltk.tokenize import RegexpTokenizer


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

def extract_phrases_from_sentence(sentence):
  try:
    t = parser.parse(sentence)
    print t
  except:
    return []
  phrases = []
  recurse(t, phrases)
  phrases = [' '.join(p) for p in phrases]
  stop = stopwords.words('english')
  phrases = [p for p in phrases if p not in stop]
  new_phrases = []
  if phrases[0].islower():
    phrases[0] = phrases[0].capitalize()
  s = sentence
  for i in range(len(phrases)):
    missing = ''
    p = phrases[i]
    while s != '':
      if s.lower().startswith(p.lower()):
        s = s[len(p):]
        break
      missing += s[0]
      s = s[1:]
    missing = missing.strip()
    if missing != '':
      new_phrases.append(missing)
    new_phrases.append(p)
  if s != '':
    if s[0] == ' ':
      s = s[1:]
    new_phrases.append(s)
  if new_phrases:
    new_phrases[0] = new_phrases[0].capitalize()
  new_phrases = filter(lambda x : x != '', new_phrases)
  return new_phrases


def main():
    # Usage example
    sentence = "Shot, beaten, marched, bombed, jailed, starved, gassed to death."
    print extract_phrases_from_sentence(sentence)
    #Returns a list of phrases 

if __name__ == "__main__":
    main()

