import json
import os
import time
import re
from stanfordcorenlp import StanfordCoreNLP

Berkeley_parser_path = "D:/berkeleyparser/"
xml_path = 'D:/Stanford_Corenlp/stanford-corenlp-full-2012-11-12/wsj_1000.xml'


# process raw data from a directory with corenlp and berkeley parser simultaneously
def parse_raw(raw_dir):
    # connect to the nlp server
    nlp = StanfordCoreNLP('http://localhost', port=9000)
    props = {'annotators': 'tokenize,ssplit,pos,parse', 'pipelineLanguage': 'en', 'outputFormat': 'json'}

    # parse_dict = json.loads(nlp.annotate(sentence, properties=props))
    parse_dict = {}

    # iterate over all raw files and run stanford parser
    # b_raw_file = open(berkeley_raw_path, 'a')
    print("Start annotate with stanford parser\n")
    start_time_stanford = time.time()
    for filename in os.listdir(raw_dir):
        # if int(filename[-4:len(filename)]) < 2055:
        #    continue
        print("start to parse file {} with stanford parser".format(filename))
        current_file = os.path.join(raw_dir, filename)
        current_doc_dict = {}
        with open(current_file, 'r', encoding='gbk') as raw:
            sent_filtered_list = []
            raw_text = raw.read()
            if filename == "wsj_1915" or filename == "wsj_2013":
                raw_list = raw_text.split("\n")
                raw_seg = ["", "", ""]
                for idx, line in enumerate(raw_list):
                    if idx < len(raw_list) // 3:
                        raw_seg[0] += line + "\n"
                    elif idx < len(raw_list) * 2 // 3:
                        raw_seg[1] += line + "\n"
                    else:
                        raw_seg[2] += line + "\n"
                for seg in raw_seg:
                    sent_dicts = json.loads(nlp.annotate(seg, properties=props))
                    for sent in sent_dicts['sentences']:
                        words, tokenized_sent = process_tokens(sent['tokens'])
                        sent_filtered_list.append({'dependencies': [], 'parsetree': process_parsetree(sent['parse']), 'words': words})

                current_doc_dict['sentences'] = sent_filtered_list
                parse_dict[filename] = current_doc_dict
                continue

            # call corenlp on current server on current raw file
            sent_dicts = json.loads(nlp.annotate(raw_text, properties=props))
            for sent in sent_dicts['sentences']:
                words, tokenized_sent = process_tokens(sent['tokens'])
                sent_filtered_list.append({'dependencies': [], 'parsetree': process_parsetree(sent['parse']), 'words': words})
                # b_raw_file.write(tokenized_sent + '\n')

            # put sentences to current doc and put current doc in parse dict
            current_doc_dict['sentences'] = sent_filtered_list
            parse_dict[filename] = current_doc_dict
            # print(parse_dict)
            # exit(0)
    print("Stanford parser annotation finished")
    print("Stanford parser used {} seconds\n".format(time.time() - start_time_stanford))

    return parse_dict  # parse_with_berkeley(berkeley_raw_path, berkeley_tree_path, parse_dict)


def process_tokens(original_tokens_list):
    processed_token_list = []
    tokenized_sent = ''
    for token in original_tokens_list:
        current_token_property = {'CharacterOffsetBegin': int(token['characterOffsetBegin'] + 9),
                                  'CharacterOffsetEnd': int(token['characterOffsetEnd'] + 9), 'Linkers': [],
                                  'PartOfSpeech': token['pos']}
        processed_current_token = [token['word'], current_token_property]
        tokenized_sent += token['word'] + ' '
        # tokenized_sent.replace(" . ", ".")
        processed_token_list.append(processed_current_token)

    return processed_token_list, tokenized_sent[0: len(tokenized_sent) - 1]


def process_dependencies(original_dep):
    processed_dep_list = []
    dependent_idx_list = []

    for token_dep in original_dep:
        tp = token_dep['@type']
        governor = token_dep['governor']['#text']
        governor_idx = token_dep['governor']['@idx']
        dependent = token_dep['dependent']['#text']
        dependent_idx = token_dep['dependent']['@idx']

        processed_token_dep = [tp, governor + '-' + governor_idx, dependent + '-' + dependent_idx]
        processed_dep_list.append(processed_token_dep)

        dependent_idx_list.append(int(dependent_idx))

    root_token_dep = processed_dep_list[0]
    root_token_idx = int(original_dep[0]['dependent']['@idx'])

    dependent_idx_list.sort()
    correct_root_idx = dependent_idx_list.index(root_token_idx)

    processed_dep_list.remove(root_token_dep)
    processed_dep_list.insert(correct_root_idx, root_token_dep)

    return []


def process_parsetree(original_parsetree):

    process_parsetree = re.sub(r"\s+", " ", original_parsetree)
    process_parsetree = process_parsetree.replace("ROOT", "")
    return process_parsetree + "\n"


def process_berkeley_tree(path_to_tree):
    processed_tree_list = []
    tree_str = ''
    with open(path_to_tree, 'r') as tree_file:
        for line in tree_file:
            if '(())' not in line:
                tree_str.split()

    return processed_tree_list


def parse_with_berkeley(berkeley_raw_path, berkeley_tree_path, parse_dict):
    print("Start annotate with Berkeley parser")
    # run berkeley parser on raw text
    arg = 'java -jar ' + Berkeley_parser_path + 'BerkeleyParser-1.7.jar -gr ' + Berkeley_parser_path + 'eng_sm6.gr -inputFile ' \
        + berkeley_raw_path + ' -outputFile ' + berkeley_tree_path
    os.system(arg)

    # add constituency parse to parse dict
    parse_tree_idx = 0
    b_tree_file = open(berkeley_tree_path, 'r')
    tree_list = b_tree_file.readlines()

    for doc in parse_dict:
        for sent in parse_dict[doc]['sentences']:
            sent['parsetree'] = tree_list[parse_tree_idx]
            parse_tree_idx = parse_tree_idx + 1
    b_tree_file.close()
    print("Berkeley parser annotation finished")
    return parse_dict


def test_parsing_time():
    print("Stanford CoreNLP started")
    nlp = StanfordCoreNLP('http://localhost', port=9000)
    props = {'annotators': 'tokenize,ssplit,pos,parse', 'pipelineLanguage': 'en', 'outputFormat': 'json'}
    raw_total = open("berkeley_raw.txt", 'r')
    raw_text = raw_total.read()
    start_time = time.time()
    sent_dicts = json.loads(nlp.annotate(raw_text, properties=props))
    print("Stanford nlp used {} seconds for a large batch".format(time.time() - start_time))


# test_parsing_time()
