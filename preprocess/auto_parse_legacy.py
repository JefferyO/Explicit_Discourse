import xmltodict
import collections
import xml.dom.minidom as mini
import json
import os
import subprocess
from stanfordcorenlp import StanfordCoreNLP

Berkeley_parser_path = "D:/berkeleyparser/"
xml_path = 'D:/Stanford_Corenlp/stanford-corenlp-full-2012-11-12/wsj_1000.xml'


# legacy version of xml to parser
def xml_to_json(xml_file_path, berkeley_tree_path, berkeley_raw_path):
    if 'wsj_2257' in xml_file_path:
        print('error signal')
    with open(xml_file_path) as xml:
        xml_str = xml.read()
    b_tree_file = open(berkeley_tree_path, 'w')
    b_tree_file.close()
    b_raw_file = open(berkeley_raw_path, 'w')
    b_raw_file.close()

    b_raw_file = open(berkeley_raw_path, 'a')
    # doc = mini.parse(xml_file_path)
    # print(doc)
    xml_dict = xmltodict.parse(xml_str)

    sent_list = xml_dict['root']['document']['sentences']['sentence']
    sent_list_filtered = []
    # berkeley_tree_list = process_berkeley_tree(berkeley_tree_path)
    for sent in sent_list:
        sent_filtered = collections.OrderedDict()
        if not isinstance(sent, str):
            if sent['basic-dependencies']:
                sent_filtered['dependencies'] = process_dependencies(sent['basic-dependencies']['dep'])
            else:
                continue
            '''
            if len(sent['dependencies'][0]) > 1:
                sent_filtered['dependencies'] = process_dependencies(sent['dependencies'][0]['dep'])
            '''
            sent_filtered['words'], tokenized_sent = process_tokens(sent['tokens'])
            b_raw_file.write(tokenized_sent + '\n')
            sent_list_filtered.append(sent_filtered)
        else:
            sent = sent_list
            if sent['basic-dependencies']:
                sent_filtered['dependencies'] = process_dependencies(sent['basic-dependencies']['dep'])
            else:
                continue
            '''
            if len(sent['dependencies'][0]) > 1:
                sent_filtered['dependencies'] = process_dependencies(sent['dependencies'][0]['dep'])
            '''
            sent_filtered['words'], tokenized_sent = process_tokens(sent['tokens'])
            b_raw_file.write(tokenized_sent + '\n')
            sent_list_filtered.append(sent_filtered)

            break

    b_raw_file.close()

    arg = 'java -jar ' + Berkeley_parser_path + 'BerkeleyParser-1.5.jar -gr ' + Berkeley_parser_path + 'eng_sm6.gr -inputFile ' \
          + berkeley_raw_path + ' -outputFile ' + berkeley_tree_path

    os.system(arg)

    b_tree_file = open(berkeley_tree_path, 'r')
    tree_list = b_tree_file.readlines()

    for i in range(0, len(tree_list)):
        sent_list_filtered[i]['parsetree'] = tree_list[i]
    '''
    for tree in tree_list:
        sent_list_filtered[tree_list.index(tree)]['parsetree'] = tree

    document = collections.OrderedDict()
    document['sentences'] = sent_list_filtered
    parses = collections.OrderedDict()
    parses['wsj_1000'] = document



    # json_str = json.dumps(parses)
    with open('D:\Test_trail\pdtb-parses.json', 'w') as json_file:
        json.dump(parses, json_file)
    '''
    return sent_list_filtered


def berkeley_parse(berkeley_raw_path, berkeley_tree_path, berkeley_parser_path, parse_dict):
    print("Start annotate with Berkeley parser")
    # run berkeley parser on raw text
    arg = 'java -jar ' + berkeley_parser_path + 'BerkeleyParser-1.7.jar -gr ' + Berkeley_parser_path + 'eng_sm6.gr -inputFile ' \
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


def process_parsetree(original_parsetree):

    processed_parsetree = ''
    parse_list = original_parsetree.split('\n')
    for component in parse_list:
        processed_parsetree += ' '.join(component.split('          '))

    processed_parsetree = processed_parsetree.replace('ROOT', '')

    for i in range(1, len(processed_parsetree)):
        if processed_parsetree[i] == '(' and processed_parsetree[i - 1] != ' ':
            processed_parsetree = processed_parsetree[0: i] + ' ' + processed_parsetree[i:]

    return processed_parsetree + '\n'

