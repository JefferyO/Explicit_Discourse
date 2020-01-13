import json
import demjson


def reformat_output(output_json_path, processed_output_path):
    # cleanup old results
    new_file = open(processed_output_path, 'w')
    new_file.close()
    new_file = open(processed_output_path, 'a')
    with open(output_json_path, 'r') as original_output:
        for line in original_output:
            terminate_idx = line.find(", 'Arg1_sent_index'")
            if terminate_idx > 0:
                line = line[0: terminate_idx] + '}\n'
            processed_str = line.replace("'", '"')
            new_file.write(processed_str)

    new_file.close()
'''
def shed_str(processed_output_path, finalized_output_path):
    processed_file = open(processed_output_path, 'r')
    finalized_file = open(finalized_output_path, 'w')
    for line in processed_file:
        terminate_idx = line.find(", 'Arg1_sent_index'")
        if terminate_idx > 0:
            processed_line = line[0: terminate_idx] + '}'
            finalized_file.write(processed_line)

    processed_file.close()
    finalized_file.close()
'''

output_path = 'D:\output.json'
final_path = 'D:\output_final.json'

# reformat_output(output_path, final_path)
# shed_str(output_path, final_path)


