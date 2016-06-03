from nltk.tree import *
from nltk.corpus import stopwords
from stat_parser import Parser

parser = Parser()

def recurse(t, phrases):
  for n in t:
    if type(n) is Tree:
      if n.label() == 'VP' or n.label() == 'NP' and phrases != []:
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
  t = parser.parse(sentence)
  phrases = []
  recurse(t, phrases)
  phrases = [' '.join(p) for p in phrases]  
  stop = stopwords.words('english')
  phrases = [p for p in phrases if p not in stop]
  new_phrases = []
  str = sentence.lower()
  for i in range(len(phrases)):
    missing = ''
    p = phrases[i]
    while str != '':
      if str.startswith(p):
        str = str[len(p):]
        break
      missing += str[0]
      str = str[1:]
    if missing != '' and missing != ' ':
      if missing[0] == ' ':
        missing = missing[1:]
      if missing[len(missing) - 1] == ' ':
        missing = missing[:-1]
      new_phrases.append(missing)
    new_phrases.append(p)
  return new_phrases


def main():
    # Usage example
    sentence = "Every great religion promises a pathway to love and peace and righteousness, and yet no religion has been spared from believers who have claimed their faith as a license to kill."
    print extract_phrases(sentence)
    #Returns a list of phrases 

if __name__ == "__main__":
    main()

