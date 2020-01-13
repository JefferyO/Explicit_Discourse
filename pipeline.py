import os
import json
from preprocess import auto_parse, process_result
import time
import argparse
import parser


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


def automatic_parses(data_directory):

    # parse raw data
    raw_path = os.path.join(data_directory, 'raw')
    parse_dict = auto_parse.parse_raw(raw_dir=raw_path)

    # write parse dict to file
    pdtb_parses = os.path.join(data_directory, 'pdtb-parses.json')
    with open(pdtb_parses, 'w') as auto_parses:
        json.dump(parse_dict, auto_parses)


# Whole discourse pipeline
def discourse_parse_pipeline(data_directory, input_dataset, input_run, output_dir, output_json_path, processed_output_path, pre_parse, explicit, gold_parse_path):

    # Generate automatic parses from raw files
    if pre_parse:
        automatic_parses(data_directory=data_directory)

    # Run discourse parser base on the automatic parses
    discourse_arg = "python parser.py " + input_dataset + " " + input_run + " " + output_dir + " " + str(explicit) + " " + str(gold_parse_path)
    os.system(discourse_arg)

    # post-process of output results
    process_result.reformat_output(output_json_path=output_json_path, processed_output_path=processed_output_path)


'''
start_time = time.time()
discourse_parse_pipeline(data_directory='D:/Test_dev', input_dataset='D:/Test_dev', input_run="None", output_dir='D:/Test_dev',
                         output_json_path='D:/Test_dev/output.json', processed_output_path='D:/Test_dev/final_output.json')

print("execution time is {} seconds".format(time.time() - start_time))
'''

if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser(description='CONLL 2015 shared task discourse parser pipeline on raw data')
    arg_parser.add_argument("-d", "--data", type=str, help="path/to/data_directory, should contains a directory names'raw' that contains all data")
    arg_parser.add_argument("-o", "--output", type=str, help="path/to/output_directory")
    arg_parser.add_argument("-p", "--pre_parse", action="store_true", help="Enabled to run pre-parse(i.e. stanford parser) on raw text, needed if want to generate discourse parse from raw text")
    arg_parser.add_argument("-e", "--explicit", action="store_true", help="Enabled to extract only explicit relation")
    # arg_parser.add_argument("-a", "--alignment", action="store_true", help="Enabled to align the output index with gold index, only for evaluation purpose")
    arg_parser.add_argument("-g", "--gold_parse", type=str, help="Path to the golden parse, needed only when alignment is enabled")
    args = arg_parser.parse_args()

    start_time = time.time()
    discourse_parse_pipeline(data_directory=args.data, input_dataset=args.data, input_run="None", output_dir=args.output,
                             output_json_path=os.path.join(args.output, "output.json"), processed_output_path=os.path.join(args.output, "final_output.json"),
                             pre_parse=args.pre_parse, explicit=args.explicit, gold_parse_path=args.gold_parse)

    print("Execution time is {} seconds".format(time.time() - start_time))
