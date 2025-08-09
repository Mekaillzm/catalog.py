# -*- coding: utf-8 -*-
"""
Created on Sat Jul 13 13:21:30 2024

@author: mekai
"""
import sv_ttk
import re
import pandas as pd
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import tkinter.messagebox as msg
import math
import sys
import numpy as np
import os

class catalog():

    def __init__(self,path=None):
        self.master=tk.Tk(screenName='Catalog')
        sv_ttk.set_theme('dark',self.master)
        #Predefined values
        self.maxColumnRange=range(12) #The maximum number of columns
        self.editorComboboxWidth=int(self.master.winfo_screenmmwidth()/20.3)
        self.dataTypes = {'Text':str,'Integer':int,'Boolean':bool,'Float':float, 'Date': pd.to_datetime}
        self.autoCapsValues = ['Always','Only Lowercase Text', 'Only First Letter', 'Never']
        
        self.analysisNumberOperatorList  = ['==','!=','<','<=','>','>=']
        self.analysisStringOperatorList = ['==','!=']
        #predefined lambdas
        self.saveFileData = lambda: self.fileData.to_csv(f'{self.prefPath}/filedata.csv')
        #self.savePref = lambda: self.pref.to_csv(f'{self.prefPath}/preferences.csv')
        
        #placeholder values
        self.df=None #Nonetype used as an indicator that a new file has been made
        self.filteredDf = None
        self.expectedFolder=None #The folder to open when a file dialog is prompted
        self.query='' #The default query entered in the search bar
        self.totalPages = 1 #The total number of pages that the search result is split into
        self.currentPage = 1
        self.pageEntryText = f'Page {self.currentPage}/{self.totalPages}' #The default page shown at startup
        self.searchResults=[]
        self.userEntry = '' #String value used to record entries in the result frame to be updated
        self.infoAnalysisUserEntry=''
        self.selections = set()
        self.recentFiles= set()
        self.favFiles = set()
        self.defaultTypes = []
        self.filters={}
        self.maxLength = 40
        
        self.setupDisplay1() #Sets up and displays widgets; does nothing that requires file data
        self.setupPreferences() #Opens preference and data file
        
        #If no path is provided to the function, obtain one from pref.csv and open the editor view if no file exists
        if path==None:
            self.filePath=f'{self.pref["currentPath"]}'
        else: 
            if not os.path.isabs(path):
                path = '/'.join(os.path.abspath(path).split('\\'))
                
            self.filePath = path
            
        if os.stat(self.filePath):
            self.readFile(self.filePath, True)
        else:
            self.openEditorView(True,4)
                        
            
        self.master.bind('<KeyRelease>',self.onKeyRelease)
        self.master.bind('<Control-Button-1>',self.controlButton1Pressed)
        self.master.bind('<Button-3>',self.openPopupMenu)
        self.infoToplevel.bind('<KeyRelease>',self.infoOnKeyRelease)
        self.infoFileRecentCombobox.bind('<<ComboboxSelected>>',self.openRecentFile)
        self.infoFileFavCombobox.bind('<<ComboboxSelected>>',self.openFavFile)
        self.infoAddCapsCombobox.bind('<<ComboboxSelected>>',self.infoAddAutoCapsSet)
        self.infoAnalysisColumnSelectCombobox.bind('<<ComboboxSelected>>',self.infoAnalysisComboboxSelected)
        self.infoAnalysisFilterColumnComboboxList[0].bind('<<ComboboxSelected>>',self.infoAnalysisFilterCombobox0Selected)
        self.infoAnalysisFilterColumnComboboxList[1].bind('<<ComboboxSelected>>',self.infoAnalysisFilterCombobox1Selected)
        self.infoAnalysisFilterColumnComboboxList[2].bind('<<ComboboxSelected>>',self.infoAnalysisFilterCombobox2Selected)
        self.infoAnalysisFilterColumnComboboxList[3].bind('<<ComboboxSelected>>',self.infoAnalysisFilterCombobox3Selected)
        self.infoAnalysisFilterColumnComboboxList[4].bind('<<ComboboxSelected>>',self.infoAnalysisFilterCombobox4Selected)

        self.infoAnalysisFilterValueComboboxList[0].bind('<<ComboboxSelected>>',self.infoAnalysisFilterCombobox0Selected)
        self.infoAnalysisFilterValueComboboxList[1].bind('<<ComboboxSelected>>',self.infoAnalysisFilterCombobox1Selected)
        self.infoAnalysisFilterValueComboboxList[2].bind('<<ComboboxSelected>>',self.infoAnalysisFilterCombobox2Selected)
        self.infoAnalysisFilterValueComboboxList[3].bind('<<ComboboxSelected>>',self.infoAnalysisFilterCombobox3Selected)
        self.infoAnalysisFilterValueComboboxList[4].bind('<<ComboboxSelected>>',self.infoAnalysisFilterCombobox4Selected)

        self.infoAnalysisFilterOperatorComboboxList[0].bind('<<ComboboxSelected>>',self.infoAnalysisFilterCombobox0Selected)
        self.infoAnalysisFilterOperatorComboboxList[1].bind('<<ComboboxSelected>>',self.infoAnalysisFilterCombobox1Selected)
        self.infoAnalysisFilterOperatorComboboxList[2].bind('<<ComboboxSelected>>',self.infoAnalysisFilterCombobox2Selected)
        self.infoAnalysisFilterOperatorComboboxList[3].bind('<<ComboboxSelected>>',self.infoAnalysisFilterCombobox3Selected)
        self.infoAnalysisFilterOperatorComboboxList[4].bind('<<ComboboxSelected>>',self.infoAnalysisFilterCombobox4Selected)

        self.searchEntry.bind('<KeyRelease>', self.updateSearch)
        self.pageEntry.bind('<KeyRelease>',self.pageOnKeyPress)
        self.addToplevel.bind('<Return>',self.addEnterPressed)
        #[self.addFrameList[i].bind('<FocusIn>',self.addFrameFocus)]
        #self.infoToplevel.bind('<Button-1>',self.infoButton1)
        #self.addToplevel.bind('<Button-1>',self.addButton1)

        
        self.master.protocol("WM_DELETE_WINDOW", self.onClose)
        self.infoToplevel.protocol("WM_DELETE_WINDOW", self.infoToplevel.withdraw)
        self.addToplevel.protocol("WM_DELETE_WINDOW", self.addToplevel.withdraw)

        #self.popupMenu.protocol("WM_DELETE_WINDOW", self.popupMenu.withdraw)
        return
    #filedialogue
    def openFile(self):
        self.save()
        file = filedialog.askopenfile(master=self.master, title=f'Select a file', filetypes=(
            ('csv files', '*.csv'), ('All files', '*.*')))
        if os.stat(file.name): 
            #print('Reading File')
            self.readFile(file.name,True)
        else:
            return
        
    def editFile(self):
        self.save()
        self.openEditorView(False,len(self.df.columns))
        
    def newFile(self):
        
        self.save()
        self.clearWidgets()
        self.df = None
        self.openEditorView(True,4)

    def openRecentFile(self,i):
        self.save()
        file=self.infoFileRecentCombobox.get()
        if os.stat(file):
            self.readFile(file,True)
    def openFavFile(self,i):
        self.save()
        file=self.infoFileFavCombobox.get()
        if os.stat(file):
            self.readFile(file,True)
    def addFavFile(self):
        self.prefUpdate()
        if self.filePath in self.favFiles:
            self.favFiles.remove(self.filePath)
        else:
            self.favFiles.add(self.filePath)
        self.configureFavButton()
    #preferences
    def setupPreferences(self):
        '''
        Checks for and creates directories required to store user preferences

        Returns
        -------
        None.

        '''
        if sys.platform.startswith("win"):
            self.prefPath = os.path.expanduser('~')+'/AppData/Local/catalogpy'
        elif sys.platform.startswith("darwin"):
            self.prefPath = os.path.expanduser('~')+'/Library/Application Support/catalogpy'
        else:
            msg.showerror('OS Not Supported',f"{sys.platform} is not supported on this app.")
            self.onClose()
            return
        #Find user directory and create it if not found
        try: os.stat(self.prefPath)
        except FileNotFoundError as e:
            os.mkdir(self.prefPath)
        
        #Open preferences file and create it if not found
        try:
            self.pref = pd.read_csv(f'{self.prefPath}/preferences.csv',index_col=0)['0']
        except FileNotFoundError as e:
            self.pref = pd.Series({'currentPath':'' ,'theme':'dark', 'recentFiles':'','favFiles':'','autoCaps':self.autoCapsValues[0]})
            self.prefSave()
        
        #Open file data file and create it if not found
        try:
            self.fileData = pd.read_csv(f'{self.prefPath}/filedata.csv',index_col=0)
        except FileNotFoundError as e:
            self.fileData=pd.DataFrame(columns=['columns','itemName','systemName','columnDataTypes','defaultColumnValues','addColumns'])
            self.saveFileData()
    

        
    #Read and open files
    
    def readDataFiles(self):
        self.pref = pd.read_csv(f'{self.prefPath}/preferences.csv',index_col=0)['0']
        self.fileData = pd.read_csv(f'{self.prefPath}/filedata.csv',index_col=0)
    #Reads file and obtains relevant information if present
    def readFile(self,path,updatePreferences=False):
        '''try:
            datesList=self.parseDates()
        except Exception as e:
            datesList=None
            Warning(e)'''
        try:self.df= pd.read_csv(path, index_col=0)
        except Exception as e:
            msg.showerror('Unable to Open File',f'Unable to read file due to:\n {e}')
            return False
        else:
            self.prefUpdate()
            #print('File read. Preferences updated')

        self.filePath=path
        
        if updatePreferences==True:
            self.prefPathUpdate()
        
        try:
            self.fileData.loc[path]
        except KeyError as e:
            self.master.update_idletasks()
            msg.showinfo('Missing Information', 'Please enter the column names and data types of this file.')
            #self.editorUpdateVisibility(len(self.df.columns))                
            self.openEditorView(True,len(self.df.columns))
        else:
            self.searchDataCreation()
            #print('Search data created')
            self.openResultsView()
            #print('Results view opened')
            self.setupDefaults()
            #print('Defaults set up')
            [self.convertColumnDataType(column) for column in range(len(self.df.columns))]
        return True

    #Allows user to edit file information such as column headings
    def openEditorView(self, newFile, visibleColumns=None):
        '''
        Sets up the display and internal elements for the editor frame

        Parameters
        ----------
        newFile : bool
            DESCRIPTION.
        visibleColumns : TYPE, optional
            DESCRIPTION. The default is None.

        Returns
        -------
        None.

        '''
        self.clearWidgets()
        self.resultFrame.place_forget()
        self.pageFrame.place_forget()
        self.placeEditorFrame()
        self.searchAddButton.config(text='Save Changes',command=self.editorSaveChanges)
        self.searchEntry.config(state='disabled')
        self.searchFavoriteButton.config(state='disabled')
        
        
        self.editorClearEntries()
        if newFile!=True:
            defaults = self.fileData.loc[self.filePath,'defaultColumnValues'].split(',')
            defaultTypes = self.fileData.loc[self.filePath, 'columnDataTypes'].split(',')
            
            self.editorItemNameEntry.insert(0,self.fileData.loc[self.filePath,'itemName'])
            self.editorSystemNameEntry.insert(0,self.fileData.loc[self.filePath,'systemName'])
            
            #defaults=['' for i in range(len(self.df.columns))]
        if self.df is not None:
            for n in range(len(self.df.columns)):
                self.editorHeadingEntryList[n].insert(0,self.df.columns[n])
                if newFile!=True:
                    self.editorEmptyEntryList[0][n].set(defaultTypes[n])
    
                    self.editorEmptyEntryList[1][n].insert(0,defaults[n])
                
        self.editorUpdateVisibility(visibleColumns)#None means that self.displayedEntryColumns will be used as the number
        
        
    def openResultsView(self):
        self.clearWidgets()
        self.editorFrame.place_forget()
        self.placeResultFrame()
        self.searchAddButton.config(text='+',command=self.openAddToplevel)
        self.searchEntry.config(state='normal')
        self.searchFavoriteButton.config(state='normal')
        #print('Initial result frame configurations complete')
        
        self.updateResultFrame()
        #print('Result display updated')
        
        self.searchResults=[]
        
        
        self.setupDisplay2()
        self.search()
        self.configureFavButton()
        #print('Result frame fully set up')
    
    def updateResultFrame(self):
        '''
        Updates visibility of headings, rows and columns on main display
        Also adjusts their width according to either the 75th percentile string length of a column, or the length of a heading, depending on whcih is longer

        Returns
        -------
        None.

        '''
        for column in self.maxColumnRange:
            self.resultFrameList[column].grid_remove()
        #print('Grid removed')
        lengths=[]

        #print('Rows removed')
        for column in range(len(self.df.columns)):

            self.resultFrameList[column].grid()
            self.resultHeadingList[column].config(text=self.df.columns[column])
            if len(self.df)>0:
                length=(int(np.quantile([len(str(a)) for a in self.df[self.df.columns[column]]],0.75)) + 4)
        
                if length < len(self.df.columns[column]): length = len(self.df.columns[column])
        
                if length > 25: length=25
            else:
                length = 25
            lengths.append(length)
        #print('Initial row length calculations complete')
        
        for i in range(100):
            if sum(lengths)/self.master.winfo_screenmmwidth() < 0.32:
                lengths = [int(length*1.2) for length in lengths]
            else:
                break
                
        for i in range(100):
            if sum(lengths)/self.master.winfo_screenmmwidth() > 0.39:
                lengths = [int(length*0.9) for length in lengths]
            else:
                break
        #print('Row lengths calculated')
        for column in range(len(self.df.columns)):
            [self.resultEntryList[column][n].config(width=lengths[column]) for n in range(self.numResults)]            
          
                    
        return
    
    def placeEditorFrame(self):
        self.editorFrame.place(x=int(self.screenMMWidth/4.49),y=int(self.screenMMHeight/2.12))


    def placeResultFrame(self):
        self.resultFrame.place(x=int(self.screenMMWidth/15),y=int(self.screenMMHeight/2.12))    #Setup initial display, before data file is read
        self.pageFrame.place(x=int(self.screenMMWidth/0.605),y=int(self.screenMMHeight/0.3112))
        
    def setupDisplay1(self):
        
        self.screenHeight,self.screenWidth = self.master.winfo_screenheight(),self.master.winfo_screenwidth()
        self.screenMMHeight,self.screenMMWidth = self.master.winfo_screenmmheight(),self.master.winfo_screenmmwidth()

        self.master.geometry(f'{self.screenWidth}x{self.screenHeight}+0+0')
        totalWidth=self.screenWidth/10

        #Frame setup
        self.searchFrame = tk.Frame(master=self.master) #contains search bar and buttons
        self.searchFrame.place(x=int(self.screenMMWidth/1.0572),y=int(self.screenMMHeight/5.3009))
        
        self.resultFrame = tk.Frame(master=self.master) #shows search results
        
        self.editorFrame = tk.Frame(master=self.master) #allows user to edit column headings and other file information
        
        self.pageFrame = tk.Frame(master=self.master) #contains widgets for switching pages
        #popup window setup
        self.infoToplevel = tk.Toplevel(master=self.master)
        self.infoToplevel.withdraw()
        
        self.popupMenu = tk.Menu(self.master,tearoff=0)
        
        self.addToplevel = tk.Toplevel(self.master)
        self.addToplevel.withdraw()
        
        #self.popupMenu.overrideredirect(True)
        #self.popupMenu.attributes('-alpha', 0.9)
        #self.popupMenu.withdraw()
        
        #Search frame
        self.searchInfoButton= ttk.Button(master=self.searchFrame,text='☰',command=self.infoToplevel.deiconify)#brings up info window
        self.searchFavoriteButton = ttk.Button(master=self.searchFrame,text='⭐',command=self.addFavFile)#used to add favorite files for easy access
        self.searchAddButton = ttk.Button(master=self.searchFrame,text='+', command=self.openAddToplevel)#Used to open item addition popup window
        
        self.searchEntry = ttk.Entry(master=self.searchFrame,width=int(0.5*totalWidth))
        
        self.searchInfoButton.grid(row=0,column=0)
        self.searchFavoriteButton.grid(row=0,column=1)
        self.searchAddButton.grid(row=0,column=3)
        
        self.searchEntry.grid(row=0,column=2)
        
        
        #Result frame
        self.resultEntryList=[]

        #self.numResults=int((self.screenHeight/2)/24)
        self.numResults=int(self.screenMMHeight/12.72)

        self.resultEntryMainFrame=tk.Frame(self.resultFrame)
        self.resultEntryMainFrame.grid(row=0,column=0,sticky='e',padx=27)
        
        self.resultFrameList = []
        self.resultRowFrameList=[[]]*len(self.maxColumnRange)
        self.resultHeadingList= []
        for column in self.maxColumnRange:
            frame=tk.Frame(master=self.resultEntryMainFrame)
            self.resultFrameList.append(frame)
            self.resultEntryList.append([])
            self.resultFrameList[column].grid(row=0,column=column)
            self.resultHeadingList.append(ttk.Label(master=frame,text='NAN'))
            self.resultHeadingList[column].grid(row=0,column=column,ipady=5)
            for row in range(self.numResults):
                rowFrame = tk.Frame(master=frame)
                self.resultRowFrameList[column].append(rowFrame)
                self.resultEntryList[column].append(
                    ttk.Entry(master=rowFrame))  
                self.resultEntryList[column][row].grid(row=0,column=1) 
                rowFrame.grid(row=row+1,column=column)
        
        #check buttons for selection
        self.resultSelectFrame=tk.Frame(self.resultFrame)
        self.resultSelectFrame.place(x=self.resultFrame.winfo_rootx(),y=self.resultFrame.winfo_rooty())
        self.resultSelectVarList = []
        self.resultSelectCheckList= []
        
        #Option to select all checkbuttons at once
        self.resultSelectPageFrame = tk.Frame(self.resultSelectFrame)
        self.resultSelectPageFrame.grid(row=0,column=0)
        
        self.resultSelectPageVar= tk.IntVar(self.resultSelectPageFrame)
        self.resultSelectPageCheck = ttk.Checkbutton(self.resultSelectPageFrame,command=self.selectPage,onvalue=1,offvalue=0,variable=self.resultSelectPageVar)      
        self.resultSelectPageCheck.grid(row=0,column=0)
        self.resultSelectPageLabel = ttk.Label(self.resultSelectPageFrame,text='📄')
        self.resultSelectPageLabel.grid(row=0,column=1)
        for n in range(self.numResults):
            self.resultSelectVarList.append(tk.IntVar(master=self.resultSelectFrame))
            self.resultSelectCheckList.append(ttk.Checkbutton(master=self.resultRowFrameList[0][n], command=self.onSelect,
                                onvalue=1, offvalue=0, variable=self.resultSelectVarList[n]))
            
            self.resultSelectCheckList[n].grid(row=0,column=0,sticky='ne')
        
                


        
        # mainMenu
        '''self.mainMenu = tk.Menu(master=self.master)
        self.fileMenu = tk.Menu(master=self.mainMenu, tearoff=0)
        self.fileMenu.add_command(label='New file')
        self.fileMenu.add_separator()
        
        self.openRecentMenu=tk.Menu(master=self.fileMenu,tearoff=0)
        self.fileMenu.add_cascade(label='Open recent')
        
        self.favMenu=tk.Menu(master=self.fileMenu,tearoff=0)
        self.fileMenu.add_cascade(label='Open starred',menu=self.favMenu)

        self.fileMenu.add_command(label='Open file')
        self.fileMenu.add_command(label='Export file')
        
        self.editMenu = tk.Menu(master=self.mainMenu, tearoff=0)
        self.editMenu.add_command(
            label='Replace')
        self.editMenu.add_command(label='Select All')
        #self.editMenu.add_command(label='Rename Columns',command=lambda:self.confirmDataIntegrity(True))
        self.mainMenu.add_cascade(menu=self.fileMenu, label='File')
        self.mainMenu.add_cascade(menu=self.editMenu, label='Edit')
        self.master.config(menu=self.mainMenu)
        '''
        #Editor frame
        self.editorMiddleFrame = tk.Frame(master=self.editorFrame)
        self.editorMiddleFrame.grid(row=1,column=0,pady=15,sticky='w')
        
        self.editorEntryFrame = tk.Frame(master=self.editorMiddleFrame)
        self.editorEntryFrame.grid(row=0,column=1)
        
        self.editorEmptyEntryFrameList = [ttk.Frame(master=self.editorEntryFrame)
                             for n in range(self.numResults)]
        
        #Readonly entries that serve display purposes only
        self.displayedEntryColumns = 4 #number of columns visible to user

        self.editorEmptyEntryList = [[],[]]
        
        #for row in range(self.numResults):
        #    self.editorEmptyEntryList.append([])-
        for n in self.maxColumnRange:
            self.editorEmptyEntryList[0].append(ttk.Combobox(master=self.editorEmptyEntryFrameList[n],state='readonly',width=self.editorComboboxWidth-4))
            #self.editorEmptyEntryList[0][n].config(state='readonly')
            self.editorEmptyEntryList[0][n]['values'] = list(self.dataTypes.keys())
            self.editorEmptyEntryList[0][n].set(list(self.dataTypes.keys())[0])
            self.editorEmptyEntryList[1].append(ttk.Entry(master=self.editorEmptyEntryFrameList[n],width=self.editorComboboxWidth))
        
        #for row in range(self.numResults):

        
        
        #entries that allow the user to enter column headings
        self.editorUpperFrame= tk.Frame(master=self.editorFrame)
        self.editorUpperFrame.grid(row=0,column=0)
        self.editorHeadingFrame=tk.Frame(master=self.editorUpperFrame)
        self.editorHeadingFrame.grid(row=0,column=1,sticky='n')
        
        self.editorHeadingEntryList = [ttk.Entry(master=self.editorHeadingFrame,width=self.editorComboboxWidth) for n in self.maxColumnRange]
        #[self.editorHeadingEntryList[n].grid(row=0,column=n,ipady=5) for n in range(self.displayedEntryColumns)]
        
        #self.editorUpdateVisibility() #Makes the necessary number of widgets visible, in this case the default number, 4

        
        self.editorUpperButtonFrame = tk.Frame(master=self.editorUpperFrame)
        self.editorUpperButtonFrame.grid(row=0,column=2)
        self.editorPlusButton = ttk.Button(master=self.editorUpperButtonFrame,text = "+",command=self.editorAddHeading,width=1)
        self.editorPlusButton.grid(row=0,column=1,ipady=5,ipadx=0)

        #self.editorLowerButtonFrame = tk.Frame(master=self.editorMiddleFrame)
        #self.editorLowerButtonFrame.grid(row=0,column=2,sticky='s')
        self.editorMinusButton = ttk.Button(master=self.editorUpperButtonFrame,text = "-",command=self.editorRemoveHeading,width=1)
        self.editorMinusButton.grid(row=0,column=0,ipady=5,ipadx=0)
        
        #Labels in editor frame
        self.editorHeadingLabel = ttk.Label(master=self.editorUpperFrame,text='Headings',width=12)
        self.editorHeadingLabel.grid(row=0,column=0)
        
        self.editorLabelFrame = ttk.Frame(master=self.editorMiddleFrame)
        self.editorLabelFrame.grid(row=0,column=0)
        
        self.editorTypesLabel = ttk.Label(master=self.editorLabelFrame,text='Data Types',width=12)
        self.editorTypesLabel.grid(row=0,column=0)
        
        self.editorDefaultsLabel = ttk.Label(master=self.editorLabelFrame,text='Default Values',width=12)
        self.editorDefaultsLabel.grid(row=1,column=0,pady=4)
        
        self.editorLowerFrame=tk.Frame(master=self.editorFrame)
        self.editorLowerFrame.grid(row=3,column=0,sticky='ws')
        
        self.editorItemNameLabel = ttk.Label(master=self.editorLowerFrame,text='This catalog is for',width=17)
        self.editorItemNameLabel.grid(row=0,column=0,sticky='w')

        self.editorSystemNameLabel=ttk.Label(master=self.editorLowerFrame,text='This catalog is called',width=17)   
        self.editorSystemNameLabel.grid(row=1,column=0)
        
        self.editorItemNameEntry = ttk.Entry(master=self.editorLowerFrame)
        self.editorItemNameEntry.grid(row=0,column=1)
        
        self.editorSystemNameEntry = ttk.Entry(master=self.editorLowerFrame)
        self.editorSystemNameEntry.grid(row=1,column=1)
        
        
        #Info window
        self.infoNotebook = ttk.Notebook(master=self.infoToplevel)
        self.infoNotebook.grid(row=0,column=0)
        
        #info toplevel File open/edit/config
        self.infoFileFrame = tk.Frame(master=self.infoNotebook)
        self.infoNotebook.add(self.infoFileFrame,text='File')
        self.infoNotebook.select(0)
        
        self.infoFileButtonFrame=tk.Frame(self.infoFileFrame)
        self.infoFileButtonFrame.grid(row=0,column=0)
        
        self.infoFileOpenButton = ttk.Button(self.infoFileButtonFrame,text='Open File', command=self.openFile, width=10)
        self.infoFileOpenButton.grid(row=2,column=0)
        
        self.infoFileEditButton = ttk.Button(self.infoFileButtonFrame,text='Edit', width=10, command=self.editFile)
        self.infoFileEditButton.grid(row=0,column=0)
        
        self.infoFileNewButton = ttk.Button(self.infoFileButtonFrame,text='New File', width=10,command=self.newFile)
        self.infoFileNewButton.grid(row=1,column=0)
        
        self.infoFileSeparator = ttk.Separator(master=self.infoFileFrame,orient=tk.VERTICAL)
        self.infoFileSeparator.grid(row=0,column=1,rowspan=3,padx=30)
        
        self.infoFileLowerFrame=tk.Frame(master=self.infoFileFrame)
        self.infoFileLowerFrame.grid(row=0,column=2)
        
        self.infoFileRecentLabel = ttk.Label(self.infoFileLowerFrame,text='Open Recent File')
        self.infoFileRecentCombobox = ttk.Combobox(self.infoFileLowerFrame, state='readonly',width=22)
        self.infoFileRecentLabel.grid(row=0,column=0)
        self.infoFileRecentCombobox.grid(row=0,column=1)
        
        self.infoFileFavLabel = ttk.Label(self.infoFileLowerFrame,text='Open Starred File')
        self.infoFileFavCombobox = ttk.Combobox(self.infoFileLowerFrame, state='readonly',width=22)
        self.infoFileFavLabel.grid(row=1,column=0)
        self.infoFileFavCombobox.grid(row=1,column=1)  
        
        #info Add window settings
        self.infoAddFrame = tk.Frame(self.infoNotebook)
        self.infoNotebook.add(self.infoAddFrame,text='Add')
        
        self.infoAddCheckFrame = tk.Frame(self.infoAddFrame)
        self.infoAddCheckFrame.grid(row=0,column=0,sticky='w')
        self.infoAddVarList = []
        self.infoAddCheckList = []
        self.infoAddLabelList = []
        
        for column in self.maxColumnRange:
            var=tk.IntVar(master=self.infoAddCheckFrame)
            self.infoAddVarList.append(var)
            check=ttk.Checkbutton(master=self.infoAddCheckFrame,variable=var,command=self.infoAddCheckbuttonPressed)

            self.infoAddCheckList.append(check)
            label= ttk.Label(self.infoAddCheckFrame)
            self.infoAddLabelList.append(label)

            if column >= len(self.maxColumnRange)/2:
                c=2
                column= int(column-len(self.maxColumnRange)/2)
            else: c = 0
            check.grid(row=column,column=c+1)    
            
            
            label.grid(row=column,column=c)            
        self.infoAddLabel1 = ttk.Label(self.infoAddFrame,text='Choose columns to add data to,\nthe rest will assume default values')
        self.infoAddLabel1.grid(row=1,column=0,sticky='w')

        
        self.infoAddSeparator = ttk.Separator(self.infoAddFrame,orient='horizontal')
        self.infoAddSeparator.grid(row=2,column=0,ipady=10)
        
        self.infoAddCapsFrame = tk.Frame(self.infoAddFrame)
        self.infoAddCapsFrame.grid(row=4,column=0)
        self.infoAddCapsCombobox= ttk.Combobox(self.infoAddCapsFrame,state='readonly')
        self.infoAddCapsCombobox['values'] = self.autoCapsValues
        self.infoAddCapsCombobox.grid(row=0,column=1)


        self.infoAddCapsLabel = ttk.Label(self.infoAddCapsFrame,text='Automatically Capitalize Text: ')
        self.infoAddCapsLabel.grid(row=0,column=0)
        
        #info toplevel analysis
        infoAnalysisWidth =15
        
        self.infoAnalysisFrame = tk.Frame(self.infoNotebook)
        self.infoNotebook.add(self.infoAnalysisFrame, text='Analyse')
        
        self.infoAnalysisLeftFrame = tk.Frame(self.infoAnalysisFrame)
        self.infoAnalysisLeftFrame.grid(row=0,column=0)
        self.infoAnalysisColumnSelectFrame = tk.Frame(self.infoAnalysisLeftFrame)
        self.infoAnalysisColumnSelectFrame.grid(row=2,column=0)
        
        self.infoAnalysisColumnSelectCombobox= ttk.Combobox(self.infoAnalysisColumnSelectFrame,state='readonly',width=infoAnalysisWidth)
        self.infoAnalysisColumnSelectCombobox.grid(row=0,column=1)
        
        self.infoAnalysisColumnSelectLabel = ttk.Label(self.infoAnalysisColumnSelectFrame,text='Select Column',width=infoAnalysisWidth-2)
        self.infoAnalysisColumnSelectLabel.grid(row=0,column=0)
        
        self.infoAnalysisLeftSeparator1 = ttk.Separator(self.infoAnalysisLeftFrame)
        self.infoAnalysisLeftSeparator1.grid(row=1,column=0,ipady=5)
        
        self.infoAnalysisLabelFrame = tk.Frame(self.infoAnalysisLeftFrame)
        self.infoAnalysisLabelFrame.grid(row=4,column=0,sticky='w')
        
        self.infoAnalysisEntryLabelList= []
        self.infoAnalysisEntryList= []
        self.infoAnalysisComboboxList=[]
        
        for row in range(9):
            label = ttk.Label(self.infoAnalysisLabelFrame,text='...',width=infoAnalysisWidth-2)
            
            entry = ttk.Entry(self.infoAnalysisLabelFrame,width=infoAnalysisWidth+4,state='disabled')
            
            combobox = ttk.Combobox(self.infoAnalysisLabelFrame,width=infoAnalysisWidth,state='readonly')
            
            self.infoAnalysisEntryLabelList.append(label)
            self.infoAnalysisEntryList.append(entry)
            self.infoAnalysisComboboxList.append(combobox)
            
            label.grid(row=row,column=0)
            entry.grid(row=row,column=1)
            combobox.grid(row=row,column=1)
            combobox.grid_remove()
        
        self.infoAnalysisLeftSeparator2 = ttk.Separator(self.infoAnalysisLeftFrame)
        self.infoAnalysisLeftSeparator2.grid(row=3,column=0,ipady=5)
        
        self.infoAnalysisFilterFrame=tk.Frame(self.infoAnalysisLeftFrame)
        self.infoAnalysisFilterFrame.grid(row=0,column=0)
        
        self.infoAnalysisFilterLabel = ttk.Label(self.infoAnalysisFilterFrame,text='Filter Data',)
        self.infoAnalysisFilterLabel.grid(row=0,column=0,pady=3,sticky='w')
        
        self.infoAnalysisFilterButtomFrame = tk.Frame(self.infoAnalysisFilterFrame)
        self.infoAnalysisFilterButtomFrame.grid(row=6,column=0,sticky='w',pady=3)
        
        self.infoAnalysisFilterRemoveButton = ttk.Button(self.infoAnalysisFilterButtomFrame,text='-',command=self.infoAnalysisRemoveFilter,width=1)
        self.infoAnalysisFilterRemoveButton.grid(row=0,column=0)

        self.infoAnalysisFilterAddButton = ttk.Button(self.infoAnalysisFilterButtomFrame,text='+',command=self.infoAnalysisAddFilter,width=1)
        self.infoAnalysisFilterAddButton.grid(row=0,column=1)
        
        #self.infoAnalysisFilterButton = ttk.Button(self.infoAnalysisFilterFrame,text='+',command=self.infoAnalysisAddFilter)
        #self.infoAnalysisFilterButton.grid(row=6,column=0,sticky='w',pady=3)
        self.infoAnalysisFilterLabelList=[]
        
        self.infoAnalysisFilterFrameList=[]
        self.infoAnalysisFilterColumnComboboxList =[]
        self.infoAnalysisFilterOperatorComboboxList = []
        self.infoAnalysisFilterValueComboboxList = []
        
        
        for row in range(5):
            frame=tk.Frame(self.infoAnalysisFilterFrame)
            
            columnCombobox = ttk.Combobox(frame,state='readonly',width=int(infoAnalysisWidth/2))
            operatorCombobox = ttk.Combobox(frame,state='readonly',width=int(infoAnalysisWidth/5))
            valueCombobox = ttk.Combobox(frame,state='normal',width=int(infoAnalysisWidth/2))

            self.infoAnalysisFilterFrameList.append(frame)
            self.infoAnalysisFilterColumnComboboxList.append(columnCombobox)
            self.infoAnalysisFilterOperatorComboboxList.append(operatorCombobox)
            self.infoAnalysisFilterValueComboboxList.append(valueCombobox)
            
            frame.grid(row=row+1,column=0)
            columnCombobox.grid(row=0,column=0)
            operatorCombobox.grid(row=0,column=1,padx=2)
            valueCombobox.grid(row=0,column=2)
            frame.grid_remove()
            
        
        #info toplevel reset
        
        self.infoResetFrame=tk.Frame(self.infoNotebook)
        self.infoNotebook.add(self.infoResetFrame,text='Reset')
        
        self.infoResetPrefButton = ttk.Button(self.infoResetFrame,text='Reset Preferences',command=self.resetPref,width=20)
        self.infoResetPrefButton.grid(row=0,column=0)
        
        self.infoResetFileDataButton = ttk.Button(self.infoResetFrame,text='Reset File Data',command=self.resetFileData,width=20)
        self.infoResetFileDataButton.grid(row=1,column=0)
        
        self.infoResetAllButton = ttk.Button(self.infoResetFrame,text='Reset All',command=self.resetAll,width=20)
        self.infoResetAllButton.grid(row=2,column=0)
        
        
        

        
        
        
        
        
        #Page frame
        self.pageBackButton = ttk.Button(self.pageFrame,text='<',command=self.pageBack)
        self.pageBackButton.grid(row=-0,column=0)
        self.pageForwardButton= ttk.Button(self.pageFrame, text='>', command=self.pageForward)
        self.pageForwardButton.grid(row=0,column=2)
        self.pageEntry = ttk.Entry(self.pageFrame,width=10)
        self.pageEntry.grid(row=0,column=1)
        
        self.pageEntry.insert(0,self.pageEntryText)
        
        
        #Popup toplevel
        self.popupMenu.add_command(label='Delete',command=self.popupDelete)
        self.popupMenu.add_command(label='Delete Selected',command=self.popupDeleteSelected)
        self.popupMenu.add_separator()
        self.popupMenu.add_command(label='Select All',command=self.popupSelectAll)
        self.popupMenu.add_command(label='Deselect All',command=self.popupDeselectAll)
        self.popupMenu.add_separator()

        self.popupMenu.add_command(label='XXX Rows Selected')
        self.popupMenu.add_separator()
        self.popupMenu.add_command(label='Revert Changes',command=self.popupRevert)
        
        
        #Add toplevel
        self.addFrame=tk.Frame(master=self.addToplevel,padx=20)
        self.addFrame.grid(row=0,column=0)
        
        self.addEntryFrame = tk.Frame(self.addFrame)
        self.addEntryFrame.grid(row=0,column=0)
        
        self.addEntryList = []
        self.addCheckList=[]
        self.addVarList = []
        self.addLabelList=[]
        self.addFrameList=[]
        self.addSubFrameList =[]
        row=0
        for column in self.maxColumnRange:
            frame = tk.Frame(self.addEntryFrame)
            subFrame = tk.Frame(frame)
            
            self.addFrameList.append(frame)
            self.addSubFrameList.append(subFrame)
            
            var=tk.IntVar(frame, value=0)
            self.addVarList.append(var)
            
            check=ttk.Checkbutton(subFrame,variable=var,onvalue=1,offvalue=0,command=self.addConfigureEntry)
            self.addCheckList.append(check)
            
            label=ttk.Label(frame)
            self.addLabelList.append(label)
            
            entry=ttk.Entry(frame)
            self.addEntryList.append(entry)

            if column>5:
                row=1
                column-=6
            frame.grid(row=row,column=column)
            
            label.grid(row=0,column=0)
            entry.grid(row=1,column=0)
            subFrame.grid(row=2,column=0)
            check.grid(row=0,column=0,sticky='ew')
            var.set(1)

        self.addButton = ttk.Button(self.addFrame,text='Add',command=self.addDFNewRow)
        self.addButton.grid(row=0,column=1,ipady=3,ipadx=3)
        
        self.addTempToplevel = tk.Toplevel(master=self.addFrame)
        self.addTempToplevel.withdraw()
        self.addTempLabel=ttk.Label(self.addTempToplevel,text='Data added')
        self.addTempLabel.grid(row=0,column=0)
        self.addTempToplevel.overrideredirect(True)
        self.addTempToplevel.attributes('-alpha', 0.9)
        
        self.addSuggestToplevel= tk.Toplevel(master=self.addFrame)
        self.addSuggestToplevel.withdraw()
        self.addSuggestToplevel.overrideredirect(True)
        self.addSuggestToplevel.attributes('-alpha', 0.9)  
        self.addSuggestButton1 =ttk.Button(self.addSuggestToplevel)        
        self.addSuggestButton1.grid(row=0,column=0)
        
        self.addSuggestButton2 =ttk.Button(self.addSuggestToplevel)        
        self.addSuggestButton2.grid(row=0,column=0)
        self.addSuggestButton3 =ttk.Button(self.addSuggestToplevel)        
        self.addSuggestButton3.grid(row=0,column=0)                      
        return
    #function for setting up display elements that require file data.
    def setupDisplay2(self):
        '''
        
        function for setting up display elements that require file data. Called by openResultsView() and editorSaveChanges()
        Returns
        -------
        None.

        '''
        sv_ttk.set_theme(self.pref['theme'],self.master) #dark theme
        #addColumns=int(self.fileData.loc[self.filePath,'addColumns'].split(','))
        
        
        self.updateAddPref()
        self.infoAddCapsCombobox.set(self.pref['autoCaps'])
        self.defaultTypes = self.fileData.loc[self.filePath, 'columnDataTypes'].split(',')
        
        self.infoAnalysisColumnSelectCombobox['values'] = self.df.columns.to_list()
        for i in range(len(self.infoAnalysisFilterFrameList)):
            self.infoAnalysisFilterColumnComboboxList[i]['values']=self.df.columns.to_list()
        #self.updateResultFrame()
        #contents of window for creating new files
        
        
    ##Everything to do with the editor frame is below
    #Command for editor plus button. Makes another column visible further to the right
    def editorAddHeading(self):
        for row in range(2):
            self.editorEmptyEntryList[row][self.displayedEntryColumns].grid(row=row,column=self.displayedEntryColumns)
        self.editorEmptyEntryList[0][self.displayedEntryColumns].config(width=self.editorComboboxWidth)
        self.editorEmptyEntryList[1][self.displayedEntryColumns].config(width=self.editorComboboxWidth+4)
        
        self.editorEmptyEntryFrameList[self.displayedEntryColumns].grid(row=1,column=self.displayedEntryColumns)
        self.editorHeadingEntryList[self.displayedEntryColumns].grid(row=0,column=self.displayedEntryColumns,ipady=5)
        self.editorHeadingEntryList[self.displayedEntryColumns].config(width=self.editorComboboxWidth+4)
        self.displayedEntryColumns+=1
        self.editorMinusButton.config(state='normal')
        #print(self.editorPlusButton.winfo_rootx()/self.master.winfo_screenmmwidth(),111)
        if self.editorPlusButton.winfo_rootx()/self.screenMMWidth > 3:
            self.editorPlusButton.config(state='disabled')
        
    #Command for editor minus button. Makes the rightmost visible column invisible
    def editorRemoveHeading(self):
        if self.displayedEntryColumns>1:            
            self.displayedEntryColumns-=1
            for row in range(2):
                self.editorEmptyEntryList[row][self.displayedEntryColumns].grid_remove()
            self.editorEmptyEntryFrameList[self.displayedEntryColumns].grid_remove()
            self.editorHeadingEntryList[self.displayedEntryColumns].grid_remove()
        if self.displayedEntryColumns<2:
            self.editorMinusButton.config(state='disabled')
        self.master.update()
        #print(self.editorPlusButton.winfo_rootx()/self.master.winfo_screenmmwidth(),222)
        
        self.editorPlusButton.config(state='normal')

        #self.editorEmptyEntryFrameList[row].grid(row=row,column=self.displayedEntryColumns)
    
    #Deletes all contents of widgets in the editor    
    def editorClearEntries(self):
        for n in range(len(self.editorHeadingEntryList)):
            self.editorHeadingEntryList[n].delete(0,tk.END)  
            self.editorEmptyEntryList[0][n].set(list(self.dataTypes.keys())[0])
            self.editorEmptyEntryList[1][n].delete(0,tk.END)
            
        self.editorItemNameEntry.delete(0,tk.END)
        self.editorSystemNameEntry.delete(0,tk.END)
    
    #Updates the number and width of the widgets shown in the editor
    def editorUpdateVisibility(self,n=None):
        '''
        Run the editor frame is opened. Adjusts labels and entries of editor frame.

        Parameters
        ----------
        n : TYPE None || int, optional
            DESCRIPTION. The default is None.

        Returns
        -------
        None.

        '''
        if n!= None:self.displayedEntryColumns=n
        for n in self.maxColumnRange:
            self.editorHeadingEntryList[n].grid_remove()
            self.editorEmptyEntryFrameList[n].grid_remove()

        self.editorComboboxWidth=int(self.screenMMWidth/20.3)
        if self.displayedEntryColumns>6:
            self.editorComboboxWidth=int(self.editorComboboxWidth**(6/self.displayedEntryColumns))
            
        hw=int(self.editorComboboxWidth+4)
        for n in range(self.displayedEntryColumns):
       #     self.editorHeadingEntryList[n].config(width=lengths[n])
            self.editorHeadingEntryList[n].config(width=hw)
            self.editorEmptyEntryList[0][n].config(width=self.editorComboboxWidth)
            self.editorEmptyEntryList[1][n].config(width=hw)
            self.editorHeadingEntryList[n].grid(row=0,column=n,ipady=5)
            self.editorEmptyEntryFrameList[n].grid(row=1,column=n)
            self.editorEmptyEntryList[0][n].grid(row=0,column=n)
            self.editorEmptyEntryList[1][n].grid(row=1,column=n)
            
            
        self.master.update()

        
        if self.editorPlusButton.winfo_rootx()/self.screenMMWidth > 3.02:
            self.editorPlusButton.config(state='disabled')
    
    #Initiates sequnce of events after the "save changes" button is pressed
    def editorSaveChanges(self):
        
        def extractData(List,position,maxLength=np.nan):
            _=[]
            for widget in List[:position]:
                item = widget.get()
                if len(item)<1 or len(item)>maxLength:
                    widget.focus_set()
                    return None
                _.append(item)
            return _
        
        columns,columnDataTypes,defaults=extractData(self.editorHeadingEntryList,self.displayedEntryColumns,self.maxLength),extractData(self.editorEmptyEntryList[0],self.displayedEntryColumns),extractData(self.editorEmptyEntryList[1],self.displayedEntryColumns)
        if None in [columns,defaults,columnDataTypes]: 
            return
        for column in range(len(columns)):
            Type  = self.dataTypes[columnDataTypes[column]]
            try: 
                if Type in [int,float]:
                    eval(defaults[column])
                else:
                    Type(defaults[column])
            except:
                msg.showwarning('Invalid Entry',f'{defaults[column]} cannot be entered in {columns[column]}. Enter a(n) "{columnDataTypes[column]} value"')
                return
                
        itemName= self.editorItemNameEntry.get()
        if len(itemName)==0:
            self.editorItemNameEntry.insert(0,'Item')
            itemName='Item'
        systemName = self.editorSystemNameEntry.get()
        if len(systemName)==0:    
            self.editorSystemNameEntry.insert(0,'System')
            systemName='Catalog'
        
        
        if self.expectedFolder == None:
            initialDir = sys.path[0]
        else: initlaDir=self.expectedFolder
        dialog = filedialog.asksaveasfile(
            master=self.master,
            title=f'Select a folder to save the file in',
            defaultextension=".csv",
            initialdir=self.expectedFolder,
            filetypes=(
                ('csv files', '*.csv'), ('All files', '*.*'))
        )
        if dialog is None: 
            return
        #if self.df is None:
        #    df = pd.DataFrame(columns=columns.split(','))
        df = pd.DataFrame()
        for i in range(len(columns)):
            try:
                df[columns[i]] = self.df[self.df.columns[i]]
            except:
                df[columns[i]] = defaults[i]
        join = lambda _ : ','.join(_)
        
        try:[self.convertColumnDataType(column) for column in range(len(df))]
        except:pass
        try:
            self.updateFileInfo(dialog.name,df)       
        except AttributeError as e:
            Warning("Attribute error: {}".format(e))
            return
        except Exception as e:
            msg.showerror('Unable to Save File',f'The following problem occurred: {e}')
            return
        
        try: 
            addColumns = self.fileData.loc[self.filePath,'addColumns']
        except:addColumns=','.join(['1']*len(self.df.columns))
        self.updateFileData(join(columns), itemName,systemName, join(columnDataTypes),join(defaults),addColumns)
        self.clearWidgets()
        #self.filterData()
        self.searchDataCreation()
        self.openResultsView()
        self.prefUpdate()
        self.setupDisplay2()
        return
    #Editor frame end
    
    #Page-turning related stuff
    
    def pageBack(self):
        self.currentPage-=1
        self.pageEntryUpdate(False)
        self.searchUpdateDisplay()
    def pageForward(self):
        self.currentPage+=1
        self.pageEntryUpdate(False)
        self.searchUpdateDisplay()
    
    def convertPageToIndex(self):
        return self.currentPage-1
    #checks if the user is done typing and initiates page-turn
    def pageOnKeyPress(self,i=None):
        def checkQueryInit():
            pageEntryText= self.pageEntry.get()
            try:
                if not re.search(f'^Page [0-9]*/{self.totalPages}$',pageEntryText) or int(pageEntryText.split('/')[0][5:]) not in range(1,self.totalPages+1):
                    self.pageEntry.delete(0,tk.END)
                    self.pageEntry.insert(0,self.pageEntryText)
            except:
                return
            def checkQuery():
                if pageEntryText == self.pageEntry.get() and self.pageEntryText != pageEntryText:
                    self.pageTurn()
                    self.pageEntryText = pageEntryText
            self.master.after(300, checkQuery)
        self.master.after(1,checkQueryInit)
    def pageTurn(self):
        self.currentPage=int(re.findall(f'^Page ([0-9]*)/{self.totalPages}$',self.pageEntry.get())[0])
        self.searchUpdateDisplay()
        self.pageButtonConfig()
        
    def pageEntryUpdate(self,resetPage=True):
        self.pageEntry.delete(0,tk.END)
        self.totalPages = max((1,len(self.searchResults)))
        if resetPage==True:
            self.currentPage = 1
        
        self.pageEntry.insert(0,f'Page {self.currentPage}/{self.totalPages}')
        self.pageEntryText= self.pageEntry.get()
        self.pageButtonConfig()
        
    def pageButtonConfig(self):
        if self.currentPage>=self.totalPages:self.pageForwardButton.config(state='disabled')
        else:self.pageForwardButton.config(state='normal')
        if self.currentPage<=1:self.pageBackButton.config(state='disabled')
        else:self.pageBackButton.config(state='normal')
    #Page END
    
    #Selection related stuff
    def onSelect(self):
        check=self.master.focus_get()
        if check in self.resultSelectCheckList:
            row=self.resultSelectCheckList.index(check)
            index=self.searchResults[self.convertPageToIndex()][row]
            
            value= self.resultSelectVarList[row].get()
            
            if value == 1:
                self.selectAdd(index)
            elif value == 0:
                self.selectRemove(index)
            
    def controlButton1Pressed(self,i):
        widget = self.master.focus_get()
        master=widget.master.master
        if master in self.resultFrameList:
            column=self.resultFrameList.index(master)
            row = self.resultEntryList[column].index(widget)
            
            index=self.searchResults[self.convertPageToIndex()][row]
            value= self.resultSelectVarList[row].get()
            
            if value == 1:
                self.selectRemove(index)
            elif value == 0:
                self.selectAdd(index)
            self.selectUpdateVar()
            
    def selectAdd(self,indexList):
        if type(indexList) in (int,float, str):
            indexList=[indexList]
        for index in indexList:
            self.selections.add(int(index))
        self.selectUpdatePageVar()
    def selectRemove(self,indexList):
        if type(indexList) in (int, float, str):
            indexList=[indexList]
        for index in indexList:
            self.selections.remove(int(index))
        self.selectUpdatePageVar()
        
    def selectUpdateVar(self):
        for row in range(self.numResults):
            try:
                self.resultSelectCheckList[row].config(state='normal')
                if self.searchResults[self.convertPageToIndex()][row] in self.selections:
                    self.resultSelectVarList[row].set(1)
                else:
                    self.resultSelectVarList[row].set(0)
            except:
                self.resultSelectVarList[row].set(0)
                self.resultSelectCheckList[row].config(state='disabled')
        
    def selectUpdatePageVar(self):
        try:
            self.resultSelectPageCheck.config(state='normal')

            if set(self.searchResults[self.convertPageToIndex()]).union(self.selections) == self.selections:
                self.resultSelectPageVar.set(1)
            else:
                self.resultSelectPageVar.set(0)
        except IndexError:
            self.resultSelectPageCheck.config(state='disabled')
        self.popupMenu.entryconfig(6,label=f'{len(self.selections)} Rows Selected')

    def selectPage(self):
        value= self.resultSelectPageVar.get()
        if value==1:
            self.selectAdd(self.searchResults[self.convertPageToIndex()])
        elif value==0:
            self.selectRemove(self.searchResults[self.convertPageToIndex()])
        self.selectUpdateVar()
    
        
    
    #Selection END
    #Updates fileData database
    def updateFileData(self,columns,itemName,systemName,columnDataTypes,defaultColumnValues,addColumns):
        self.fileData.loc[self.filePath]=columns,itemName,systemName,columnDataTypes,defaultColumnValues,addColumns
        self.fileData.to_csv(f'{self.prefPath}/filedata.csv')
    def updateFileInfo(self,path,df):
        self.pref['currentPath'] = path
        self.filePath=path
        self.df=df
        self.save()
        
    def prefPathUpdate(self):
        self.pref['currentPath'] = self.filePath
    def prefUpdate(self):
        '''
        Updates display elements for recent files and favorite files

        Returns
        -------
        None.

        '''
        recentFiles=self.pref['recentFiles']
        try:
            if np.isnan(recentFiles): recentFiles=''
        except:pass
        recentFiles=set(recentFiles.split(','))
        for file in recentFiles.copy():
            if len(file)<1:
                recentFiles.remove(file)
        recentFiles.add(self.filePath)
        if len(recentFiles) > 7:
            recentFiles.remove(list(recentFiles)[0])
        
        self.recentFiles = recentFiles
        self.pref['recentFiles']=','.join(recentFiles)
        self.infoFileRecentCombobox['values'] = list(recentFiles)
        
        favFiles = self.pref['favFiles']
        try:
            if np.isnan(favFiles): favFiles=''
        except:pass
        favFiles = set(favFiles.split(','))
        for file in favFiles.copy():
            if len(file)<1:
                favFiles.remove(file)
        self.infoFileFavCombobox['values'] = list(favFiles)
        self.favFiles=favFiles
        
    def configureFavButton(self):
        if self.filePath in self.favFiles:
            self.searchFavoriteButton.config(text='✅')
        else:
            self.searchFavoriteButton.config(text='⭐')
        if len(self.favFiles)>7:
            self.searchFavoriteButton.config(state='disabled')
        else:self.searchFavoriteButton.config(state='normal')
        self.infoFileFavCombobox['values'] = list(self.favFiles)
        self.pref['favFiles'] = ','.join(self.favFiles)
        

    def prefSave(self):
        try:
            self.pref.to_csv(f'{self.prefPath}/preferences.csv')
        except:
            Warning('Unable to save preference file')
            pass
    def save(self):
        try:
            self.saveFileData()
        except:pass
        try: self.df.to_csv(self.filePath)
        except:
            Warning('Unable to save data file')
    
    #Seaches through the given file data types and returns a list containing the index location of each column that contains dates
    def parseDates(self):
        df=self.fileData.loc[self.filePath]
        dTypes=df['columnDataTypes'].split(',')
        
        indexList=[]
        for i in range(len(dTypes)):
            if dTypes[i]=='Date':
                indexList.append(i)
        return indexList
    

    
    #Popup window
    def openPopupMenu(self,i):
        self.popupMenu.post(self.master.winfo_pointerx(),
                             self.master.winfo_pointery())
        #self.popupMenu.geometry(f'+{self.master.winfo_pointerx()}+{self.master.winfo_pointery()}')
    
    def popupDelete(self):
        widget = self.master.focus_get()
        master = widget.master.master
        if master in self.resultFrameList:
            column = self.resultFrameList.index(master)
            row = self.resultEntryList[column].index(widget)
            index = self.searchResults[self.convertPageToIndex()][row]
            self.df.drop(index,axis=0,inplace=True)
            if index in self.selections:
                self.selectRemove(index)
            self.searchDataCreation()
            self.search()
            
            
    def popupDeleteSelected(self):        
        self.df.drop(self.selections,axis=0,inplace=True)
        self.selectRemove(self.selections.copy())
        #self.filterData()
        self.searchDataCreation()
        self.search()
    
    def popupSelectAll(self):
        self.selectAdd(self.df.index)
        self.selectUpdateVar()
    def popupDeselectAll(self):
        self.selectRemove(self.selections.copy())
        self.selectUpdateVar()
    def popupRevert(self):
        self.readFile(self.filePath)
    
    #Search related stuff
    #Detects when a user stops typing in the search bar
    def updateSearch(self,i):
        '''
        Performs debouncing for search, running the final search when the user stops typing for 300 ms.

        Parameters
        ----------
        i : TYPE
            DESCRIPTION.

        Returns
        -------
        None.

        '''
        def checkQueryInit():
            query= self.searchEntry.get()
            def checkQuery():
                if query == self.searchEntry.get() and self.query != query:
                    self.search()
                    self.query = query
            self.master.after(300, checkQuery)
        self.master.after(1,checkQueryInit)
    def searchDataCreation(self):
        '''
        Combines all columns in data to create searchable data

        Returns
        -------
        None.

        '''
        self.filterData()
        self.searchData={}
        for index in self.filteredDf.index:
            self.searchData[index] = str(' ').join([str(item)
                                         for item in self.df.loc[index].to_list()])
        
    #runs a search
    def search(self):
        query = self.searchEntry.get()
        if query=='':
            self.df.sort_values(self.df.columns[0]).index
        try:
            result=self.print_list(self.searchData,query,True,len(self.df.index))
            result.reverse()
        except:
            result = []
        self.searchResults=[]
        for n in range(0,len(result),self.numResults):
            self.searchResults.append(result[n:n+self.numResults])
        self.pageEntryUpdate()
        self.searchUpdateDisplay()

    def searchClearDisplay(self):
        for column in self.maxColumnRange:
            for row in range(self.numResults):
                self.resultEntryList[column][row].config(state='normal')
                self.resultEntryList[column][row].delete(0,tk.END)
        self.selectUpdateVar()
        self.selectUpdatePageVar() 

    def searchUpdateDisplay(self):        
        self.searchClearDisplay()
        try: resultPage = self.searchResults[self.convertPageToIndex()]
        except IndexError:resultPage=[]
        for row in range(self.numResults):
            try:
                resultId = resultPage[row]
            except Exception as e:
                resultId=None
            for column in range(len(self.df.columns)):
                if resultId!=None:
                    #print(self.df.loc[resultId,self.df.columns[column]],resultId)
                    self.resultEntryList[column][row].insert(0,self.df.loc[resultId,self.df.columns[column]])
                else:self.resultEntryList[column][row].config(state='disabled')
        return
        
    def print_list(self,data, search=None,returnIndex=False,numValues=20):
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
        if search == None: 
            for index, item in data.items():
                print('{}: {}\n'.format(index, item))
        #def look_for(DICT, search_item):
        output,found,n,has_result,_=[],dict(),0,False,re.findall('[^a-z0-9 -=]', search.lower())+[' ']
        for old in _:
            search=search.replace(old,_[0])
        search = search.lower().strip().split(_[0])
        
        for word in search:
            addAmt=1
            
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
            if has_result==False:
                f=dict()
                broken_search=dict()
                broken_dict=dict()
                num=0
                for letter in word:
                    broken_search[letter]=broken_search.get(letter,0)+1
                for index, item in data.items():
                    pos = item.find('(')
                    item=item[:pos].lower().split()
                    for word in item:
                        for l in word:
                            broken_dict[l]=broken_dict.get(l,0)+1
                        for letter, num in broken_dict.items():
                            try: broken_dict[letter]==broken_search[letter]
                            except: f[index]=f.get(index,0)-addAmt
                            else: f[index]=f.get(index,0)+addAmt
                        for index, item in f.items():
                            if item < 1: continue
                            found[index]=found.get(index,0)+item/2
                            n+=1
                            f=dict()
                        broken_dict = dict()
            has_result=False
            
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
            found=dict()
            broken_search=dict()
            broken_dict=dict()
            n=0
            for word in search:
                addAmt=1
                if word[0]=='-':
                    addAmt=-1
                for letter in word:
                    broken_search[letter]=broken_search.get(letter,0)+addAmt
            for index, item in data.items():
                
                pos = item.find('(')
                item=item[:pos].lower()          
                for l in item:
                    broken_dict[l]=broken_dict.get(l,0)+1
                for letter, n in broken_dict.items():
                    try:
                        broken_dict[letter]==broken_search[letter]
                    except:
                        found[index]=found.get(index,0)-1
                    else:
                        found[index]=found.get(index,0)+1
                        
    
                broken_dict=dict()
            if n>0:    
                found2 = dict()
                for index, item in found.items():
                    if item<=0:continue
                    #item = item*100/max(found.values())
                    found2[item] = found2.get(item, []) + [index]
                for item, index in sorted(found2.items()):
                    for i in index:
                        output.append(i)
            output=[]
        
        if returnIndex==False and not output==[]:
            return [data[index] for index in output][-numValues:]
        else:
            return output[-numValues:]   
                
    #Writing 

    def onKeyPress(self,i):
        #print(i.keysym=='Control_L')
        pass           
    def onKeyRelease(self,i):
        if self.master.focus_get().master.master in self.resultFrameList:
            def checkQueryInit():
                self.updateDf()
            self.master.after(1,checkQueryInit)
        '''#print("updated skipped")
            def checkQueryInit():
                userEntry = self.master.focus_get().get()
                #print("update check initiated")
                def checkQuery():
                    if userEntry == self.master.focus_get().get() and self.userEntry != userEntry:
                        self.updateDf()
                        self.userEntry = userEntry
                        print(True)
                self.master.after(150, checkQuery)
            self.master.after(1,checkQueryInit)    '''


    
    #Dataframe related stuff
    def convertDataType(self,value,column):
        dataType = self.dataTypes[self.defaultTypes[column]]
        if dataType==bool and type(value)==str:
            if value.lower() in ['y','yes','true','t']:
                value = True
            elif value.lower() in ['n', 'no','false','f']:
                value = False
            else:
                value = bool(value)
        elif dataType in [int,float] and type(value)==str:
            value = eval(value)
        else:
            try:
                if np.isnan(value):
                    value=self.fileData.loc[self.filePath,'defaultColumnValues'].split(',')[column]
            except Exception as e:pass
        value= dataType(value)
            
        return value
            
    def convertColumnDataType(self,column):
        columnName = self.df.columns[column]
        for row in self.df.index:
            self.df.loc[row,columnName] = self.convertDataType(self.df.loc[row,columnName], column)
        dataType = self.dataTypes[self.defaultTypes[column]]
        if dataType != pd.to_datetime: self.df[columnName] = self.df[columnName].astype(dataType)
            
    def setupDefaults(self):
        self.defaultTypes=self.fileData.loc[self.filePath,'columnDataTypes'].split(',')
        
    
        
    
    def updateDf(self):
        #print("updating")
        entry =self.master.focus_get()
        master = entry.master.master
        if master in self.resultFrameList:
            column = self.resultFrameList.index(master)
            row=self.resultEntryList[column].index(entry)
            
            self.df.loc[self.searchResults[self.convertPageToIndex()][row],self.df.columns[column]] = self.convertDataType(entry.get(),column)
            
            self.searchDataCreation()
            #print("updated")
            
    #Row addition related stuff
    
    def updateAddPref(self):
        addColumns = self.fileData.loc[self.filePath,'addColumns'].split(',')
        for column in self.maxColumnRange:
            
            try:
                value = int(addColumns[column])
            except:value=0
            self.infoAddVarList[column].set(value)
            self.infoAddCheckList[column].config(state='normal')
            if column < len(self.df.columns):
                self.infoAddLabelList[column].config(text=self.df.columns[column])
            else:
                self.infoAddLabelList[column].config(text='')
                self.infoAddVarList[column].set(0)
                self.infoAddCheckList[column].config(state='disabled')
                

        return
    
    def addDFNewRow(self):
        for column in range(len(self.df.columns)):
            if self.addFrameList[column].winfo_ismapped():
                self.autoCaps(self.addEntryList[column])
        values=[]
        for column in range(len(self.df.columns)):
            useColumn = self.infoAddVarList[column].get()
            if useColumn:
                value=self.addEntryList[column].get()
            if not useColumn or len(value)==0:
                value=self.fileData.loc[self.filePath,'defaultColumnValues'].split(',')[column]
            try:values.append(self.convertDataType(value, column))
            except:
                self.addEntryList[column].focus_set()
                return
        if len(self.df.index)>0:
            index=max(self.df.index)+1
        else:
            index=0
        self.df.loc[index] = values
        self.searchDataCreation()
        
        self.search()
        self.master.after(750,lambda:self.addTempToplevel.withdraw())
        self.clearAddEntries()
        self.addTempToplevel.deiconify()
        self.addTempToplevel.geometry(f'+{self.master.winfo_pointerx()+5}+{self.master.winfo_pointery()-5}')
        
    def clearAddEntries(self):
        for column in self.maxColumnRange:
            self.addEntryList[column].delete(0,tk.END)
    def clearAddToplevel(self):
        self.clearAddEntries()
        for column in self.maxColumnRange:
            self.addVarList[column].set(1)
    def openAddToplevel(self):
        displayedColumn=0
        row=0
        for column in self.maxColumnRange:
            self.addLabelList[column].config(text='')
            self.addFrameList[column].grid_remove()
            if self.infoAddVarList[column].get()==1:
                if displayedColumn>5:
                    row=1
                    displayedColumn-=6
                self.addFrameList[column].grid(row=row,column=displayedColumn)
                self.addLabelList[column].config(text=self.df.columns[column])
                displayedColumn+=1
                
        
        self.addToplevel.deiconify()
        #self.addToplevel.geometry(f'{50+200*sum([self.infoAddVarList[i].get()==1 for i in range(len(self.df.columns))])}x120+0+{self.master.winfo_pointery()}')

        return    

    def addEnterPressed(self,i):
        '''
        Sequence for when the Enter key is pressed while the "Add" toplevel is in focus.        

        Parameters
        ----------
        i : TYPE
            DESCRIPTION.

        Returns
        -------
        None.

        '''
        widget =self.addToplevel.focus_get()
        if widget.master in self.addFrameList:
            index = self.addFrameList.index(widget.master)
            for column in range(len(self.df.columns)):
                if self.addFrameList[column].winfo_ismapped():
                    entry = self.addEntryList[column]
                    if len(entry.get())<=0:
                        entry.focus_set()
                        self.autoCaps(widget)
                        break
            else:
                self.addDFNewRow()
    def addConfigureEntry(self):
        widget=self.master.focus_get()

        if widget in self.addCheckList:
            column=self.addCheckList.index(widget)
            if self.addVarList[column].get()==1:
                self.addEntryList[column].config(state='normal')
            else:
                self.addEntryList[column].config(state='disabled')
    def addButton1(self,i=None):
        if self.addFrame.winfo_ismapped():
            widget=self.master.focus_get()

            self.master.after(500,lambda:infoAddSaveFileData(widget))        
            
            if widget in self.addEntryList:
                entries = self.addEntryList.copy()
                entries.remove(widget)
                for entry in entries:
                    self.autoCaps(entry)
    
    #Info toplevel related stuff
    
    def infoAddCheckbuttonPressed(self,i=None):
        #def infoAddSaveFileData():
        widget = self.master.focus_get()
        if widget in self.infoAddCheckList:
            self.fileData.loc[self.filePath,'addColumns']= ','.join([str(self.infoAddVarList[i].get()) for i in range(len(self.df.columns))])
        #self.master.after(2000,infoAddSaveFileData)
        return
    
    def infoAnalysisReset(self):
        self.infoAnalysisColumnSelectCombobox['values']=[]
        self.infoAnalysisColumnSelectCombobox.set('')
        self.infoAnalysisClearFilters()
        self.infoAnalysisClearEntries()
        self.infoAnalysisAddFilter()
        #self.infoAnalysisFilterFrame.grid_remove()
    def infoAnalysisClearEntries(self):
        for i in range(len(self.infoAnalysisEntryLabelList)):
            self.infoAnalysisEntryList[i].grid()
            self.infoAnalysisComboboxList[i].grid_remove()
            
            self.infoAnalysisEntryList[i].config(state='normal')
            self.infoAnalysisComboboxList[i].config(state='readonly')
            
            self.infoAnalysisEntryLabelList[i].config(text='')
            self.infoAnalysisComboboxList[i].set('...')
            self.infoAnalysisComboboxList[i]['values']=[]
            self.infoAnalysisEntryList[i].delete(0,tk.END)
            
            self.infoAnalysisEntryList[i].config(state='disabled')
    def infoAnalysisClearFilters(self):
        for i in range(len(self.infoAnalysisFilterFrameList)):
            self.infoAnalysisFilterColumnComboboxList[i]['values']=[]
            self.infoAnalysisFilterOperatorComboboxList[i]['values']=[]
            self.infoAnalysisFilterOperatorComboboxList[i].set('==')            
            self.infoAnalysisFilterValueComboboxList[i]['values']=[]
            self.infoAnalysisFilterColumnComboboxList[i].set('')
            self.infoAnalysisFilterOperatorComboboxList[i].set('==')            
            self.infoAnalysisFilterValueComboboxList[i].set('')
            self.infoAnalysisFilterFrameList[i].grid_remove()
            
            
        self.filters = {}
        

        
    def infoAnalysisComboboxSelected(self,i=None,data=None):
        self.infoAnalysisClearEntries()
        #self.infoAnalysisFilterFrame.grid()
        self.infoAnalysisDisplayUpdate()
    def infoAnalysisDisplayUpdate(self,data=None):
        try:
            if data==None: data=self.filteredDf.copy()
        except:
            pass
        
        column =self.infoAnalysisColumnSelectCombobox.get()
        if column=='':
            return
        index =  self.df.columns.to_list().index(column)
        dtype = self.dataTypes[self.defaultTypes[index]]
        if dtype in (int,float):
            describedData = data[column].describe()
        

            for i in range(len(self.infoAnalysisEntryLabelList)):

                if i < len(describedData.index):
                    self.infoAnalysisEntryList[i].grid()
                    self.infoAnalysisComboboxList[i].grid_remove()
                    self.infoAnalysisEntryList[i].config(state='normal')

                    self.infoAnalysisEntryLabelList[i].config(text=describedData.index[i])
                    self.infoAnalysisEntryList[i].delete(0,tk.END)
                    self.infoAnalysisEntryList[i].insert(0,describedData[describedData.index[i]])
                    
                    self.infoAnalysisEntryList[i].config(state='disabled')
                elif i==8:
                    self.infoAnalysisEntryList[i].grid()
                    self.infoAnalysisComboboxList[i].grid_remove()
                    self.infoAnalysisEntryList[i].config(state='normal')

                    self.infoAnalysisEntryLabelList[i].config(text='sum')
                    self.infoAnalysisEntryList[i].delete(0,tk.END)
                    self.infoAnalysisEntryList[i].insert(0,data[column].sum())
                    
                    self.infoAnalysisEntryList[i].config(state='disabled')
                    
        elif dtype in (str,bool):
            describedData = data[column].describe()
            for i in range(len(self.infoAnalysisEntryLabelList)):

                if i < len(describedData.index):
                    self.infoAnalysisEntryList[i].grid()
                    self.infoAnalysisComboboxList[i].grid_remove()
                    self.infoAnalysisEntryList[i].config(state='normal')

                    self.infoAnalysisEntryLabelList[i].config(text=describedData.index[i])
                    self.infoAnalysisEntryList[i].delete(0,tk.END)
                    self.infoAnalysisEntryList[i].insert(0,describedData[describedData.index[i]])
                    
                    self.infoAnalysisEntryList[i].config(state='disabled')
    def infoAnalysisFilterCombobox0Selected(self,i):
        i=0
        self.infoAnalysisFilterUpdateComboboxes(i)
        self.infoAnalysisSetFilter(i)
    def infoAnalysisFilterCombobox1Selected(self,i):
        i=1
        self.infoAnalysisFilterUpdateComboboxes(i)
        self.infoAnalysisSetFilter(i)
    def infoAnalysisFilterCombobox2Selected(self,i):
        i=2
        self.infoAnalysisFilterUpdateComboboxes(i)
        self.infoAnalysisSetFilter(i)
    def infoAnalysisFilterCombobox3Selected(self,i):
        i=3
        self.infoAnalysisFilterUpdateComboboxes(i)
        self.infoAnalysisSetFilter(i)
    def infoAnalysisFilterCombobox4Selected(self,i):
        i=4
        self.infoAnalysisFilterUpdateComboboxes(i)
        self.infoAnalysisSetFilter(i)
        pass
    def infoAnalysisFilterUpdateComboboxes(self,i):
        column=self.infoAnalysisFilterColumnComboboxList[i].get()
        if len(column)>0:
            index=self.df.columns.to_list().index(column)
            dtype = self.dataTypes[self.defaultTypes[index]]
            values=self.df[column].unique().tolist()
            self.infoAnalysisFilterValueComboboxList[i]['values']= values
            try:
                _=self.infoAnalysisFilterValueComboboxList[i].get()
                if dtype(_) not in values and _ not in values:
                    self.infoAnalysisFilterValueComboboxList[i].set('')    
                
            except Exception as e:
                self.infoAnalysisFilterValueComboboxList[i].set('')
            
            if dtype in (int,float,pd.to_datetime):
                self.infoAnalysisFilterOperatorComboboxList[i]['values']=self.analysisNumberOperatorList
            else:
                self.infoAnalysisFilterOperatorComboboxList[i]['values']=self.analysisStringOperatorList
                if self.infoAnalysisFilterOperatorComboboxList[i].get() not in self.analysisStringOperatorList:
                    self.infoAnalysisFilterOperatorComboboxList[i].set('==')
            
    def infoAnalysisSetFilter(self,i):
        column=self.infoAnalysisFilterColumnComboboxList[i].get()
        index=self.df.columns.to_list().index(column)
        dtype = self.dataTypes[self.defaultTypes[index]]
        operator = self.infoAnalysisFilterOperatorComboboxList[i].get()
        value= self.infoAnalysisFilterValueComboboxList[i].get()
        if column in self.df.columns and operator in self.analysisNumberOperatorList and value!='':
            if dtype in [str,bool] and value in self.infoAnalysisFilterValueComboboxList[i]['values'] or dtype in(int,float,pd.to_datetime):
                value=dtype(value)
                self.filters[i] = [column,operator,value]
                self.searchDataCreation()
                self.search()
                self.infoAnalysisDisplayUpdate(self.filteredDf)
            elif i in self.filters.keys():
                self.infoAnalysisRemoveFilterData(i)
                
        elif i in self.filters.keys():
                self.infoAnalysisRemoveFilterData(i)
    def filterData(self):

        self.filteredDf=self.df.copy()
        
        for i in list(self.filters.keys()):
            c,o,v = self.filters[i][0],self.filters[i][1],self.filters[i][2]
            try:
                if o == '==':
                    self.filteredDf = self.filteredDf[self.filteredDf[c]==v]
                elif o== '!=':
                    self.filteredDf = self.filteredDf[self.filteredDf[c]!=v]
                elif o =='<':
                    self.filteredDf = self.filteredDf[self.filteredDf[c]<v]
                elif o=='<=':
                    self.filteredDf = self.filteredDf[self.filteredDf[c]<=v]
                elif o=='>':
                    self.filteredDf = self.filteredDf[self.filteredDf[c]>v]
                elif o=='>=':
                    self.filteredDf = self.filteredDf[self.filteredDf[c]>=v]
            except:
                continue
                    
    def configFilterButtons(self,numVisible=None):
        limit=len(self.infoAnalysisFilterFrameList)
        if numVisible==None:numVisible = sum([self.infoAnalysisFilterFrameList[i].winfo_ismapped() for i in range(limit)])
        
        if numVisible <=1:
            self.infoAnalysisFilterRemoveButton.config(state='disabled')
        else:
            self.infoAnalysisFilterRemoveButton.config(state='normal')
        if numVisible>=limit:
            self.infoAnalysisFilterAddButton.config(state='disabled')
        else:
            self.infoAnalysisFilterAddButton.config(state='normal')
            
    def infoAnalysisAddFilter(self):
        for i in range(len(self.infoAnalysisFilterFrameList)):
            if self.infoAnalysisFilterFrameList[i].winfo_ismapped():
                continue
            self.infoAnalysisFilterFrameList[i].grid()
            break
        self.configFilterButtons(i+1)
        
    def infoAnalysisRemoveFilter(self):
        for i in range(len(self.infoAnalysisFilterFrameList)-1,-1,-1):
            if not self.infoAnalysisFilterFrameList[i].winfo_ismapped():
                continue
            self.infoAnalysisFilterFrameList[i].grid_remove()
            break
        self.configFilterButtons(i)
        self.infoAnalysisFilterColumnComboboxList[i].set('')
        self.infoAnalysisFilterOperatorComboboxList[i].set('==')            
        self.infoAnalysisFilterValueComboboxList[i].set('')
        self.infoAnalysisRemoveFilterData(i)
    def infoAnalysisRemoveFilterData(self,i):
        self.filters.pop(i)
        self.searchDataCreation()
        self.search()
        self.infoAnalysisDisplayUpdate(self.filteredDf)

    def infoOnKeyRelease(self,i=None):
        if self.master.focus_get().master in self.infoAnalysisFilterFrameList:
            #print("updated skipped")
            def checkQueryInit():
                userEntry = self.master.focus_get().get()
                
                #print("update check initiated")
                def checkQuery():
                    if userEntry == self.master.focus_get().get() and self.infoAnalysisUserEntry != userEntry:
                        self.infoAnalysisSetFilter(self.infoAnalysisFilterFrameList.index(self.master.focus_get().master))
                        self.infoAnalysisUserEntry = userEntry
                self.master.after(300, checkQuery)
            self.master.after(1,checkQueryInit)    
            
    def infoAddAutoCapsSet(self,i):
        value=self.infoAddCapsCombobox.get()
        if value in self.autoCapsValues:
            self.pref['autoCaps']=value
    def autoCaps(self,entry):
        value=entry.get()
        if value=='':
            return
        value=self.capitalize(value)
        entry.delete(0,tk.END)
        entry.insert(0,value)
    def capitalize(self,value):
        method = self.autoCapsValues.index(self.pref['autoCaps'])
        if method == 3:
            return value
        def cap(value):
            value=value.split()
            _=value.copy()
            
            for i in range(len(_)):
                value[i]=_[i].capitalize()
            return ' '.join(value)
        if method == 0:
            return cap(value)
        elif method==1:
            if not re.search('[A-Z]',value):
                return cap(value)
            else:
                return value
        elif method==2:
            if len(value)>0:
                value = value[0].upper()+value[1:]
            else:value=value.capitalize()
            return value
        
    
    #Resetting
    
    def resetPref(self):
        confirm=msg.askokcancel('Confirm Reset','Are you sure you want to set all preferences to their default values? This will close the app.')
        if confirm:
            del self.pref
            os.remove(f'{self.prefPath}/preferences.csv')
            self.onClose()
    def resetFileData(self):
        confirm=msg.askokcancel('Confirm Reset','Are you sure you want to delete all file data for every file? This will close the app.')
        if confirm:
            del self.fileData
            os.remove(f'{self.prefPath}/filedata.csv')
            self.onClose()
    def resetAll(self):
        confirm=msg.askokcancel('Confirm Reset','Are you sure you want to reset all settings and data? This will close the app.')
        if confirm:
            del self.pref
            del self.fileData
            os.remove(f'{self.prefPath}/filedata.csv')
            os.remove(f'{self.prefPath}/preferences.csv')
            self.onClose()
        
    #Things relating to emptying and closing
    def clearWidgets(self):
        for column in range(len(self.infoAddCheckList)):
            self.infoAddVarList[column].set(0)
            self.infoAddCheckList[column].config(state='disabled')
        self.editorClearEntries()
        self.clearAddToplevel()
        self.searchResults=[[]]
        self.searchClearDisplay()
        self.searchEntry.delete(0,tk.END)
        self.infoAnalysisReset()
        
        self.pageEntryUpdate(True)
    
    #File closure sequence
    def onClose(self):
        self.save()
        self.prefSave()
        self.master.destroy()

    
    
    
    