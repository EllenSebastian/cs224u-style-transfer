# anchoring paraphrase extraction algorithm from Pasca & Dienes 2005

import nltk
from collections import defaultdict
import string 

minp = 1
maxp = 5

stopwords = set(['that', 'which', 'the', 'he', 'him', 'she', 'her', 'his', 'and', 'a', 'an'])

def remove_punct(s):
	s = str(s)
	return s.translate(string.maketrans("",""), string.punctuation)

def parse_sentences(file):
	with open(file, 'r') as in_file:
		text = in_file.read()
		text = text.decode('utf-8').encode('ascii','ignore')
		sents = nltk.sent_tokenize(text)
	#' '.join(sent.split()) removes extraneous whitespace
	return [' '.join([i for i in remove_punct(sent).lower().split() if i not in stopwords]) for sent in sents]


# version for 1 corpus (same as paper)
def single_corpus_paraphrase_extraction(file, Lc):
	sentences = parse_sentences(file)
	print 'parsed file'
	ngrams = set([])
	for sentence in sentences:
		sentence = sentence.split(' ')
		for ngram_len in range(2 * Lc + minp, 2 * Lc + maxp + 1):
			for start in range(0, len(sentence) - ngram_len):
				# must be stored as strings because list is an unhashable type.
				ngrams.add(' '.join(sentence[start:start+ngram_len]))
	print 'extracted ', len(ngrams), 'ngrams'
	anchor_cand_pairs = defaultdict(list) # anchor --> list of candidates
	for ngram in ngrams:
		# notation based on paper p.123
		ngram = ngram.split()
		cstl = ngram[0:Lc]
		cstr = ngram[len(ngram) - Lc:]
		var = ngram[Lc:len(ngram) - Lc]
		anchor = cstl + cstr
		anchor_cand_pairs[' '.join(anchor)].append(' '.join(var))
	print 'extracted ', len(anchor_cand_pairs.keys()), 'anchors'
	paraphrase_pairs = defaultdict(int)
	for anchor in anchor_cand_pairs.keys():
		for cand1 in anchor_cand_pairs[anchor]:
			for cand2 in anchor_cand_pairs[anchor]:
				if cand1 == cand2: continue
				elif cand2 > cand1:
					paraphrase_pairs[(cand1, cand2)] += 1
				else:
					paraphrase_pairs[(cand2, cand1)] += 1
	print [i for i in sorted(paraphrase_pairs.iteritems(),key=lambda (k,v): v,reverse=True)[0:10]]
	return paraphrase_pairs


trump_results = single_corpus_paraphrase_extraction('trump_ascii.txt', 3)
# [(('im', 'were'), 10), (('build a wall', 'have a wall'), 4), (('have', 'make'), 4), (('and', 'and they'), 4), (('and', 'and ive seen it and'), 4), (('arab', 'arab name arab'), 4), (('best', 'greatest'), 4), (('2 billion car', '25 billion car'), 4), (('get', 'have'), 4), (('do', 'get'), 4)]
# Lc = 3 is better than 2 for Trump.

bible_results = single_corpus_paraphrase_extraction('../data/bible/americanstandardbible.txt', 3)
# [(('to', 'unto'), 218), (('god', 'jehovah'), 96), (('thy', 'your'), 82), (('them', 'you'), 74), (('on', 'upon'), 72), (('came', 'shall come'), 70), (('thee', 'you'), 66), (('came to', 'shall come to'), 64), (('israel', 'judah'), 56), (('said', 'spake'), 54)]
# Lc = 2 is better for bible.

shakespeare_results = single_corpus_paraphrase_extraction('../data/shakespeare-aligned/sparknotes/all_shakespeare_ascii.txt')
# does terrible with either Lc = 2 or 3 because sentences are too short. 


# american standard:
# 2.5 million ngrams from bible
# 1.8million without stopwords

# turump: 45257 sentences, 200597 ngrams
# TODO genericize some words (years, etc)
# TODO POS tagging as in paper
# TODO try sentence start and end markers
# try giving some weight to lexically similar anchors that are not exactly the same
# TODO stemming
# possible bug leading to phrase judgmentseat saying this man persuadeth men to' in americanstandard