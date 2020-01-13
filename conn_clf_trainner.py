import json
import os
import config
import codecs
import collections


def get_doc_offset(parse_dict, DocID, sent_index, list):
    offset = 0
    for i in range(sent_index):
        offset += len(parse_dict[DocID]["sentences"][i]["words"])
    temp = []
    for item in list:
        temp.append(item + offset)
    return temp


def get_golden_conn_list(relation_path):
    pdtb_file = open(relation_path, 'r')
    relations = [json.loads(x) for x in pdtb_file]
    golden_conn_list = []
    for relation in relations:
        if relation['Type'] == "Explicit":
            token_idx_list_sent = [token_idx[-1] for token_idx in relation['Connective']['TokenList']]
            token_idx_list_doc = [token_idx[-3] for token_idx in relation['Connective']['TokenList']]
            sent_idx = relation['Connective']['TokenList'][0][-2]
            golden_conn_list.append([relation['DocID'], sent_idx, token_idx_list_sent, token_idx_list_doc])
    pdtb_file.close()

    return golden_conn_list


def write_labeled_instance_to_svm(relation_path, conn_path, feat_path, svm_path):
    with open(conn_path, 'r') as candidate:
        candidate_conns = json.load(candidate)
    candidate_conns_list = [[x[0], x[1], set(x[2])] for x in candidate_conns['conns_list']]
    target_list = []
    for conn in candidate_conns_list:
        target = 0
        for gold_conn in get_golden_conn_list(relation_path):
            if conn[0] == gold_conn[0] and conn[1] == gold_conn[1] and conn[2].issubset(gold_conn[2]):
                target = 1
                break
        target_list.append(target)
    feat = open(feat_path, "r")
    feat_list = feat.readlines()
    feat_list_svm = [str(target) + " " + feat for target, feat in zip(target_list, feat_list)]

    with open(svm_path, 'w') as svm:
        for feat_svm in feat_list_svm:
            svm.write(feat_svm)


def train_model(svm_path):
    arg_create_instance = config.MALLET_PATH + r"\bin\mallet import-svmlight --input " + svm_path + " --output conn_train.mallet"
    os.system(arg_create_instance)
    arg_train_conn_model_cv = config.MALLET_PATH + r"\bin\mallet train-classifier --cross-validation 10 --input .\conn_train.mallet --output-classifier " + conn_model_path + " --trainer MaxEnt"
    arg_train_conn_model = config.MALLET_PATH + r"\bin\mallet train-classifier --input .\conn_train.mallet --output-classifier " + conn_model_path + " --trainer MaxEnt"
    os.system(arg_train_conn_model)

# train_model(svm_path=feat_svmlight_path)


def alignment(gold_parse_dict, proposed_parse_dict):
    gold_token_dict = collections.OrderedDict()
    prop_token_dict = collections.OrderedDict()
    for doc_name in proposed_parse_dict:
        doc_alignment_list = []
        gold_sent_list = gold_parse_dict[doc_name]['sentences']
        proposed_sent_list = proposed_parse_dict[doc_name]['sentences']
        # Extract the tokenized document:
        gold_doc_token = []
        prop_doc_token = []
        for sent in gold_sent_list:
            gold_doc_token += [token[0] for token in sent['words']]
        for sent in proposed_sent_list:
            prop_doc_token += [token[0] for token in sent['words']]
        gold_token_dict[doc_name] = gold_doc_token
        prop_token_dict[doc_name] = prop_doc_token

    gold_token_dict.keys()
    prop_token_dict.keys()

    alignment_corpus = collections.OrderedDict()
    large_error_list = []
    for doc_name in gold_token_dict.keys():
        # if doc_name != "wsj_1545":
        #     continue
        print("Aligning the doc {}".format(doc_name))
        cur_gold_tokens = gold_token_dict[doc_name]
        cur_prop_tokens = prop_token_dict[doc_name]
        alignment_list = []
        gold_cur_idx = 0
        prop_cur_idx = 0
        '''
        for prop_idx, prop_token in enumerate(cur_prop):
            gold_token = cur_gold[gold_cur_idx]
            alignment_list.append({"prop_idx": prop_idx, "prop_token": prop_token,
                                   "gold_idx": gold_cur_idx, "gold_token": gold_token})
            # exactly match
            if prop_token == gold_token:
                gold_cur_idx += 1
            elif prop_token in gold_token:
                print("{} is substring of {}".format(prop_token, gold_token))
            else:
                gold_cur_idx += 1
        alignment_corpus[doc_name] = alignment_list
        '''
        for idx, token in enumerate(cur_prop_tokens):
            alignment_list.append({"prop_idx": idx, "prop_token": token,
                                   "gold_idx": [], "gold_token": ""})
        prev_error = False
        error_count = 0
        while gold_cur_idx < len(cur_gold_tokens) and prop_cur_idx < len(cur_prop_tokens):
            prop_token = cur_prop_tokens[prop_cur_idx]
            gold_token = cur_gold_tokens[gold_cur_idx]
            gold_token = gold_token.replace(r"\/", r"/")
            alignment_list[prop_cur_idx]['gold_idx'].extend([gold_cur_idx])
            alignment_list[prop_cur_idx]['gold_token'] += gold_token
            # if prop_cur_idx == 609:
            #     print("pause_here")

            # case 1: exact match
            if prop_token == gold_token:
                gold_cur_idx += 1
                prop_cur_idx += 1
                prev_error = False

            # case 2: prop is a substring of gold
            elif prop_token in gold_token:
                prev_error = False
                # print("prop_token {} is substring of gold_token {}".format(prop_token, gold_token))
                # If the longer gold token is fully filled:
                if alignment_list[prop_cur_idx]['prop_token'] == alignment_list[prop_cur_idx]['gold_token'][-len(alignment_list[prop_cur_idx]['prop_token']):] \
                        and len(alignment_list[prop_cur_idx - 1]['prop_token']) + len(alignment_list[prop_cur_idx]['prop_token']) >= len(alignment_list[prop_cur_idx]['gold_token']) - 1:
                    gold_cur_idx += 1
                prop_cur_idx += 1
            # case 3: gold is a substring of prop
            elif gold_token in prop_token:
                prev_error = False
                # print("gold_token {} is substring of prop_token {}".format(gold_token, prop_token))

                # The case of "N.Y.."
                if prop_cur_idx < len(cur_prop_tokens) - 1 and prop_token[-1] == "." and cur_prop_tokens[prop_cur_idx + 1] == "." and prop_token[-2] != ".":
                    # print("N.Y.. case met, prop_token is {}, gold_token is {}".format(prop_token, gold_token))
                    prop_cur_idx += 1

                # If the longer proposed token is fully filled:
                elif alignment_list[prop_cur_idx]['prop_token'][-1] == alignment_list[prop_cur_idx]['gold_token'][-1] \
                        and len(alignment_list[prop_cur_idx]['gold_token']) >= len(alignment_list[prop_cur_idx]['prop_token']) - 1:
                    prop_cur_idx += 1
                gold_cur_idx += 1

            # case 4: 1/2-year case
            elif (len(gold_token) >= 5 and gold_token[1] == '/' and gold_token[3] == '-') and gold_token[:3] in prop_token:
                prop_cur_idx += 1
                continue

            # case 4: tokenize error, ignore
            else:
                # print("error tokens at idx {}, prop is {}, gold is {}".format(prop_cur_idx ,prop_token, gold_token))
                error_count += 1
                # check whether previous already error
                if prev_error:
                    prev_error = False
                    alignment_list[prop_cur_idx]['gold_idx'] = []
                    alignment_list[prop_cur_idx]['gold_token'] = ""
                    # Case when prop is one position ahead of gold
                    if prop_token == cur_gold_tokens[gold_cur_idx - 1]:
                        gold_cur_idx -= 1
                        continue
                    # Case when gold is one position ahead of prop
                    else:
                        alignment_list[prop_cur_idx - 1]['gold_idx'] = []
                        alignment_list[prop_cur_idx - 1]['gold_token'] = ""
                        prop_cur_idx -= 1
                        continue

                # The case of dummy
                '''.
                if gold_token == ".":
                    prev_error = False
                    gold_cur_idx += 1
                    continue
                if prop_token == ".":
                    prev_error = False
                    prop_cur_idx += 1
                    continue
                '''
                prev_error = True
                gold_cur_idx += 1
                prop_cur_idx += 1

        alignment_corpus[doc_name] = alignment_list
        if error_count >= 10:
            large_error_list.append(doc_name)

    # print(large_error_list)
    return alignment_corpus


def align_all(gold_dict, parse_dict, relations):
    alignment_dict = alignment(gold_parse_dict=gold_dict, proposed_parse_dict=parse_dict)
    aligned_relation_list = []
    for prop_relation in relations:
        doc_name = prop_relation['DocID']
        prop_arg1 = prop_relation['Arg1']['TokenList']
        prop_arg2 = prop_relation['Arg2']['TokenList']
        prop_conn = prop_relation['Connective']['TokenList']
        aligned_arg1 = []
        aligned_arg2 = []
        aligned_conn = []
        for idx in prop_arg1:
            aligned_arg1 += alignment_dict[doc_name][idx]['gold_idx']
        for idx in prop_arg2:
            aligned_arg2 += alignment_dict[doc_name][idx]['gold_idx']
        for idx in prop_conn:
            aligned_conn += alignment_dict[doc_name][idx]['gold_idx']
            prop_relation['Arg1']['TokenList'] = aligned_arg1
            prop_relation['Arg2']['TokenList'] = aligned_arg2
            prop_relation['Connective']['TokenList'] = aligned_conn
        aligned_relation_list.append(prop_relation)

    return aligned_relation_list


def write_labeled_instance_to_svm_alignment(relation_path, conn_path, feat_path, svm_path, gold_parse_path, proposed_parse_path):
    gold_parse_dict = json.loads(codecs.open(gold_parse_path, encoding='utf-8', errors='ignore').read())
    proposed_parse_dict = json.loads(codecs.open(proposed_parse_path, encoding='utf-8', errors='ignore').read())
    alignment_result_dict = alignment(proposed_parse_dict=proposed_parse_dict, gold_parse_dict=gold_parse_dict)
    golden_conns_list = get_golden_conn_list(relation_path)
    target_list = []
    with open(conn_path, 'r') as candidate:
        candidate_conns = json.load(candidate)
    candidate_conns_list = [[x[0], x[1], x[2]] for x in candidate_conns['conns_list']]
    for conn in candidate_conns_list:
        target = 0
        for gold_conn in golden_conns_list:
            if conn[0] == gold_conn[0]:
                conn_prop_idx = get_doc_offset(parse_dict=proposed_parse_dict, DocID=conn[0], sent_index=conn[1], list=conn[2])
                conn_gold_idx = gold_conn[3]    # get_doc_offset(parse_dict=gold_parse_dict, DocID=gold_conn[0], sent_index=gold_conn[1], list=gold_conn[2])
                conn_aligned_idx = []
                for idx in conn_prop_idx:
                    conn_aligned_idx += alignment_result_dict[conn[0]][idx]['gold_idx']
                # print([alignment_result_dict[conn[0]][idx]['gold_token'] for idx in conn_prop_idx])
                if set(conn_aligned_idx).issubset(set(conn_gold_idx)):
                    target = 1
                    break
        target_list.append(target)
    feat = open(feat_path, "r")
    feat_list = feat.readlines()
    feat_list_svm = [str(target) + " " + feat for target, feat in zip(target_list, feat_list)]
    feat.close()
    with open(svm_path, 'w') as svm:
        for feat_svm in feat_list_svm:
            svm.write(feat_svm)


conn_feat_path = r"D:\conll2015_discourse\parser_output\feature\conn_clf_feature.txt"
feat_svmlight_path = r"D:\Test_train\conn_feat.txt"
test_feat_svmlight_path = r"D:\Test_dev\conn_feat_test.txt"
gold_relation_path = r"D:\conll15-st-03-04-15-train\pdtb-data.json"
candidate_conn_path = r"D:\Test_train\conns_candidate_list.json"
conn_model_path = r"D:\conll2015_discourse\model\conn_train_cv.model"
prop_pdtb_path = r"D:\Test_train\pdtb-parses.json"
gold_pdtb_path = r"D:\conll15-st-03-04-15-train\pdtb-parses.json"


# write_labeled_instance_to_svm_alignment(relation_path=gold_relation_path, conn_path=candidate_conn_path, feat_path=conn_feat_path,
#                                         svm_path=feat_svmlight_path, gold_parse_path=gold_pdtb_path, proposed_parse_path=prop_pdtb_path)


# write_labeled_instance_to_svm(relation_path=gold_relation_path, conn_path=candidate_conn_path, feat_path=conn_feat_path, svm_path=feat_svmlight_path)
# train_model(svm_path=feat_svmlight_path)

# proposed_parse_path = r"D:\Test_train\pdtb-parses.json"
# gold_parse_path = r"D:\conll15-st-03-04-15-train\pdtb-parses.json"
# gold_parse_dict = json.loads(codecs.open(gold_parse_path, encoding='utf-8', errors='ignore').read())
# proposed_parse_dict = json.loads(codecs.open(proposed_parse_path, encoding='utf-8', errors='ignore').read())
# alignment(gold_parse_dict=gold_parse_dict, proposed_parse_dict=proposed_parse_dict)
