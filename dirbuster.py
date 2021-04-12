import requests as req
import re
import threading
import time

def parseUrl(url):
    # Parsing url
    ok = re.search(r".*\.[^\.]+$", url)
    if not ok:
        return False
    rgx2 = re.search(r"(?:http|https):\/\/", url)
    # Check if the url has http(s) in the beginning
    # and format it otherwise
    urlF = not rgx2 and "https://"+url or url

    return urlF

def getWordList(mode):
    fileList = ['directory-list-lowercase-2.3-small',
            'directory-list-lowercase-2.3-medium', 'directory-list-lowercase-2.3-big']
    file = open("lists/"+fileList[mode+1]+".txt", "r")
    wordlist = file.read().split("\n")
    return wordlist

def auraBuster(url, mode):
    # Mode handling
    if mode > 3 or mode < 1:
        print("Invalid mode!")
        return False
    # Test url
    try:
        urlF = parseUrl(url)
        if not urlF:
            print("Invalid url syntax!\nCorrect: 'http(s)://www.site.com' or 'site.com'")
            return False
        r = req.get(urlF)
    except:
        print("No response from "+urlF)
        return False
    if not r.ok:
        print("No response from "+urlF)
        return
    # Bust
    def testSite(finalUrl):
        rF = req.get(finalUrl)
        if rF.status_code != 404:
            print("Valid directory found!\n"+finalUrl+"\n")
            return
        return False
    wordList = getWordList(mode)
    threads = []
    for word in wordList:
        try:
            finalUrl = urlF+word+"/"
            t = threading.Thread( target=testSite, args=(finalUrl,) )
            threads.append(t)
            t.start()
            time.sleep(0.5)
        except:
            print("Error: unable to start thread")

website = input("Type the website: ")
mode = input("Type the wordlist mode (1: small, 2: medium, 3: big): ")
print("Searching directories...")
auraBuster(website, int(mode))