import glob, re, sys, os, ssl, unicodedata, itertools, lxml, bs4, requests, multiprocessing
import pandas as pd
from nltk.tokenize import sent_tokenize
from dataclasses import dataclass
from pathlib import Path
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from multiprocessing.pool import Pool
from grobid_client_python import grobid_client as grobid
from bs4 import BeautifulSoup


############################################################################################
# Toolkit for pdf conversion to excel spreadsheet, parses out text by keywords from each pdf
# Written/modified by Corinn Small, corinn.small@ucsf.edu
############################################################################################



def convert_text(inpath,outpath):
    '''
    converts text from pdf to tei.xml using grobid web service api, remember computer has to be connected to the server: cd grobid-0.6.1/ -> ./gradlew run
    input: path to papers
    output: tei.xml file per pdf
    '''

    print('Converting text...')
    print('')
        
    client = grobid.grobid_client(config_path="./grobid_client_python/config.json")
    client.process("processFulltextDocument", inpath, outpath)
    
    print('Done')


def read_tei(tei_file):
    '''
    input: xml file
    output: a beautifulsoup object
    
    '''

    with open(tei_file, 'r') as tei:
        soup = BeautifulSoup(tei, 'html.parser')
        return soup
    raise RuntimeError('Cannot generate a soup from the input')
    

def elem_to_text(elem, default='NA'):
    '''
    Returns element if it exists, if not, returns NA
    
    '''

    if elem:
        return elem.getText()
    else:
        return default
    



class TEIFile(object):
    '''
    class for storing pdf info
    '''

    def __init__(self, filename):
        self.filename = filename
        self.soup = read_tei(filename)  #creates soup object
        self._text = None
        self._title = ''  
        self._abstract = ''
        self._keytext = {}
        self._check = None
        
    @property
    def doi(self, id_='DOI'):
        '''
        retrieves id
        '''
    
        idno_elem = self.soup.find('idno', type='DOI')
        if not idno_elem:
            return 'no id'
        else:
            return idno_elem.getText()
    
    @property
    def title(self):
        '''
        retrieves title
        '''
        if not self._title:
            self._title = self.soup.title.getText()
        return self._title
    
    @property
    def abstract(self):
        '''
        retrieves abstract
        '''
        
        if not self._abstract:
            abstract = self.soup.abstract.getText(separator=' ', strip=True)
            self._abstract = abstract
        return self._abstract
      
    @property
    def authors(self):
        '''
        retrieves authors
        '''
        authors_in_header = self.soup.analytic.find_all('author')

        result = []
        
        @dataclass
        class Person:
            firstname: str
            middlename: str
            surname: str
                
        for author in authors_in_header:
            persname = author.persname
            if not persname:
                continue
            firstname = elem_to_text(persname.find("forename", type="first"))
            middlename = elem_to_text(persname.find("forename", type="middle"))
            surname = elem_to_text(persname.surname)
            person = Person(surname, firstname, middlename)
            result.append(person)
        return result
    
    @property
    def text(self):
        '''
        retrieves text, asks for user's input about longer subsections (can include the subsection title in the searchable text)
        returns dictionary by subsection
        '''
        #print(self.soup.prettify())
        print(self.filename.split('/')[-1])
        print('')
        
        if not self._text:
            paper_text = {}  
                
            divs = self.soup.body.find_all('div')
            #print(divs)
                
            for div in divs:   
                if not div.get('type'):  # if div is neither an appendix nor reference
                    heads = div.find_all('head')  #find all subsections
                    #print(heads)
                    
                    if not heads:  #if there aren't any subsections
                        sect = []
                        for p in div.find_all('p'):  #add all sentences to one section titled 'body'
                            #print(p)
                            sect_text = p.get_text(separator=' ', strip=True)
                            sect.append(sect_text)
                            paper_text['body'] = sect  
                        
                        #print(sect)
                        
                    else:  #otherwise for each subsection create a new list with corresponding text and add it to a div dictionary
                        for head in heads:
                            sect_ = []
                            head_text = head.get_text(separator=' ', strip=True).lower()
                            
                            
                            if len(head_text.split(' ')) > 7:  #if the head title is < 7 words long (arbitrary #) ask the user to clarify its validity
                                print('subtitle sentence: ', head_text)
                                
                                ans = input('Is this subsection a full sentence? y/n')
                                ok_ans = ('y','n')
                                
                                while ans not in ok_ans:
                                    print('Y or N only please!')
                                    ans = input('Is this subsection a full sentence? y/n')

                                if ans == 'y':  #if the title is a sentence
                                    print('Including subsection title in searchable text, but still include it as a separate subsection...')
                                    print('')
                                    sect_.append(head_text)  #include it in the text
                                    for p in div.find_all('p'):  #for each paragraph find all text 
                                        #print(p)
                                        sect_text = p.get_text(separator=' ', strip=True)
                                        sect_.append(sect_text)  #add it to the list


                                elif ans == 'n':  #if the title is not a sentence
                                    ans1 = input('Does this subsection make sense? y/n')  #does the title make sense in general?

                                    while ans1 not in ok_ans:
                                        print('Y or N only please!')
                                        ans1 = input('Is this subsection a full sentence? y/n')


                                    if ans1 == 'y':  #if the title makes sense treat it as a regular subsection
                                        print('Valid subsection...')
                                        print('')

                                        for p in div.find_all('p'):
                                            #print(p)
                                            sect_text = p.get_text(separator=' ', strip=True)
                                            sect_.append(sect_text)

                                    elif ans1 == 'n':  #if the title doesn't make sense, mark self._check True so the user knows to check it later
                                        print('Flagging nonsense...')
                                        print()

                                        self._check = True

                                        for p in div.find_all('p'):  #still include the subsection's text in list for keyword searching
                                            #print(p)
                                            sect_text = p.get_text(separator=' ', strip=True)
                                            sect_.append(sect_text)

                                    

                            else:  #if the subsection title is not longer than 7 words, find all text and add it to the list
                                for p in div.find_all('p'):
                                    #print(p)
                                    sect_text = p.get_text(separator=' ', strip=True)
                                    sect_.append(sect_text)
                                    #print('subsection title < 7 words')
                        
                                
                            
                            paper_text[head_text] = sect_ 
                                    
                                    
                        #for figure descriptions....(WORK IN PROGRESS)
                            if head_text.find('fig') != -1:  #if figure is treated as its own subsection, find all text and include it in its own list
                                print('Figure treated as subsection: ', head_text)
                    
                                for p in div.find_all('p'):
                                    #print(p)
                                    sect_text = p.get_text(separator=' ', strip=True)
                                    sect_.append(sect_text)
                                    paper_text['figure'] = sect_
                                
                            for fig in self.soup.body.find_all('figure'):   #for figure sections find the figure descriptions and print it
                                figDesc = fig.find_all('figDesc')
                                for f in figDesc:
                                    print('Figure Description: ',f)
                                           
                  
                
            #if paper is short, all the text might show up in the abstract section of the xml file instead of div
            if not divs:
                self._check = True
                
                sect = []
                ps = self.soup.abstract.find_all('p')
                
                if not ps:
                    sect_text = self.soup.abstract.get_text(separator=' ', strip=True)
                    sect.append(sect_text)


                else:
                    for p in ps:
                        sect_text = p.get_text(separator=' ', strip=True)
                        sect.append(sect_text)

                paper_text['body'] = sect   #add all sentences to one section titled 'body'
                
                    
                
                
                
            self._text = paper_text
        return self._text
    
    

    
    def keytext(self, keywords):
        '''
        retrieves sentences by keyword
        returns dictionary
        '''
        
        
        for keyword in keywords:
            self._keytext[keyword] = []
            
        
        for k,v in self._text.items():  #for subsection and text 
                for keyword in keywords:  #search thru sentences 
                    sub_dict = {}
                    section = k.lower()
                    sub_dict[section] = []  #create list for each subsection in dictionary
                    
                    for i in v:  #for paragraph in text
                        sentences = sent_tokenize(i)  #get list of sentences
                        sentences = [s.lower() for s in sentences]
                        
                    
                        for sentence in sentences:
                            result = re.findall('\\b' + keyword + '\\b', sentence)  #find keyword in sentence

                            if len(result) > 0:  #if keyword exists, 
                                sub_dict[section].append(sentence)  #add sentence to subsection list

                            else:  
                                pass
                    
                    #print(sub_dict)
                    self._keytext[keyword].append(sub_dict)  #adds each subsection to keyword dictionary
                        
        return self._keytext                   




