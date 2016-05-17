from nltk.translate import bleu_score

# use sentence_bleu to evaluate single-sentence paraphrases. 
# reference = known good translation into the destination language
reference = 'The king is staying up all night drinking and dancing'.split(' ')
# hypothesis = system's translation into the destination language
hypothesis1 = 'The king doth wake tonight and takes his rouse'.split(' ')
hypothesis2 = 'The king stays up tonight and takes his rouse'.split(' ')
hypothesis3 = 'The king stays up tonight drinking and dancing'.split(' ')
hypothesis4 = 'The king stays up all night drinking and dancing'.split(' ')

for hyp in [hypothesis1, hypothesis2, hypothesis3, hypothesis4, reference]:
	print bleu_score.sentence_bleu([reference], hyp)


# use corpus_bleu to evaluate multi-sentence paraphrases.
reference1 = 'the musicians make a ruckus to celebrate his draining another cup.'.split(' ')
hypothesis1_1 = 'The kettle-drum and trumpet thus bray out The triumph of his pledge.'.split(' ')

print bleu_score.corpus_bleu(
	[[reference], [reference1]],  # list of references for each sentence in the corpus
	[hypothesis1, hypothesis1_1]) # 1 hypothesis for each sentence in the corpus 
