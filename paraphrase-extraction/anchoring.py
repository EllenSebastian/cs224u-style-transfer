import nltk
from collections import defaultdict
import string 
import nltk.tag.stanford as st
from nltk.stem.porter import PorterStemmer
stemmer = PorterStemmer()

tagger = st.StanfordNERTagger(
	'../stanford-ner-2015-12-09/classifiers/english.all.3class.distsim.crf.ser.gz',
	'../stanford-ner-2015-12-09/stanford-ner-3.6.0.jar')

minp = 1
maxp = 5

stopwords = set(['that', 'which', 'the', 'and', 'a', 'an', 'it'])

# also stem?
def tokenize(s, removeStopwords=False, stem=False):
	s = str(s).lower()
	s = s.translate(string.maketrans("",""), string.punctuation)
	if (not removeStopwords) and (not stem):
		return ['$S'] + nltk.word_tokenize(s) + ['$E']
	if (not removeStopwords):
		return ['$S'] + [stemmer.stem(i) for i in nltk.word_tokenize(s)] + ['$E']
	if (not stem):
		return ['$S'] + [i for i in nltk.word_tokenize(s) if i not in stopwords] + ['$E']		
	return ['$S'] + [stemmer.stem(i) for i in nltk.word_tokenize(s) if i not in stopwords] + ['$E']

def parse_sentences(file, removeStopwords=False, stem=False):
	with open(file, 'r') as in_file:
		text = in_file.read()
		text = text.decode('utf-8').encode('ascii','ignore')
		sents = nltk.sent_tokenize(text)
	#' '.join(sent.split()) removes extraneous whitespace
	#return [' '.join([i for i in remove_punct(sent).lower().split() if i not in stopwords]) for sent in sents]
	result = [' '.join(tokenize(sent, removeStopwords, stem)) for sent in sents]
	return [i for i in result if len(i) > 3]


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
def single_corpus_paraphrase_extraction(sentences, Lc):
	#sentences = parse_sentences(file)
	print 'parsed file'
	ngrams = collect_ngrams(sentences, Lc)
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



def two_corpus_paraphrase_extraction(sentences1, sentences2, Lc1, Lc2):
	print 'parsed', len(sentences1), ',', len(sentences2),' sentences'
	ngrams1 = collect_ngrams(sentences1, Lc1)
	ngrams2 = collect_ngrams(sentences2, Lc2)
	print 'collected ', len(ngrams1), ',', len(ngrams2),' ngrams'
	anchor_cands1 = collect_anchor_cand_pairs(ngrams1, Lc1)
	anchor_cands2 = collect_anchor_cand_pairs(ngrams2, Lc2)
	print 'collected ', len(anchor_cands1.keys()), ',', len(anchor_cands2.keys()),' anchors'
	c1_to_c2 = defaultdict(int)
	for anchor in set(anchor_cands1.keys()) & set(anchor_cands2.keys()):
		for cand1 in anchor_cands1[anchor]:
			for cand2 in anchor_cands2[anchor]:
				if cand1 == cand2: continue
				else:
					c1_to_c2[(cand1, cand2)] += 1
	print [i for i in sorted(c1_to_c2.iteritems(),key=lambda (k,v): v,reverse=True)[0:50]]
	return c1_to_c2


# for paraphrasing FROM corpus1 TO corpus2
def two_corpus_paraphrase_extraction_from_corpus(corpus1, corpus2, Lc1, Lc2):
	sentences1 = parse_sentences(corpus1)
	sentences2 = parse_sentences(corpus2)
	print 'parsed', len(sentences1), ',', len(sentences2),' sentences'
	return two_corpus_paraphrase_extraction(sentences1, sentences2)


#trump_sentences_stemmed_nostop = parse_sentences('trump_ascii.txt', True, True)
#trump_sentences_stemmed = parse_sentences('trump_ascii.txt', False, True)
#trump_sentences_nostop = parse_sentences('trump_ascii.txt', True, False)
#trump_sentences = parse_sentences('trump_ascii.txt', False, False)

#for s in [trump_sentences_stemmed_nostop, trump_sentences_stemmed, trump_sentences_nostop, trump_sentences]:
#	trump_results = single_corpus_paraphrase_extraction(s, 3)
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

twain_dickens_nonparallel = two_corpus_paraphrase_extraction(
	'../data/twain/all_twain_clean.txt',
	'../data/dickens/all_dickens_clean.txt', 2, 2)


twain_dickens_nonparallel3 = two_corpus_paraphrase_extraction(
	'../data/twain/all_twain_clean.txt',
	'../data/dickens/all_dickens_clean.txt', 3, 3)


# replace all people, places and organizations with PERSON, PLACE, or ORGANIZATION
# best if the senetneces DO contain stopwords
def tag_named_entities(sentences):
	tags_to_keep = set(['PERSON','PLACE','ORGANIZATION'])
	for sentence in sentences:
		tagged = tagger.tag(sentence)
		outsentence = [w[1] if w[1] in tags_to_keep else w[0]]


twain_dickens_nonparallel = two_corpus_paraphrase_extraction(
	'../data/twain/huckfinn_short.txt',
	'../data/dickens/taleoftwocities_short.txt', 2, 2)


twain_dickens_nonparallel3 = two_corpus_paraphrase_extraction(
	'../data/twain/all_twain_clean.txt',
	'../data/dickens/all_dickens_clean.txt', 3, 3)



dickens_sentences = parse_sentences('../data/dickens/taleoftwocities_clean.txt')
twain_sentences = parse_sentences('../data/twain/huckfinn_clean.txt')

dickens_all_sentences = parse_sentences('../data/dickens/all_dickens_clean.txt')
twain_all_sentences = parse_sentences('../data/twain/all_twain_clean.txt')
dickens_sentence_sample = random.sample(dickens_all_sentences, 47000)
dickens_twain_stemmed = two_corpus_paraphrase_extraction(dickens_sentence_sample, twain_all_sentences, 2, 2)
# [((u'i', u'he'), 213), ((u'wa', u'is'), 134), ((u'he', u'i'), 129), ((u'is', u'wa'), 120), ((u'he', u'it'), 119), ((u'i', u'we'), 115), ((u'i', u'they'), 104), ((u'i', u'it'), 99), ((u'i', u'you'), 99), ((u'she', u'he'), 93), ((u'it', u'he'), 93), ((u';', u','), 87), ((u'he', u'she'), 87), ((u'you', u'i'), 84), ((u'he', u'they'), 80), ((u'it', u'i'), 77), ((u'do', u'did'), 76), ((u"n't", u'not'), 76), ((u"'s", u'wa'), 76), ((u',', u';'), 74), ((u"'s", u'is'), 73), ((u'i', u'she'), 67), ((u'he', u'we'), 65), ((u'she', u'i'), 62), ((u'there', u'it'), 60), ((u'it', u'that'), 60), ((u'she', u'it'), 59), ((u'you', u'he'), 58), ((u'that', u'it'), 57), ((u'you', u'it'), 53), ((u'we', u'i'), 52), ((u'it', u'there'), 51), ((u'you', u'we'), 50), ((u'and', u'but'), 48), ((u'not', u"n't"), 47), ((u"'", u"''"), 46), ((u'they', u'he'), 46), ((u'that', u'so'), 45), ((u'wa', u"'s"), 45), ((u'she', u'they'), 44), ((u'my', u'hi'), 44), ((u'he', u'you'), 44), ((u'he', u'there'), 44), ((u'her', u'hi'), 43), ((u'did', u'do'), 42), ((u'you', u'they'), 40), ((u'thi', u'it'), 40), ((u'they', u'i'), 39), ((u'am', u'wa'), 39), ((u'hi', u'her'), 38)]
# 

dickens_twain_stemmed = two_corpus_paraphrase_extraction(dickens_sentences, twain_sentences, 2,2)
# [((u'i', u'he'), 114), ((u'he', u'i'), 73), ((u'is', u'wa'), 66), ((u'i', u'we'), 62), ((u'you', u'i'), 58), ((u'she', u'he'), 53), ((u'i', u'you'), 51), ((u'wa', u'is'), 47), ((u'he', u'we'), 43), ((u'he', u'they'), 39), ((u'am', u'wa'), 38), ((u'have', u'had'), 37), ((u'she', u'i'), 36), ((u'i', u'they'), 34), ((u'i', u'she'), 32), ((u'he', u'she'), 31), ((u'can', u'could'), 31), ((u'she', u'they'), 29), ((u'they', u'he'), 29), ((u'wa', u'am'), 28), ((u'you', u'we'), 28), ((u'wish', u'want'), 27), ((u'she', u'we'), 25), ((u'you', u'he'), 24), ((u'we', u'he'), 24), ((u'did', u'do'), 24), ((u'he', u'you'), 24), ((u'you', u'they'), 23), ((u'know', u'think'), 23), ((u'dont', u'do not'), 23), ((u'think', u'know'), 22), ((u'could', u'can'), 22), ((u'had', u'have'), 22), ((u'do', u'did'), 22), ((u'dont', u'didnt'), 21), ((u'we', u'i'), 21), ((u'know', u'see'), 21), ((u'should', u'would'), 20), ((u'ha', u'had'), 19), ((u'they', u'we'), 19), ((u'they', u'i'), 19), ((u'you', u'him'), 18), ((u'will', u'could'), 18), ((u'think', u'wish'), 18), ((u'are', u'were'), 18), ((u'we', u'you'), 17), ((u'could', u'would'), 17), ((u'my', u'hi'), 17), ((u'never', u'not'), 17), ((u'think', u'said'), 16)]

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
