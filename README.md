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
