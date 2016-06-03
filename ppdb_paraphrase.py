from collections import defaultdict
from score_phrases import batch_select_best_phrase
from nltk import sent_tokenize, word_tokenize
import re
import json

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
    sentence = word_tokenize(sentence)
    paraphrases = []
    for p_length in range(1, min(len(sentence), max_source_len)):
        for i in range(len(sentence) - p_length + 1):
            source = ' '.join(sentence[i:i+p_length])
            if source in ppdb:
                for target in ppdb[source]:
                    paraphrase = sentence[:i] + [target] + sentence[i+p_length:]
                    paraphrases.append(untokenize(paraphrase))
    return list(set(paraphrases))

def paraphrase_text(text, model):
    paraphrased_text = []
    print 'Tokenizing...'
    sentences = sent_tokenize(text)

    # A list of lists of candidate paraphrases
    paraphrases = []

    print 'Generating paraphrases...'
    for sentence in sentences:
        paraphrases.append(get_paraphrases(sentence))

    print 'Selecting paraphrases...'
    selected_paraphrases = batch_select_best_phrase(paraphrases, model)
    for s, p in zip(sentences, selected_paraphrases):
        print s, '->', p

    return ' '.join(selected_paraphrases)

def main():
    with open('data/obama/hiroshima.txt') as f:
        text = f.read()
        text.encode("ascii","ignore")
        paraphrase_text(text, 'cv/checkpoint_37000.t7')

if __name__ == "__main__":
    main()
