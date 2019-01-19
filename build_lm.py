#!/usr/bin/env python3
import sys
from math import log10


def truncate(f):
    return '%.10f' % f


def get_n_grams_dicts():
    unigram = dict()
    bigram= dict()
    trigram = dict()

    with open(sys.argv[1]) as fp:
        for line in fp:
            if line == "\n":
                continue

            splits = line.replace("\n", "").split("\t")
            count = splits[0]
            token = splits[1]

            if len(token.split()) == 1:
                unigram[token] = int(count)
            elif len(token.split()) == 2:
                bigram[token] = int(count)
            else:
                trigram[token] = int(count)

        return unigram, bigram, trigram


def write_to_file(output_file, value, prob, lgprob, key):
    output_file.write(str(value) + " " + truncate(prob) + " " + truncate(lgprob) + " " + key + "\n")


def main():
    unigrams, bigrams, trigrams = get_n_grams_dicts()

    output_file = open(sys.argv[2], "w+")  # Write to lm_file
    output_file.write("\data\\" + "\n")
    output_file.write("ngram 1: type=" + str(len(unigrams)) + " token=" + str(sum(unigrams.values())) + "\n")
    output_file.write("ngram 2: type=" + str(len(bigrams)) + " token=" + str(sum(bigrams.values())) + "\n")
    output_file.write("ngram 3: type=" + str(len(trigrams)) + " token=" + str(sum(trigrams.values())) + "\n")
    output_file.write("\n")

    output_file.write("\\1 - grams:" + "\n")
    N = sum(unigrams.values())
    for key, value in unigrams.items():
        prob = value / N
        lgprob = log10(prob)
        write_to_file(output_file, value, prob, lgprob, key)

    output_file.write("\n\\2 - grams:" + "\n")
    for key, value in bigrams.items():
        prob = 0
        splits = key.split()
        if len(splits) == 2:
            if key.split()[0] in unigrams:
                prob = value / unigrams[splits[0]]
                lgprob = log10(prob)
                write_to_file(output_file, value, prob, lgprob, key)

    output_file.write("\n\\3 - grams:" + "\n")
    for key, value in trigrams.items():
        splits = key.split()

        if len(splits) == 3:
            bigram_key = splits[0] + " " + splits[1]
            if bigram_key in bigrams:
                prob = value / bigrams[bigram_key]
                lgprob = log10(prob)
                write_to_file(output_file, value, prob, lgprob, key)

    output_file.write("\n" + "\end\\")
    output_file.close()


if __name__ == '__main__':
    main()