#!/usr/bin/env python3

import re
import sys
import requests
import os

HTTP_HEADER = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
DIR_AUDIO="/Users/jkewz/Desktop/fr/sons_de_mots/"
URL_ROOT="https://www.collinsdictionary.com/us/dictionary/french-english/"

# 2 audios for one entry
# portugais

# no audio
# gamin

# audio available for nf too (check $variation?)
# acteur, actrice

# keep track
# - scraped; file url; filename
# - no sound
# - no word entry


# given a word, get its html source page
# returns a list of strings; each string is a line from html source page
def getAllHTML(word):
	# word page url
	url = URL_ROOT+word
	try:
		html = requests.get(url)

		if html.status_code==200:
			htmlLst = str.split(str(html.content), "\\n")
			return htmlLst
		else:
			print("html.status_code not 200 for {0}.".format(word))
	except:
		print("Failed to get html source page for {0}.".format(word))

# given a line from html file, determine if the line contains the target audio file
# such a line would have the following hallmarks:
# mini_h2
# span punctuation
# data-src-mp3
# collinsdictionary.com/us/sounds/f/fr_
# fr_[...].mp3
# return a boolean value
def isFrMP3(htmlStr):
    cond1 = "mini_h2" in htmlStr
    cond2 = "span punctuation" in htmlStr
    cond3 = "data-src-mp3" in htmlStr
    cond4 = "collinsdictionary.com/us/sounds/f/fr_" in htmlStr
    cond5 = (len(re.findall("fr_[\w]+.mp3", htmlStr))==1)
    return cond1 & cond2 & cond3 & cond4 & cond5

# given a list of strings representing lines from html source page
# a list containing line(s) from html source page that contains target mp3
def getHTMLwithMP3(htmlList):
	
	return [line for line in htmlList if isFrMP3(line)]


# given a line from html file, extract the url and filename (incl. file extension) of audio file
# assumes that isFrMp3(hmtlStr) is True
# return 2 strings, the url and the filename with file extension
def getUrlFilename(htmlStr):
    # bulk of the string containing url
    url = re.findall('data-src-mp3=\"[\w_.:/]+\"', htmlStr)
    
    # try to extract url
    try:
        # remove the leading data-src-mp3=" and the tailing "
        url = url[0][(len('data-src-mp3=\"')):(len(url)-2)]
    except:
        sys.exit("Exception occurred when getting url. Exited.")

    # from url, try to extract filename
    try:
        filename = re.findall('/[\w_]+.mp3', url)[0]
        # remove the leading /
        filename = filename[1:]
    except:
        sys.exit("Exception occurred when getting filename. Exited.")
    
    return url, filename


# download an audio file named filename from url into fileDest
# url, filename, fileDest: strings
# fileDest should be absolute path; not relative  or using ~/
def downloadFile(url, filename, fileDest):

	# cd into fileDest
	try:
		os.chdir(fileDest)
	except:
		sys.exit("Can't cd into {0}. Exited.".format(fileDest))

	# download only if filename does not exist
	# do not overwrite if it exists
	if os.path.isfile(filename):
		print("{0} already exists. No downloading performed.".format(filename))
	else:
		try:
			# refs: 
			# https://stackoverflow.com/questions/38489386/python-requests-403-forbidden
			# https://stackoverflow.com/questions/39128738/downloading-a-song-through-python-requests
			
			result = requests.get(url, headers=HTTP_HEADER)

			# w: open for writing, truncating the file first
			# b: binary mode
			# x: create a new file and open it for writing
			# 'x' mode implies 'w' and raises an `FileExistsError` if the file 
			# already exists
			with open(filename, 'xb') as f:
				f.write(result.content)
		except:
			print("Error when trying to download {0}.".format(filename))


# main function to get audio files for a list of words
# wordList: a list containing strings; each string is a word
def scrapeAudioMain(wordList):
	return

# TODO?
# - each step has a try/except
# - print step info in except so as to know which step failed

# - wrap all steps in one try/except
# - except tell which word failed

# function to get audio file for a single word
def scrapeAudioSingleWord(word):

    # GET word page html
    wordHTML = getAllHTML(word)

    # IDENTIFY relevant html lines
    wordHTMLwithMP3 = getHTMLwithMP3(wordHTML)

    # EXTRACT word audio url(s) and filename(s)
    # DOWNLOAD word audio
    if len(wordHTMLwithMP3)>0:
    	for item in wordHTMLwithMP3:
    		itemUrl, itemFilename = getUrlFilename(item)
    		downloadFile(itemUrl, itemFilename, DIR_AUDIO)
    else:
    	# ?

    # RECORD word, audio url(s), audio filename(s)
    # warning if >1 entry for a word
