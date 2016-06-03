from __future__ import print_function
import numpy as np
import subprocess
import os

def is_ascii(s):
    return all(ord(c) < 128 for c in s) and (not '\\' in s)

def batch_select_best_phrase(phrases, model, temp=1):
    """
    Inputs:
        phrases:
            a list of lists of candidate paraphrases, e.g
            [["The great day", "The awesome day"],["The big house","The huge house"]]
        model:
            a checkpoint .t7 file stored in torch-rnn/
            containing a neural language model trained through
            train.lua
    Output:
        a list of top matches
    """

    # Write the list to a file

    phrases_ascii = []
    for sentence in phrases:
        cps = filter(is_ascii, sentence)
        cps = map(lambda x: x.encode('ascii'), cps)
        phrases_ascii.append(cps)

    phrases = phrases_ascii

    os.chdir('torch-rnn')

    with open('temp.txt','w') as f:
        for sentence in phrases:
            for candidate_paraphrase in sentence:
                print(candidate_paraphrase, file=f)

            print("===============================", file=f)

    # Feed the list to score.lua in batch mode
    p = subprocess.Popen(
            [
                'th', 'score.lua',
                '-checkpoint', model,
                '-text', "none",
                '-temperature', str(temp),
                '-batch', '1'
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
    os.chdir('..')

    # Get a list of indices into phrases corresponding to the best candidate
    # per sentence
    best_idxs = p.stdout.read().strip().split(",")[:-1]
    best_idxs = map(int, best_idxs)

    best_candidates = []

    for i, sentence in enumerate(phrases):
        if sentence:
            best_candidates.append(sentence[best_idxs[i]])

    return best_candidates


def get_score(phrase, model, temp):
    os.chdir('torch-rnn')
    p = subprocess.Popen(
            [
                'th', 'score.lua',
                '-checkpoint', model,
                '-text', phrase,
                '-temperature', str(temp)
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
    os.chdir('..')
    return float(p.stdout.read().strip())

def select_best_phrase(phrases, model, temp=1, verbose=False):
    """
    Inputs:
        phrases:
            a list of candidate strings
        model:
            a checkpoint .t7 file stored in torch-rnn/
            containing a neural language model trained through
            train.lua
    Output:
        the string in the phrases list with the highest
        probability according to the language model
    """
    os.chdir('torch-rnn')
    scores = []
    for p in phrases:
        score = get_score(p, model, temp)
        scores += [score]
        if verbose:
            print (p, score)
    max_idx = np.argmax(scores)
    os.chdir('..')
    return phrases[max_idx]

def test_checkpoint(checkpoint_name):
    print('Checkpoint: ' + checkpoint_name)
    test_phrases = ["make America great again",
            "The widow rung a bell for supper",
            "'tis nobler in the mind to suffer",
                    "doubt that the sun doth move"]

    best_phrase = select_best_phrase(test_phrases, checkpoint_name, verbose=True)
    print('Best phrase: ' + best_phrase)

def main():
    for checkpoint in ['cv/checkpoint_37000.t7',
                       'shakespeare/checkpoint_17050.t7',
                       'twain/checkpoint_82150.t7']:
        test_checkpoint(checkpoint)

if __name__ == "__main__":
    main()
