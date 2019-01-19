#!/usr/bin/env python3
import sys
from collections import Counter


def add_sentence_markers(sentence):
    return "<s> " + sentence + " </s>"


def generate_n_grams(tokens, N):
    grams = [tokens[i:i + N] for i in range(len(tokens) - N + 1)]
    gram_list = []
    for gram in grams:
        gram_list.append(" ".join(gram))
    return gram_list


def sort_dict(dic):
    """
    :param dic: Dictionary to sort
    :return: sorted Dictionary first by value and if required by key (alphabetically)
    """
    return sorted(dic.items(), key=lambda k: (-k[1], k[0]))


def get_n_grams():
    """
    Generates n_grams
    :return: dict, dict, dict
            Unigram, Bigram, trigram
    """
    unigram_list = []
    bigram_list = []
    trigram_list = []

    # Open training_data file
    with open(sys.argv[1]) as fp:
        for line in fp:
            tokens = add_sentence_markers(line).split()
            unigram_list.extend(generate_n_grams(tokens, 1))
            bigram_list.extend(generate_n_grams(tokens, 2))
            trigram_list.extend(generate_n_grams(tokens, 3))

    return sort_dict(Counter(unigram_list)), sort_dict(Counter(bigram_list)), sort_dict(Counter(trigram_list))


def write_to_file(output_file, ngrams):
    for key, value in ngrams:
        output_file.write(str(value) + "\t" + key + "\n")


def main():
    unigrams, bigrams, trigrams = get_n_grams()
    # Open ngram_count_file for writing
    output_file = open(sys.argv[2], "w+")

    write_to_file(output_file, unigrams)
    write_to_file(output_file, bigrams)
    write_to_file(output_file, trigrams)

    output_file.close()


if __name__ == '__main__':
    main()