StanfordNLP - Python NLP Library for Many Human Languages
https://stanfordnlp.github.io/stanfordnlp/index.html

###################################################################################################################
### Installation
pip install stanfordnlp

###################################################################################################################
### Resources
stanfordnlp.github.io/CoreNLP/tutorials.html
https://pypi.org/project/stanfordnlp/

###################################################################################################################
### Usage - Manual (REPL)
- Reference: https://pypi.org/project/stanfordnlp/
- Type python to enter REPL
>>> import stanfordnlp
>>> stanfordnlp.download('en')   # This downloads the English models for the neural pipeline (1*)
>>> nlp = stanfordnlp.Pipeline() # This sets up a default neural pipeline in English (2*)
>>> doc = nlp("Barack Obama was born in Hawaii.  He was elected president in 2008.")
>>> doc.sentences[0].print_dependencies()
1* - I didn't have room in the default location, so I had to provide an alternate location, see example below
2* - If you use an alternate location, you need to specify this via 'model_dir' parameter, see example below

================= Example Output =================
>>> import stanfordnlp
>>> stanfordnlp.download('en')
Using the default treebank "en_ewt" for language "en".
Would you like to download the models for: en_ewt now? (Y/n)
Y

Default download directory: /usr2/bstaab/stanfordnlp_resources
Hit enter to continue or type an alternate directory.
/local/mnt/workspace/bstaab/CS/cs540/final/stanford

Downloading models for: en_ewt
Download location: /local/mnt/workspace/bstaab/CS/cs540/final/stanford/en_ewt_models.zip
100%|¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦| 1.96G/1.96G [03:37<00:00, 7.90MB/s]

Download complete.  Models saved to: /local/mnt/workspace/bstaab/CS/cs540/final/stanford/en_ewt_models.zip
Extracting models file for: en_ewt
>>> nlp = stanfordnlp.Pipeline(models_dir="/local/mnt/workspace/bstaab/CS/cs540/final/stanford")
Use device: cpu
---
Loading: tokenize
With settings:
{'model_path': '/local/mnt/workspace/bstaab/CS/cs540/final/stanford/en_ewt_models/en_ewt_tokenizer.pt', 'lang': 'en', 'shorthand': 'en_ewt', 'mode': 'predict'}
---
Loading: pos
With settings:
{'model_path': '/local/mnt/workspace/bstaab/CS/cs540/final/stanford/en_ewt_models/en_ewt_tagger.pt', 'pretrain_path': '/local/mnt/workspace/bstaab/CS/cs540/final/stanford/en_ewt_models/en_ewt.pretrain.pt', 'lang': 'en', 'shorthand': 'en_ewt', 'mode': 'predict'}
---
Loading: lemma
With settings:
{'model_path': '/local/mnt/workspace/bstaab/CS/cs540/final/stanford/en_ewt_models/en_ewt_lemmatizer.pt', 'lang': 'en', 'shorthand': 'en_ewt', 'mode': 'predict'}
Building an attentional Seq2Seq model...
Using a Bi-LSTM encoder
Using soft attention for LSTM.
Finetune all embeddings.
[Running seq2seq lemmatizer with edit classifier]
---
Loading: depparse
With settings:
{'model_path': '/local/mnt/workspace/bstaab/CS/cs540/final/stanford/en_ewt_models/en_ewt_parser.pt', 'pretrain_path': '/local/mnt/workspace/bstaab/CS/cs540/final/stanford/en_ewt_models/en_ewt.pretrain.pt', 'lang': 'en', 'shorthand': 'en_ewt', 'mode': 'predict'}
Done loading processors!
---
>>> doc = nlp("Barack Obama was born in Hawaii.  He was elected president in 2008.")
>>> doc.sentences[0].print_dependencies()
('Barack', '4', 'nsubj:pass')
('Obama', '1', 'flat')
('was', '4', 'aux:pass')
('born', '0', 'root')
('in', '6', 'case')
('Hawaii', '4', 'obl')
('.', '4', 'punct')

###################################################################################################################
### Usage - Script
- cd cs540_project_green_team/stanfordNLP
- python ./demo.py
- NOTE: One of the steps is to download the language model(s) which is 1.96G compressed and ~2.5G decompressed
        I did not have room in the default location, so I provided an alternate location.  If you do this, you 
        need to call the demo script with the -d option so it knows where to download/find the model
        - python ./demo.py -d "/local/mnt/workspace/bstaab/CS/cs540/final/stanford"

================= Example Output =================
(venv) /local/mnt/workspace/bstaab/CS/cs540/final/cs540_project_green_team/stanfordNLP> python ./demo.py -d "/local/mnt/workspace/bstaab/CS/cs540/final/stanford"
Using the default treebank "en_ewt" for language "en".

The model directory already exists at "/local/mnt/workspace/bstaab/CS/cs540/final/stanford/en_ewt_models". Do you want to download the models again? [y/N]
N
---
Building pipeline...
Use device: cpu
---
Loading: tokenize
With settings:
{'model_path': '/local/mnt/workspace/bstaab/CS/cs540/final/stanford/en_ewt_models/en_ewt_tokenizer.pt', 'lang': 'en', 'shorthand': 'en_ewt', 'mode': 'predict'}
---
Loading: pos
With settings:
{'model_path': '/local/mnt/workspace/bstaab/CS/cs540/final/stanford/en_ewt_models/en_ewt_tagger.pt', 'pretrain_path': '/local/mnt/workspace/bstaab/CS/cs540/final/stanford/en_ewt_models/en_ewt.pretrain.pt', 'lang': 'en', 'shorthand': 'en_ewt', 'mode': 'predict'}
---
Loading: lemma
With settings:
{'model_path': '/local/mnt/workspace/bstaab/CS/cs540/final/stanford/en_ewt_models/en_ewt_lemmatizer.pt', 'lang': 'en', 'shorthand': 'en_ewt', 'mode': 'predict'}
Building an attentional Seq2Seq model...
Using a Bi-LSTM encoder
Using soft attention for LSTM.
Finetune all embeddings.
[Running seq2seq lemmatizer with edit classifier]
---
Loading: depparse
With settings:
{'model_path': '/local/mnt/workspace/bstaab/CS/cs540/final/stanford/en_ewt_models/en_ewt_parser.pt', 'pretrain_path': '/local/mnt/workspace/bstaab/CS/cs540/final/stanford/en_ewt_models/en_ewt.pretrain.pt', 'lang': 'en', 'shorthand': 'en_ewt', 'mode': 'predict'}
Done loading processors!
---

Input: Barack Obama was born in Hawaii.  He was elected president in 2008.
The tokenizer split the input into 2 sentences.
---
tokens of first sentence:
<Token index=1;words=[<Word index=1;text=Barack;lemma=Barack;upos=PROPN;xpos=NNP;feats=Number=Sing;governor=4;dependency_relation=nsubj:pass>]>
<Token index=2;words=[<Word index=2;text=Obama;lemma=Obama;upos=PROPN;xpos=NNP;feats=Number=Sing;governor=1;dependency_relation=flat>]>
<Token index=3;words=[<Word index=3;text=was;lemma=be;upos=AUX;xpos=VBD;feats=Mood=Ind|Number=Sing|Person=3|Tense=Past|VerbForm=Fin;governor=4;dependency_relation=aux:pass>]>
<Token index=4;words=[<Word index=4;text=born;lemma=bear;upos=VERB;xpos=VBN;feats=Tense=Past|VerbForm=Part|Voice=Pass;governor=0;dependency_relation=root>]>
<Token index=5;words=[<Word index=5;text=in;lemma=in;upos=ADP;xpos=IN;feats=_;governor=6;dependency_relation=case>]>
<Token index=6;words=[<Word index=6;text=Hawaii;lemma=Hawaii;upos=PROPN;xpos=NNP;feats=Number=Sing;governor=4;dependency_relation=obl>]>
<Token index=7;words=[<Word index=7;text=.;lemma=.;upos=PUNCT;xpos=.;feats=_;governor=4;dependency_relation=punct>]>

---
dependency parse of first sentence:
('Barack', '4', 'nsubj:pass')
('Obama', '1', 'flat')
('was', '4', 'aux:pass')
('born', '0', 'root')
('in', '6', 'case')
('Hawaii', '4', 'obl')
('.', '4', 'punct')

