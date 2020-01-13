import json
import codecs
import os

gold_parse_path = 'D:/conll15-st-03-04-15-dev/pdtb-parses.json'
proposed_parse_path = 'D:/Test_dev/pdtb-parses.json'

gold_parse_dict = json.loads(codecs.open(gold_parse_path, encoding='utf-8', errors='ignore').read())

proposed_parse_dict = json.loads(codecs.open(proposed_parse_path, encoding='utf-8', errors='ignore').read())

gold_docname_list = list(gold_parse_dict.keys())
proposed_docname_list = list(proposed_parse_dict.keys())

doc_list = []
error_rate_dict = {}
for doc_name in proposed_docname_list:
    gold_doc = gold_parse_dict[doc_name]
    proposed_doc = proposed_parse_dict[doc_name]
    sent_num  = len(gold_doc['sentences'])
    wrong_count = 0
    for sent_gold, sent_proposed in zip(gold_doc['sentences'], proposed_doc['sentences']):
        gold_tree = sent_gold["parsetree"][0:-3]
        prop_tree = sent_proposed["parsetree"][0:-2]
        if  gold_tree != prop_tree:
            wrong_count += 1
            print(gold_tree)
            print('\n')
            print(prop_tree)
            print('\n')

    error_rate_dict[doc_name] = {"sent_num" : sent_num, "error_ratio" : wrong_count / sent_num}
    print("The error ratio in document {} is {}".format(doc_name ,wrong_count / len(gold_doc['sentences'])))


