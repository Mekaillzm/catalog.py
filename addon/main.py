# -*- coding: utf-8 -*-
"""
Created on Sat Dec 16 13:01:07 2023

@author: mekai
"""

import pandas as pd
import re
import numpy as np
import random as rn
#auth= pd.read_csv('data/auth.csv',index_col=0)
import tkinter as tk
from tkinter import ttk
import sys
global file
file='data\\islstudents.csv'

import catalogue
class main():
    def __init__(self):
        
        #self.mainWin=tk.Tk(screenName='Main')
        self.titles=pd.DataFrame(columns=['Timestamp','Name','Email','Quote','Title'])
        self.titleErrors=pd.read_csv('data/title_errors.csv',index_col=0)
        self.quotes=pd.DataFrame(columns=['Timestamp','Name','Email','Quote','Consent'])
        self.auth=pd.read_csv('data/auth.csv',index_col=0)
        self.quoteErrors=pd.read_csv('data/quote_errors.csv',index_col=0)
        self.curData=None
        self.integratedComboboxes={}
        self.swearWords=pd.read_csv('data/word_filter_list.csv',index_col=0)
        
        #Frames
        self.cat=catalogue.catalogue(file)
        self.mainWin=self.cat.mainWin        
        self.df=self.cat.df
        self.qWin = tk.Toplevel(master=self.mainWin,takefocus=0)
        self.qWin.withdraw()
        self.qWin.protocol("WM_DELETE_WINDOW", self.qWin.withdraw)
        
        def openQWin():
            self.qWin.geometry(f'+{900}+{130}')
            self.qWin.deiconify()
            
        self.qButton=ttk.Button(master=self.cat.searchFrame,text='Quotes & Titles',command=openQWin)
        self.qButton.grid(row=0,column=6,ipady=2)
        
        self.topFrame=tk.Frame(master=self.qWin)
        self.topFrame.grid(row=0,column=0,sticky='w')
        
        self.getQuotesButton=ttk.Button(master=self.topFrame,text='Get Quotes',command=self.getQuotes,width=15)
        self.getQuotesButton.grid(row=0,column=0)
        
        self.getTitlesButton=ttk.Button(master=self.topFrame,text='Get Titles',command=self.getTitles,width=15)
        self.getTitlesButton.grid(row=3,column=0)
        
        self.quoteCombobox= ttk.Combobox(master=self.topFrame,width=13,state='normal')
        self.quoteCombobox.grid(row=1,column=0)
        
        self.titleCombobox= ttk.Combobox(master=self.topFrame,width=13,state='normal')
        self.titleCombobox.grid(row=4,column=0)
        
        
        
        
        #Lower frame
        self.bottomFrame=tk.Frame(master=self.qWin)
        self.bottomFrame.grid(row=1,column=0,pady=10)
        
        self.errorTitle= ttk.Label(master=self.bottomFrame,text='Errors',relief='groove')
        self.errorTitle.grid(row=0,column=0,pady=10,ipadx=1)
        
        self.errorUpperFrame= tk.Frame(master=self.bottomFrame)
        self.errorUpperFrame.grid(row=1,column=0)
        
        self.errorUpperSubFrame=tk.Frame(master=self.errorUpperFrame)
        self.errorUpperSubFrame.grid(row=0,column=1)
        
        self.errorEnteredNameCombobox = ttk.Combobox(master=self.errorUpperSubFrame,width=20,state='readonly')
        self.errorEnteredNameCombobox.grid(row=0,column=0)
        
        self.errorRemoveButton = ttk.Button(master=self.errorUpperSubFrame,width=2,text='-',command=self.removeError,state='disabled')
        self.errorRemoveButton.grid(row=0,column=1)
        
        self.errorEnteredNameLabel=ttk.Label(master=self.errorUpperFrame,text='Name entered in form',foreground='grey')
        self.errorEnteredNameLabel.grid(row=1,column=1)
        
        self.errorLowerFrame= tk.Frame(master=self.bottomFrame)
        self.errorLowerFrame.grid(row=2,column=0,pady=5,sticky='w')
        
        self.errorSelectNameCombobox = ttk.Combobox(master=self.errorLowerFrame,width=24,state='readonly')
        self.errorSelectNameCombobox.grid(row=0,column=1)
        
        self.errorSelectNameLabel=ttk.Label(master=self.errorLowerFrame,text='Choose the correct name',foreground='grey')
        self.errorSelectNameLabel.grid(row=1,column=1)
                
        self.errorProceedButton=ttk.Button(master=self.bottomFrame,text='>',width=3,command=self.resolveError,state='disabled')
        self.errorProceedButton.grid(row=2,column=1,sticky='s')
        
        self.compileButton=ttk.Button(master=self.bottomFrame,text='Compile',command=self.compileData)
        self.compileButton.grid(row=3,column=0)
        
        self.resetButton=ttk.Button(master=self.bottomFrame,text='Reset',command=self.Reset)
        self.resetButton.grid(row=4,column=0)



        
        self.errorEnteredNameCombobox.bind('<<ComboboxSelected>>', self.errorNameSelected) 
        self.qWin.bind('<Key>',self.onKeypress)
        self.mainWin.mainloop()
        return
    
    def readResponseFile(self,nColumns):
        path=None
        error=False
        while path==None:
            if error!=False:
                tk.messagebox.showerror(
                    'Unable To Read File', f'Failed to read file because of:{error}\nPlease select a valid file.')
                error=False
            file = tk.filedialog.askopenfile(master=self.mainWin, title=f'Select a file for {self.curData}s', filetypes=(
                ('csv files', '*.csv'), ('All files', '*.*')))
            if file==None:
                return None
            try:
                 if len(pd.read_csv(file).columns)!=nColumns:
                     error='Invalid file format. Some data may be missing'
                     continue            
            except Exception as e:
                error=e

            else:
                path=file.name
        self.qWin.deiconify()
        return path
    
    def getQuotes(self):
        self.curData='quote'
        path=self.readResponseFile(5)
        if path==None:
            return
        self.quotes=pd.read_csv(path)
        self.quotes.columns=['Timestamp','Email','Name','Quote','Consent']
        self.quoteErrors=pd.read_csv('data/quote_errors.csv',index_col=0)
        
        self.quotes,self.quoteErrors=self.authenticateStudentNames(self.quotes, self.quoteErrors, 'quote')
        self.enterErrorData(self.quoteErrors)
        self.quoteCombobox['values'] = self.df[self.df['Quote']!=';']['Students'].to_list()
        self.integratedComboboxes[self.quoteCombobox]=self.df[self.df['Quote']!=';']['Students'].to_list()
        self.fileWrite()
        self.cat.forceUpdate()
        return
    
    def getTitles(self):
        self.curData='title'
        path=self.readResponseFile(5)
        if path==None:
            return
        self.titles=pd.read_csv(path)
        
        self.titles.columns=['Timestamp','Email','Name','Title', 'Consent']
        self.titleErrors=pd.read_csv('data/title_errors.csv',index_col=0)
        
        self.titles,self.titleErrors=self.authenticateStudentNames(self.titles, self.titleErrors, 'title')
        #self.cat.forceUpdate()
        self.enterErrorData(self.titleErrors)
        self.titleCombobox['values']=self.df[self.df['Titles']!=';']['Students'].to_list()
        self.integratedComboboxes[self.titleCombobox]=self.df[self.df['Titles']!=';']['Students'].to_list()
        
        self.calculateFinalTitle()
        self.fileWrite()
        self.cat.forceUpdate()
        return
    def calculateFinalTitle(self):
        for ID in self.df[self.df['Titles']!=';'].index:
            
            titles=self.df.loc[ID, 'Titles'].split(';')[1:]
            modalTitles=pd.Series(dtype='object')
            uniqueTitles=set(titles)
            
            relevancy=0
            finalTitle=''
            for title in uniqueTitles:
                for i in titles: 
                    _=self.answer_relevancy(i,title)
                    #print(_)
                    if _>65:
                        modalTitles[title]=modalTitles.get(title,0)+1
            
            
            _=modalTitles[modalTitles==modalTitles.max()]
            #print(_)
            if len(_)==1:
                self.df.loc[ID,'Final Title']=_.index[0]
            else: 
                self.df.loc[ID,'Final Title']=_.index[rn.randint(0,len(_)-1)]
        
    def onKeypress(self,i=None):
        for index in range(len(self.integratedComboboxes)):
            
            combobox=list(self.integratedComboboxes.keys())[index]
            if not combobox.winfo_ismapped(): 
                continue
            values=list(self.integratedComboboxes.values())[index]
            entry=combobox.get()
            values=self.print_list(values,entry)
            combobox['values']=values
    
    def enterErrorData(self,data):
        self.errorEnteredNameCombobox['values']=data[data['Error']=='Name Not Found']['Name'].to_list()
        try:self.errorEnteredNameCombobox.set(self.errorEnteredNameCombobox['values'][0])
        except:self.errorEnteredNameCombobox.set('')
        self.errorNameSelected()
        
    def errorNameSelected(self,i=None):
        name=self.errorEnteredNameCombobox.get()
        self.errorResultIDs=self.print_list(self.df['Students'],name,True)
        self.errorResultIDs.reverse()
        values=self.df.loc[self.errorResultIDs]['Students'].to_list()
        self.errorButtonsConfig()
        self.errorSelectNameCombobox['values']=values
        self.errorSelectNameCombobox.set(values[0])
        
    def errorButtonsConfig(self):
        if len(self.errorEnteredNameCombobox['values'])>0:
            self.errorRemoveButton.config(state='normal')
            self.errorProceedButton.config(state='normal')

        else:
            self.errorRemoveButton.config(state='disabled')
            self.errorProceedButton.config(state='disabled')




        
    def resolveError(self):
        prevName=self.errorEnteredNameCombobox.get()
        name=self.errorSelectNameCombobox.get()
        if len(name)<1 or len(prevName)<1:
            return
        value = self.df.loc[self.errorResultIDs[self.errorSelectNameCombobox['values'].index(name)]]
        _=list(self.errorEnteredNameCombobox['values'])
        
        _.remove(prevName)

        if self.curData=='title':
            data=self.titleErrors[self.titleErrors['Name']==prevName]
            self.titleErrors,spamErrorFound=self.checkTitleSpam(data, value.name, data.index[0], self.titleErrors)
            if spamErrorFound!=True:self.addTitle(data, value.name, data.index[0])
            self.calculateFinalTitle()
            
        elif self.curData=='quote' and self.df.loc[value.name]['Quote'] == ';':
            data=self.quoteErrors[self.quoteErrors['Name']==prevName]
            #print(data,value)
            self.addQuote(data,value.name,data.index[0])
        else:
            self.removeError()
            return
        self.errorEnteredNameCombobox['values']=_
        if len(_)>0:
            self.errorEnteredNameCombobox.set(_[0])
            self.errorEnteredNameCombobox['values']=_
        else:
            self.errorEnteredNameCombobox.set('')
            self.errorEnteredNameCombobox['values']=[]

        
        self.errorNameSelected()
        self.fileWrite()
        self.cat.forceUpdate()
    def removeError(self):
        prevName=self.errorEnteredNameCombobox.get()
        _=list(self.errorEnteredNameCombobox['values'])
        _.remove(prevName)
        if len(_)>0:
            self.errorEnteredNameCombobox.set(_[0])
            self.errorEnteredNameCombobox['values']=_
        else:
            self.errorEnteredNameCombobox.set('')
            self.errorEnteredNameCombobox['values']=[]
        
        self.errorNameSelected()
    def answer_relevancy(self,ans, solution, multiple_solutions=False, results=False):
        result = dict()
        def get_rel(answer, solution):
            r = list()
            if type(answer) == type(str()):
                answer = [answer]
            for ans in answer:
                ans = str().join(re.findall('\S', ans.lower().strip()))
                solution = str().join(re.findall('\S', solution.lower().strip()))
                ans_dict = dict()
                sol_dict= dict()
                for letter in solution:
                    sol_dict[letter] = sol_dict.get(letter, 0) + 1
                relevancy = 0
                for letter in ans:
                    ans_dict[letter] = ans_dict.get(letter, 0) + 1
                for letter, occurrences in ans_dict.items():
                    try:
                        if sol_dict[letter] == occurrences: 
                            relevancy += 1            
                    except:  relevancy -= 1
                relevancy = (relevancy/len(sol_dict))*100
                r.append(relevancy)
                    
            return max(r)
        r= list()
        if multiple_solutions != False:
            ans = ans.split(',')
            sol = solution.split(',')
            if len(ans)!=len(sol): ans = ans*2
            
            for item in range(len(sol)):
                r.append(get_rel(ans, sol[item]))
            #except: None
            r = max(r)
        else: r = get_rel(ans,solution)
        #if r>=100 and ans!=solution:
            
        return r
    
    
    def print_list(self,data, search=None, returnIndex=False, numValues=20):
    
        output=[]
        if type(data) in (type(list()), type(tuple())):
            index = range(len(data))
            if search == None: 
                output=index
            else: 
                d = dict()
                for num in index:
                    d[num] = data[num]
                data=d
                del d
        output = []
        if type(data) in (type(list()), type(tuple())):
            index = range(len(data))
            if search == None:
                output = index
            else:
                d = dict()
                for num in index:
                    d[num] = data[num]
                data = d
            # return output
        if search == None:
            for index, item in data.items():
                print('{}: {}\n'.format(index, item))
        # def look_for(DICT, search_item):
        output, found, n, has_result, _ = [], dict(), 0, False, re.findall(
            '[^a-z0-9 "-]', search.lower())+[' ']
        for old in _:
            search = search.replace(old, _[0])
        search = search.lower().strip().split(_[0])
        for word in search:
            
            addAmt = 1
            if len(word) > 1:
                if word[0] == '-':
                    addAmt = -1
                    word = word[1:]
                if word[0]=='"' and word[-1]=='"':
                    addAmt=2
                    word=word[1:-1]
                
            for index, item in data.items():
                item = str(item).lower().strip()
                if re.search(f'(\A|\s){word}(\s|$)',item):
                    found[index] = found.get(index, 0) + addAmt*3
                    has_result = True
                    n += 1
                if word in item:
                    found[index] = found.get(index, 0) + addAmt
                    has_result = True
                    n += 1
    
                    
            if has_result == False:
                f = dict()
                broken_search = dict()
                broken_dict = dict()
                num = 0
                for letter in word:
                    broken_search[letter] = broken_search.get(letter, 0)+1
                for index, item in data.items():
                    pos = str(item).find('(')
                    item = str(item)[:pos].lower().split()
                    for word in item:
                        for l in word:
                            broken_dict[l] = broken_dict.get(l, 0)+1
                        for letter, num in broken_dict.items():
                            try:
                                broken_dict[letter] == broken_search[letter]
                            except:
                                f[index] = f.get(index, 0)-addAmt
                            else:
                                f[index] = f.get(index, 0)+addAmt
                        for index, item in f.items():
                            if item < 1:
                                continue
                            found[index] = found.get(index, 0)+item/2
                            n += 1
                            f = dict()
                        broken_dict = dict()
            has_result = False
    
        if n > 0:
            found2 = dict()
            for index, item in found.items():
                #item = item*100/max(found.values())
                found2[item] = found2.get(item, []) + [index]
            for item, index in sorted(found2.items()):
                for i in index:
                    output.append(i)
        else:
            #print("No results for '{}'. Try a different word or phrase.".format(search))
            found = dict()
            broken_search = dict()
            broken_dict = dict()
            n = 0
            for word in search:
                addAmt = 1
                if len(word) > 0 and word[0] == '-':
                    addAmt = -1
                for letter in word:
                    broken_search[letter] = broken_search.get(letter, 0)+addAmt
            for index, item in data.items():
                item=str(item)
                pos = item.find('(')
                item = item[:pos].lower()
                for l in item:
                    broken_dict[l] = broken_dict.get(l, 0)+1
                for letter, n in broken_dict.items():
                    try:
                        broken_dict[letter] == broken_search[letter]
                    except:
                        found[index] = found.get(index, 0)-1
                    else:
                        found[index] = found.get(index, 0)+1
    
                broken_dict = dict()
            if n > 0:
                found2 = dict()
                for index, item in found.items():
                    if item <= 0:
                        continue
                    #item = item*100/max(found.values())
                    found2[item] = found2.get(item, []) + [index]
                for item, index in sorted(found2.items()):
                    for i in index:
                        output.append(i)
            output = [
                "No good matches for '{}', try a different word or phrase.".format(search)]
    
        if returnIndex == False and not output == ["No good matches for '{}', try a different word or phrase.".format(search)]:
            return [data[index] for index in output][-numValues:]
        else:
            return output[-numValues:]
        
    def appendError(self,errors,data,i,errorType,relevancy):
        errors=pd.concat([errors,data.loc[i:i]])
        errors.loc[i,'Error'] = errorType
        errors.loc[i,'Relevancy'] = relevancy
        return errors
    def simplifyName(self,name):
        name=name.lower().split()
        finalName=[]
        for n in name:
            if n in ['muhammad','bin','binte','sheikh','mohammad']:
                continue
            finalName.append(n)
        return finalName
    def authenticateStudentNames(self,data,errors,dtype):
        for i in data.index:
            ID=None
            IDlist= self.print_list(self.df['Students'],data.loc[i,'Name'],True,50)
            IDlist.reverse()
            _=0
            for item in IDlist:    
                relevancy=self.answer_relevancy(self.df.loc[item,'Students'], data.loc[i,'Name'])
                
                if _<relevancy:
                    ID=item
                    _=relevancy
                    continue

            if _ < 75:

                enteredFullName=self.simplifyName(data.loc[i,'Name'])
                IDlist=IDlist[:7]
                _2=0

                ID2=None
                for item in IDlist:
                    fullName=self.simplifyName(self.df.loc[item, 'Students'])

                    simplifiedNameRelevancy=self.answer_relevancy(str(' ').join(fullName), str(' ').join(enteredFullName))
                    if _<simplifiedNameRelevancy:
                        ID=item
                        _=simplifiedNameRelevancy
                        
                    splitNameRelevancy=[sum(list(map(lambda n: n==name, enteredFullName))) for name in fullName]
                    splitNameRelevancy=sum(splitNameRelevancy)/max((len(fullName), len(enteredFullName)))
                    if _2<splitNameRelevancy:
                        _2=splitNameRelevancy
                        ID2=item
                #try:print(_,_2,enteredFullName,self.df.loc[ID,'Students'],self.df.loc[ID2,'Students'])
                #except:pass
                
                if (_2>0.6, ID2==ID)!= (True, True):
                    '''if _2>0.6:
                        fullName=self.df.loc[ID,'Students'].lower().split()
                        print(sum([sum(list(map(lambda n: n==name, enteredFullName))) for name in fullName])/(max((len(fullName), len(enteredFullName)))-1), fullName)
                        if 'muhammad' in [fullName[0], enteredFullName[0]] and (sum([sum(list(map(lambda n: n==name, enteredFullName))) for name in fullName])/max((len(fullName), len(enteredFullName)))) ==  1:
                            print(fullName)'''
                    if _>5 and _2>0.2:
                        errors=self.appendError(errors,data,i,'Name Not Found',_)
                    else:
                        errors=self.appendError(errors,data,i,'Name Not Present',_)
                    continue
                #else:print(self.df.loc[ID, 'Students'],enteredFullName, _, _2)
                    
            #print(self.swearWords[self.swearWords['Word']=='shit'], data.loc[i,data.columns[3]].split(' '))
            if sum(map(lambda word: len(self.swearWords[self.swearWords['Word']==word]), data.loc[i,data.columns[3]].lower().split(' '))) > 0:
                errors=self.appendError(errors, data, i, 'Inappropriate Language',_)
            
            if dtype=='quote':
                if self.df.loc[ID, 'Quote'] != ';':
                    errors=self.appendError(errors,data,i,'duplicate',_)
                    continue
                self.addQuote(data, ID, i)
            elif dtype=='title':
                errors,spamErrorFound=self.checkTitleSpam(data, ID, i, errors, _)
                
                if spamErrorFound!=True: self.addTitle(data, ID, i)

        return data, errors
    
    def checkTitleSpam(self,data,ID,i,errors,relevancy=np.nan):
        if data.loc[i,'Email'] in self.auth.index:
        #try:
            if str(ID) in str(self.auth.loc[data.loc[i,'Email'],'Title']).split(';'):  
                self.auth.loc[data.loc[i,'Email'],'Title']=str(self.auth.loc[data.loc[i,'Email'],'Title'])+';'+str(ID)
                
                errors=self.appendError(errors,data,i,'spam',relevancy)
                return errors, True
            else:
                self.auth.loc[data.loc[i,'Email'],'Title']=self.auth.loc[data.loc[i,'Email'],'Title']+';'+str(ID)
                
        #except:
        else:    self.auth.loc[data.loc[i,'Email'],'Title']=str(ID)
        return errors, False
    
    def addTitle(self, data, ID, i):
        self.df=self.cat.df
        
        titles=self.df.loc[ID,'Titles']
        if self.df.loc[ID,'Titles']!=';':
            titles+=';'
    
        titles+=f"{data.loc[i,'Title']}"
        self.df.loc[ID,'Titles']=titles

    def addQuote(self,data, ID, i):
        self.df=self.cat.df
        try:
            if self.auth.loc[data.loc[i,'Email'],'Quote'] < 1:
                self.auth.loc[data.loc[i,'Email'],'Quote']=1
            else:
                self.auth.loc[data.loc[i,'Email'],'Quote']=self.auth.loc[data.loc[i,'Email'],'Quote']+1
                self.quoteErrors=self.appendError(self.quoteErrors,data,i,'spam',_)
                return
        except:
            self.auth.loc[data.loc[i,'Email'],'Quote']= 1
        for column in ['Email','Quote']:
            self.df.loc[ID,column]=data.loc[i,column]
    
    def filterData(self, word):
        def f(word):
            return word in self.badWords['Word']
        return filter(f, word)
        
    def compileData(self,i=None):
        self.df.loc[list(set(list(self.df[self.df['Email']!=';'].index) + list(self.df[self.df['Titles']!=';'].index)))].to_csv('compiled_data.csv')
        return
    def Reset(self):
        _=tk.messagebox.askyesno(title='Confirm Reset',message='Are you sure you want to reset all student data?')
        if _!=True:
            return
        
        #quoteErrors=pd.read_csv('quote_errors.csv',index_col=0)
        self.quoteErrors=self.quoteErrors[0:0]
        self.titleErrors=self.titleErrors[0:0]
 
        self.df['Titles']=';'
        self.df['Final Title']=';'
        self.df['Quote']=';'
        self.df['Email']=';'
        self.quoteCombobox['values']=[]
        self.titleCombobox['values']=[]
        self.cat.df=self.df
        self.auth=self.auth[0:0]
        self.fileWrite()
        
        self.qWin.deiconify()
        self.cat.forceUpdate()
        #errors=errors[1:1]
    def fileWrite(self):
        self.df=self.cat.df
        self.quoteErrors.to_csv('data/quote_errors.csv')
        self.titleErrors.to_csv('data/title_errors.csv')
        self.df.to_csv(file)

        self.auth.to_csv('data/auth.csv')
        
_=main()
 
