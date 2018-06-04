#!/usr/bin/python3
import xml.etree.ElementTree as ET
import random #Funciones aleatorias
import re #reeeeeeeeeeeee
import time
import json #Base
import os

med_ver = "0.70b 7E2-06"

rep_params = {
    "match_param":re.compile("(\[:(\d){1,9}:]+)"),
    "match_bot_param":re.compile("\$\[([A-Za-z0-9]+)\]")
    #"match_emoji":re.compile("\[:emoji\(([A-Z0-9]+)\):]")
    }

class BotClient():
    def __init__(self):
        print("Medea Engine ver %s" % med_ver)
        self.seeddate = time.localtime(time.time())
        random.seed(self.seeddate.tm_sec * self.seeddate.tm_min * self.seeddate.tm_yday + self.seeddate.tm_mon - self.seeddate.tm_year)
        self.dictionary = Dictionary()
        config = open("chatbot/AI.json", "r")
        rawdata = config.read()
        self.bot = json.loads(rawdata)
        config.close()
        for filename in os.listdir('chatbot'):
            if filename.endswith(".pyb"):
                print("Processing %s..." % filename)
                self.tree = ET.parse('chatbot/' + filename)
                self.root = self.tree.getroot().find("Concept")
                for pattern in self.root.findall('Default'):
                    self.dictionary.make_pattern(pattern, True)
                for pattern in self.root.findall('Model'):
                    #print("- Add %s from %s" % (pattern.find("Pattern").text, filename))
                    self.dictionary.make_pattern(pattern, False)
        print("Dictionary loaded with %i words and %i rules" % (len(self.dictionary.words), self.dictionary.rules))
    def chat(self, msg):
        #print("Requested reply for: %s", msg)
        return self.dictionary.process_response(msg, self.bot)
    def getbotdata(self, param):
        return self.bot[param]

class Dictionary():
    def __init__(self):
        self.rules = 0
        self.words = {"*":[],"_":[],"?":[],"^":[]}
        self.previous = ""
        self.default_pattern = None
        #print("Dictionary Initialized")
    def make_pattern(self, model, default=False):
        ifconditions = []
        replies = ()
        if model.find('If') == None:
            if model.find('Random') == None:
                replies = tuple(model.findall('Response'))
            else:
                replies = tuple(model.find('Random').findall("Item"))
        else:
            # print("-- Conditional rule")
            conditions = model.findall('If')
            for cond in conditions:
                print("Cond ", cond)
                prev = cond.get('previous')
                cond_replies = cond.findall('Response') + cond.findall('Item')
                ifconditions.insert(len(ifconditions), {"type":"Response","value":prev,"inverse":False,"Replies":cond_replies})
        # print("Processed: ", ifconditions)
        inp = model.find('Pattern').text
        cpat = ChatPattern(model.find('Pattern').text, replies, ifconditions if len(ifconditions)>0 else None)
        if not default:
            self.insert_word(inp.lstrip().split(" ")[0], cpat)
        else:
            self.default_pattern = cpat
            # print("Default set: ", self.default_pattern.replies[0])
    def insert_word(self, word, pattern):
        if(self.search_word(word) == False):
            self.words[word] = []
            self.words[word].insert(len(self.words[word]), pattern)
            self.rules = self.rules + 1
        else:
            self.words[word].insert(len(self.words[word]), pattern)
            self.rules = self.rules + 1
    def search_word(self, word):
        for w in self.words.keys():
            if(w == word):
                return True
        return False
    def process_response(self, text, bot_data):
        topweight = 0
        utext = text.upper()
        iwords = utext.lstrip().split(" ")
        results = []
        likable = 0
        if self.search_word(iwords[0]):
            for p in self.words[iwords[0]]:
                matches = p.regexp.findall(utext)
                if(len(matches) > 0):
                    if p.weight > topweight:
                        results.insert(len(results), ChatResult(p, p.weight, matches))
                        topweight = p.weight
                        likable = len(results)-1
        for p in self.words["*"]:
            matches = p.regexp.findall(utext)
            if(len(matches) > 0):
                if p.weight > topweight:
                    results.insert(len(results), ChatResult(p, p.weight, matches))
                    topweight = p.weight
                    likable = len(results)-1
        for p in self.words["_"]:
            matches = p.regexp.findall(utext)
            if(len(matches) > 0):
                if p.weight > topweight:
                    results.insert(len(results), ChatResult(p, p.weight, matches))
                    topweight = p.weight
                    likable = len(results)-1
        for p in self.words["?"]:
            matches = p.regexp.findall(utext)
            if(len(matches) > 0):
                if p.weight > topweight:
                    results.insert(len(results), ChatResult(p, p.weight, matches))
                    topweight = p.weight
                    likable = len(results)-1
        for p in self.words["^"]:
            matches = p.regexp.findall(utext)
            if(len(matches) > 0):
                if p.weight > topweight:
                    results.insert(len(results), ChatResult(p, p.weight, matches))
                    topweight = p.weight
                    likable = len(results)-1
        # print("Results: ", len(results))
        if(len(results) > 0):
            self.previous = results[likable].match.match
            # print(self.previous)
            if results[likable].match.conditional:
                if(results[likable].match.condition_meets(self.previous)):
                    return results[likable].match.getreply(results[likable].matches, bot_data).lstrip()
            else:
                return results[likable].match.getreply(results[likable].matches, bot_data).lstrip()
        else:
            return self.default_pattern.getreply("", bot_data).lstrip()

def preprocess(msg):
    operators = {
        " _ ":"\s([^\s]+)\s", #MIDDLE, Match one word
        " * ":"\s(.+)\s", #Match one or more words
        " ? ":"\s?([^\s]+)?\s", #Match one or none words
        " ^ ":"\s(.*)?\s", #Match none or any words
        "_ ":"^([^\s]+)\s", # FIRST
        "* ":"^(.+)\s",
        "? ":"([^\s]+)?\s?",
        "^ ":"^(.*)?\s?",
        " _":"\s([^\s]+)$", #LAST
        " *":"\s(.+)$",
        " ?":"\s([^\s]+)?$",
        " ^":"\s(.*)$"
    }
    temp = msg.lstrip().upper()
    for op in operators.keys():
        temp = temp.replace(op, operators[op])
    temp = re.sub(r"^(\*)$", "(.+)", temp)
    temp = re.sub(r"^(\_)$", "^([^\s]+)$", temp)
    temp = re.sub(r"^(\^)$", "^(.*)?$", temp)
    temp = re.sub(r"^(\?)$", "^([^\s]+)?$", temp)
    # print(temp)
    return temp

class ChatPattern():
    def __init__(self, match, reply, conditions=None):
        #self.regexp = re.compile(match.replace("_ ", "([*\s]+) ").replace("* ", "(.*) ").replace(" _ ", " ([*\s]+) ").replace(" * ", " (.*) ").replace(" _", " ([*\s]+)").replace(" *", " (.*)").upper())
        self.match = match
        self.regexp = re.compile(preprocess(match))
        self.weight = 0
        self.conditional = True if conditions!=None else False
        self.reverseconditional = False
        self.conditions = []
        if conditions != None:
            self.conditions = conditions
        # print("Conditions: ", self.conditions)
        if "*" in match or "_" in match or "*" in match or "?" in match:
            words = match.split(" ")
            temp = 0
            for w in words:
                if w == "*":
                    self.weight = self.weight + 95
                elif w == "_":
                    self.weight = self.weight + 5
                elif w == "?":
                    self.weight = self.weight + 10
                elif w == "^":
                    self.weight = self.weight + 100
                else:
                    self.weight = self.weight + 1
        else:
            self.weight = 1000 + len(match.split(" "))
        self.replies = []
        for i in reply:
            self.replies.insert(len(self.replies), i.text)
    def getreply(self, matches, bot_data):
        if matches is None:
            if not self.conditional:
                return random.choice(self.replies)
        raw = random.choice(self.replies)
        params = rep_params["match_param"].findall(raw)
        bot_params = rep_params["match_bot_param"].findall(raw)
        for r in params:
            if type(matches[0]) is tuple:
                raw = raw.replace(r[0], matches[0][int(r[1])].lower())
            elif type(matches[0]) is str:
                raw = raw.replace(r[0], matches[0].lower())
        for b in bot_params:
            raw = raw.replace("$["+b+"]", bot_data[b])
        return raw
    def condition_meets(self, previous):
        if(self.conditions["type"]=="response"):
            if(self.conditions["value"]==previous):
                return True;
        return False;

class ChatResult():
    def __init__(self,match,weight,matches):
        self.match = match
        self.weight = weight
        self.matches = matches
