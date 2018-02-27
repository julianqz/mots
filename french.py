import csv
import re
from random import sample

# meta parameters
QUIZ_SIZE = 5
CSV_PATH = "/Users/jkewz/Desktop/fr/"
CSV_FILENAME = "mots.csv"

CSV_COL_FREQ = "frequency_rank"
CSV_COL_NA   = "noun_article"
CSV_COL_WORD = "word"
CSV_COL_POS  = "part_of_speech"
CSV_COL_VAR  = "variation"
CSV_COL_MEAN = "meaning"
CSV_COL_PHR  = "phrases"
CSV_COL_REL  = "related"
CSV_COL_REG  = "register"

CSV_COL_N_FREQ = 0
CSV_COL_N_NA   = 1
CSV_COL_N_WORD = 2
CSV_COL_N_POS  = 3
CSV_COL_N_VAR  = 4
CSV_COL_N_MEAN = 5
CSV_COL_N_PHR  = 6
CSV_COL_N_REL  = 7
CSV_COL_N_REG  = 8

LEGAL_NOUN_POS = ("nm", "nf", "nm/nf", "nmpl", "nfpl", "nm/nf pl", "nmi", "nfi")
LEGAL_GENDER_INPUTS = ("m", "f", "mf", "mpl", "fpl", "mfpl", "mi", "fi")

# print info about expected input
def printInputInfo():

	print("Type in any order.")
	print("Use ';' without space for separation.")
	print("'{0}' for {1}, '{2}' for {3}, '{4}' for {5}".format(
		LEGAL_GENDER_INPUTS[0], LEGAL_NOUN_POS[0], 
		LEGAL_GENDER_INPUTS[1], LEGAL_NOUN_POS[1], 
		LEGAL_GENDER_INPUTS[2], LEGAL_NOUN_POS[2]))
	print("'{0}' for {1}, '{2}' for {3}, '{4}' for {5}".format(
		LEGAL_GENDER_INPUTS[3], LEGAL_NOUN_POS[3], 
		LEGAL_GENDER_INPUTS[4], LEGAL_NOUN_POS[4], 
		LEGAL_GENDER_INPUTS[5], LEGAL_NOUN_POS[5]))
	print("'{0}' for {1}, '{2}' for {3}".format(
		LEGAL_GENDER_INPUTS[6], LEGAL_NOUN_POS[6], 
		LEGAL_GENDER_INPUTS[7], LEGAL_NOUN_POS[7]))
	#print("'m' for nm, 'f' for nf, 'mf' for nm/nf")
	#print("'mpl' for nmpl, 'fpl' for nfpl, 'mfpl' for nm/nf pl")
	print("E.g.: 'f', 'm;f', 'f;m', 'mf;f;m'")


# capture input gender & process into a list
def getGenderFromKeyboard():

	print("Your input:")
	allGendersStr = input()
	
	allGendersStr = allGendersStr.lower()
	allGendersList = allGendersStr.split(sep=";")

	isLegal = [gender in LEGAL_GENDER_INPUTS for gender in allGendersList]

	if sum(isLegal)==len(allGendersList):
		return allGendersList
	else:
		print("Incorrect input format.")
		printInputInfo()
		return getGenderFromKeyboard()


# assess input gender (list) by comparing with truth (list)
def assessGenderInput(genderInput, genderTruth):

	genderInput.sort()
	genderTruth.sort()

	lenInput = len(genderInput)
	lenTruth = len(genderTruth)

	if genderInput == genderTruth:
		return True
	else:
		if lenInput > lenTruth:
			print("Too many! Expecting {0}; received {1}.".format(lenTruth, lenInput))
		else:
			counter = 0
			for g in genderInput:
				if g in genderTruth:
					counter += 1
			print("{0} out of {1} correct.".format(counter, lenTruth))
		return False

# format parsed true gender (list from parseNounGender)
# for printing as correct answer
def formatAnswer(genderTruth):

	genderTruth.sort()
	
	answer = ""
	for gender in genderTruth:
		if len(answer)==0:
			answer = gender
		else:
			answer = answer + ";" + gender

	return answer


# posStr: a string, like "nm", "adj; nm/nf"
# returns a list
def parsePos(posStr):
	
	posStr = posStr.lower()

	# split by semi-colon
	posList = posStr.split("; ")

	return posList


# parse through parts of speech of a noun to produce a list of gender(s)
# if input contains irregular format, a msg will be printed and None returned
def parseNounGender(posStr, verbose=False):

	posList = parsePos(posStr)

    # keep only pos starting with "n" (thereby excluding "conj") and of length >1
    # "n" (e.g. Londres), for which gender info is unavail., is excluded
	posList = [item for item in posList if item[0]=="n" and len(item)>1]

	# check that posList is not empty 
	# will be empty for non-nouns or nouns without gender info (e.g. Londres, n)
	if len(posList)==0:
		if verbose: print("No noun POS with gender. None returned.")
		return

	# check legality of posList against LEGAL_NOUN_POS
	for item in posList:
		if item not in LEGAL_NOUN_POS:
			print("Noun POS contains illegal item ({0}). None returned.".format(item))
			return

	# parse
	# nm       -> m
	# nf       -> f
	# nm/nf    -> mf
	# nmpl     -> mpl
	# nfpl     -> fpl
	# nm/nf pl -> mfpl
	genderList = []
	for item in posList:
		if item=="nm/nf":
			genderList.extend(["mf"])
		elif item=="nm/nf pl":
			genderList.extend(["mfpl"])
		else:
			genderList.extend([item[1:]])

	#print(genderList)
	return genderList


# parse through a string containing the word meaning for each of its POS

# most generic description of the kind of pattern to parse: "{;;}; {;;}; {;;}"
# examples & desired parsed outcome:
#   population -> ["population"]
#   ball; bullet -> ["ball; bullet"]
#   {blue}; {blue; bruise} -> ["blue", "blue; bruise"]

# toParse: a string that may or may not contain pair(s) of {}
# returns a list; no. of entries in list depends on no. of pairs of {} (1 entry if no {})
def parseMeaning(toParse):
    
    if "{" in toParse:
        # separate {}'s by semi-colon
        # +: to match 1 or more repetitions of the preceding RE
        # \w: matches Unicode word characters; this includes most characters that can be part 
        #     of a word in any language, as well as numbers and the underscore
        parsedWithCurly = re.findall("{[\w\s,;-]+}", toParse)
        
        # within each {}, remove {}
        parsedWithoutCurly = [re.search("[\w\s,;-]+", item)[0] for item in parsedWithCurly]
        
        return parsedWithoutCurly
    else:
        return [toParse]


# posStr: a string of POS(s); like "nm", "adj; nm/nf"
# meanStr: a string of meaning(s); like "blue", "bright; shiny", "{bright}; {blue}"
# maskGender: boolean value; if True, mask gender of nouns
# no return; prints formatted/aligned/padded POS + meaning
def formatPOSnMean(posStr, meanStr, maskGender):
	posList = parsePos(posStr)
	meanList = parseMeaning(meanStr)
	nPos = len(posList)

	# find POS that are nouns
	nounIdx = [idx for idx in range(nPos) if posList[idx][0]=="n"]

	# if noun POS exist(s), and if maskGender is True
	if len(nounIdx)>0 and maskGender:
	    for j in nounIdx:
	    	posList[j] = "NOUN"

	# find max len of POS
	maxLen = max([len(item) for item in posList])
	# calculate number of white spaces for padding
	nPad = [maxLen-len(item) for item in posList]
	# apply padding(s)
	posListPadded = [" "*nPad[i] + posList[i] for i in range(nPos)]

	# print with meaning(s)
	for i in range(nPos):
		print(posListPadded[i] + " :", meanList[i])


# display a word, given its row from csv (as a list)
# binary combinatorial options of displaying individual components

# format; [] indicates optional

# word [freq]
# variation
# POS1:  meaning1
# POS2:  meaning2
# ...
# [phrases]
# [-> related]
# [register]

# example

# mécontent #4158
# mécontente
# adj:   unhappy; discontented; displeased
# nm/nf: malcontent
# -> le mécontentement #4823

# wordInfo: a list
# maskGender: if True, mask gender of nouns
# freq, phrases, related, register: boolean values
def displayWord(wordInfo, maskGender, freq, phrases, related, register):
    
    # word [freq]
    if freq and len(wordInfo[CSV_COL_N_FREQ])>0:
    	print(wordInfo[CSV_COL_N_WORD] + " #" + wordInfo[CSV_COL_N_FREQ])
    else:
    	print(wordInfo[CSV_COL_N_WORD])

    # variation
    # only print if not "" (otherwise it'd look like there's a blank line)
    if len(wordInfo[CSV_COL_N_VAR])>0:
    	print(wordInfo[CSV_COL_N_VAR])
    
    # align/format POS and meaning
    formatPOSnMean(wordInfo[CSV_COL_N_POS], wordInfo[CSV_COL_N_MEAN], maskGender)

    # phrases
    if phrases and len(wordInfo[CSV_COL_N_PHR])>0:
    	print(wordInfo[CSV_COL_N_PHR])

    # related
    if related and len(wordInfo[CSV_COL_N_REL])>0:
    	print("-> " + " " + wordInfo[CSV_COL_N_REL])

    # register
    if register and len(wordInfo[CSV_COL_N_REG])>0:
    	print(wordInfo[CSV_COL_N_REG])


# given noun and its true gender(s) in a list
# solicit and assess user input of gender(s)
def genderQuizSingleWord(wordInfo):

	quizWord = wordInfo[CSV_COL_N_WORD]
	posFull = wordInfo[CSV_COL_N_POS]
	genderTruth = parseNounGender(posFull, verbose=False)
	meaning = parseMeaning(wordInfo[CSV_COL_N_MEAN])

	# set max number of failures allowed
	remainingTrials = 3

	# display word
	print("* * * * * * * * * * * * * * * * * *")
	displayWord(wordInfo, maskGender=True, freq=True, phrases=True, related=True, register=True)


	# TODO: play pronuncation of the word (optional? indicated by keyboard input?)

	while remainingTrials > 0:
		remainingTrials -=1
		# solicit input
		currentInput = getGenderFromKeyboard()
		# assess input
		currentAssess = assessGenderInput(currentInput, genderTruth)
		if currentAssess:
			print("Très bien!")
			return
		else:
			if remainingTrials>0:
				print("{0} trials left.".format(remainingTrials))
			else:
				# reveal correct answer
				correctAnswer = formatAnswer(genderTruth)
				print("Correct answer: {0}".format(correctAnswer))


# given a list of words and their corresponding POS
# each word is a string; each POS is a string too
# run gender quiz for nouns for which gender info is available in their POS
def genderQuizWordList(wordRows):

	for i in range(len(wordRows)):
		genderQuizSingleWord(wordRows[i])


# given a csv, generate:
# a nested list
# each nested component is itself a list, representing a column from csv
# items in nested componenets correspond in terms of index
# e.g. a list of words; each word is a string (e.g. "courageux")
# e.g. a list of POS corresponding to the words; each POS is a string (e.g. "adj; nm")
def getWordInfofromCSV(csvname):
    
    with open(csvname, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        wordColsAll = [ [ row[CSV_COL_FREQ], row[CSV_COL_NA], row[CSV_COL_WORD], row[CSV_COL_POS], row[CSV_COL_VAR], row[CSV_COL_MEAN], row[CSV_COL_PHR], row[CSV_COL_REL], row[CSV_COL_REG] ] for row in reader ]
    
    # columns    
    # can't int("")
    lstFreq = [wordColsCur[CSV_COL_N_FREQ] for wordColsCur in wordColsAll]
    lstNA   = [wordColsCur[CSV_COL_N_NA] for wordColsCur in wordColsAll]
    lstWord = [wordColsCur[CSV_COL_N_WORD] for wordColsCur in wordColsAll]
    lstPOS  = [wordColsCur[CSV_COL_N_POS] for wordColsCur in wordColsAll]
    lstVar  = [wordColsCur[CSV_COL_N_VAR] for wordColsCur in wordColsAll]
    lstMean = [wordColsCur[CSV_COL_N_MEAN] for wordColsCur in wordColsAll]
    lstPhr  = [wordColsCur[CSV_COL_N_PHR] for wordColsCur in wordColsAll]
    lstRel  = [wordColsCur[CSV_COL_N_REL] for wordColsCur in wordColsAll]
    lstReg  = [wordColsCur[CSV_COL_N_REG] for wordColsCur in wordColsAll]
    
    # rows
    # nested list; each entry is itself a list corresponding to a word
    wordRows = [ [lstFreq[idx], lstNA[idx], lstWord[idx], lstPOS[idx], lstVar[idx], lstMean[idx], lstPhr[idx], lstRel[idx], lstReg[idx]] for idx in range(len(lstWord))]

    #return [lstFreq, lstNA, lstWord, lstPOS, lstVar, lstMean, lstPhr, lstRel, lstReg]
    return wordRows

# main wrapper function
# given a csv file, run noun gender quiz through its words
# if size is specified as an integer (must be <= # words), do random sampling
def genderQuizMain(csvname, size=None):

	# get wordList and posList
	wordInfo = getWordInfofromCSV(csvname)
	
	# index of words that are or can be nouns
	# noun if POS isn't "conj" and POS contains "n"
	# ASSUMPTION: a word won't be both conj and a noun at the same time
	nounIdx = [idx for idx in range(len(wordInfo)) if "n" in wordInfo[idx][CSV_COL_N_POS] and wordInfo[idx][CSV_COL_N_POS]!="conj"]

	# random sampling
	# only nouns are sampled
	if size is not None:
		try:
			randIdx = sample(list(nounIdx), k=size)
			wordInfo = [wordInfo[i] for i in randIdx]
		except:
			print("size must be >0 & <= {0}".format(len(nounIdx)))
			return

	# run quiz through list
	printInputInfo()
	genderQuizWordList(wordInfo)


# run
genderQuizMain(CSV_PATH+CSV_FILENAME, QUIZ_SIZE)
#genderQuizMain(CSV_PATH+CSV_FILENAME)
#genderQuizMain(CSV_FILENAME, QUIZ_SIZE)

# for testing

#printInputInfo()
#getGenderFromKeyboard()
#assessGenderInput(["a","c"], ["a","c", "b"])
#genderQuizSingleWord("tour", ["m","f"])
#parseNounGender("nm/nf; nmpl; nf; nm; nm/nf pl; nfpl")
#parseNounGender("n; adj")
#wL = ["tour", "garçon", "police", "gens", "courageux", "Londres"]
#pL = ["nm; nf", "nm", "nf", "nmpl", "adj", "n"]
#genderQuizWordList(wL, pL)

#wL, pL = getWordPOSfromCSV("mots.csv")
#print(wL[0:5])
#print(pL[0:5])
#genderQuizWordList(wL[0:3], pL[0:4])

#print(formatAnswer(["m","f", "mf", "mpl", "fpl", "mfpl"]))

#formatPOSnMean("adj", "bright; blue", True)
#formatPOSnMean("adj; nm", "{bright; blue}; {brightness; blue}", True)
#formatPOSnMean("adj; nm", "{bright; blue}; {brightness; blue}", False)