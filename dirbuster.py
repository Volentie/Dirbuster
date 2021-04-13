import requests as req
import re
import threading
import time
import random as ran
import json
from bs4 import BeautifulSoup

#       --------------=====:[ TIME VARIABLES ]:=====--------------
PROXYSEARCHTIME = 2
SITETESTTIME = 5
THREADCREATINGTIME = 0.5

# Proxies table
_Proxies = []
ProxiesJson = {}
currentProxy = None

def getLastProxy():
    global currentProxy
    try:
        open("lastproxy.txt", "x")
    except Exception:
        with open("lastproxy.txt", "r") as file:
            currentProxy = file.read()

def setLastProxy():
    global currentProxy
    with open("lastproxy.txt", "w") as file:
        file.write(currentProxy)

getLastProxy()            

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

def auraWrite(fileName, content):
    try:
        file = open(fileName, "x")
        print("Creating and writing in a new file named: "+fileName)
        file.write(content)
        file.close()
    except Exception:
        file = open(fileName, "w")
        print("Overwriting on an already existing file: "+fileName)
        file.write(content)
        file.close()
    bs = str( len( bytes( content, "utf-8" ) ) )
    print( "Wrote " + bs + " bytes in " + fileName )

def getProxies(get=False):
    # Get proxies list and format it
    global _Proxies
    global ProxiesJson
    if get:
        page = "https://free-proxy-list.net/"
        response = req.get(page)
        # Try to request a response
        try:
            response = req.get(page)
            soup = BeautifulSoup(response.content, 'html.parser' )
        except Exception as error:
            print("Unable to get proxies list: ", error)
            return False
        # Format the list
        rgx = r"\d+\.\d+\.\d+\.\d+:\d+" # Pattern
        unformatedTable = soup.find("textarea", class_="form-control").text
        proxies = re.findall(rgx, unformatedTable)
        # Writing json
        table = {}
        for i in range(len(proxies)):
            table[i] = proxies[i]
    try:
        file = open("proxies.json", "x")
        print("Creating proxies json file...")
        json.dump(table, file)
        ProxiesJson = table
    except Exception:
        file = open("proxies.json", "r")
        ProxiesJson = json.load(file)

getProxies()

# Dump to global proxies
_Proxies = list( ProxiesJson.values() )

# def priorProxy(mode, content=""):
#     global _Pproxies
#     if mode == 0:
#         try:
#             file = open("Pproxies.json", "x")
#             print("Creating prioritary proxies json file...")
#         except Exception:
#             with open("Pproxies.json", "r") as file:
#                 doc = json.load(file)
#                 if len( doc ) != 0:
#                     _Pproxies = doc
#     if mode == 1:
#         with open("Pproxies.json", "w") as file:
#             index = len( _Pproxies ) > 1 and len(_Pproxies) or 0
#             _Pproxies[index] = content
#             json.dump(_Pproxies, file)

def deleteProxy(value):
    global ProxiesJson
    for i in range( len( ProxiesJson ) - 1 ):
        if str(i) in ProxiesJson:
            if ProxiesJson[str(i)] == value:
                ProxiesJson.pop(str(i))
                
    with open("proxies.json", "w") as file:
        json.dump( ProxiesJson, file )

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
    # Test site function
    global rF
    def testSite(finalUrl):
        global rF
        # Test proxies until find a valid one
        global currentProxy
        isProxy = False
        if not currentProxy:
            while not isProxy:
                randomProxy = _Proxies[ran.randint(0, len(_Proxies)-1)]
                try:
                    rF = req.get(finalUrl, proxies={"https" : "https://"+randomProxy}, timeout=PROXYSEARCHTIME)
                    print("Valid proxy found: "+randomProxy)
                    currentProxy = randomProxy
                    setLastProxy()
                    isProxy = True
                except Exception:
                    deleteProxy(randomProxy)

        # Test site
        if rF.status_code != 404:
            print("Valid directory found!\n"+finalUrl+"\n")
            currentProxy = None
            return
        return False

    # Wordlist treating
    global currentProxy
    if currentProxy:
        try:
            rF = req.get(url, proxies={"https" : "https://"+currentProxy}, timeout=SITETESTTIME)
        except Exception:
            print("Last proxy timed out")
            currentProxy = None
    wordList = getWordList(mode)
    threads = []
    for word in wordList:
        try:
            finalUrl = urlF+word+"/"
            t = threading.Thread( target=testSite, args=(finalUrl,) )
            threads.append(t)
            t.start()
            time.sleep(THREADCREATINGTIME)
        except Exception as error:
            print("Error: unable to start thread: ", error)

website = input("Type the website: ")
mode = input("Type the wordlist mode (1: small, 2: medium, 3: big): ")
print("Searching directories...")
auraBuster(website, int(mode))