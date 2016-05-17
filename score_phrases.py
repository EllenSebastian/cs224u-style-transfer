import numpy as np
import subprocess
import os

def get_score(phrase, model, temp):
    p = subprocess.Popen(
            [
                'th', 'score.lua',
                '-checkpoint','cv/%s' % model,
                '-text', phrase,
                '-temperature', str(temp)
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
    return float(p.stdout.read().strip())

def select_best_phrase(phrases, model, temp=1, verbose=False):
    os.chdir('torch-rnn')
    scores = []
    for p in phrases:
        score = get_score(p, model, temp)
        scores += [score]
        if verbose:
            print (p, score)
    max_idx = np.argmax(scores)
    best_phrase = phrases[max_idx]
    if verbose:
        print 'Best phrase: %s' % best_phrase
    os.chdir('..')
    return best_phrase

def main():
    # Usage example
    test_phrases = ["make America great again",
                    "make America float again",
                    "make America plump again",
                    "make America fsdfs again"]
    select_best_phrase(test_phrases, "checkpoint_37000.t7", verbose=True)


if __name__ == "__main__":
    main()