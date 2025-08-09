# -*- coding: utf-8 -*-
"""
Created on Sun Oct 24 13:59:24 2021

@author: mekai
"""

# -*- coding: utf-8 -*-
"""
Created on Sun Aug 29 12:29:05 2021

@author: mekai
"""


import pandas as pd
from tkinter import *
from tkinter.ttk import *
from tkinter import filedialog
import tkinter.messagebox as msg
import math
import sys
if 'R:\Mekaill\Zeug\python\pkgs' not in sys.path: sys.path.append('R:\Mekaill\Zeug\python\pkgs')

import re
import os

class catalogue():
    
    def findDateColumns(self,textDf=None): #finds the index values of the columns with date values
        try:
            if textDf!=None:self.textDf=pd.read_csv(textDf[:-4]+'-text.csv',index_col=0)
            else:textDf=self.textDf
            _=[]
            for i in range(len(self.textDf.iloc[7].item().split('♣'))):
                if self.textDf.iloc[7].item().split('♣')[i]=='date':_.append(i+1)
        except:_=None
        return _      
    
    
    def __init__(self,file=''):
        self.itemName='item'
        self.systemName='catalogue'
        
        # windows
        self.mainWin = Tk(screenName='Catalogue')
        self.mainWin.geometry(
            f'{self.mainWin.winfo_screenwidth()}x{self.mainWin.winfo_screenheight()}+0+0')
        self.mainWin.title('Catalog')
        
        #maximum possible number of columns
        self.maxColumnRange=range(15)
        self.integratedComboboxes={}
        self.fileName=file
        self.curState='none'
        self.prefPath=(sys.path[-1]+'\\preferences.csv')
        if self.fileName!='':        
            self.curState = 'temporary'
            if self.testData(pd.read_csv(self.fileName,index_col=0)):
                self.readDfFile(self.fileName)
            
        
        try:
            self.pref = pd.read_csv(self.prefPath, index_col=0)['0']
            
        except:
            self.pref = pd.Series({'firstTimeSetup': False,'favourites':''})
            self.pref.to_csv(self.prefPath)
            
            #self.curState = 'new'
            # self.newDf()
        else:
            if self.curState!='temporary':
            
                self.curState = self.pref['firstTimeSetup']
    
                try:
                    self.fileName = self.pref['fileName']
                    self.readDfFile(self.fileName)
                except:
                    self.curState='fileNotFound'
                    self.tutorial()
                #self.df.to_csv(self.fileName)
        #if self.curState != False and self.curState!='False':
        #    self.tutorial()
        #self.confirmDataIntegrity()
        

        try:
            self.recentFileList=self.pref['recent'].split('?')
            self.recentFilePathList=self.pref['recentPaths'].split('?')
        except:
            self.pref['recent']=''
            self.pref['recentPaths']=''
            self.recentFileList=[]
            self.recentFilePathList=[]
        
            

        self.mainWin.title(f'{self.fileName.split("/")[-1]}')
        self.results = []

        # self.searchResult=Tk(screenName='Result')
        # self.addWindow=Tk(screenName='Add')
        self.query = ''
        
        #self.columns=self.df.columns.to_list() #Redefined in updateText() and used to alter column values if the dataframe 

        # frames

        self.searchFrame = Frame(master=self.mainWin)
        self.resultFrame = Frame(master=self.mainWin)
        self.pageFrame = Frame(master=self.mainWin)
        self.noResultFrame = Frame(master=self.mainWin)
        self.selectFrame = Frame(master=self.mainWin)

        # windows
        self.addFrame = Toplevel(master=self.mainWin)
        

        self.infoWin = Toplevel(master=self.mainWin)
        self.infoWin.title('Information')
        self.infoSumWin=Toplevel(master=self.infoWin)

        self.askBorrower = Toplevel(master=self.mainWin)

        self.advancedSelectWin = Toplevel(master=self.mainWin)
        self.advancedSelectWin.title('Replace')

        self.pageWin = Toplevel(master=self.mainWin)

        # searchFrame
        self.searchEntry = Entry(
            master=self.searchFrame, state=NORMAL, width=120, foreground='grey')
        self.addButton = Button(master=self.searchFrame,
                                command=self.addFrame.deiconify, text=f'Add {self.itemName.capitalize()}')
        self.infoButton = Button(
            master=self.searchFrame, command=self.infoWin.deiconify, text='i', width=1)
        
        self.favButton = Button(master=self.searchFrame,command=self.setFav,width=4) #used to save file paths for easier access
        try:self.favList=self.pref['favourites'].split('?')
        except:self.favList=[]
        self.result = None


        # addFrame
        self.addFrame.geometry(
            f'+{int(self.mainWin.winfo_screenwidth()/2)-270}+{int(self.mainWin.winfo_screenheight()/2)-50}')

        self.addFrame1 = Frame(master=self.addFrame)

        self.addTitleLabel = Label(master=self.addFrame1)
        self.addAuthorLabel = Label(master=self.addFrame1)
        self.addTypeLabel = Label(master=self.addFrame1)
        self.addDonorLabel = Label(master=self.addFrame1)
        self.addSuccessLabel = Label(
            master=self.addFrame1, foreground='grey')

        self.addTitle = Entry(master=self.addFrame1)
        self.addAuthor = Entry(master=self.addFrame1)
        self.addType = Entry(master=self.addFrame1)
        self.addDonor = Entry(master=self.addFrame1)
        self.addAddButton = Button(
            master=self.addFrame1, command=self.confirmAdd, text='Add', takefocus=0)

        self.addTitleLocked = IntVar(master=self.addFrame1)
        self.addAuthorLocked = IntVar(master=self.addFrame1)
        self.addTypeLocked = IntVar(master=self.addFrame1)
        self.addDonorLocked = IntVar(master=self.addFrame1)

        self.lockTitle = lambda: self.lockEntry(
            self.addTitle, self.addTitleLocked)
        self.lockAuthor = lambda: self.lockEntry(
            self.addAuthor, self.addAuthorLocked)
        self.lockType = lambda: self.lockEntry(
            self.addType, self.addTypeLocked)
        self.lockDonor = lambda: self.lockEntry(
            self.addDonor, self.addDonorLocked)

        self.addTitleCheck = Checkbutton(
            master=self.addFrame1, text='lock', variable=self.addTitleLocked, command=self.lockTitle, takefocus=0)
        self.addAuthorCheck = Checkbutton(
            master=self.addFrame1, text='lock', command=self.lockAuthor, variable=self.addAuthorLocked, takefocus=0)
        self.addTypeCheck = Checkbutton(
            master=self.addFrame1, text='lock', command=self.lockType, variable=self.addTypeLocked, takefocus=0)
        self.addDonorCheck = Checkbutton(
            master=self.addFrame1, text='lock', command=self.lockDonor, variable=self.addDonorLocked, takefocus=0)

        def showShortcuts():
            if self.addShortcutsLabel.winfo_ismapped():
                self.addShortcutsLabel.grid_remove()
                self.addAutoCapsFrame.grid_remove()
                self.addShortcutsButton.config(text='Shortcuts')
            else:
                self.addShortcutsLabel.grid()
                self.addAutoCapsFrame.grid()
                self.addShortcutsButton.config(text='-')
        self.addShortcutsButton = Button(
            master=self.addFrame, text='Shortcuts', command=showShortcuts, takefocus=0)
        self.addShortcutsLabel = Label(master=self.addFrame, text=f'Press CTRL and almost any key after selecting some text to create a hotkey for that text.\nPress the same character combination to paste the text.\nFor example, you could press CTRL+S while selecting the word "science" under the type heading.\nAfter this, the word "science" could be pasted under any other heading by pressing CTRL+S.\n\nUse the lock options to "lock" text boxes and prevent the text inside them from being removed after you add a {self.itemName}.\n\nPress ENTER to jump to the nearest empty textbox or add the {self.itemName} if all textboxes have been filled.\n\nPress TAB to jump to the next textbox', foreground='grey')

        self.addAutoCapsFrame = Frame(master=self.addFrame)
        self.addAutoCapsLabel = Label(
            master=self.addAutoCapsFrame, text='Automatically Capitalize Text')
        self.addAutoCapsCombobox = Combobox(
            master=self.addAutoCapsFrame, state='readonly', width=20)
        self.addAutoCapsCombobox['values'] = (
            'Always', 'Only Lowercase Text', 'Never')
        try:self.addAutoCapsCombobox.set(self.pref['autoCaps'])
        except:
            self.pref['autoCaps']='Only Lowercase Text'
            self.addAutoCapsCombobox.set('Only Lowercase Text')
            self.pref['recent']=''
            self.pref['recentPaths']=''
            
        self.addHotkeys = {}

        for check in (self.addTitleCheck, self.addAuthorCheck, self.addTypeCheck, self.addDonorCheck):
            check.invoke()
            check.invoke()

        self.addFrame.withdraw()

        self.addSuggestWin = Toplevel(master=self.addFrame, takefocus=0)

        self.addSuggestLabel = Label(
            master=self.addSuggestWin, text='Suggestions')
        self.addSuggestB1 = Button(
            self.addSuggestWin, text='', command=self.b1SuggestionPlace)
        self.addSuggestB2 = Button(
            self.addSuggestWin, text='', command=self.b2SuggestionPlace)
        self.addSuggestB3 = Button(
            self.addSuggestWin, text='', command=self.b3SuggestionPlace)

        self.addSuggestWin.overrideredirect(True)
        self.addSuggestWin.attributes('-alpha', 0.9)
        # self.mainWin.wm_attributes("type",'dock')

        #resultFrame
        self.numResults = 20
        
        self.resultTitleFrame = Frame(master=self.resultFrame)
        self.resultFrames = [Frame(master=self.resultFrame)
                             for n in range(self.numResults)]

        self.pageSelected = IntVar(master=self.resultFrame)
        self.selectPageButton = Checkbutton(
            master=self.resultTitleFrame, text='📄', command=self.onSelectPage, var=self.pageSelected)

        self.resultLabels = [
            Label(text=column, master=self.resultTitleFrame) for column in self.maxColumnRange]
        self.resultEntries = []
        self.numRowsVisible = range(self.numResults)

        self.resultId = [Label(master=self.resultFrames[n], width=7,
                               anchor=E, foreground='grey') for n in range(self.numResults)]
        self.resultCheckVars = [IntVar(master=self.resultFrame)
                                for n in range(self.numResults)]
        self.resultChecks = [Checkbutton(master=self.resultFrames[n], command=self.onSelect,
                                         onvalue=1, offvalue=0, variable=self.resultCheckVars[n]) for n in range(self.numResults)]
        self.selected = set()
        # self.selectionsOpen=False
        for row in range(self.numResults):
            self.resultEntries.append([])
            for n in range(len(self.maxColumnRange)):
                self.resultEntries[row].append(
                    Entry(master=self.resultFrames[row]))
        # pageFrame
        self.resultForwardButton = Button(
            master=self.pageFrame, text='>', width=2, command=self.pageForward)
        self.resultBackButton = Button(
            master=self.pageFrame, text='<', width=2, command=self.pageBack, state=DISABLED)
        self.resultPageLabel = Label(master=self.pageFrame, text='Page 1 of 1')

        self.page = 0

        # info frame
        self.infoFrame= Frame(master=self.infoWin)
        sw = 25
        self.bookCombobox = Combobox(
            master=self.infoFrame, state='normal', width=sw)
        self.bookLabel = Label(master=self.infoFrame)

        self.bookNumLabel = Label(
            master=self.infoFrame)
        self.bookNumEntry = Entry(
            master=self.infoFrame, state='readonly', width=sw+3)

        self.bookUniqueNumLabel = Label(
            master=self.infoFrame)
        self.bookUniqueEntry = Entry(
            master=self.infoFrame, state='readonly', width=sw+3)

        self.authorLabel = Label(master=self.infoFrame)
        self.authorCombobox = Combobox(
            master=self.infoFrame, state='normal', width=sw)

        self.donorLabel = Label(master=self.infoFrame)
        self.donorCombobox = Combobox(
            master=self.infoFrame, state='normal', width=sw)
        self.donorInfo = Label(master=self.infoFrame)

        self.bookTypeLabel = Label(master=self.infoFrame)
        self.bookTypeCombobox = Combobox(
            master=self.infoFrame, state='normal', width=sw)

        self.authorInfo = Label(master=self.infoFrame)
        self.typeInfo = Label(master=self.infoFrame)
        self.bookInfo = Label(master=self.infoFrame)

        self.infoWin.withdraw()
        # No result frame
        self.noResultLabel = Label(master=self.noResultFrame, text="No result found, try searching using other relevant information.", font=(
            'MS Comic Sans', 15), relief=SUNKEN)

        # ask borrower
        self.askBorrowerEntry = Entry(master=self.askBorrower)
        self.askBorrowerLabel = Label(
            master=self.askBorrower)

        self.askDueDateEntry = Entry(master=self.askBorrower)
        self.askDueDateLabel = Label(
            master=self.askBorrower)

        self.askBorrowerButton = Button(
            master=self.askBorrower, text='Continue', command=self.borrowerEntered)
        
        self.borrowedList = []
        
        # selectFrame
        self.selectButton = Button(
            master=self.selectFrame, text='Deselect', command=self.activateSelect)
        
        #self.selectAllButton=Button(master=self.selectFrame,text='Select All',command=self.onSelectAll)
        self.selectDeleteButton = Button(
            master=self.selectFrame, text='Delete', command=self.onDeleteSelected)
        self.selectNumSelected = Label(
            master=self.selectFrame, text='0 {self.itemName.capitalize()}s Selected', width=22)
        self.selectBorrowButton = Button(
            master=self.selectFrame,command=self.onSelectedBorrow)
        self.selectAvailableButton = Button(
            master=self.selectFrame, command=self.onSelectedAvailable)
        #self.selectAdvancedButton=Button(master=self.selectFrame,text='Find and Replace',command=self.advancedSelectWin.deiconify)
        
        # advancedSelectWin
            
        self.replaceCombobox=Combobox(master=self.advancedSelectWin,width=14)
        self.replaceComboboxSubLabel=Label(master=self.advancedSelectWin,text='Choose a column',foreground='grey')
        self.advancedSelectSubFrame=Frame(master=self.advancedSelectWin)
        self.replaceEntry=Entry(master=self.advancedSelectSubFrame,width=24)
        self.replaceButton=Button(master=self.advancedSelectSubFrame,text='Replace',command=self.replaceColumnValues)
        
        self.replaceLabel=Label(master=self.advancedSelectWin,text=f"Enter replacement for all selected {self.itemName}(s)",foreground='grey')
        
        '''self.selectReplaceWordFrame = Frame(master=self.advancedSelectWin)
        self.selectReplaceWordLabel = Label(
            master=self.selectReplaceWordFrame, text='Value to Replace')
        self.selectReplaceWordInfoLabel = Label(
            master=self.selectReplaceWordFrame, text='The word/value to be replaced, leave blank to all values entirely', foreground='grey')
        self.selectReplaceWordEntry = Entry(master=self.selectReplaceWordFrame)

        self.selectReplaceEntire = IntVar(master=self.advancedSelectWin)
        self.selectReplaceEntireCheckbutton = Checkbutton(
            master=self.advancedSelectWin, text='Replace Entire Value', var=self.selectReplaceEntire)
        self.selectReplaceFrame = Frame(master=self.advancedSelectWin)
        self.selectReplaceEntries = []'''

        '''for n in range(len(self.resultEntries[0])):
            width = 20
            #if self.df.columns[n] in (self.columns[0], self.columns[1], self.columns[5], self.columns[-1]):
            #    width = 30
            self.selectReplaceEntries.append(
                Entry(master=self.selectReplaceFrame, width=width))
            
        self.selectReplaceLabels = [
            Label(master=self.selectReplaceFrame) for column in self.maxColumnRange]
        self.advancedSelectInfoLabel = Label(
            master=self.advancedSelectWin, text=f'Type and click Replace to replace the values in the selected {self.itemName}s.', foreground='grey')
        self.advancedSelectReplaceButton = Button(
            master=self.advancedSelectWin, text='Replace', command=self.selectReplace)
        '''
        # deleteMenu
        bw = 30
        self.deleteMenu = Menu(master=self.mainWin, tearoff=0)

        def setItemBorrowed():
            index = self.getFocusedItem()
            if index != None:
                self.borrowedList = [index]

                self.onBorrowed(True)

        def setItemAvailable():
            index = self.getFocusedItem()
            if index != None:
                self.borrowedList = [index]
                self.onAvailable()
        self.deleteMenu.add_command(label='Delete', command=self.delete)
        self.deleteMenu.add_command(command=setItemBorrowed,label='Set As Borrowed')
        self.deleteMenu.add_command(
            label='Set As Available', command=setItemAvailable)
        
        # mainMenu
        self.mainMenu = Menu(master=self.mainWin)
        self.fileMenu = Menu(master=self.mainMenu, tearoff=0)
        self.fileMenu.add_command(label='New file', command=self.newDf)
        self.fileMenu.add_separator()
        
        self.openRecentMenu=Menu(master=self.fileMenu,tearoff=0)
        self.fileMenu.add_cascade(label='Open recent', menu=self.openRecentMenu)
        
        self.favMenu=Menu(master=self.fileMenu,tearoff=0)
        self.fileMenu.add_cascade(label='Open starred',menu=self.favMenu)

        self.fileMenu.add_command(label='Open file', command=self.openDf)
        self.fileMenu.add_command(label='Export file')
        
        self.editMenu = Menu(master=self.mainMenu, tearoff=0)
        self.editMenu.add_command(
            label='Replace', command=self.openReplace)
        self.editMenu.add_command(label='Select All', command=self.onSelectAll)
        #self.editMenu.add_command(label='Rename Columns',command=lambda:self.confirmDataIntegrity(True))
        self.mainMenu.add_cascade(menu=self.fileMenu, label='File')
        self.mainMenu.add_cascade(menu=self.editMenu, label='Edit')
        self.mainWin.config(menu=self.mainMenu)
        
        #openRecent

        try:
            self.openRecentMenu.add_command(label=self.recentFileList[-1],command=lambda:self.openRecent(self.recentFilePathList[-1]))
            self.openRecentMenu.add_command(label=self.recentFileList[-2],command=lambda:self.openRecent(self.recentFilePathList[-2]))
            self.openRecentMenu.add_command(label=self.recentFileList[-3],command=lambda:self.openRecent(self.recentFilePathList[-3]))
            self.openRecentMenu.add_command(label=self.recentFileList[-4],command=lambda:self.openRecent(self.recentFilePathList[-4]))
        except:pass            
        # pageWin
        
        self.pageWin.overrideredirect(True)
        self.pageWin.attributes('-alpha', 0.9)
        self.cursorInPageWin = False
        self.cursorInPageFrame = False

        self.pageLabel = Label(master=self.pageWin, text='Go To Page')
        self.pageEntry = Entry(master=self.pageWin, width=5)
        self.pageButton = Button(
            master=self.pageWin, text='>', command=self.swapPage, width=2)

        # mapping
        # self.mainFrame.grid(row=1,column=0)
        self.mainWin.after(500, lambda: self.searchFrame.grid(
            row=0, column=1, pady=40,padx=10))


        #searchFrame
        self.addButton.grid(row=0, column=2, ipady=3)
        self.searchEntry.grid(row=0, column=3, ipady=3)
        self.infoButton.grid(row=0, column=0, ipady=3)
        self.favButton.grid(row=0,column=1,ipady=3)

        self.addAddButton.grid(row=1, column=4)
        # self.searchCombobox.grid(row=0,column=1)
        # self.searchButton.grid(row=0,column=3)
        self.addFrame1.grid(row=0, column=0)

        self.addTitleLabel.grid(row=0, column=0)
        self.addAuthorLabel.grid(row=0, column=1)
        self.addTypeLabel.grid(row=0, column=2)
        self.addDonorLabel.grid(row=0, column=3)

        self.addTitle.grid(row=1, column=0, padx=1)
        self.addAuthor.grid(row=1, column=1, padx=1)
        self.addType.grid(row=1, column=2, padx=1)
        self.addDonor.grid(row=1, column=3, padx=1)

        self.addTitleCheck.grid(row=2, column=0)
        self.addAuthorCheck.grid(row=2, column=1)
        self.addTypeCheck.grid(row=2, column=2)
        self.addDonorCheck.grid(row=2, column=3)

        self.addShortcutsButton.grid(row=1, column=0, sticky='w', pady=5)
        self.addShortcutsLabel.grid(row=2, column=0, sticky='w', pady=3)
        self.addShortcutsLabel.grid_remove()
        self.addAutoCapsFrame.grid(row=3, column=0, sticky='w')
        self.addAutoCapsFrame.grid_remove()

        self.addAutoCapsLabel.grid(row=0, column=0, padx=2)
        self.addAutoCapsCombobox.grid(row=0, column=1)

        self.addSuccessLabel.grid(row=1, column=5)
        self.addSuccessLabel.grid_remove()

        # self.addSuggestLabel.grid(row=2,column=0,sticky='nw')
        self.addSuggestB1.grid(row=1, column=0, pady=1, padx=1)
        self.addSuggestB2.grid(row=1, column=1, pady=1, padx=0)
        self.addSuggestB3.grid(row=1, column=2, pady=1, padx=1)
        self.addSuggestWin.withdraw()

        self.resultFrame.grid(row=2, column=1, padx=25,sticky='w')
        self.resultFrame.grid_remove()

        self.pageFrame.grid(row=3, column=1)
        self.resultBackButton.grid(row=0, column=0, sticky='e', pady=30)
        self.resultForwardButton.grid(row=0, column=2, sticky='w', pady=30)
        self.resultPageLabel.grid(row=0, column=1, sticky='e', pady=30)

        self.noResultFrame.grid(row=2, column=1, padx=273)
        self.noResultLabel.grid(row=0, column=0)
        self.noResultFrame.grid_remove()

        self.selectFrame.grid(row=3, column=1, sticky='s')
        self.selectFrame.grid_remove()

        self.selectButton.grid(row=0, column=0)
        self.selectBorrowButton.grid(row=0, column=1)
        self.selectNumSelected.grid(row=0, column=2, padx=50)
        self.selectAvailableButton.grid(row=0, column=3)

        self.selectDeleteButton.grid(row=0, column=4)

        # self.selectAllButton.grid(row=0,column=0)
        # self.selectAdvancedButton.grid(row=0,column=5)
        
        self.mapList = lambda l, row, minCol=0, disclude=0: [
            l[n].grid(row=row, column=n+minCol) for n in range(len(l)-disclude)]
        self.unmapList = lambda l: [item.grid_remove() for item in l]
        self.delList = lambda l: [entry.delete(0, END) for entry in l]

        
        self.replaceCombobox.grid(row=1,column=0,sticky='w')
        self.replaceComboboxSubLabel.grid(row=2,column=0,sticky='w')
        self.advancedSelectSubFrame.grid(row=1,column=1)
        self.replaceEntry.grid(row=1,column=1,sticky='w')
        self.replaceButton.grid(row=1,column=2,sticky='w')
        self.replaceLabel.grid(row=2,column=1,sticky='e')
        '''self.mapList(self.selectReplaceLabels, 0, 0)
        self.mapList(self.selectReplaceEntries, 1, 0)

        self.selectReplaceWordFrame.grid(row=2, column=0, sticky='w', pady=15)
        self.selectReplaceWordLabel.grid(row=0, column=0)
        self.selectReplaceWordEntry.grid(row=0, column=1)
        self.selectReplaceWordInfoLabel.grid(row=0, column=2)

        self.selectReplaceEntireCheckbutton.grid(row=3, column=0, sticky='w')

        self.selectReplaceFrame.grid(row=0, column=0)
        self.advancedSelectInfoLabel.grid(row=1, column=0, sticky='w')
        self.advancedSelectReplaceButton.grid(row=0, column=1, sticky='ws')
        '''
        self.advancedSelectWin.withdraw()

        self.infoFrame.grid(row=0,column=0)
        self.bookLabel.grid(row=0, column=0, sticky='w')
        self.bookCombobox.grid(row=0, column=1)
        self.bookInfo.grid(row=0, column=2, sticky='w')

        self.bookNumLabel.grid(row=1, column=0, sticky='w')
        self.bookNumEntry.grid(row=1, column=1)

        self.bookUniqueNumLabel.grid(row=2, column=0, sticky='w')
        self.bookUniqueEntry.grid(row=2, column=1)

        self.authorLabel.grid(row=3, column=0, sticky='w')
        self.authorCombobox.grid(row=3, column=1)
        self.authorInfo.grid(row=3, column=2, sticky='w')

        self.donorLabel.grid(row=4, column=0, sticky='w')
        self.donorCombobox.grid(row=4, column=1)
        self.donorInfo.grid(row=4, column=2, sticky='w')

        self.bookTypeLabel.grid(row=5, column=0, sticky='w')
        self.bookTypeCombobox.grid(row=5, column=1)
        self.typeInfo.grid(row=5, column=2, sticky='w')

        self.askBorrowerLabel.grid(row=0, column=0, sticky='w')
        self.askBorrowerEntry.grid(row=0, column=1)

        self.askDueDateLabel.grid(row=1, column=0, sticky='w')
        self.askDueDateEntry.grid(row=1, column=1)
        self.askBorrowerButton.grid(row=1, column=2)
        self.askBorrower.withdraw()
        self.infoSumWin.withdraw()
        #resultFrame
        self.resultTitleFrame.grid(row=0,column=0,sticky='w')
        self.selectPageButton.grid(row=0, column=0, sticky='w',ipadx=30)
        [self.resultFrames[n].grid(row=n+1, column=0, sticky='e')
         for n in range(len(self.resultFrames))]

        
        [self.resultId[n].grid(row=n+1, column=1, sticky='e', padx=10)
         for n in range(len(self.resultId))]
        [self.resultChecks[n].grid(row=n+1, column=0, sticky='e')
         for n in range(len(self.resultId))]
        #[self.resultChecks[n].config(state=DISABLED) for n in range(len(self.resultId))]
        # self.doneButton.grid(row=0,column=0,sticky='NW')

        # deleteOrBorrowWin
        # self.deleteButton.grid(row=0,column=0)
        # self.borrowButton.grid(row=1,column=0)
        # self.deleteOrBorrowWin.withdraw()

        self.pageWin.withdraw()

        
        self.pageLabel.grid(row=0, column=0)
        self.pageEntry.grid(row=0, column=1)
        self.pageButton.grid(row=0, column=2)

        #updateText
        self.updateText()

        # bindings
        self.searchEntry.bind('<Key>', self.updateSearch)

        self.askBorrower.bind('<Key>', self.askBorrowerShortcuts)

        def askBorrowerAutoCaps(i=None):
            if self.askBorrower.focus_get() == self.askDueDateEntry:
                self.autoCaps(self.askBorrowerEntry)
        self.askBorrower.bind('<Button-1>', askBorrowerAutoCaps)
        self.mainWin.bind('<Key>', self.onKeypress)
        self.mainWin.bind('<Button-1>', self.button1)
        self.mainWin.bind('<Button-3>', self.button2)
        #self.mainWin.bind('<Motion>',self.motion)
        self.addFrame.bind('<Key>', self.swapEntry)
        self.addFrame.bind('<Button-1>', self.addFrameOnClick)
        self.infoWin.bind('<<ComboboxSelected>>', self.infoDisplay)
        self.infoWin.bind('<Key>', self.comboboxKeypress)

        self.addSuggestWin.bind('<Key>', self.addSuggestKeypress)

        self.pageFrame.bind('<Enter>', self.openPageWin)
        self.pageWin.bind('<Enter>', self.openPageWin2)

        self.pageFrame.bind('<Leave>', self.closePageWin)
        self.pageWin.bind('<Leave>', self.closePageWin2)

        self.pageWin.bind('<Key>', self.pageEnter)

        def withdrawAddFrame(i=None):
            self.addFrame.withdraw()
            self.addSuggestWin.withdraw()
        self.addFrame.protocol("WM_DELETE_WINDOW", withdrawAddFrame)
        self.askBorrower.protocol(
            "WM_DELETE_WINDOW", self.askBorrower.withdraw)
        self.advancedSelectWin.protocol(
            "WM_DELETE_WINDOW", self.advancedSelectWin.withdraw)

        self.infoWin.protocol("WM_DELETE_WINDOW", self.infoWin.withdraw)
        self.mainWin.protocol("WM_DELETE_WINDOW", self.onClose)

        self.mainWin.bind('<<ComboboxSelected>>', self.cbSelect)
        self.mainWin.after(10, self.search)
        self.mainWin.after(20, self.updateInfoFrame)

        if self.curState!='temporary':self.mainWin.mainloop()
    
    def newDf(self, userInput=True, openAdd=False,atStartup=False):
        self.save()
        if userInput == False:
            self.df = pd.DataFrame(columns=['Title',
                 'Author',
                 'Type',
                 'Date Added',
                 'Available',
                 'Borrower',
                 'Borrow Date',
                 'Due Date',
                 'Times Borrowed',
                 'Donor'])

            return

        folder = filedialog.askdirectory(
            master=self.mainWin,
            title=f'Select a folder to save the {self.systemName} in',
            initialdir=sys.path[0],
        )
        newDfWin = Toplevel(master=self.mainWin)
        newDfEntry = Entry(master=newDfWin)
        
        def enterName(i=None, openAdd=openAdd):
            if i != None and i.char != '\r':
                return
            #self.confirmDataIntegrity(new=True)
            self.columns=self.df.columns
            [self.resultLabels[n].config(text=self.columns[n]) for n in range(len(self.resultLabels))]

            self.fileName = f'{folder}/{newDfEntry.get()}.csv'
            self.pref['fileName'] = self.fileName
            newDfWin.destroy()
            self.mainWin.title(f'{self.fileName.split("/")[-1]}')
            if openAdd == True:
                self.addFrame.deiconify()
            return

        newDfEnterButton = Button(
            master=newDfWin, text='Enter', command=enterName)
        newDfLabel = Label(
            master=newDfWin, text=f'What should this new {self.systemName} be called?')
        newDfLabel.grid(row=0, column=0)
        newDfEntry.grid(row=0, column=1)
        newDfEnterButton.grid(row=0, column=2)
        newDfWin.geometry(
            f'+{int(self.mainWin.winfo_screenwidth()/2)-200}+{int(self.mainWin.winfo_screenheight()/2)-50}')
        newDfWin.bind('<Key>', enterName)
        newDfEntry.focus_set()
        df = pd.DataFrame(columns=self.columns)
        self.df = df
        self.fileName = ''
        if atStartup==False:
            self.updateText()
            try:
                self.search(False, True, True)
            except:
                pass
        return df

    def forceUpdate(self):
        self.readDfFile(self.fileName)
        self.search(False,False,True)

    def updateText(self):
        try:
            self.textDf=pd.read_csv(self.fileName[:-4]+'-text.csv',index_col=0)

        except:
            try:self.textDf=pd.DataFrame({'id':['columns','itemName','systemName','action1','state1','action2','state2','columnDTypes','lastColumnAndItemRelation','secondColumnAndItemRelation','defaultColumnValues'],
                                      'text':[[f'{n}♣' for n in range(len(self.df.columns))],'item','catalog','action1','altered','action2','normal',str('♣').join(['str']*len(self.df.columns)),'relating to','relating to',str('♣').join(['-']*len(self.df.columns))]}).set_index('id')
            except:pass
            
            #self.textDf.to_csv(self.fileName[:-4]+'-text.csv')
        #self.numRowsVisible=range(0)
        #self.columns=self.df.columns
        try:self.itemName=self.textDf.loc['itemName'].values[0]
        except:self.textDf.loc['itemName']='item'
        
        self.calculateDefaults= lambda string: (string*len(self.columns))[:-1]
        self.calculateDefaultList = lambda i: [i]*len(self.columns)
        try:self.systemName=self.textDf.loc['systemName'].values[0]
        except:self.textDf.loc['systemName']='catalog'
        try:self.textDf.loc['columns'].values[0].split('♣')
        except:self.textDf.loc['columns']=str('♣').join(self.df.columns)
        try:self.action1=self.textDf.loc['action1'].values[0]
        except:
            self.textDf.loc['action1']='action1'
            self.action1='action1'
        try:self.state1=self.textDf.loc['state1'].values[0]
        except:
            self.textDf.loc['state1']='altered'
            self.state1='altered'
        try:self.state2=self.textDf.loc['state2'].values[0]
        except:
            self.textDf.loc['state2']='normal'
            self.state2='normal'
        try:self.action2=self.textDf.loc['action2'].values[0]
        except:
            self.textDf.loc['action2']='action2'
            self.action2='action2'
        
        try:self.columnDTypes=self.textDf.loc['columnDTypes'].values[0].split('♣')
        except:
            self.textDf.loc['columnDTypes']= self.calculateDefaults('str♣')
            self.columnDTypes= self.calculateDefaultList('str')
        try:
            self.columnDefaults=self.textDf.loc['defaultColumnValues'].values[0].split('♣')
        except:
            self.textDf.loc['defaultColumnValues']=self.calculateDefaults('Unknown♣')
            self.columnDefaults=self.calculateDefaultList('Unknown')

        if self.curState!= 'temporary':self.textDf.to_csv(self.fileName[:-4]+'-text.csv')
        
        

        self.addFrame.title(f'Add {self.itemName.capitalize()}')
       
        self.askBorrower.title(f'Enter {self.state1}er and {self.columns[-1]}')
        self.askBorrowerLabel.config(text=f'Who {self.state1} this {self.itemName}?')

        self.addSuccessLabel.config(text=f'Successfully added {self.itemName}!')
        self.bookLabel.config(text=f'List of {self.columns[0]}(s)')
        self.addTitleLabel.config(text=self.columns[0])
        self.bookUniqueNumLabel.config(text=f'Unique {self.itemName}(s)')
        self.bookNumLabel.config(text=f'Number of {self.itemName}(s)')  
        try:
            self.addAuthorLabel.config(text=self.columns[1])
            self.authorLabel.config(text=f'{self.columns[1]}(s)')
        except:
            self.addAuthorLabel.config(text='-')
            self.authorLabel.config(text='-')
        try:
            self.addDonorLabel.config(text=self.columns[-1])
            self.donorLabel.config(text=f'{self.columns[-1]}(s)')
        except:
            self.addDonorLabel.config(text='-')
            self.donorLabel.config(text='-')
        try:
            self.addTypeLabel.config(text=self.columns[2])
            self.bookTypeLabel.config(text=f'{self.columns[2]}(s)')
            self.defaultSearchString = f'Type to search by {self.columns[0]}, {self.columns[1]}, {self.columns[2]} etc.'

        except:
            self.addTypeLabel.config(text='-')
            self.bookTypeLabel.config(text='-')
            self.defaultSearchString = f'Type to search'

            self.addDonorLabel.config(text=self.columns[-1])
            self.askBorrowerLabel.config(text=f'Who {self.state1} this {self.itemName}?')


        self.replaceCombobox.set("")
        self.replaceCombobox["values"]=self.df.columns.to_list()


        self.bookTypeCombobox.set('')
        self.authorCombobox.set('')
        self.donorCombobox.set('')
        self.bookCombobox.set('')
        
        self.addButton.config(text=f'Add {self.itemName.capitalize()}')
        self.selected=set()
        try:
            _=f"What's this {self.itemName}'s {self.columns[-4]}?"
        except:
            _=f"Enter Information:"
        self.askDueDateLabel.config(text=_)
        
        self.selectBorrowButton.config(text=f'Set As {self.state1.capitalize()}')
        self.selectAvailableButton.config(text=f'Set As {self.state2.capitalize()}')
        
        self.deleteMenu.entryconfigure(1,label=f'Set As {self.state1.capitalize()}')
        self.deleteMenu.entryconfigure(2, label=f'Set As {self.state2.capitalize()}')

        '''[self.selectReplaceLabels[n].config(text=self.columns[n]) for n in range(len(self.df.columns))]'''
        self.updateInfoFrame()
        self.infoDisplay()
        self.updateNumSelected()
        
        self.searchEntry.delete(0,END)
        self.updateFavButton()
        
        for label in self.resultId:
            label.config(text='')
        widths=[]
        #widths=[round(self.df[col].astype(str).map(len).mean()+10) for col in self.df.columns]
        #[self.resultLabels[n].config(width=widths[n]) for n in range(len(self.resultLabels))]
        for row in self.resultEntries:
            for n in range(len(self.df.columns)):
                widths.append(round(self.df[self.df.columns[n]].astype(str).map(len).mean()+10))
                if widths[n]>40:widths[n]=40
                row[n].config(width=widths[n])
                row[n].delete(0,END)
        self.results=[]
        n=0
        while len(self.columns)<len(self.df.columns):
            self.columns.append(f'unnamed {n}')
        for n in range(len(self.df.columns)):
            if self.columns[n]!=self.df.columns[n]:
                self.df.rename({self.df.columns[n]:self.columns[n]},axis=1,inplace=True)
        
        [self.resultLabels[n].config(width=widths[n],text=f'{" "*(int(widths[n]/1.2)-len(self.columns[n]))}{self.columns[n]}') for n in range(len(self.df.columns))]
        
        
        #map the required number of result columns
        [self.unmapList(self.resultEntries[n]) for n in range(self.numResults)]
        self.unmapList(self.resultLabels)
        [self.mapList(self.resultEntries[n], n+1, 2, self.maxColumnRange[-1]-len(self.df.columns)+1)
         for n in range(len(self.resultEntries))]
        [self.resultLabels[n].grid(row=0, column=n+2) 
         for n in range(len(self.df.columns))]
        
        self.pageWin.withdraw()
        self.infoWin.withdraw()
        self.askBorrower.withdraw()
        self.addFrame.withdraw()
        self.advancedSelectWin.withdraw()

        self.button1(None)
        
        #for n in range(len(self.recentFileList)):
        self.openRecentMenu.delete(0,len(self.recentFileList))
        try:
            self.openRecentMenu.add_command(label=self.recentFileList[-1],command=lambda:self.openRecent(self.recentFilePathList[-1]))
            self.openRecentMenu.add_command(label=self.recentFileList[-2],command=lambda:self.openRecent(self.recentFilePathList[-2]))
            self.openRecentMenu.add_command(label=self.recentFileList[-3],command=lambda:self.openRecent(self.recentFilePathList[-3]))
            self.openRecentMenu.add_command(label=self.recentFileList[-4],command=lambda:self.openRecent(self.recentFilePathList[-4]))
        except:pass       
        

            
        return
    
    def testData(self,data):
        
        try:
            self.print_list(data=data,search=' ')
        except:
            return False
        else:
            if len(data.columns)>=1 and len(data.columns) in self.maxColumnRange:
                return True
        return False
    def readDfFile(self,path):
        self.df= pd.read_csv(path, index_col=0,parse_dates=self.findDateColumns(path))
        self.fileName=path
        self.columns=self.df.columns

    def openDf(self,atStartup=False,path=None,file=None):
        self.save()
        while path==None:
            file = filedialog.askopenfile(master=self.mainWin, title=f'Select a file', filetypes=(
                ('csv files', '*.csv'), ('All files', '*.*')))
            if file==None:
                return
            try:
                 pd.read_csv(file, index_col=0)
            except Exception as e:
                msg.showerror(
                    'Unable To Read File', f'Failed to read file because of:{e}\nPlease select a valid file.')
            else:
                path=file.name
            
        if atStartup==False:
            test=self.testData(pd.read_csv(path, index_col=0,parse_dates=self.findDateColumns(path)))
            if test==True:
                self.readDfFile(path)
                self.updateRecent(path)
                self.updateText()
                self.search(False, True, True)
            else:                
                msg.showerror('Unable to read file',f'Failed to read "{self.fileName}",\nreverting to "{self.fileName}"')
                self.updateText()
                self.search(False,True,True) 
        else:
            self.readDfFile(path)
        
        self.pref['fileName'] = self.fileName
        self.mainWin.title(f'{self.fileName.split("/")[-1]}')
        try:
            self.itemName=self.pref[f'itemName~{self.fileName}']
            self.systemName=self.pref[f'itemName~{self.systemName}']
        except:pass
        
    def updateRecent(self,path):
        displayName=path.split('/')[-1]
        
        if path in self.recentFilePathList:
            self.recentFileList.remove(displayName)
            self.recentFilePathList.remove(path)
        self.recentFileList.append(displayName)
        self.recentFileList= self.recentFileList[-5:]
        self.recentFilePathList.append(path)
        self.recentFilePathList= self.recentFilePathList[-5:]
        
        self.updateText()

    def openRecent(self,path):
         
         self.openDf(False,path)
        
        #except:
        #    pass
    def confirmDataIntegrity(self,new=False):
        '''self.dataIsUsable=False
        if self.df.shape[1]!=10 or new==True:
            dfCols=['Title',
                     'Author',
                     'Type',
                     'Date Added',
                     'Available',
                     'Borrower',
                     'Borrow Date',
                     'Due Date',
                     'Times Borrowed',
                     'Donor']
        else:self.dataIsUsable=True'''
        return
    def cbSelect(self, i):
        # self.result=self.df[self.df[self.columns[0]]==self.searchCombobox.get()]
        # self.result=self.df[self.results[self.searchCombobox['values'].index(self.searchCombobox.get())]:self.results[self.searchCombobox['values'].index(self.searchCombobox.get())]]
        return
   # def motion(self,i):
   #     return
   #     if self.infoFrame.winfo_ismapped():self.updateInfoSum(i)
    #def updateInfoSum(self,i):
    #    for row in range(len(self.resultEntries)):
    #        break
        return
    def updateInfoFrame(self):
        try:
            self.bookNumEntry.config(state='normal')
            self.bookUniqueEntry.config(state='normal')
    
            self.bookNumEntry.delete(0, END)
            self.bookUniqueEntry.delete(0, END)
    
            self.bookNumEntry.insert(0, str(len(self.df)))
            self.bookUniqueEntry.insert(0, str(len(self.df[self.columns[0]].unique())))
    
            self.bookNumEntry.config(state='readonly')
            self.bookUniqueEntry.config(state='readonly')
    
            self.bookTypeCombobox['values'] = sorted(
                list(self.df[self.columns[2]].unique()))
            self.integratedComboboxes[self.bookTypeCombobox]= sorted(
                list(self.df[self.columns[2]].unique()))

            self.authorCombobox['values'] = sorted(
                list(self.df[self.columns[1]].unique()))
            self.integratedComboboxes[self.authorCombobox] = sorted(
                list(self.df[self.columns[1]].unique()))
            self.donorCombobox['values'] = sorted(list(self.df[self.columns[-1]].unique()))
            self.integratedComboboxes[self.donorCombobox] = sorted(list(self.df[self.columns[-1]].unique()))
            self.bookCombobox['values'] = sorted(list(self.df[self.columns[0]].unique()))
            self.integratedComboboxes[self.bookCombobox]=sorted(list(self.df[self.columns[0]].unique()))
        except Exception as e:print(e)
        
    def setFav(self): #saves file paths for easier access
        if self.fileName in self.favList:
            self.favList.remove(self.fileName)
            self.updateFavButton(-1)
        else:
            self.favList.append(self.fileName)
            
            self.updateFavButton(1)
        return
    def updateFavButton(self,change=0):
        if self.fileName in self.favList:
            self.favButton.config(text='✅',state='normal')
        else:            
            self.favButton.config(text='⭐',state='normal')
            if len(self.favList)>7:
                self.favButton.config(state='disabled')
            
        self.favMenu.delete(0,len(self.favList)-change)
        
        try:
            self.favMenu.add_command(label=self.favList[-1].split('/')[-1],command=lambda: self.openDf(False,self.favList[-1]))
            self.favMenu.add_command(label=self.favList[-2].split('/')[-1],command=lambda: self.openDf(False,self.favList[-2]))
            self.favMenu.add_command(label=self.favList[-3].split('/')[-1],command=lambda: self.openDf(False,self.favList[-3]))
            self.favMenu.add_command(label=self.favList[-4].split('/')[-1],command=lambda: self.openDf(False,self.favList[-4]))
            self.favMenu.add_command(label=self.favList[-5].split('/')[-1],command=lambda: self.openDf(False,self.favList[-5]))
            self.favMenu.add_command(label=self.favList[-6].split('/')[-1],command=lambda: self.openDf(False,self.favList[-6]))
            self.favMenu.add_command(label=self.favList[-7].split('/')[-1],command=lambda: self.openDf(False,self.favList[-7]))
        except:pass
    def updateNumSelected(self):
        self.selectNumSelected.config(
            text=f'{len(self.selected)} {self.itemName.capitalize()}(s) Selected')
        if len(self.selected) > 0 and not self.selectFrame.winfo_ismapped():
            self.selectFrame.grid()
            self.replaceButton.config(state='normal')
        elif len(self.selected) < 1:
            self.selectFrame.grid_remove()
            self.replaceButton.config(state='disabled')

    def activateSelect(self):
        '''if self.selectionsOpen==False:
            [self.resultChecks[n].config(state=NORMAL) for n in range(len(self.resultId))]        
            self.selectionsOpen=True
            self.updateNumSelected()
            self.selectFrame.grid()
            self.selectPageButton.config(state='normal')
            #self.selectButton.config(text='Deselect')
        else:'''
        for n in range(len(self.resultChecks)):
            if self.resultCheckVars[n].get() == 0:
                continue
            self.resultCheckVars[n].set(0)
        # self.selectButton.config(text='Select')
        # self.selectionsOpen=False
        self.pageSelected.set(0)
        self.selectFrame.grid_remove()
        self.selected = set()

    def onSelect(self):
        focus = self.mainWin.focus_get()
        if type(focus) == Checkbutton:
            index = self.resultChecks.index(focus)
            if self.resultCheckVars[index].get() == 1:
                self.selected.add(int(self.resultId[index]['text']))
            else:
                self.selected.remove(int(self.resultId[index]['text']))
            self.updateNumSelected()
            if set(self.results[self.page]).union(self.selected) == self.selected:
                self.pageSelected.set(1)
            else:
                self.pageSelected.set(0)

    def onSelectPage(self):
        if self.pageSelected.get() == 1:
            self.selected = self.selected.union(set(self.results[self.page]))
        else:
            self.selected = self.selected.difference(
                set(self.results[self.page]))
        self.search(False, False, False)
        self.updateNumSelected()

    def onDeleteSelected(self):
        if len(self.selected) < 1:
            info = msg.showinfo(master=self.mainWin, title='Cannot Perform Deletion',
                                message=f'Cannot perform the requested action as no {self.itemName}(s) have been selected.\nPlease select a {self.itemName} and try again.')
            return
        confirm = msg.askyesno(master=self.mainWin, title='Confirm Deletion',
                               message=f'Are you sure you want to permanently delete {len(self.selected)} {self.itemName}(s)? This cannot be undone.')
        
        if confirm:
            #self.update()
            for index in self.selected:
                self.df.drop(int(index), inplace=True)
                self.selected = set()
                self.updateNumSelected()
                self.search(False, False, True)

    def onSelectedBorrow(self):
        self.borrowedList = list(self.selected)
        self.onBorrowed()
        pass

    def onSelectedAvailable(self):
        self.borrowedList = list(self.selected)
        self.onAvailable()

    def openReplace(self):
        self.advancedSelectWin.geometry('+850+80')
        self.advancedSelectWin.deiconify()
    '''def selectReplace(self):
        #self.update()
        replaceValue = self.selectReplaceWordEntry.get()
        replaced = set()
        for index in self.selected:
            for n in range(len(self.selectReplaceEntries)):
                text, col = self.selectReplaceEntries[n].get(
                ), self.df.columns[n]
                if len(text) < 1 or replaceValue not in str(self.df.loc[index, col]).lower():
                    continue
                if self.columnDTypes[n]=='date':
                    try:
                        text = pd.to_datetime(text)
                    except:
                        text = float('nan')
                elif self.columnDTypes[n]=='int':
                    try:
                        text = float(text)
                    except:
                        text = float('nan')
                elif self.columnDTypes[n]=='bool':
                    text = text.lower().strip()
                    if text in ('yes', 'y', 'ye', '1', 't', 'true', 'es', 'ys'):
                        text = 'yes'
                    elif text in ('no', 'n', 'o', 'false', 'f', 'on', '0'):
                        text = 'no'
                    else:
                        text = float('nan')

                if not self.selectReplaceEntire.get() and len(replaceValue) > 0:

                    newText = self.df.loc[index, col]
                    while replaceValue in newText.lower():
                        loc1, loc2 = newText.lower().find(replaceValue), newText.lower().find(
                            replaceValue)+len(replaceValue)
                        newText = f'{newText[:loc1]}{text}{newText[loc2:]}'
                else:
                    newText = text
                replaced.add(self.df.loc[index, self.columns[0]])
                self.df.loc[index, col] = newText
        self.delList(self.selectReplaceEntries)
        if len(replaced) < 1:
            info = msg.showinfo(master=self.advancedSelectWin, title='Failed to Replace Values',
                                message=f'Failed to replace the entered values into any {self.itemName}(s). No {self.itemName}(s) met your set criteria.')
        else:
            self.search(False, False, False)
            info = msg.showinfo(master=self.advancedSelectWin, title='Successfully Replaced Values',
                                message=f'Success!\nValues in these {self.itemName}(s) have been replaced:\n{str(", ").join(replaced)}')
        self.advancedSelectWin.deiconify()'''

    def onSelectAll(self):
        self.selected = set(self.df.index)
        self.search(False, False, False)
        self.updateNumSelected()
        info = msg.showinfo(master=self.mainWin, title=f'Selected All {self.itemName.capitalize()}(s))',
                            message=f"Careful! You've selected every {self.itemName} in the whole {self.systemName}")
        
    def replaceColumnValues(self):
        column=self.replaceCombobox.get()
        n=self.replaceCombobox['values'].index(column)
        entry=self.replaceEntry.get()
        dataType = self.columnDTypes[n]
        if dataType == 'int':
            try:entry = eval(entry)
            except:pass
        elif dataType == 'date':
            try:
                entry = pd.to_datetime(entry)
            except:
                entry = pd.to_datetime('NaT')
        
        self.df.loc[list(self.selected),column]=entry
        self.search(False,False,True)
        
    def search(self, update=True, resetPage=True, performSearch=True):
        # get results
        if performSearch == True:
            self.results = []
            query = self.searchEntry.get()
            if query == self.defaultSearchString and self.searchEntry.focus_get() != True:
                query = ''
            if query != '':

                _ = self.print_list(query, True, numValues=len(self.df))
                _.reverse()
            else:
                _ = self.df.sort_values(self.columns[0]).index
            for n in range(0, len(_), self.numResults):
                self.results.append(_[n:n+self.numResults])
        #go to first page
        if resetPage == True:
            self.swapPage(0,False)
        # enter prev data
        if update == True:
            #self.update()
            self.updateInfoFrame()
            self.save()


        if len(self.results) <= 1:
            self.resultForwardButton.config(state=DISABLED)
        else:
            self.resultForwardButton.config(state=NORMAL)
        self.resultPageLabel['text'] = f'Page {self.page+1} of {len(self.results)}'


        try:
            if len(self.results[self.page]) < len(self.numRowsVisible):
                for row in range(len(self.results[self.page]), len(self.resultId)):
                    self.resultFrames[row].grid_remove()
            elif len(self.results[self.page]) > len(self.numRowsVisible):
                for row in self.numRowsVisible:
                    self.resultFrames[row].grid_remove()
                for row in range(len(self.results[self.page])-1, -1, -1):
                    self.resultFrames[row].grid()
                # self.unmapList(self.resultId)
                #[self.unmapList(l) for l in self.resultEntries]
                # self.unmapList(self.resultChecks)

            for l in self.resultEntries:
                for entry in l:
                    entry.delete(0, END)
            # self.result=self.df[self.results[self.searchCombobox.current()]:self.results[self.searchCombobox.current()]+1]

            # self.mainFrame.grid_remove()
            # update results
            for row in range(len(self.results[self.page])):
                for n in range(len(self.df.columns)):
                    self.resultEntries[row][n].insert(
                        0, self.df.loc[self.results[self.page][row], self.df.columns[n]])
                if self.results[self.page][row] in self.selected:
                    self.resultCheckVars[row].set(1)
                else:
                    self.resultCheckVars[row].set(0)
                self.resultId[row].config(text=self.results[self.page][row])
        except:
            self.resultFrame.grid_remove()
            self.noResultFrame.grid()
            self.numRowsVisible = range(0)
        else:
            self.numRowsVisible = range(len(self.results[self.page]))
            if set(self.results[self.page]).union(self.selected) == self.selected:
                self.pageSelected.set(1)
            else:
                self.pageSelected.set(0)
            self.resultFrame.grid()
            self.noResultFrame.grid_remove()
        return

    def confirmAdd(self,data=None):
        if data==None:
            c1 = self.addTitle.get()
            c2 = self.addAuthor.get()
            c3 = self.addType.get()
            cEnd = self.addDonor.get()
        elif len(data)==4:
            c1,c2,c3,cEnd=[str(i) for i in data]
        else:
            return
        index = self.df.index.max()+1

        if math.isnan(index):
            index = 0
        
        #entries = [self.columns[0]: title, self.columns[1]: auth, self.columns[2]: Type, self.columns[3]: pd.to_datetime(
        #    'today'), self.columns[4]: 'yes', self.columns[5]: '', self.columns[6]: '', self.columns[7]: '', self.columns[8]: 0, cEnd]
        entry=pd.DataFrame(index=[index])
        for n in range(len(self.columns)):
            if n<3:_=[c1,c2,c3][n]
            elif n==len(self.columns)-1:
                _=cEnd
            else:_=''
            if len(_)<=0:
                _=self.columnDefaults[n]
            if self.columnDTypes[n]=='int':
                try:_=eval(_)
                except:_=float('nan')
            elif 'date' in self.columnDTypes[n]:
                try:
                    _=pd.to_datetime(_)
                except:
                    _=pd.to_datetime('NaT')

            entry[self.columns[n]]=_

        self.df = pd.concat([self.df,entry])
        self.save()

        self.addSuccessLabel.grid()
        self.mainWin.after(1500, self.addSuccessLabel.grid_remove)
        self.addTitle.delete(0, END)
        self.addAuthor.delete(0, END)
        self.addType.delete(0, END)
        self.addDonor.delete(0, END)
        self.search(True, False, True)

    def autoCaps(self, entry):
        text = entry.get()
        mode = self.addAutoCapsCombobox.get()
        if mode == 'Never':
            return
        if mode == 'Only Lowercase Text' and not re.search('[A-Z]', text):
            entry.delete(0, END)
            entry.insert(0, str(' ').join(
                [word.capitalize() for word in text.split()]))
        elif mode == 'Always':
            entry.delete(0, END)
            entry.insert(0, str(' ').join(
                [word.capitalize() for word in text.split()]))

    def b1SuggestionPlace(self):
        self.focus.delete(0, END)
        self.focus.insert(END, self.addSuggestB1['text'])

    def b2SuggestionPlace(self):
        self.focus.delete(0, END)
        self.focus.insert(END, self.addSuggestB2['text'])
        pass

    def b3SuggestionPlace(self):
        self.focus.delete(0, END)
        self.focus.insert(END, self.addSuggestB3['text'])
        pass

    def addFrameOnClick(self, i):
        try:
            if type(self.focus) == Entry:
                self.autoCaps(self.focus)
        except:
            pass
        x, y = self.addFrame.winfo_pointerxy()
        if self.addFrame.winfo_rootx() <= x <= self.addFrame.winfo_rootx()+510 and self.addFrame.winfo_rooty()+20 <= y <= self.addFrame.winfo_rooty()+40:
            self.addSuggest()
            return
        self.addSuggestWin.withdraw()

    def addSuggest(self, i=None):
        self.focus = self.addFrame.focus_get()
        if type(self.focus) == Entry:
            entry, sortedDf = self.focus.get(), self.df.sort_values(
                self.columns[0], ascending=True).copy()[-50:]

            # Make suggestions
            if len(entry) == 0:

                if self.focus == self.addTitle:
                    s1 = max(sortedDf[self.columns[0]].to_list(),
                             key=sortedDf[self.columns[0]].to_list().count)
                    s2 = self.df[self.df[self.columns[0]] !=
                                 s1].loc[self.df[self.df[self.columns[0]] != s1].index.max(), self.columns[0]]
                    s3 = max(sortedDf[(sortedDf[self.columns[0]] != s1) & (sortedDf[self.columns[0]] != s2)][self.columns[0]].to_list(
                    )[-15:], key=sortedDf[self.columns[0]].iloc[-15:].to_list().count)
                    self.addSuggestB1.config(text=s1)
                    self.addSuggestB2.config(text=s2)
                    self.addSuggestB3.config(text=s3)
                elif self.focus == self.addAuthor and len(self.df.columns)>1:
                    _ = self.df[self.df[self.columns[0]] == self.addTitle.get()]
                    s1 = max(sortedDf[self.columns[1]].to_list(),
                             key=sortedDf[self.columns[1]].to_list().count)
                    s2 = self.df[self.df[self.columns[1]] !=
                                 s1].loc[self.df[self.df[self.columns[1]] != s1].index.max(), self.columns[1]]
                    s3 = max(sortedDf[(sortedDf[self.columns[1]] != s1) & (sortedDf[self.columns[1]] != s2)][self.columns[1]].to_list(
                    ), key=sortedDf[self.columns[1]].to_list()[-15:].count)
                    if len(_) > 0:
                        self.addSuggestB1.config(
                            text=_.loc[_.index[0], self.columns[1]])
                        self.addSuggestB2.config(text=s1)
                        self.addSuggestB3.config(text=s2)
                    else:
                        self.addSuggestB1.config(text=s1)
                        self.addSuggestB2.config(text=s2)
                        self.addSuggestB3.config(text=s3)
                elif self.focus == self.addType and len(self.df.columns) > 2:
                    _ = self.df[self.df[self.columns[1]] == self.addAuthor.get()]
                    s1 = max(sortedDf[self.columns[2]].to_list(),
                             key=sortedDf[self.columns[-1]].to_list().count)
                    s2 = self.df[self.df[self.columns[2]] !=
                                 s1].loc[self.df[self.df[self.columns[2]] != s1].index.max(), self.columns[2]]
                    s3 = max(sortedDf[(sortedDf[self.columns[2]] != s1) & (sortedDf[self.columns[2]] != s2)][self.columns[2]].to_list(
                    )[-15:], key=sortedDf[self.columns[2]].to_list()[-15:].count)
                    if len(_) > 0:
                        self.addSuggestB1.config(
                            text=_.loc[_.index[0], self.columns[2]])
                        self.addSuggestB2.config(text=s1)
                        self.addSuggestB3.config(text=s2)
                    else:
                        self.addSuggestB1.config(text=s1)
                        self.addSuggestB2.config(text=s2)
                        self.addSuggestB3.config(text=s3)
                elif self.focus == self.addDonor and len(self.df.columns) > 3:
                    s1 = max(sortedDf[self.columns[-1]].to_list(),
                             key=sortedDf[self.columns[-1]].to_list().count)
                    s2 = self.df.loc[self.df.index.max(), self.columns[-1]]
                    s3 = max(sortedDf[(sortedDf[self.columns[-1]] != s1) & (sortedDf[self.columns[-1]] != s2)][self.columns[-1]].to_list(
                    )[-15:], key=sortedDf[self.columns[-1]].to_list()[-15:].count)
                    self.addSuggestB1.config(text=s1)
                    self.addSuggestB2.config(text=s2)
                    self.addSuggestB3.config(text=s3)
            else:
                if self.focus == self.addTitle:
                    col = self.columns[0]
                elif self.focus == self.addAuthor:
                    col = self.columns[1]
                elif self.focus == self.addType:
                    col = self.columns[2]
                else:
                    col = self.columns[-1]
                results = self.print_list(
                    str(entry), False, 3, list(self.df[col].unique()), True)
                results.reverse()
                if results == ["No good matches for '{}', try a different word or phrase.".format([entry.lower()])]:
                    self.addSuggestWin.withdraw()
                    return
                remove = []
                for n in range(1, len(results)):
                    # try:
                    if results[n] == results[n-1]:
                        remove.append(n)
                    # except:pass
                if 2 not in remove and 1 in remove:
                    results[1] = results[2]
                    remove = [2]
                for n in remove:
                    results[n] = ''

                try:
                    self.addSuggestB1.config(text=results[0])
                except:
                    pass
                try:
                    self.addSuggestB2.config(text=results[1])
                except:
                    self.addSuggestB2.config(text='')
                try:
                    self.addSuggestB3.config(text=results[2])
                except:
                    self.addSuggestB3.config(text='')

            def animateSuggestWin():
                finalX, finalY = self.focus.winfo_pointerx()-self.addSuggestB1.winfo_width() - \
                    int(self.addSuggestB2.winfo_width() /
                        2), self.focus.winfo_y()+self.addFrame.winfo_y()+55
                global curX, curY
                curX, curY = self.addSuggestWin.winfo_rootx(), self.addSuggestWin.winfo_rooty()
                numFrames = 10
                distX, distY = int(
                    (finalX-curX)/numFrames), int((finalY-curY)/numFrames)

                def frame():
                    global curX, curY
                    # if curX!=finalX or curY!=finalY:
                    self.addSuggestWin.geometry(f'+{curX+distX}+{curY+distY}')
                    curX, curY = self.addSuggestWin.winfo_rootx(), self.addSuggestWin.winfo_rooty()

                self.addSuggestWin.after(numFrames, frame)
                self.addSuggestWin.after(numFrames*2, frame)
                self.addSuggestWin.after(numFrames*3, frame)
                self.addSuggestWin.after(numFrames*4, frame)
                self.addSuggestWin.after(numFrames*5, frame)
                self.addSuggestWin.after(numFrames*6, frame)
                self.addSuggestWin.after(numFrames*7, frame)
                self.addSuggestWin.after(numFrames*8, frame)
                self.addSuggestWin.after(numFrames*9, frame)
                self.addSuggestWin.after(numFrames*10, frame)
                self.addSuggestWin.after(
                    110, lambda: self.addSuggestWin.geometry(f'+{finalX}+{finalY}'))
            _ = False
            if self.addSuggestWin.winfo_ismapped():
                self.mainWin.after(10, animateSuggestWin)
                _ = True
            if self.addSuggestB1['text'] != '' and self.addSuggestB2['text'] != '' and self.addSuggestB3['text'] != '':
                self.addSuggestWin.deiconify()
                if _ == False:
                    self.addSuggestWin.geometry(
                        f'+{self.focus.winfo_pointerx()-self.addSuggestB1.winfo_width()-int(self.addSuggestB2.winfo_width()/2)}+{self.focus.winfo_y()+self.addFrame.winfo_y()+55}')
            self.focus.focus_set()
        else:
            self.addSuggestWin.withdraw()

    def lockEntry(self, entry, intvar):
        if intvar.get() == 1:
            entry.config(state=DISABLED)
        else:
            entry.config(state=NORMAL)

    def addSuggestKeypress(self, i):
        # self.addSuggestWin.withdraw()
        self.focus.focus_set()
        # if i.keysym=='BackSpace':
        #    try:self.focus.delete(len(self.focus.get())-1,END)
        #   except:pass
        # else:self.focus.insert(END,i.char)
        # self.addSuggestWin.deiconify()

    def swapEntry(self, i):
        focus = self.addFrame.focus_get()

        if i.state in (12, 4) and i.keysym not in ('c', 'v', 'a'):
            if type(focus) == Entry:
                try:
                    sel = focus.selection_get()
                    text = focus.get()
                except:
                    try:
                        focus.insert(0, self.addHotkeys[str(i.keysym)])
                    except:
                        pass
                else:
                    if len(text) > 0 and focus.select_present():
                        self.addHotkeys[str(i.keysym)] = sel
                    else:
                        try:
                            focus.insert(END, self.addHotkeys[str(i.keysym)])
                        except:
                            pass
            return
        if i.char == '\r':
            Type = self.addType.get()
            auth = self.addAuthor.get()
            title = self.addTitle.get()
            donor = self.addDonor.get()
            self.autoCaps(focus)
            if len(title) > 0:
                self.addAuthor.focus_set()
                if len(auth) > 0:
                    self.addType.focus_set()
                    if len(Type) > 0:
                        self.addDonor.focus_set()
                        if len(donor) > 0:

                            self.confirmAdd()
                            self.addTitle.focus_set()
        elif i.keysym == 'Escape':
            self.addSuggestWin.withdraw()
            return
        self.mainWin.after(1, self.addSuggest)

    def infoDisplay(self, i=None):
        auth = self.authorCombobox.get()
        donor = self.donorCombobox.get()
        Type = self.bookTypeCombobox.get()
        book = self.bookCombobox.get()
        if len(auth) > 0:
            if self.columnDTypes[1]=='int':auth=float(auth)
            self.authorInfo.config(
                text=f'{len(self.df[self.df[self.columns[1]]==auth])} {self.itemName}(s) {self.textDf.loc["secondColumnAndItemRelation"].values[0]} {auth} exist in this {self.systemName}.')
        else:self.authorInfo.config(text='')
        if len(donor) > 0:
            if self.columnDTypes[-1]=='int':donor=float(donor)
            self.donorInfo.config(
                text=f'{len(self.df[self.df[self.columns[-1]]==donor])} {self.itemName}(s) {self.textDf.loc["lastColumnAndItemRelation"].values[0]} {donor} exist in this {self.systemName}.')
        else:self.donorInfo.config(text='')
        if len(Type) > 0:
            if self.columnDTypes[2]=='int':Type=float(Type)

            self.typeInfo.config(
                text=f'{len(self.df[self.df[self.columns[2]]==Type])} {self.itemName}(s) of {Type} exist in this {self.systemName}.')
        else:self.typeInfo.config(text='')
        if len(book) > 0:
            if self.columnDTypes[0]=='int':book=float(book)

            self.bookInfo.config(
                text=f'{len(self.df[self.df[self.columns[0]]==book])} copy(s) of {book} exist in this {self.systemName}.')
        else:self.bookInfo.config(text='')
    def onBorrowed(self, useMouseLoc=False):

        interfere = False
        index = self.borrowedList[0]
        self.df.loc[index, self.columns[6]] = pd.to_datetime('today')
        self.df.loc[index, self.columns[4]] = 'no'

        timesBorrowed = float(self.df.loc[index, self.columns[8]])+1
        self.df.loc[index, self.columns[8]] = timesBorrowed

        self.askBorrowerLabel.config(
            text=f'Who {self.state1} {self.df.loc[index,self.columns[0]][:20]}?')

        try:
            row = self.resultEntries[self.results[self.page].index(
                self.borrowedList[0])]
        except:
            if useMouseLoc == False:
                interfere = True
        if interfere == True:
            self.askBorrower.geometry(
                f'+{self.mainWin.winfo_pointerx()-200}+{self.mainWin.winfo_pointery()-50}')

        elif useMouseLoc == True:
            self.askBorrower.geometry(
                f'+{self.mainWin.winfo_pointerx()}+{self.mainWin.winfo_pointery()}')
        else:
            self.askBorrower.geometry(
                f'+{row[0].winfo_rootx()}+{row[0].winfo_rooty()}')
            self.search(False, False, False)
        self.askBorrower.deiconify()
        self.askBorrowerEntry.focus_set()

    def onAvailable(self):
        #self.update()
        for item in self.borrowedList:
            self.df.loc[item, self.columns[4]] = 'yes'
            for col in self.df.columns[5:8]:
                self.df.loc[item, col] = float('nan')
            self.search(False, False, False)
            continue
        self.borrowedList = []

    def borrowerEntered(self):
        index = self.borrowedList[0]
        self.df.loc[index, self.columns[5]] = self.askBorrowerEntry.get()
        date = self.askDueDateEntry.get()
        try:
            date = pd.to_datetime(date)
        except:
            pass
        self.df.loc[index, self.columns[7]] = date

        self.askBorrowerEntry.delete(0, END)
        self.askDueDateEntry.delete(0, END)
        self.askBorrower.withdraw()
        self.search(False, False, False)

        self.borrowedList.pop(0)
        if len(self.borrowedList) > 0:
            self.onBorrowed()

    def askBorrowerShortcuts(self, i):
        if i.char == '\r':
            if len(self.askDueDateEntry.get()) > 0:
                self.borrowerEntered()
            elif len(self.askBorrowerEntry.get()) > 0:
                self.autoCaps(self.askBorrowerEntry)
                self.askDueDateEntry.focus_set()

    def delete(self, entryLoc=None):
        if entryLoc != None:
            index = self.resultId[entryLoc]['text']
        else:
            index = self.getFocusedItem()
            if index == None:
                return
        confirmation = msg.askyesno(master=self.mainWin, title=f'Confirm {self.itemName} deletion',
                                    message=f'Are you sure you want to permanently delete {self.df.loc[index,self.columns[0]]} {self.textDf.loc["secondColumnAndItemRelation"].values[0]} {self.df.loc[index,self.columns[1]]} from the {self.systemName}?')
        if confirmation == True:
            self.df.drop(index, inplace=True)
            self.search(False, False, True)
            if index in self.selected:
                self.selected.remove(index)
            self.updateNumSelected()

    def onKeypress(self, i):
        try:
            entry = self.mainWin.focus_get()
            entryLoc = [
                entry in lst for lst in self.resultEntries].index(True)
        except:
            entryLoc=None
        else:
            row=self.resultEntries[entryLoc]
            
            for n in range(len(self.df.columns)):
                entry = row[n].get()
                
                if len(entry) <= 0:
                    continue
                if self.columnDTypes[n] == 'int':
                    try:entry = eval(entry)
                    except:pass
                elif self.columnDTypes[n] == 'date':
                    try:
                        entry = pd.to_datetime(entry)
                    except:
                        entry = pd.to_datetime('NaT')
                self.df.loc[int(self.resultId[entryLoc]['text']),
                            self.df.columns[n]] = entry
               # print(self.resultId[entryLoc]['text'])
            if i.state in (12, 4):
                if i.keysym in ('r', 'b'):
    
                    entry = self.mainWin.focus_get()

                    if i.keysym == 'b':
                        self.borrowedList = [
                            int(self.resultId[entryLoc]['text'])]
                        available = row[4].get()
                        if available in (True, 'True', 1, '1', 'yes', 'Yes'):
                            self.onBorrowed(True)
                        else:
                            self.onAvailable()
                    else:
                        self.delete()
                    

                elif i.keysym == 'slash':
                    self.searchEntry.focus_set()
                    self.button1(None)
        if entryLoc==None and i.state in (12, 4) and i.keysym in ('r','b'):
            if i.keysym == 'b':
                _ = f'that has been {self.state1}'
            else:
                _ = 'that you want to remove'
            msg.showinfo(master=self.mainWin, title='Select an entry',
                         message=f'Please select an entry relevant to the {self.itemName} {_}')
        return
    def comboboxKeypress(self,i=None):
        for index in range(len(self.integratedComboboxes)):
            combobox=list(self.integratedComboboxes.keys())[index]
            if not combobox.winfo_ismapped(): 
                continue
            values=list(self.integratedComboboxes.values())[index]
            entry=combobox.get()
            values=self.print_list(data=values,search=entry,override=True)
            combobox['values']=values
        return

    def button1(self, i):
        if len(self.searchEntry.get()) < 1 and self.searchEntry.focus_get() != self.searchEntry:
            self.searchEntry.insert(0, self.defaultSearchString)
            self.searchEntry.config(foreground='grey')
        elif self.searchEntry.get() == self.defaultSearchString and self.searchEntry.focus_get() == self.searchEntry:
            self.searchEntry.delete(0, END)
            self.searchEntry.config(foreground='black')

    def getFocusedItem(self):
        focus = self.mainWin.focus_get()
        if type(focus) == Entry:
            try:
                entryLoc = [
                    focus in lst for lst in self.resultEntries].index(True)
            except:
                pass
            else:
                return int(self.resultId[entryLoc]['text'])

    def button2(self, i):
        index = self.getFocusedItem()
        if index != None:
            self.deleteMenu.post(self.mainWin.winfo_pointerx(),
                                 self.mainWin.winfo_pointery())

    def updateSearch(self, i):
        def _():
            query = self.searchEntry.get()

            def checkQuery():
                if query == self.searchEntry.get() and self.query != query:
                    self.search()
                    self.query = query
            self.mainWin.after(300, checkQuery)
        self.mainWin.after(1, _)
        # self.result=self.df[self.results[self.searchCombobox['values'].index(self.searchCombobox.get())]:self.results[self.searchCombobox['values'].index(self.searchCombobox.get())]+1]

    def update(self):
        '''for row in range(len(self.results[self.page])):
            for n in range(len(self.df.columns)):
                entry = self.resultEntries[row][n].get()
                if len(entry) <= 0:
                    continue
                if self.columnDTypes[n] == 'int':
                    entry = float(entry)
                elif self.columnDTypes[n] == 'date':
                    try:
                        entry = pd.to_datetime(entry)
                    except:
                        entry = pd.to_datetime('NaT')
                self.df.loc[int(self.resultId[row]['text']),
                            self.df.columns[n]] = entry'''
        return

    def tutorial(self):
        if self.curState=='fileNotFound':
            
            t1 = msg.showwarning(master=self.mainWin, title='Error',
                              message='Could not locate data file')
        else:
            t1 = msg.showinfo(master=self.mainWin, title='One Catalogue. Infinite Possibilities',
                              message=f'Just go through one small step to get started!')
        if t1 == 'ok':
            t2=msg.askyesno(master=self.mainWin,title=f'Choose File',message='Would you like to start with an empty {self.systemName}?\n(Press "No" if you have a data file)')
            
            if t2==True:
                self.newDf(True,True,True)
            else:
                self.openDf(atStartup=True)

    def pageForward(self):
        #self.update()
        self.page += 1
        self.search(False, False, False)
        if len(self.results) <= self.page+1:
            self.resultForwardButton.config(state=DISABLED)
        if self.page > 0:
            self.resultBackButton.config(state=NORMAL)

        return

    def pageBack(self):
        #self.update()
        self.page -= 1
        self.search(False, False, False)
        if self.page <= 0:
            self.resultBackButton.config(state=DISABLED)
        if len(self.results) > self.page+1:
            self.resultForwardButton.config(state=NORMAL)

    def swapPage(self, page=None,updateDisplay=True):
        #if updateDisplay==True:
            #try:self.update()
            #except:pass
        try:
            if page == None:
                page = int(self.pageEntry.get())-1
            if 0 <= page <= len(self.results)-1:
                self.page = page
                # self.pageEntry.config(foreground='black')
                self.pageEntry.delete(0, END)

            else:
                # self.pageEntry.config(foreground='red')
                return

        except:
           # self.pageEntry.config(foreground='red')
            return
        if updateDisplay==True: self.search(False, False, False)
        if self.page <= 0:
            self.resultBackButton.config(state=DISABLED)
        else:
            self.resultBackButton.config(state=NORMAL)
        if len(self.results) > self.page+1:
            self.resultForwardButton.config(state=NORMAL)
        else:
            self.resultForwardButton.config(state=DISABLED)
        self.mainWin.after(60, self.pageWinDeiconify)
        

    def openPageWin2(self, i):
        self.cursorInPageWin = True
        self.pageWinDeiconify()

    def openPageWin(self, i):
        self.cursorInPageFrame = True
        self.pageWinDeiconify()

    def pageWinDeiconify(self):
        self.pageWin.geometry(f'+{self.pageFrame.winfo_rootx()}+{self.pageFrame.winfo_rooty()+55}')

        if len(self.results)>0 and self.cursorInPageFrame == True or self.cursorInPageWin == True:
            self.mainWin.deiconify()
            self.pageWin.deiconify()
            self.pageEntry.focus_set()
        else:
            self.pageWin.withdraw()

    def closePageWin(self, i):
        self.cursorInPageFrame = False
        self.pageWinDeiconify()

    def closePageWin2(self, i):

        self.cursorInPageWin = False
        self.pageWinDeiconify()

    def pageEnter(self, i):
        if i.keysym in ['Enter', 'Return']:
            self.swapPage()
        entry = self.pageEntry.get()

        def animate():
            self.pageWin.geometry(f'+{self.pageFrame.winfo_rootx()}+{self.pageFrame.winfo_rooty()+55}')
            self.mainWin.after(50, lambda: self.pageWin.geometry(
                f'+{self.pageFrame.winfo_rootx()+2}+{self.pageFrame.winfo_rooty()+53}'))
            self.mainWin.after(90, lambda: self.pageWin.geometry(
                f'+{self.pageFrame.winfo_rootx()-2}+{self.pageFrame.winfo_rooty()+55}'))
            self.mainWin.after(130, lambda: self.pageWin.geometry(
                f'+{self.pageFrame.winfo_rootx()-1}+{self.pageFrame.winfo_rooty()+57}'))
            self.mainWin.after(170, lambda: self.pageWin.geometry(
                f'+{self.pageFrame.winfo_rootx()}+{self.pageFrame.winfo_rooty()+55}'))

        try:
            int(entry)
        except:
            self.pageButton.config(state=DISABLED)
            animate()
            # self.pageEntry.config(foreground='darkred')
        else:
            if 0 < int(entry) <= len(self.results):
               # self.pageEntry.config(foreground='black')
                self.pageButton.config(state=NORMAL)
            else:
                # self.pageEntry.config(foreground='darkred')
                self.pageButton.config(state=DISABLED)
                animate()
    def save(self):
        try: self.df.to_csv(self.fileName)
        except:pass
    def onClose(self):
        #try:
            #self.update()
        #except:
        #    pass
        self.save()
        try:
            self.pref['autoCaps']=self.addAutoCapsCombobox.get()
            self.pref['recent']='?'.join(self.recentFileList[-5:])
            self.pref['recentPaths']='?'.join(self.recentFilePathList[-5:])
            self.pref['favourites']='?'.join(self.favList)
        except:pass
        try:
            self.pref.to_csv(self.prefPath)
        except:
            pass
        self.mainWin.destroy()

    def print_list(self, search=None, returnIndex=False, numValues=20, data=None,override=False):
        if type(data)==type(None):data=self.df
        
        if override!=True:
            _ = dict()
            for index in data.index:
                _[index] = str(' ').join([str(item)
                                             for item in data.loc[index].to_list()])
            data=_
        #data=[str(' ').join([str(item) for item in self.df.loc[row].to_list()]) for row in self.df.index]
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


