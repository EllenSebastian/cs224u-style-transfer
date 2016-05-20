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

def collect_ngrams(sentences, Lc):
	ngrams = set([])
	for sentence in sentences:
		sentence = sentence.split(' ')
		for ngram_len in range(2 * Lc + minp, 2 * Lc + maxp + 1):
			for start in range(0, len(sentence) - ngram_len):
				# must be stored as strings because list is an unhashable type.
				ngrams.add(' '.join(sentence[start:start+ngram_len]))
	return ngrams

def collect_anchor_cand_pairs(ngrams, Lc):
	anchor_cand_pairs = defaultdict(list) # anchor --> list of candidates
	for ngram in ngrams:
		# notation based on paper p.123
		ngram = ngram.split()
		cstl = ngram[0:Lc]
		cstr = ngram[len(ngram) - Lc:]
		var = ngram[Lc:len(ngram) - Lc]
		anchor = cstl + cstr
		anchor_cand_pairs[' '.join(anchor)].append(' '.join(var))
	return anchor_cand_pairs



# version for 1 corpus (same as paper)
def single_corpus_paraphrase_extraction(file, Lc):
	sentences = parse_sentences(file)
	print 'parsed file'
	ngrams = collect_ngrams(sentences)
	print 'extracted ', len(ngrams), 'ngrams'
	anchor_cand_pairs = collect_anchor_cand_pairs(ngrams, Lc)
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


# for paraphrasing FROM corpus1 TO corpus2
def two_corpus_paraphrase_extraction(corpus1, corpus2, Lc1, Lc2):
	sentences1 = parse_sentences(corpus1)
	sentences2 = parse_sentences(corpus2)
	print 'parsed sentences'
	ngrams1 = collect_ngrams(sentences1, Lc1)
	ngrams2 = collect_ngrams(sentences2, Lc2)
	anchor_cands1 = collect_anchor_cand_pairs(ngrams1, Lc1)
	anchor_cands2 = collect_anchor_cand_pairs(ngrams2, Lc2)
	both_anchors = set(anchor_cands1.keys()) & set(anchor_cands2.keys())
	c1_to_c2 = defaultdict(int)
	c2_to_c1 = defaultdict(int)
	for anchor in both_anchors:
		for cand1 in anchor_cands1[anchor]:
			for cand2 in anchor_cands2[anchor]:
				if cand1 == cand2: continue
				else:
					c1_to_c2[(cand1, cand2)] += 1
					c2_to_c1[(cand2, cand1)] += 1
	print [i for i in sorted(c1_to_c2.iteritems(),key=lambda (k,v): v,reverse=True)[0:50]]
	return c1_to_c2

# trump_results = single_corpus_paraphrase_extraction('trump_ascii.txt', 3)
# [(('im', 'were'), 10), (('build a wall', 'have a wall'), 4), (('have', 'make'), 4), (('and', 'and they'), 4), (('and', 'and ive seen it and'), 4), (('arab', 'arab name arab'), 4), (('best', 'greatest'), 4), (('2 billion car', '25 billion car'), 4), (('get', 'have'), 4), (('do', 'get'), 4)]
# Lc = 3 is better than 2 for Trump.

# bible_results = single_corpus_paraphrase_extraction('../data/bible/americanstandardbible_clean.txt', 3)
# [(('to', 'unto'), 218), (('god', 'jehovah'), 96), (('thy', 'your'), 82), (('them', 'you'), 74), (('on', 'upon'), 72), (('came', 'shall come'), 70), (('thee', 'you'), 66), (('came to', 'shall come to'), 64), (('israel', 'judah'), 56), (('said', 'spake'), 54)]
# Lc = 2 is better for bible.

# shakespeare_results = single_corpus_paraphrase_extraction('../data/shakespeare-aligned/sparknotes/all_shakespeare_ascii.txt')
# does terrible with either Lc = 2 or 3 because sentences are too short. 

# americanstandard_paraphrases = single_corpus_paraphrase_extraction(corpus1, 3)

# kingjames_paraphrases = single_corpus_paraphrase_extraction('../data/bible/kingjamesbible_clean.txt', 3)

# american_kingjames_nonparallel = two_corpus_paraphrase_extraction(
#	'../data/bible/americanstandardbible_proverbs_revelation_clean.txt',
#	'../data/bible/kingjamesbible_genesis_psalms_clean.txt', 3, 3)

#bible_dickens_nonparallel = two_corpus_paraphrase_extraction(
#	'../data/bible/americanstandardbible_proverbs_revelation_clean.txt',
#	'../data/dickens/all_dickens_clean.txt', 3, 3)

#twain_dickens_nonparallel = two_corpus_paraphrase_extraction(
#	'../data/twain/all_twain_clean.txt',
#	'../data/dickens/all_dickens_clean.txt', 2, 2)




# some other first person novels?
# american standard:
# 2.5 million ngrams from bible
# 1.8million without stopwords

# turump: 45257 sentences, 200597 ngrams
# TODO genericize some words (years, etc)
# TODO POS tagging as in paper
# TODO try sentence start and end markers
# try giving some weight to lexically similar anchors that are not exactly the same
# TODO stemming
# possible bug leading to phrase judgmentseat saying this man persuadeth men to' in americanstandard - problem with line breaks?


#[(('jehovah', 'lord'), 2167), (('of jehovah', 'of lord'), 512), (('saith jehovah', 'saith lord'), 203), (('thy', 'thine'), 171), (('jehovah thy', 'lord thy'), 144), (('unto jehovah', 'unto lord'), 139), (('jehovah god', 'lord god'), 134), (('jehovah thy god', 'lord thy god'), 133), (('jehovah', 'god'), 118), (('jehovah god of', 'lord god of'), 99), (('jehovah hath', 'lord hath'), 94), (('jehovah of', 'lord of'), 92), (('before jehovah', 'before lord'), 91), (('thus saith jehovah', 'thus saith lord'), 89), (('lord jehovah', 'lord god'), 87), (('are', 'be'), 83), (('will', 'shall'), 82), (('house of jehovah', 'house of lord'), 82), (('my', 'mine'), 80), (('peoples', 'people'), 76), (('jehovah of hosts', 'lord of hosts'), 75), (('unto', 'to'), 72), (('o jehovah', 'o lord'), 69), (('for jehovah', 'for lord'), 67), (('show', 'shew'), 59), (('jehovah your', 'lord your'), 56), (('nations', 'heathen'), 54), (('word of jehovah', 'word of lord'), 53), (('jehovah god of israel', 'lord god of israel'), 53), (('saith lord jehovah', 'saith lord god'), 51), (('jehovah your god', 'lord your god'), 51), (('jehovah i', 'lord i'), 50), (('to', 'unto'), 50), (('tent of meeting', 'tabernacle of congregation'), 49), (('thy heart', 'thine heart'), 48), (('thy hand', 'thine hand'), 47), (('jehovah is', 'lord is'), 47), (('anything', 'any thing'), 47), (('on', 'in'), 46), (('jehovah our', 'lord our'), 45), (('jehovah came', 'lord came'), 44), (('jehovah to', 'lord to'), 43), (('jehovah in', 'lord in'), 41), (('from', 'of'), 41), (('jehovah for', 'lord for'), 41), (('saith jehovah of', 'saith lord of'), 39), (('honor', 'honour'), 38), (('as jehovah', 'as lord'), 38), (('saith jehovah of hosts', 'saith lord of hosts'), 38), (('jehovah our god', 'lord our god'), 38)]
