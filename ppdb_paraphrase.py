from collections import defaultdict
from score_phrases import batch_select_best_phrase
from nltk import sent_tokenize, word_tokenize
from extract_phrases import extract_phrases_from_sentence
import re
import json
import itertools

def parse_ppdb_line(line):
    fields = line.split(' ||| ')
    return (fields[1], fields[2])

def process_ppdb(ppdb_file, json_file):
    ppdb = defaultdict(list)
    with open(ppdb_file) as f:
        for line in f:
            source, target = parse_ppdb_line(line)
            ppdb[source].append(target)
    json.dump(ppdb, open(json_file, "wb"))

def load_ppdb(json_file):
    return json.load(open(json_file, "rb"))

print "Loading PPDB..."
ppdb = load_ppdb('ppdb-s.json')

def untokenize(words):
    """
    From https://github.com/commonsense/metanl/

    Untokenizing a text undoes the tokenizing operation, restoring
    punctuation and spaces to the places that people expect them to be.
    Ideally, `untokenize(tokenize(text))` should be identical to `text`,
    except for line breaks.
    """
    text = ' '.join(words)
    step1 = text.replace("`` ", '"').replace(" ''", '"').replace('. . .',  '...')
    step2 = step1.replace(" ( ", " (").replace(" ) ", ") ")
    step3 = re.sub(r' ([.,:;?!%]+)([ \'"`])', r"\1\2", step2)
    step4 = re.sub(r' ([.,:;?!%]+)$', r"\1", step3)
    step5 = step4.replace(" '", "'").replace(" n't", "n't").replace(
         "can not", "cannot")
    step6 = step5.replace(" ` ", " '")
    return step6.strip()

def get_paraphrases(sentence, max_source_len=4):
    """
    Inputs:
        sentence:
            a string to paraphrase
        max_source_len:
            the maximum number of words in the source to query PPDB with at a time
            all phrases containing [1,max_source_len] words will be looked up in PPDB
            if a phrase is found in PPDB, it is replaced with the paraphrase and considered
            a candidate.
    Output:
        a list of candidate paraphrases for "sentence". each candidate sentence contains
        only 1 substitution
    """
    paraphrases = [sentence]
    sentence = word_tokenize(sentence)
    for p_length in range(1, min(len(sentence), max_source_len) + 1):
        for i in range(len(sentence) - p_length + 1):
            source = ' '.join(sentence[i:i+p_length])
            if source in ppdb:
                for target in ppdb[source]:
                    paraphrase = sentence[:i] + [target] + sentence[i+p_length:]
                    paraphrases.append(untokenize(paraphrase))
    return list(set(paraphrases))

def fixed_chunker(sentence, chunk_len=4):
    sentence = word_tokenize(sentence)
    chunks = [sentence[pos:pos + chunk_len] for pos in xrange(0, len(sentence), chunk_len)]
    chunks = [untokenize(c) for c in chunks]
    return chunks

def stopwords_chunker(sentence):
    sentence = word_tokenize(sentence)
    stopwords = [",","and","-","or","that","which"]
    chunks = []
    j = 0
    for i in xrange(len(sentence)):
        if sentence[i] in stopwords:
            if sentence[j:i] != []:
                chunks.append(sentence[j:i])
            j = i
    chunks.append(sentence[j:])
    chunks = [untokenize(c) for c in chunks]
    return chunks

def get_multi_paraphrases(sentence, model, chunker=stopwords_chunker):
    """
    Splits sentence up into chunks according to the chunker function, finds
    paraphrases for each chunk and concatenates together the best-scoring
    paraphrase per chunk. Returns a string with the best paraphrase for
    sentence.

    chunker can be: - fixed_chunker
                    - stopwords_chunker
                    - extract_phrases_from_sentence
    """
    chunks = chunker(sentence)
    c_paraphrases = []
    for c in chunks:
        c_paraphrases.append(get_paraphrases(c))
    selected_paraphrases = batch_select_best_phrase(c_paraphrases, model)
    return ' '.join(selected_paraphrases)

    # sentence_paraphrases = set(itertools.product(*c_paraphrases))
    # sentence_paraphrases = [' '.join(p) for p in sentence_paraphrases]

    # return list(set(sentence_paraphrases))

def paraphrase_text(text, model):
    """
    Splits text into sentences, and paraphrases each sentence separately. Currently
    uses get_paraphrases on each sentence to generate candidate paraphrases, which
    only performs one paraphrase substitution per sentence.

    model should be a string containing the location in torch-rnn of the language
    model checkpoint, e.g. 'cv/checkpoint_37000.t7'
    """
    paraphrased_text = []
    print 'Tokenizing...'
    sentences = sent_tokenize(text)

    # A list of lists of candidate paraphrases
    paraphrases = []

    print 'Generating paraphrases...'
    for sentence in sentences:
        paraphrases.append(get_paraphrases(sentence))

    print 'Selecting paraphrases...'
    transformed_sentences = batch_select_best_phrase(paraphrases, model)
    for s, p in zip(sentences, transformed_sentences):
        print s, '->', p

    return ' '.join(transformed_sentences)

def paraphrase_text_by_chunks(text, model, chunker=stopwords_chunker):
    paraphrased_text = []
    print 'Tokenizing...'
    sentences = sent_tokenize(text)

    transformed_sentences = []

    print 'Generating paraphrases...'
    for sentence in sentences:
        transformed_sentence = get_multi_paraphrases(sentence, model, chunker=chunker)
        print sentence, '->', transformed_sentence
        transformed_sentences += [transformed_sentence]

    return ' '.join(transformed_sentences)

def main():
    styles = {
        'trump' : 'cv/checkpoint_37000.t7',
        'shakespeare' : 'shakespeare/checkpoint_17050.t7',
        'twain' : 'twain/checkpoint_82150.t7'
    }
    with open('data/sources/dream.txt') as f:
        text = f.read()
        text.encode("ascii","ignore")
        print paraphrase_text_by_chunks(text, styles['shakespeare'], chunker=extract_phrases_from_sentence)

if __name__ == "__main__":
    main()
