import stanfordnlp
from stanfordnlp.utils.resources import DEFAULT_MODEL_DIR

class Parser:
	def __init__(self, langModelDir):
		self.pipeline = stanfordnlp.Pipeline(models_dir=langModelDir, lang='en', use_gpu=True)
		
	def parseText(self, inp):
		doc = self.pipeline(inp)
		self.sentences = doc.sentences

	def getNouns(self, sentenceIdx=0):
		nouns = []
		for s in self.sentences[sentenceIdx].dependencies:
			if s[2].upos == "NOUN":
				nouns.append(s[2].text)
		return nouns
		
	def getVerbs(self, sentenceIdx=0):
		nouns = []
		for s in self.sentences[sentenceIdx].dependencies:
			if s[2].upos == "VERB":
				nouns.append(s[2].text)
		return nouns
