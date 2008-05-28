"""\
Planet Name Generator
Creates a generator class using a specified textfile with syllables
A very "lazy" generator
"""
import random
import os.path

class PlanetGenerator:
	"""\
	Class Planet Generator
	"""
	def __init__(self, s = os.path.abspath(os.path.curdir) + '/tp/server/utils/default.txt', theSeed= None):
		"""\
		Initialization:
		s is a string containing the file name
		"""
		syl = open(s)
		self.syllables = []
		for s in syl:
			self.syllables.append(s.strip())
		syl.close()
		random.seed(theSeed)

	def genName(self, maxWords =2, maxSyllables = 3):
		"""/
		Name Generator
		theSeed is the seed number used for the number generator.
		"""
		numberOfWords = random.randint(1, 2)
		numberOfSyllables = random.randint(2, 4)
		for x in range(0, numberOfWords):
			for y in range(0,numberOfSyllables):
				randomSyl = random.randint(0, len(self.syllables) - 1)
				try:
					word += self.syllables[randomSyl]
				except:
					word = self.syllables[randomSyl]
			word = word.capitalize()
			try:
				name += ' ' + word
			except:
				name = word
			word = ""

		return name


#Testing Code
#p = PlanetGenerator("default.txt", 100)
#for x in range(1 , 10): print p.genName()
