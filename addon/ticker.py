import pandas as pd
import sys
import math
import tkinter as tk
from tkinter import ttk

import re
if 'R:\Mekaill\Zeug\python\pkgs' not in sys.path: sys.path.append('R:\Mekaill\Zeug\python\pkgs')

import datetime as dt
import catalogue as cat

class ticker():
    def __init__(self):
        
        self.cat=cat.catalogue('R:\Mekaill\Zeug\python\jlp\data.csv')
        self.mainWin=self.cat.mainWin
        self.defaultAmount=750
        self.defaultAmountText='previous'

        self.infoWin=self.cat.infoWin
        #info
        self.infoSideFrame=tk.Frame(master=self.infoWin)
        self.infoSideFrame.grid(row=0,column=4)
        def runTicker():
            self.defaultPayEntry()
            if pd.to_datetime(self.cat.df.iloc[-1]['Date']).weekday()==6:
                self.runSundayTicker()
            else: self.runTuitionTicker()
        self.runTickerButton=ttk.Button(master=self.infoSideFrame,text='Run Ticker',command=runTicker)
        self.runTickerButton.grid(row=2,column=0,sticky='w')
        
        self.payCalcFrame=tk.Frame(master=self.infoSideFrame)
        self.payCalcFrame.grid(row=0,column=0)
        
        self.payCalcSubFrame=tk.Frame(master=self.payCalcFrame)
        self.payCalcSubFrame.grid(row=0,column=0)
        self.payCalcCombobox=ttk.Combobox(master=self.payCalcSubFrame,state='readonly')
        
        
        self.payCalcMonths=[]
        
        self.payCalcCombobox.grid(row=0,column=0,sticky='e')
        
        self.payCalcOutputLabel=ttk.Label(master=self.payCalcSubFrame,state='readonly',relief='groove',width=15)
        self.payCalcOutputLabel.grid(row=0,column=1,sticky='w')
        
        self.payCalcLabel=ttk.Label(master=self.payCalcFrame,text='The amount owed in selected month',foreground='grey')
        self.payCalcLabel.grid(row=1,column=0,sticky='w')
        
        self.payEntryFrame = tk.Frame(master=self.infoSideFrame)
        self.payEntryFrame.grid(row=1,column=0,pady=10,sticky='w')
        
        self.payEntry = ttk.Entry(master=self.payEntryFrame,width=23,foreground='lightgrey')
        self.payEntry.insert(0,self.defaultAmountText)
        self.payEntry.grid(row=0,column=0,sticky='w')
        
        self.payEntryLabel = ttk.Label(master=self.payEntryFrame,text='Current pay per day',foreground='grey')
        self.payEntryLabel.grid(row=1,column=0,sticky='w')
        
        self.payCalcCombobox.bind('<<ComboboxSelected>>',self.payCalc)
        self.payCalcCombobox.bind('<1>',self.findPayPeriod)

        self.payEntry.bind('<1>',self.configPayEntry)
        self.findPayPeriod()

        self.mainWin.mainloop()
        
    def runSundayTicker(self):
        #path=f'{sys.path[0]}\\data.csv'
        
        '''def checkFolder():
            global df
            global index
            global tuitionDf
            index={}
            try:
                tuitionDf=pd.read_csv(str(path[:-8]+'tuition_'+path[-8:]),index_col=0)
            except:
                tuitionDf=pd.DataFrame(columns=['Date','Amount','Opened'])
            else:
                index['tuition']=tuitionDf.index[-1]+1
            try:
            	df=pd.read_csv(path,index_col=0)
            except:
            	df=pd.DataFrame(columns=['Date','Amount','Opened'])
            	index=0
            else: index['sunday']=df.index[-1]+1
        checkFolder()'''
        
        #_=input('Was the library opened? :')
        #if re.search('[ty]',_):opened=True
        #else:
        #    opened=False
        
        
        try:
            paydays=int(((pd.to_datetime('today',utc=True)-pd.to_datetime(self.cat.df.iloc[-1]['Date'],utc=True)).days/7))
        except:paydays=1
        
        #try:
        #    tuitionPaydays=math.ceil((pd.to_datetime('today',utc=True)-pd.to_datetime(df.iloc[-1]['Date'],utc=True)).days*3/7)
        #except:
        #    tuitionPaydays=1
            
        
        lastSunday=pd.to_datetime('today')-pd.Timedelta(f'{dt.datetime.today().weekday()+1} days')
        #lastTuitionDayOffset=-6
        #while dt.datetime.today().weekday()-lastTuitionDayOffset not in (1,3,5): 
        #    lastTuitionDayOffset+=1
        
        #lastTuitionDay=pd.to_datetime('today')-pd.Timedelta(f'{dt.datetime.today().weekday()-1} days')
        
        for n in range(paydays):
            date= (lastSunday - pd.Timedelta(f'{((paydays-n)-1)*7} days')).tz_localize('UTC')
            self.cat.confirmAdd([date,self.defaultAmount,True,'-'])
    def runTuitionTicker(self):
        #self.tDf=self.cat.df.copy()
        #self.tDf['Day']=[pd.to_datetime(i).weekday() for i in self.cat.df['Date']]
        day=pd.to_datetime(self.cat.df.iloc[-1]['Date']).weekday()
        dayOffset=2

        if day >5: 
            day=1
            dayOffset=2
        while day not in [1,3,5]:
            day+=1
            dayOffset=1
        print(day)
        while pd.to_datetime('now',utc=True) - (pd.to_datetime(self.cat.df.iloc[-1]['Date'],utc=True)+pd.Timedelta(f'{dayOffset} days')) > pd.Timedelta('0 days'):
            day=(pd.to_datetime(self.cat.df.iloc[-1]['Date'])+pd.Timedelta(f'{dayOffset} days')).weekday()
            if day not in [1,3,5]:
                dayOffset+=1
            else:
                self.cat.confirmAdd([(pd.to_datetime(self.cat.df.iloc[-1]['Date'])+pd.Timedelta(f'{dayOffset} days')),self.defaultAmount,True,'-'])
                dayOffset=2

            
                
                
               
                
        
        return
    def defaultPayEntry(self):
        if self.payEntry.get()==self.defaultAmountText:
            self.payEntry.delete(0,'end')
            self.payEntry.insert(0,self.cat.df.iloc[-1]['Amount'])
            self.payEntry.config(foreground='black')
            self.defaultAmount=self.cat.df.iloc[-1]['Amount']
        elif len(self.payEntry.get())==0:
            self.payEntry.insert(0,self.defaultAmountText)
            self.payEntry.config(foreground='lightgrey')
            self.defaultAmount=self.cat.df.iloc[-1]['Amount']
        else:
            self.defaultAmount=self.payEntry.get()
    def configPayEntry(self,i=None):
        if self.payEntry.get()==self.defaultAmountText:
            self.payEntry.delete(0,'end')
            self.payEntry.config(foreground='black')
    def findPayPeriod(self,i=None):
        
        self.calcDf=self.cat.df.copy()
        self.calcDf['Month']=[pd.to_datetime(i).month for i in self.cat.df['Date']]
        self.calcDf['Year']=[pd.to_datetime(i).year for i in self.cat.df['Date']]
        
        
        self.months=['January',
         'February',
         'March',
         'April',
         'May',
         'June',
         'July',
         'August',
         'September',
         'October',
         'November',
         'December']
        self.payMonths = []
        i = self.calcDf.iloc[-1]
        for y in self.calcDf['Year'].unique():
            for m in range(len(self.months)):
                if len(self.calcDf[(self.calcDf['Month']==m+1)&(self.calcDf['Year']==int(y))]) > 0: self.payMonths.append(self.months[m] + ' ' + str(y))
                if m+1==i['Month'] and y==i['Year']:break                
                
                
            
        self.payCalcCombobox['values'] = self.payMonths
        self.payCalcCombobox.set('')
        return
            
    def payCalc(self,a=None):
        pay=0
        m,y=self.payCalcCombobox.get().split(' ')
        months = self.calcDf[(self.calcDf['Month']==self.months.index(m)+1)&(self.calcDf['Year']==int(y))]
        for i in months.index:
            pay+=self.cat.df.loc[i,'Amount']
        self.payCalcOutputLabel['text']=pay
            
_=ticker()