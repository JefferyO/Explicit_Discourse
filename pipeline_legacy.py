import os
import collections
import json
from stanfordcorenlp import StanfordCoreNLP
import subprocess
import argparse
from glob import glob
from preprocess import auto_parse, process_result


# remove the starting part to ensure the correct stanford parser result
def pre_process_row_for_stanford(raw_dir_path):
    dummy_start = '.START \n\n'

    for filename in os.listdir(raw_dir_path):
        file = open(os.path.join(raw_dir_path, filename), 'r', encoding='gbk')
        file_str = str(file.read())
        file.close()
        file = open(os.path.join(raw_dir_path, filename), 'wb')
        file.close()
        file = open(os.path.join(raw_dir_path, filename), 'wb')

        if dummy_start in file_str:
            file_str = file_str.replace(dummy_start, '')
        file.write(bytes(file_str, encoding='gbk'))
        file.close()


# legacy code that only used when processing with corenlp local pipeline
def sent_split_to_file(data_raw_path):
    # split sent into one sent per file
    for filename in os.listdir(data_raw_path):
        # create directory for each raw file to store sent_split file
        current_dir_name = filename + '_sent_split'
        current_dir_path = os.path.join(data_raw_path, current_dir_name)
        os.mkdir(current_dir_path)
        count = 0   # num of sent in each current file

        # read raw file sentences
        current_raw_path = os.path.join(data_raw_path, filename)
        with open(current_raw_path, 'r', encoding='gbk') as raw:
            for line in raw:
                line_str = str(line)
                if line_str != '\n':
                    count += 1
                    # create a sent file for each nonempty sent
                    current_sent_file = filename + '_' + str(count)
                    current_sent_file_path = os.path.join(current_dir_path, current_sent_file)
                    sent_f = open(current_sent_file_path, 'wb')
                    sent_f.write(bytes(line_str, encoding='gbk'))
                    sent_f.close()


# run core-nlp on raw data
def run_stanford_nlp(data_raw_path, stanford_parser_path):
    cwd = os.getcwd()
    berkeley_tree_path = os.path.join(cwd, 'berkeley_tree.txt')
    berkeley_raw_path = os.path.join(cwd, 'berkeley_raw.txt')

    # start the CoreNLP server
    os.chdir(stanford_parser_path)

    '''
    # connect to corenlp intercative shell
    arg_corenlp = 'java -cp "*" edu.stanford.nlp.pipeline.StanfordCoreNLP'
    os.system(arg_corenlp)
    current_raw_path = os.path.join(data_raw_path, 'wsj_2201')
    with open(current_raw_path, 'r', encoding='gbk') as raw:
        for line in raw:
            print(subprocess.check_output([line]).decode(encoding='GBK'))

    '''
    # os.chdir(cwd)


# legacy parses for old xml version
def automatic_parses_legacy(data_directory, stanford_parser_path, berkeley_raw_path, berkeley_tree_path):
    parses = collections.OrderedDict()

    xml_list = filter(lambda x: 'wsj' in x, [xml_file for xml_file in glob(stanford_parser_path + '/*.xml')])

    for xml_file in xml_list:
        # convert parses of WSJ raw files from xml to CONLL desired json format
        current_sent_list = auto_parse.xml_to_json(xml_file_path=xml_file, berkeley_raw_path=os.path.join(os.getcwd(), berkeley_raw_path),
                                                   berkeley_tree_path=os.path.join(os.getcwd(), berkeley_tree_path))
        current_doc = collections.OrderedDict()
        current_doc['sentences'] = current_sent_list

        # get current WSJ name
        wsj_name = xml_file.replace('.xml', '')
        wsj_name = wsj_name.replace(stanford_parser_path + '\\', '')
        parses[wsj_name] = current_doc

    pdtb_parses = os.path.join(data_directory, 'pdtb-parses.json')
    with open(pdtb_parses, 'w') as auto_parses:
        json.dump(parses, auto_parses)


# legacy pipeline for old xml file base version
def discourse_parse(data_directory, stanford_parser_path, output_directory,
                    berkeley_raw_path='berkeley_raw.txt', berkeley_tree_path='berkeley_tree.txt'):
    data_raw_path = data_directory + '/raw'

    # pre-process auto-parses
    pre_process_row_for_stanford(data_raw_path)

    # pre_process_row_for_stanford(data_raw_path)
    automatic_parses(data_directory=data_directory, stanford_parser_path=stanford_parser_path,
                     berkeley_raw_path=berkeley_raw_path, berkeley_tree_path=berkeley_tree_path)

    # run discourse parser
    arg_parser = 'python parser.py ' + data_directory + ' none ' + output_directory
    os.system(arg_parser)

    # post-process to CONLL required evaluation format
    output_path = os.path.join(output_directory, 'output.json')
    final_output_path = os.path.join(output_directory, 'output_final.json')
    process_result.reformat_output(output_json_path=output_path, processed_output_path=final_output_path)

