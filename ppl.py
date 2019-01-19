#!/usr/bin/env python3
import sys
from math import log10


def truncate(f):
    return '%.10f' % f


def add_sentence_markers(sentence):
    return "<s> " + sentence + " </s>"


def read_lm_file():
    ngram_dict = dict()
    unigram_token_size = 0
    bigram_token_size = 0
    trigram_token_size = 0

    with open(sys.argv[1]) as fp:
        for line in fp:
            if line == "\n":
                continue

            if line[0:5] == "ngram":
                splits = line.split()
                token_size = int(splits[3].replace("token=", ""))

                if line[0:7] == "ngram 1":
                    unigram_token_size = token_size
                elif line[0:7] == "ngram 2":
                    bigram_token_size = token_size
                else:
                    trigram_token_size = token_size
                continue

            if len(line) > 0:
                if line[0] == "\\":
                    continue
                else:
                    splits = line.split()
                    if len(splits) >= 4:
                        count = int(splits[0])
                        ngram = " ".join(splits[3:])

                        ngram_dict[ngram] = count
    return unigram_token_size, bigram_token_size, trigram_token_size, ngram_dict


def interpolate(unigram_token_size, bigram_token_size, trigram_token_size, ngram_dict, lambda1, lambda2, lambda3):
    output_file = open(sys.argv[6], "w+")

    with open(sys.argv[5]) as f:  # Read test data
        sentences = f.read().splitlines()

    sent_num = len(sentences)
    total_word_num = 0
    total_oov_num = 0
    total_sum_lgprob = 0

    for i, sentence in enumerate(sentences):
        if sentence == "\n":
            continue

        sum_lgprob = 0
        word_num = 0
        oov_num = 0

        tokens = add_sentence_markers(sentence).split()
        # word_num += number of words in the sent excluding BOS and EOS
        word_num = word_num + len(tokens) - 2
        total_word_num = total_word_num + word_num
        tokens.remove("<s>")

        output_file.write("\n" + "Sent #" + str((i + 1)) + ": " + sentence + "\n")

        for index, token in enumerate(tokens):
            sub_tokens = tokens[:index + 1] if index < 3 else tokens[index - 2: index + 1]
            if token in ngram_dict:
                token_numerator = ""
                token_denominator = ""
                prob = 0

                is_unseen = None
                if len(sub_tokens) == 1:
                    token_numerator = token
                    token_denominator = "<s>"

                    bigram_probab_value, bigram_is_unseen = bigram_prob(["<s>", token], ngram_dict)
                    is_unseen = bigram_is_unseen
                    prob = lambda2 * bigram_probab_value \
                           + lambda1 * (ngram_dict[" ".join(sub_tokens)] / unigram_token_size)
                elif len(sub_tokens) == 2:
                    sub_tokens = ["<s>"] + sub_tokens
                    token_numerator = sub_tokens[2]
                    token_denominator = " ".join(sub_tokens[0:2])

                    prob, is_unseen = trigram_interpolation(sub_tokens, ngram_dict, lambda1, lambda2, lambda3, unigram_token_size)
                elif len(sub_tokens) == 3:
                    token_numerator = sub_tokens[2]
                    token_denominator = " ".join(sub_tokens[0:2])
                    prob, is_unseen = trigram_interpolation(sub_tokens, ngram_dict, lambda1, lambda2, lambda3, unigram_token_size)

                if is_unseen:
                    output_file.write(str(index + 1) + ": " + "lg P(" + token_numerator + " | " + token_denominator + ") = " + truncate(log10(prob)) + " " + "(unseen ngrams)" + "\n")
                else:
                    output_file.write(str(index + 1) + ": " + "lg P(" + token_numerator + " | " + token_denominator + ") = " + truncate(log10(prob)) + "\n")
                sum_lgprob = sum_lgprob + log10(prob)
            else:
                if len(sub_tokens) == 1:
                    sub_tokens = ["<s>"] + sub_tokens

                output_file.write(str(index + 1) + ": " + "lg P(" + token + " | " + " ".join(sub_tokens[:len(sub_tokens) - 1]) + ") = -inf (unknown word)" + "\n")
                oov_num = oov_num + 1

        cnt = word_num + 1 - oov_num
        total = -1 * (sum_lgprob / cnt)
        ppl = 10 ** total

        total_oov_num = total_oov_num + oov_num
        total_sum_lgprob = total_sum_lgprob + sum_lgprob

        output_file.write("1 sentence, " + str(word_num) + " words, " + str(oov_num) + " OOVs" + "\n")
        output_file.write("lgprob=" + truncate(sum_lgprob) + " ppl=" + truncate(ppl) + "\n\n\n")

    N = total_word_num + sent_num - total_oov_num
    ave_lgprob = total_sum_lgprob / N
    ppl = 10 ** (-1 * ave_lgprob)

    output_file.write("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%" + "\n")
    output_file.write("sent_num=" + str(sent_num) + " word_num=" + str(total_word_num) + " oov_num=" + str(total_oov_num) + "\n")
    output_file.write("lgprob= " + truncate(total_sum_lgprob) + " ave_lgprob=" + truncate(ave_lgprob) + " ppl=" + truncate(ppl) + "\n")

    output_file.close()


def trigram_interpolation(tokens, ngram_dict, lambda1, lambda2, lambda3, unigram_token_size):
    trigram_prob_value, is_unseen = trigram_prob(tokens, ngram_dict)
    bigram_prob_value, useless_is_unseen = bigram_prob(tokens[1:], ngram_dict)
    prob = lambda3 * trigram_prob_value\
               + lambda2 *  bigram_prob_value\
               + lambda1 * (ngram_dict[" ".join(tokens[2:])] / unigram_token_size)

    return prob, is_unseen


def bigram_prob(tokens, ngram_dict):
    key1 = " ".join(tokens)
    key2 = tokens[0]

    if (key1 in ngram_dict) & (key2 in ngram_dict):
        return ngram_dict[key1] / ngram_dict[key2], False
    else:
        return 0, True


def trigram_prob(tokens, ngram_dict):
    key1 = " ".join(tokens)
    key2 = " ".join(tokens[0:2])

    if (key1 in ngram_dict) & (key2 in ngram_dict):
        return ngram_dict[key1] / ngram_dict[key2], False
    else:
        return 0, True


def main():
    unigram_token_size, bigram_token_size, trigram_token_size, ngram_dict = read_lm_file()

    lambda1 = float(sys.argv[2])
    lambda2 = float(sys.argv[3])
    lambda3 = float(sys.argv[4])

    interpolate(unigram_token_size, bigram_token_size, trigram_token_size, ngram_dict, lambda1, lambda2, lambda3)


if __name__ == '__main__':
    main()
