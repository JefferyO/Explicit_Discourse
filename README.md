# Explicit_Discourse
Explicit discourse parser from raw text
Based on the [CoNLL 2015 Shared Task](https://www.cs.brandeis.edu/~clp/conll15st/intro.html) and its [best performance model](https://github.com/lanmanok/conll2015_discourse)
Initially designed for reconstruct [ASER Knowledge Graph](https://hkust-knowcomp.github.io/ASER/) based on the predicted explicit discourse relation, but could be used for more general purpose of explicit discourse parsing.
## Settings and Dependencies:
* Python 3.7
* [ETE 3](http://etetoolkit.org/docs/latest/index.html)
* [Mallet 2.0.8](http://mallet.cs.umass.edu/download.php)
* [Stanford CoreNLP 3.9.1](https://stanfordnlp.github.io/CoreNLP/history.html)
* The settings for mallet and working directory is needed, see the [original model](https://github.com/lanmanok/conll2015_discourse)
## Input data format:
* The input data directory must contain a sub-directory named <raw> that contains the raw text files for parsing, one document per file. 

## Usage
* Before running the pipeline, if you want to parser raw text data, a Stanford CoreNLP server is needed to be established locally, with the command:
```Bash
java -mx4g -cp "*" edu.stanford.nlp.pipeline.StanfordCoreNLPServer -port 9000 -timeout 15000
```
more details at [CoreNLP website]:(https://stanfordnlp.github.io/CoreNLP/corenlp-server.html)
* Following are commands provided for the parser:
  * Required:
  [-d] / [--data]: The input data directory, as specified in II
  [-o] / [--output]: The output data directory, to which you want to store your output json file. The output json file will have name <final_output.json>

  * Optional:
  [-p] / [--pre_parse]: Enabled if you want to parse a dataset with only raw text files, this will generate automatic parses using Stanford CoreNLP as pre-parse for the discourse parser.
  [-e] / [--explicit]: Enabled if you want to extract only explicit relations, which is the requirement of ASER relation extraction
  [-g] / [--gold_parse]: Enabled if you want to align the output index with the golden index, which is only needed if you want you to evaluate the parser on the CoNLL-2015 development set, and is only possible under the condition when you have golden pre-parse.
* Description could be found with help command:
```Bash
python pipeline.py -h
```
### Examples
* Extract only explicit discourse relations from raw text data, run following command:
python pipeline.py -d /path/to/data/directory -o /path/to/output/directory -p -e

### Output Format
* For the purpose of conducting further ASER relation extraction based on the discourse output, the <final_output.json> has the following format, for your reference:
It has a json object per line, with format:

{“ID”: 0, 

“DocID”: “the doc name”, 

“Arg1”: {“TokenList”: [28, 29, 30, …]}, 

“Arg2”: {“TokenList”: [47, 48, …]}, 

“Type”: “Explicit/Implicit”, 

“Sense”: “One of the PDTB senses”, 

“Connective”: {“TokenList”: [44]}}

