import os
import re
import typing
from typing import Dict, List, Tuple

import tornado.web

MATCH_LISTS: Dict[str, Tuple[List[str], List[List[str]]]] = {}
MATCH_LISTS_DIR = os.path.join(os.path.dirname(__file__), "matchLists")

def makeWordLists():
    matchLists = os.listdir(MATCH_LISTS_DIR)
    for matchList in matchLists:
        with open(os.path.join(MATCH_LISTS_DIR, matchList), "r") as matchFile:
            fileHeadings = []
            for line in matchFile:
                if line[0] != "#":
                    fileHeadings = line.split("\t")
                    break

            headerLen = len(fileHeadings)
            fileEntries: List[List[str]] = []
            for line in matchFile:
                entry = line.split("\t")
                if len(entry) != headerLen:
                    print("ERROR: invalid line in file: %s isn't same length as header line %s"%(entry, fileHeadings))
                else:
                    fileEntries.append(entry)

            name = matchList
            if name.endswith(".txt"):
                name = name[:-4]

            MATCH_LISTS[name] = (fileHeadings, fileEntries)

makeWordLists()

INDEX_HTML = """
<h1>Search phrase list using a regex</h1>
<p>Search using: /listRegex/{wordListName}/{regex}<br />
or: /listRegex/?wordListName={wordListName}&amp;regex={regex}</p>
<form method='get' action="/listRegex/">
<select name="wordListName">
%s
</select>
regex to search: <input type="text" name="regex"></input>
</form>
"""%("<br />".join(["<option value='%s'>%s</option>"%(listName, listName) for listName in MATCH_LISTS]))

class ListRegex(tornado.web.RequestHandler):
    def get(self, wordListName: str=None, regexUrlComponent=None):
        """ This is what gets called when the user request the page specified below in the requests list """
        # Any URL encoding in the component will have been undone before getting here

        # If you use the form above to query, then it will come through as the regex 'get' argument instead
        if not regexUrlComponent:
            wordListName = self.get_argument("wordListName", "")
            if wordListName == "":
                message = "Need to specify a wordListName"
                raise tornado.web.HTTPError(status_code=400, reason=message, log_message=message)
            regexUrlComponent = self.get_argument("regex", "")
            if regexUrlComponent == "":
                message = "Need to specify a regex"
                raise tornado.web.HTTPError(status_code=400, reason=message, log_message=message)

        if wordListName not in MATCH_LISTS:
            message = "Invalid word list.  Try one of: %s"%(list(MATCH_LISTS.keys()))
            raise tornado.web.HTTPError(status_code=400, reason=message, log_message=message)

        print(regexUrlComponent)

        if regexUrlComponent.startswith("?regex="):
            regexUrlComponent = regexUrlComponent[7:]

        (headerList, wordList) = MATCH_LISTS[wordListName]

        try:
            # Attempt to compile the regex for later use
            # If the user has given a bad regex, then this can except
            compRegex = re.compile(regexUrlComponent)
        except re.error as e:
            # Send an error message saying what was wrong with the regex to the user
            message = "Invalid regex: %s. Input was: '%s'"%(e.msg, regexUrlComponent)
            raise tornado.web.HTTPError(status_code=400, reason=message, log_message=message)

        matchEntries = []
        # Do the actual job here - find the entries that match the word list
        for entry in wordList:
            if compRegex.search(entry[0]):
                matchEntries.append(entry)

        # Convert from a list of tuples into a list of dicts
        matchInfo = []
        for entry in matchEntries:
            matchInfo.append(dict(zip(headerList, entry)))

        # JSON return calls must be a dict, cannot be a list
        retInfo = {
            "matches": matchInfo,
        }

        # Send the data to the client.
        # This would normally be a string, but if you put a dict in, then it will be sent as JSON
        self.write(retInfo)

requests = [
    # Match against anything specified after regexWordList, treating the entire rest of the string as the regex
    (r"/listRegex/([^/]+)/(.+)", ListRegex),
    (r"/listRegex/", ListRegex),
]

indexItems = [
    INDEX_HTML,
]
