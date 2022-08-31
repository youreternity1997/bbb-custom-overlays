# -*- coding: utf-8 -*-
"""
Created on Sat May 30 13:36:35 2020

@author: hutton
"""
import configparser
import tkinter as tk
from  tkinter  import ttk
from datetime import timedelta
import time
import datetime as dt
import sqlite3
import logging
import threading
import json
import re
from api.barcode_scanner_serial import BarcodeScanner
from api.camera import VideoCapture
from api.printer import Printer
from api.screenlock import ScreenLock
from api.dateentry import DateEntry
from api.detect_battery import Detect_Battery
from api.batteryV2 import BatteryV2
from PIL import Image, ImageTk, ImageFilter
import cv2
import os
import zxing
import time
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as pathches
from Light_corr_pack.light_correct import creat_cor 
from MED.gen_th import MED
from collections import deque
from statistics import mean
import tkinter.font as tkFont
import zipfile
import glob
import shutil
import time

tab_height = 80
bar_height = 25
main_height = 478 - bar_height -tab_height
other_heitht = 478 - bar_height
TESTLOADINGTIME = 330
ONETOONE = 0
ONETOMORE = 1
NOWAIT = 2
ADMIN = False
resol = "./1280x720"
whitephoto = resol+"/"+"white1.jpg"
# randomly put
photoname = resol+"/"+"QRcode.jpg"
imgdir = "/home/debian/Drug_Detector/data_image_folder/"
threshold = [[8,8,8,10],[8,8,8,10],[8,8,8,10]]
# get from barcode
#line_loc_th_0=[116,116+50,168,168+50,215,215+50,300,300+50]
#line_loc_th_1=[113,113+50,186,186+50,250,250+50,354,354+50]
#line_loc_th_2=[145,145+50,209,209+50,286,286+50,358,358+40]
#line_loc_th=[line_loc_th_0,line_loc_th_1,line_loc_th_2]
button_bg = 'white'
frame_bg = '#d8d8d8'
day_backlight='100'
night_backlight='50'

class DrugDetectorApp(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self.title('Drug Detector')
        self.geometry('272x478')
        self.configure(background=button_bg)
        self.conf = {}
        self.settingConf = {}
        self._barframe = None
        self._mainframe = None
        self._tabframe = None
        self.dateTime = dt.datetime.now()
        self.afterJID = None
        self.camera = None
        self.inspectorId = ""
        self.all_fonts = {}
        self.pressedIndex = -1
        self.Languagevalue = tk.StringVar()
        self.Languagevalue.set("中文")

        self.init_language()
        self.init_devices()
        self.init_images()
        self.init_db_conn()
        self.init_fonts()
        self.init_time_second()
        self.back_main_frame(WelcomePage)
        self.screensaver = ScreenLock()
		
    def init_fonts(self):
        self.all_fonts = {
                "中文":{
                    "bigger_label": tkFont.Font(family="helvetica", size=30),
                    "time_label": tkFont.Font(family="helvetica", size=25),
                    "general": tkFont.Font(family="helvetica", size=18, weight="bold"),
                    "middle_label": tkFont.Font(family="helvetica", size=15),
                    "bar_label": tkFont.Font(family="helvetica", size=12),
                    "small_label": tkFont.Font(family="helvetica", size=10),
                },
                "English":{ 
                    "bigger_label": tkFont.Font(family="MS UI Gothic", size=30),
                    "time_label": tkFont.Font(family="MS UI Gothic", size=25),
                    "general": tkFont.Font(family="MS UI Gothic", size=18, weight="bold"),
                    "middle_label": tkFont.Font(family="MS UI Gothic", size=13),
                    "bar_label": tkFont.Font(family="MS UI Gothic", size=12),
                    "small_label": tkFont.Font(family="MS UI Gothic", size=10),
                }
            }
    def init_devices(self):
        Cameras = []
        Camera_path = glob.glob('/dev/vi*') # ('dev/video1')
        print('Camera_path=', Camera_path)
        
        if Camera_path == []:
             print('No any camera captured')
        else:
            # Check all cameras
            for Camera_name in Camera_path:
                Camera_id = int(Camera_name[-1]) # 1 or 0 else
                cap = cv2.VideoCapture(Camera_id)
                cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))
                cap.set(cv2.CAP_PROP_FPS, 5)
                cap.set(cv2.CAP_PROP_EXPOSURE, 0.015)
                cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
                cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
                success, frame = cap.read()
                if not success:
                    print('Error: video('+str(Camera_id)+') can not read')
                else:
                    print('video('+str(Camera_id)+') successly read')
                    Cameras.append(Camera_id)
                    cap.release()
            # Asign only camera
            try:
                self.camera = VideoCapture(Cameras[0], 720, 1280)
            except:
                print('Error: System Captures camera but can not read')
                        

    def init_language(self):
        # 創建對象
        self.conf = configparser.ConfigParser()
        # 讀取INI
        self.conf.read("DD_chinese.ini", encoding='utf-8')

    def init_images(self):
        self.images = {"system": tk.PhotoImage(file = "images/icon/settings_36dp.png"),
                       "testing": tk.PhotoImage(file = "images/icon/testing_32dp.png"),
                       "search": tk.PhotoImage(file = "images/icon/search_36dp.png"),
                       "export": tk.PhotoImage(file = "images/icon/export_36dp.png"),
                       "usb": tk.PhotoImage(file = "images/icon/usb_48dp.png"),
                       "power100": tk.PhotoImage(file = "images/icon/battery/power100.png"),
		       "power75": tk.PhotoImage(file = "images/icon/battery/power75.png"),
                       "power50": tk.PhotoImage(file = "images/icon/battery/power40.png"),
                       "power25": tk.PhotoImage(file = "images/icon/battery/power20.png"),
                       "power0": tk.PhotoImage(file = "images/icon/battery/power0.png"),
                       "charging": tk.PhotoImage(file = "images/icon/battery/charging.png"),
                       "bg": tk.PhotoImage(file = "images/icon/bg.png"),
                       "logo": tk.PhotoImage(file = "images/icon/other_pic.png"),
                       "scan": tk.PhotoImage(file = "images/icon/barcodescan.png"),
                       "date_picker": tk.PhotoImage(file = "images/icon/date_picker.png")}
        self.frames = [tk.PhotoImage(file='images/load.gif',format = 'gif -index %i' %(i)) for i in range(12)]

    def init_db_conn(self):
        try:
            conn = sqlite3.connect("DD.db")
            sql = "create table if not exists users (id_card varchar(20) primary key, sex int, birth date, phone varchar(10) NULL);"
            conn.execute(sql)
            conn.commit()
            sql = "create table if not exists results (tid INTEGER  primary key AUTOINCREMENT, id_card varchar(20), did int not null, car varchar(20), test_date Datetime, type varchar(10), expire_date varchar(8), lot varchar(8), serial_number varchar(9), result text, CONSTRAINT fk_departments FOREIGN KEY (id_card) REFERENCES users(id_card) );"
            conn.execute(sql)
            conn.commit()
            sql = "CREATE TABLE IF NOT EXISTS cape ( cape_id integer PRIMARY KEY AUTOINCREMENT, type text NOT NULL Unique, T1_A text DEFAULT NA ,T2_A text DEFAULT NA ,T3_A text DEFAULT NA ,T1_B text DEFAULT NA ,T2_B text DEFAULT NA ,T3_B text DEFAULT NA ,T1_C text DEFAULT NA ,T2_C text DEFAULT NA ,T3_C text DEFAULT NA);" 
            conn.execute(sql)
            conn.commit()
            sql = "CREATE TABLE IF NOT EXISTS drug ( drug_id integer PRIMARY KEY AUTOINCREMENT, name text NOT NULL Unique, density_thres integer NOT NULL, gradient_thres integer NOT NULL );"
            conn.execute(sql)
            conn.commit()
            conn.close()
        except ValueError:
            logging.error('Connetion error!')

    def init_time_second(self):
        self.settingConf = configparser.ConfigParser()
        self.settingConf.read('../share/DD_setting.ini', encoding='utf-8')

    def back_main_frame(self, frame_class):
        self.grid_columnconfigure(0, weight=1)
        # Main bar on the top
        if self._barframe is None:
            self._barframe = BarPage(self)
            self._barframe.grid(column=0, row=0, sticky="nsew")
            self._barframe.grid_propagate(0)
            self._barframe.pack_propagate(0)
        # Main page on the middle
        new_frame = frame_class(self)
        if self._mainframe is not None:
            self._mainframe.destroy()
        self._mainframe = new_frame
        self._mainframe.grid(column=0, row=1, padx=7, sticky="nsew")
        self._mainframe.grid_propagate(0)
        self._mainframe.pack_propagate(0)
        if self._tabframe is None:
            # Main tab on the bottom
            self._tabframe = TabPage(self)
            self._tabframe.grid(column=0, row=2, sticky="nsew", padx=5, pady=5)
            self._tabframe.grid_propagate(0)
            self._tabframe.pack_propagate(0)

    def switch_main_frame(self, frame_class):
        # Main page on the middle
        new_frame = frame_class(self)
        if self._mainframe is not None:
            self._mainframe.destroy()
        self._mainframe = new_frame
        self._mainframe.grid(column=0, row=1, padx=7, sticky="nsew")
        self._mainframe.grid_propagate(0)
        self._mainframe.pack_propagate(0)

    def switch_input_frame(self, entry, *args):
        self._inputframe = VKeyboard(self, entry, *args)
        self._inputframe.grid(column=0, row=1, sticky="nsew")
        self._inputframe.grid_propagate(0)
        self._inputframe.pack_propagate(0)

    def switch_frame(self, frame_class, *args):
        if self._tabframe is not None:
            self._tabframe.destroy()
            self._tabframe = None
        new_frame = frame_class(self, *args)
        if self._mainframe is not None:
            self._mainframe.destroy()
        self._mainframe = new_frame
        self._mainframe.grid(column=0, row=1, padx=7, pady=(5,10), sticky="nsew")
        self._mainframe.grid_propagate(0)
        self._mainframe.pack_propagate(0)

class VKeyboard(tk.Frame):
    def __init__(self, master, entry, title, max_word = 0):
        tk.Frame.__init__(self, master)
        tk.Frame.configure(self,bg=frame_bg)

        self.entryFrame = tk.Frame(self, bg=frame_bg)
        self.entry = entry
        self.topTextVar = tk.StringVar()
        self.topTextVar.set(entry.get())
        self.topLevelEntry = tk.Entry(self.entryFrame, font=master.all_fonts[master.Languagevalue.get()]["bar_label"], width=20, textvariable = self.topTextVar)
        if max_word > 0:
            self.topTextVar.trace("w", lambda *args: self.del_word(self.entry, max_word))
            self.topTextVar.trace("w", lambda *args: self.del_word(self.topLevelEntry, max_word))

        self.topLevelEntry.pack(pady = 5,side=tk.LEFT)
        tk.Button(self.entryFrame, text=master.conf['main_page_section']['btn_ok'], font=master.all_fonts[master.Languagevalue.get()]["bar_label"],
                  command=lambda inputframe=self: self.back_frame(inputframe)).pack(padx= 10, side=tk.LEFT)
        tk.Label(self, text=title, font=master.all_fonts[master.Languagevalue.get()]["bar_label"],bg=frame_bg).pack(pady=5)
        self.entryFrame.pack()
        self.create()

    def select(self, entry, value):
        global uppercase
        uppercase = False

        if value == "Space":
            value = ' '
        elif value == 'Enter':
            value = '\n'
        elif value == 'Tab':
            value = '\t'

        if value == "Del":
            if isinstance(entry, tk.Entry):
                entry.delete(len(entry.get())-1, 'end')
                self.topLevelEntry.delete(len(self.topLevelEntry.get())-1, 'end')
            else: # tk.Text
                entry.delete('end - 2c', 'end')
                self.topLevelEntry.delete('end - 2c', 'end')
        elif value in ('Caps Lock', 'Shift'):
            uppercase = not uppercase # change True to False, or False to True
        elif value =='Eng':
            self.kb_num.pack_forget()
            self.kb_en.pack(fill='x', side=tk.BOTTOM)
        elif value =='123':
            self.kb_en.pack_forget()
            self.kb_num.pack(fill='x', side=tk.BOTTOM)
        else:
            if uppercase:
                value = value.upper()
            entry.insert('end', value)
            self.topLevelEntry.insert('end', value)
        return
    def create(self):
        alphabets_num = [
        ['+','1','2','3'],
        ['*','4','5','6'],
        ['/','7','8','9'],
        ['Eng','-','0','Del']
        ]
        alphabets_en = [
        ['A','B','C','D'],
        ['E','F','G','H'],
        ['I','J','K','L'],
        ['M','N','O','P'],
        ['Q','R','S','T'],
        ['U','V','W','X'],
        ['123','Y','Z','Del']
        ]
        self.kb_num = tk.Frame(self)
        self.kb_en = tk.Frame(self)
        for y, row in enumerate(alphabets_num):

            x = 0

            for text in row:

                if self.master.Languagevalue.get()=="English":
                    width= 4
                else:
                    width = 5
                height = 2
                columnspan = 1

                tk.Button(self.kb_num, text=text, width=width,height=height,font=self.master.all_fonts[self.master.Languagevalue.get()]["middle_label"],
                          command=lambda value=text: self.select(self.entry, value),
                          padx=3, pady=3, bd=1,bg="#ebebeb", fg="black", takefocus = False
                         ).grid(row=y, column=x, columnspan=columnspan)

                x+= columnspan

        for y, row in enumerate(alphabets_en):

            x = 0

            for text in row:

                if self.master.Languagevalue.get()=="English":
                    width= 4
                else:
                    width = 5
                height = 2
                columnspan = 1

                tk.Button(self.kb_en, text=text, width=width,height=height,font=self.master.all_fonts[self.master.Languagevalue.get()]["middle_label"],
                          command=lambda value=text: self.select(self.entry, value),
                          padx=3, pady=1, bd=1,bg="#ebebeb", fg="black", takefocus = False
                         ).grid(row=y, column=x, columnspan=columnspan)

                x+= columnspan
        self.kb_num.pack(fill='x', side=tk.BOTTOM)

    def back_frame(self, inputframe):
        inputframe.destroy()

    def del_word(self, entry, max_word):
        data = entry.get()
        if len(data) > max_word:
            entry.delete(0, len(data))
            entry.insert(0, data[-1:])

'''
Main Page
'''
class TabPage(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        self.configure(height=tab_height, bg=button_bg)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=1)
        self.grid_columnconfigure(3, weight=1)
        self.all_pages = [SystemPage, TestingPage, SearchPage, ExportPage]
        self.tab_buttons = {}
        #tk.Button(self, text=master.conf['main_page_section']['btn_system'], image=master.images['system'], compound = tk.TOP, bg=button_bg, bd=1, highlightthickness=0, activebackground='#9ca4ab',command=lambda: self.pressed(1)).grid(column=3,row=0,sticky="nsew")
        self.tab_buttons[0] = tk.Button(self, text=master.conf['main_page_section']['btn_system'], image=master.images['system'], compound = tk.TOP, bg=button_bg, bd=1, highlightthickness=0, activebackground='#9ca4ab', command= lambda: self.pressed(0))
        self.tab_buttons[1] = tk.Button(self, text=master.conf['main_page_section']['btn_testing'], image=master.images['testing'], compound = tk.TOP, bg=button_bg, bd=1, highlightthickness=0, activebackground='#9ca4ab',command=lambda: self.pressed(1))
        self.tab_buttons[2] = tk.Button(self, text=master.conf['main_page_section']['btn_search'], image=master.images['search'], compound = tk.TOP, bg=button_bg, bd=1, highlightthickness=0, activebackground='#9ca4ab',command=lambda: self.pressed(2))
        self.tab_buttons[3] = tk.Button(self, text=master.conf['main_page_section']['btn_export'], image=master.images['export'], compound = tk.TOP, bg=button_bg,  bd=1, highlightthickness=0, activebackground='#9ca4ab',command=lambda: self.pressed(3))
        for i in range(4):
            self.tab_buttons[i].grid(column=i, row=0, padx=2, sticky="nsew")
        if master.pressedIndex!=-1:
            for i in range(4): 
                self.tab_buttons[i].configure(bg=button_bg)
            self.tab_buttons[master.pressedIndex].configure(bg='#9ca4ab')
    def pressed(self, index):
        self.master.pressedIndex=index
        for i in range(4): 
            self.tab_buttons[i].configure(bg=button_bg)
        self.tab_buttons[index].configure(bg='#9ca4ab')
        if index==2:
            self.master.switch_frame(self.all_pages[index])
        self.master.switch_main_frame(self.all_pages[index])


class BarPage(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        tk.Frame.configure(self, height=bar_height,bg=button_bg)

        self.timeSettingSec = timedelta(seconds=int(master.settingConf['Datetime']['seconds']))
        self.timeSettingDay = timedelta(days=int(master.settingConf['Datetime']['days']))

        master.dateTime = dt.datetime.now() + self.timeSettingDay + self.timeSettingSec

        self.date = tk.StringVar()
        self.date.set((dt.datetime.now() + self.timeSettingDay + self.timeSettingSec).strftime("%Y/%m/%d"))

        self.time = tk.StringVar()
        self.time.set((dt.datetime.now() + self.timeSettingDay + self.timeSettingSec).strftime("%H:%M"))
        self.datelabel = tk.Label(self, textvariable=self.date, bg=button_bg, font=master.all_fonts[master.Languagevalue.get()]['bar_label']).pack(side="left", fill="x")
        self.powerlabel = tk.Label(self, image=master.images['power100'], bg=button_bg)
        self.powerlabel.pack(side="right", fill="x", padx=10)
        self.timelabel = tk.Label(self, textvariable=self.time, bg=button_bg, font=master.all_fonts[master.Languagevalue.get()]['bar_label']).pack(side="right", fill="x")
        self.toggleBtn = tk.Button(self, text=master.conf['bar_page_section']['btn_day'], font=master.all_fonts[master.Languagevalue.get()]['bar_label'], relief="raised", command=self.toggle)
        os.system("echo " +day_backlight+">/sys/class/backlight/backlight/brightness")
        self.toggleBtn.pack()
        self.update_clock()
        self.t1 = threading.Thread(target = lambda: self.init_detect_BatteryV2())
        self.t1.daemon = True
        self.t1.start()
        
    def toggle(self):
        if self.toggleBtn.config('relief')[-1] == 'sunken':
            self.toggleBtn.config(relief="raised")
            self.toggleBtn.config(text=self.master.conf['bar_page_section']['btn_day'])
            os.system("echo "+day_backlight+" > /sys/class/backlight/backlight/brightness")
        else:
            self.toggleBtn.config(relief="sunken")
            self.toggleBtn.config(text=self.master.conf['bar_page_section']['btn_night'])
            os.system("echo "+night_backlight+" > /sys/class/backlight/backlight/brightness")

    def init_detect_BatteryV2(self):
        def callback_BatteryCharge(channel):
            print("channel " + channel)
            self.powerlabel.configure(image=self.master.images['charging'])
            self.powerlabel.image = self.master.images['charging']
            b.level = 'charging'
        try:
            b = BatteryV2("P9_30", "P9_40", callback_BatteryCharge)
        except (TypeError, NameError, Exception) as exc:
            raise RuntimeError("Failed to ceate BatteryV2") from exc
        else:
            b.setUp()

        while True:
            if b.isCharge() == 1:
                print("volatge " + str(b.voltage()))
                # input voltage
                # voltage = float(input("input voltage:"))
                voltage = b.voltage()

                try:
                    level = b.batteryLevel(voltage)
                    print("battery level " + level)
                except (TypeError) as exc:
                    print("battery TypeError")
 
                if b.level != level:
                    self.powerlabel.configure(image=self.master.images[level])
                    self.powerlabel.image = self.master.images[level]
                    b.level = level

                if level == "power0":
                    root = tk.Tk()
                    # root.geometry('300x200')
                    root.resizable(False, False)
                    root.title('Battery Low')
                    message = tk.Label(root, text="Force to shut down system")
                    message.pack()

            time.sleep(1)

    def init_detect_battery(self):
        window = deque(maxlen=1)
        detector = Detect_Battery()
        while 1:
            conn, volt = detector.detect()
            window.append(volt)
            voltage = mean(window)
            if conn == 0:
                self.powerlabel.configure(image=self.master.images['charging'])
                self.powerlabel.image = self.master.images['charging']
            elif voltage > 1.68:
                self.powerlabel.configure(image=self.master.images['power100'])
                self.powerlabel.image = self.master.images['power100']
            elif voltage > 1.58:
                self.powerlabel.configure(image=self.master.images['power75'])
                self.powerlabel.image = self.master.images['power75']
            elif voltage > 1.48:
                self.powerlabel.configure(image=self.master.images['power50'])
                self.powerlabel.image = self.master.images['power50']
            elif voltage > 1.4:
                self.powerlabel.configure(image=self.master.images['power25'])
                self.powerlabel.image = self.master.images['power25']
            elif voltage <= 1.4:
                self.powerlabel.configure(image=self.master.images['power0'])
                self.powerlabel.image = self.master.images['power0']
            time.sleep(1)

    def update_clock(self):
        self.timeSettingSec = timedelta(seconds=int(self.master.settingConf['Datetime']['seconds']))
        self.timeSettingDay = timedelta(days=int(self.master.settingConf['Datetime']['days']))
        self.master.dateTime = dt.datetime.now() + self.timeSettingDay + self.timeSettingSec
        self.date.set((dt.datetime.now() + self.timeSettingDay + self.timeSettingSec).strftime("%Y/%m/%d"))
        self.time.set((dt.datetime.now() + self.timeSettingDay + self.timeSettingSec).strftime("%H:%M"))
        if self.master.afterJID is not None:
            self.master.after_cancel(self.master.afterJID)
        self.master.afterJID = self.master.after(1000, self.update_clock)

class WelcomePage(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        self.configure(height=main_height)
        tk.Frame.configure(self, bg=frame_bg)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        tk.Label(self, text=master.conf['main_page_section']['label_welcome'], compound = tk.CENTER, font=master.all_fonts[master.Languagevalue.get()]['general'],
                 bg=frame_bg).grid(column=0, row=0, sticky="nsew")

'''
System Flow Page
'''
class SystemPage(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        self.configure(height=main_height)
        tk.Frame.configure(self,bg=frame_bg)
        print(master.Languagevalue.get())
        tk.Button(self, text=master.conf['system_page_section']['btn_timeSetting'], bg=button_bg, font=master.all_fonts[master.Languagevalue.get()]["general"], height=2,
                  command=lambda: master.switch_frame(SetTimePage)).pack(padx = 10,pady = 30, fill='both', anchor='center')
        tk.Button(self, text=master.conf['system_page_section']['btn_languageSetting'], bg=button_bg, font=master.all_fonts[master.Languagevalue.get()]["general"], height=2,
                  command=lambda: master.switch_frame(LanguagePage)).pack(padx = 10, fill='both')
        tk.Button(self, text=master.conf['system_page_section']['btn_testingPaperAdjust'], bg=button_bg, font=master.all_fonts[master.Languagevalue.get()]["general"], height=2,
                  command=lambda: master.switch_frame(TestPaperPage)).pack(padx = 10,pady = 30, fill='both')

class SetTimePage(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        self.configure(height=other_heitht)
        self.pack_propagate(0)
        tk.Frame.configure(self,bg=frame_bg)
        self.valid_date = True

        tk.Label(self, text=master.conf['system_page_section']['btn_timeSetting'], font=master.all_fonts[master.Languagevalue.get()]["general"],bg=frame_bg).pack(pady=10)
        self.dateTime = master.dateTime
        self.switch_input_frame = master.switch_input_frame
        self.conf = master.conf
        style = ttk.Style()
        style.configure('TCombobox', arrowsize=30)
        style.configure('Vertical.TScrollbar', arrowsize=28)
        self.option_add('*TCombobox*Listbox.font', master.all_fonts[master.Languagevalue.get()]["time_label"])
        self.entry_frame = DateEntry(self)
        self.entry_frame.pack(padx=10)
        tk.Label(self, text=master.conf['system_page_section']['label_timeSettingHour'], font=master.all_fonts[master.Languagevalue.get()]["bar_label"],bg=frame_bg).pack(pady = 5)
        self.hourstr = tk.StringVar()
        self.hourstr.set(master.dateTime.hour)
        self.hourselect = ttk.Combobox(self,value=list(range(0,24)), width=12, font=master.all_fonts[master.Languagevalue.get()]["time_label"], textvariable=self.hourstr, height=5).pack()
        
        tk.Label(self, text=master.conf['system_page_section']['label_timeSettingMinute'], font=master.all_fonts[master.Languagevalue.get()]["bar_label"],bg=frame_bg).pack(pady = 5)
        self.minstr = tk.StringVar()
        self.minstr.set(master.dateTime.minute)
        ttk.Combobox(self,value=list(range(0,60)), width=12, font=master.all_fonts[master.Languagevalue.get()]["time_label"], textvariable=self.minstr, height=5).pack()
        
        

        tk.Button(self, text=master.conf['main_page_section']['btn_cancel'], font=master.all_fonts[master.Languagevalue.get()]["general"], bg=button_bg, height=2,
                  command=lambda: master.back_main_frame(SystemPage)).pack(padx = 10, pady = 10, fill='both', side=tk.BOTTOM)
        self.confirm_btn = tk.Button(self, text=master.conf['main_page_section']['btn_ok'], font=master.all_fonts[master.Languagevalue.get()]["general"], bg=button_bg, height=2,
                  command=lambda: self.setDate(master))
        self.confirm_btn.pack(padx = 10, pady = 10, fill='both', side=tk.BOTTOM)

    def setDate(self, master):
        year = int(self.entry_frame.year.get())
        month = int(self.entry_frame.month.get())
        day = int(self.entry_frame.day.get())
        hour = int(self.hourstr.get())
        minute = int(self.minstr.get())
        TimeSettingday = (dt.datetime(year, month, day, hour, minute)-dt.datetime.now()).days
        TimeSettingSec = (dt.datetime(year, month, day, hour, minute)-dt.datetime.now()).seconds+1
        master.settingConf.remove_option('Datetime', 'days')
        master.settingConf.remove_option('Datetime', 'seconds')
        master.settingConf.set('Datetime', 'days', str(TimeSettingday))
        master.settingConf.set('Datetime', 'seconds', str(TimeSettingSec))
        master.settingConf.write(open('../share/DD_setting.ini', 'w'))
        master.back_main_frame(SystemPage)

    def switch_button_status(self):
        if self.valid_date:
            self.confirm_btn.config(state=tk.NORMAL)
        else:
            self.confirm_btn.config(state=tk.DISABLED)

class LanguagePage(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        self.configure(height=other_heitht)
        tk.Frame.configure(self,bg=frame_bg)
        style = ttk.Style()
        style.configure('TCombobox', arrowsize=30)
        style.configure('Vertical.TScrollbar', arrowsize=28)
        self.option_add('*TCombobox*Listbox.font', master.all_fonts[master.Languagevalue.get()]["time_label"])
        tk.Label(self, text=master.conf['system_page_section']['btn_languageSetting'], font=master.all_fonts[master.Languagevalue.get()]["general"],bg=frame_bg).pack(pady = 10)
        self.LanguageBox = ttk.Combobox(self,value=["中文","English"], width=12, textvariable=master.Languagevalue, font=master.all_fonts[master.Languagevalue.get()]["time_label"])
        self.LanguageBox.pack()
        
        tk.Button(self, text=master.conf['main_page_section']['btn_cancel'], font=master.all_fonts[master.Languagevalue.get()]["general"], bg=button_bg, height=2,
                  command=lambda: master.back_main_frame(SystemPage)).pack(padx = 10, pady = 10, fill='both', side=tk.BOTTOM)
        tk.Button(self, text=master.conf['main_page_section']['btn_ok'], font=master.all_fonts[master.Languagevalue.get()]["general"], bg=button_bg, height=2,
                  command=self.go).pack(padx = 10, fill='both', side=tk.BOTTOM)

    def go(self, event=None):
        logging.debug(self.LanguageBox.get())
        if self.LanguageBox.get() == "中文":
            self.master.conf.read("DD_chinese.ini", encoding='utf-8')
            self.master.Languagevalue.set("中文")
        elif self.LanguageBox.get() == "English":
            self.master.conf.read("DD_english.ini", encoding='utf-8')
            self.master.Languagevalue.set("English")
        self.master.back_main_frame(SystemPage)

class TestPaperPage(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        self.configure(height=other_heitht)
        tk.Frame.configure(self,bg=frame_bg)
        tk.Label(self, text=master.conf['system_page_section']['btn_testingPaperAdjust'], font=master.all_fonts[master.Languagevalue.get()]["general"], bg=frame_bg).pack(pady = 10)
        tk.Button(self, text=master.conf['system_page_section']['btn_lightAdjust'], font=master.all_fonts[master.Languagevalue.get()]["general"], bg=button_bg, height=2,
                  command=lambda: master.switch_frame(LigthtPreAdjustPage)).pack(padx = 10,pady = 30, fill='both', anchor='center')
        tk.Button(self, text=master.conf['main_page_section']['btn_cancel'], font=master.all_fonts[master.Languagevalue.get()]["general"], bg=button_bg, height=2,
                  command=lambda: master.back_main_frame(SystemPage)).pack(padx = 10, pady = 10, fill='both', side=tk.BOTTOM)
        tk.Button(self, text=master.conf['system_page_section']['btn_standardCurveMaker'], font=master.all_fonts[master.Languagevalue.get()]["general"], bg=button_bg, height=2,
                  command=lambda: self.nextpage(master)).pack(padx = 10, fill='both')

    def nextpage(self, master):
        if(ADMIN == True):
            master.switch_frame(TestPaperPreAdjustPage)
        else:
            master.switch_frame(AdminLoginPage)

    def logout(self, master):
        global ADMIN
        ADMIN = False
        master.switch_frame(TestPaperPage)

class LigthtPreAdjustPage(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        self.configure(height=other_heitht)
        tk.Frame.configure(self,bg=frame_bg)
        tk.Label(self, text=master.conf['system_page_section']['btn_lightAdjust'], font=master.all_fonts[master.Languagevalue.get()]["general"],bg=frame_bg).pack(pady = 10)
        tk.Label(self, text=master.conf['system_page_section']['label_lightPreAdjust'].replace('\\n', '\n'), font=master.all_fonts[master.Languagevalue.get()]["bar_label"],bg=frame_bg).pack(pady = 10)
        if not os.path.exists('dif_array.npy') or (dt.datetime.now() - dt.datetime.fromtimestamp(float(self.master.settingConf['LightAdjust']['adjust_time']))).days >= 90:
            tk.Label(self, text=master.conf['system_page_section']['label_lightPreAdjustAlert'].replace('\\n', '\n'), font=master.all_fonts[master.Languagevalue.get()]["bar_label"], fg='red',bg=frame_bg).pack(pady = 10)
            
        tk.Button(self, text=master.conf['main_page_section']['btn_cancel'], font=master.all_fonts[master.Languagevalue.get()]["general"], bg=button_bg, height=2,
                  command=lambda: master.back_main_frame(SystemPage)).pack(padx = 10, pady = 10, fill='both', side=tk.BOTTOM)
        tk.Button(self, text=master.conf['main_page_section']['btn_ok'], font=master.all_fonts[master.Languagevalue.get()]["general"], bg=button_bg, height=2,
                  command=lambda: master.switch_frame(LigthtAdjustingPage)).pack(padx = 10, fill='both',side=tk.BOTTOM)




class LigthtAdjustingPage(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        self.configure(height=other_heitht)
        tk.Frame.configure(self,bg=frame_bg)
        tk.Label(self, text=master.conf['system_page_section']['btn_lightAdjust'], font=master.all_fonts[master.Languagevalue.get()]["general"], bg=frame_bg).pack(pady = 10)
        self.camera = master.camera
        self.camera.open()
        self.loadlabel = tk.Label(self,bg=frame_bg)
        self.loadlabel.pack(pady = 10)
        self.textlabel = tk.Label(self, text=master.conf['system_page_section']['label_lightAdjust'], font=master.all_fonts[master.Languagevalue.get()]["bar_label"],bg=frame_bg)
        self.textlabel.pack(pady = 10)
        self.cfbutton = tk.Button(self, text=master.conf['main_page_section']['btn_cancel'], font=master.all_fonts[master.Languagevalue.get()]["general"], bg=button_bg, height=2,
                  command=lambda: self.cancel())
        self.cfbutton.pack(padx = 10, pady = 10, fill='both', side=tk.BOTTOM)
        self.temp=0
        th = threading.Thread(target = self.take_snapshot, name='snap_shot')
        th.start()
        self.after(0, self.update, 0)
    def cancel(self):
        self.master.back_main_frame(SystemPage)

    def take_snapshot(self):
        time.sleep(2)
        success, img = self.camera.read()
        if success != False:
            img = cv2.flip(img, -1)
            cv2.imwrite(whitephoto, img)
            # whitephoto
            t1 = time.time()
            cor = creat_cor(whitephoto, x0=170, y0=120)
            dif_array = cor.main('false')
            t2 = time.time()
            np.save('dif_array', dif_array)
            self.temp = 2
            print('light_correct_time=', t2-t1)
            print("snapshot successful")
            self.master.settingConf.set('LightAdjust', 'adjust_time', str(dt.datetime.now().timestamp()))
            self.master.settingConf.write(open('../share/DD_setting.ini', 'w'))
        else:
            self.temp = 2
            print("snapshot error")
            self.camera.release()
            self.master.back_main_frame(SystemPage)

    def update(self, ind):
        if self.temp!=2:
            frame = self.master.frames[ind]
            ind += 1
            if ind == 12:
                ind=0
            if ind % 2 == 0:
                dot = "."
                dot = dot*(ind//2)
                self.textlabel.configure(text = self.master.conf['system_page_section']['label_lightAdjust']+dot)
            self.loadlabel.configure(image=frame)
            self.after(100, self.update, ind)
        else:
            self.loadlabel.destroy()
            self.camera.release()
            self.textlabel.configure(text = self.master.conf['system_page_section']['label_lightAdjustFinish'])
            self.cfbutton.configure(text = self.master.conf['main_page_section']['btn_ok'])

class TestPaperPreAdjustPage(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        self.configure(height=other_heitht)
        tk.Frame.configure(self,bg=frame_bg)
        tk.Label(self, text=master.conf['system_page_section']['btn_testingPaperAdjust'], font=master.all_fonts[master.Languagevalue.get()]["general"],bg=frame_bg).pack(pady = 10)
        tk.Label(self, text=master.conf['system_page_section']['label_testingPaperPreAdjust'].replace('\\n', '\n'), font=master.all_fonts[master.Languagevalue.get()]["bar_label"],bg=frame_bg).pack(pady = 10)
        tk.Button(self, text=master.conf['main_page_section']['btn_cancel'], font=master.all_fonts[master.Languagevalue.get()]["general"], bg=button_bg, height=2,
                  command=lambda: master.back_main_frame(SystemPage)).pack(padx = 10, pady = 10, fill='both', side=tk.BOTTOM)
        tk.Button(self, text=master.conf['system_page_section']['btn_testingPaperAdjustStart'], font=master.all_fonts[master.Languagevalue.get()]["general"], bg=button_bg, height=2,
                  command=lambda: master.switch_frame(InsertTestPaper0AdjustPage)).pack(padx = 10, fill='both',side=tk.BOTTOM)

class InsertTestPaper0AdjustPage(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        self.configure(height=other_heitht)
        tk.Frame.configure(self,bg=frame_bg)
        self.camera = master.camera
        self.camera.open()
        tk.Label(self, text=master.conf['system_page_section']['btn_testingPaperAdjust'], font=master.all_fonts[master.Languagevalue.get()]["general"],bg=frame_bg).pack(pady = 10)
        tk.Label(self, text=master.conf['system_page_section']['label_insertTestPaper0Adjust'].replace('\\n', '\n'), font=master.all_fonts[master.Languagevalue.get()]["bar_label"], bg=frame_bg).pack(pady = 10)
        tk.Button(self, text=master.conf['main_page_section']['btn_cancel'], font=master.all_fonts[master.Languagevalue.get()]["general"], bg=button_bg, height=2,
                  command=lambda: self.cancel()).pack(padx = 10, pady = 10, fill='both', side=tk.BOTTOM)
        tk.Button(self, text=master.conf['system_page_section']['btn_testingPaperCapture'], font=master.all_fonts[master.Languagevalue.get()]["general"], bg=button_bg, height=2,
                  command=lambda: self.take_snapshot()).pack(padx = 10, fill='both',side=tk.BOTTOM)

    def take_snapshot(self):
        time.sleep(2)
        files = glob.glob('/home/debian/Drug_Detector/standard_curve_data/*')
        for f in files:
            os.remove(f)
        success, img = self.camera.read()
        if success != False:
            img = cv2.flip(img, -1)
            cv2.imwrite('/home/debian/Drug_Detector/standard_curve_data/TestPaper0.jpg', img)
            print("snapshot successful")
            self.camera.release()
            self.master.switch_frame(InsertTestPaperNAdjustPage)
        else:
            self.camera.release()
            self.master.back_main_frame(SystemPage)
            print("snapshot error")

    def cancel(self):
        self.camera.release()
        self.master.back_main_frame(SystemPage)


class InsertTestPaperNAdjustPage(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        self.configure(height=other_heitht)
        tk.Frame.configure(self,bg=frame_bg)
        self.camera = master.camera
        self.camera.open()
        self.num_text = tk.StringVar()
        tk.Label(self, text=master.conf['system_page_section']['btn_testingPaperAdjust'], font=master.all_fonts[master.Languagevalue.get()]["general"],bg=frame_bg).pack(pady = 10)
        tk.Label(self, text=master.conf['system_page_section']['label_insertTestPaperNAdjust'].replace('\\n', '\n'), font=master.all_fonts[master.Languagevalue.get()]["bar_label"],bg=frame_bg).pack(pady = 10)
        entry = tk.Entry(self, textvariable=self.num_text)
        entry.pack()
        entry.focus_set()
        entry.bind("<1>", lambda event, entry = entry: self.master.switch_input_frame(entry, master.conf['system_page_section']['label_insertTestPaperNAdjust'].split('\\n\\n')[1]))
        self.testpaperfinish = tk.Label(self, font=master.all_fonts[master.Languagevalue.get()]["bar_label"],bg=frame_bg,fg="red")
        self.testpaperfinish.pack(pady=3)
        tk.Button(self, text=master.conf['main_page_section']['btn_cancel'], font=master.all_fonts[master.Languagevalue.get()]["general"], bg=button_bg, height=2,
                  command=lambda: self.cancel()).pack(padx = 10, pady = 10, fill='both', side=tk.BOTTOM)
        tk.Button(self, text=master.conf['system_page_section']['btn_testingPaperFinish'], font=master.all_fonts[master.Languagevalue.get()]["general"], bg=button_bg, height=2,
                  command=lambda: self.finish()).pack(padx = 10, fill='both',side=tk.BOTTOM)
        tk.Button(self, text=master.conf['system_page_section']['btn_testingPaperCapture'], font=master.all_fonts[master.Languagevalue.get()]["general"], bg=button_bg, height=2,
                  command =lambda: self.take_snapshot()).pack(padx = 10, pady = 10, fill='both',side=tk.BOTTOM)
    def take_snapshot(self):
        time.sleep(2)
        success, img = self.camera.read()
        if success != False:
            img = cv2.flip(img, -1)
            cv2.imwrite('/home/debian/Drug_Detector/standard_curve_data/TestPaper'+ self.num_text.get() +'.jpg', img)
            self.testpaperfinish.config(text=self.master.conf['system_page_section']['label_preTestPaperNAdjust']+self.num_text.get()+self.master.conf['system_page_section']['label_afterTestPaperNAdjust'])
            print("snapshot successful")
        else:
            self.testpaperfinish.config(text=self.master.conf['system_page_section']['label_preTestPaperNAdjust']+self.num_text.get()+" fail.")
            print("snapshot error")
    def finish(self):
        self.camera.release()
        self.master.switch_frame(TestPaperAdjustedPage)
    def cancel(self):
        self.camera.release()
        self.master.back_main_frame(SystemPage)

class TestPaperAdjustedPage(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        self.configure(height=other_heitht)
        tk.Frame.configure(self,bg=frame_bg)
        tk.Label(self, text=master.conf['system_page_section']['btn_testingPaperAdjust'], font=master.all_fonts[master.Languagevalue.get()]["general"],bg=frame_bg).pack(pady = 10)
        tk.Label(self, text=master.conf['system_page_section']['label_testPaperAdjusted'], font=master.all_fonts[master.Languagevalue.get()]["bar_label"],bg=frame_bg).pack(pady = 10)
        

        tk.Button(self, text=master.conf['system_page_section']['btn_testingPaperFinish'], font=master.all_fonts[master.Languagevalue.get()]["general"], bg=button_bg, height=2,
                  command=lambda: self.finish()).pack(padx = 10, pady = 10, fill='both',side=tk.BOTTOM)
   
    def finish(self):
        self.Achive_Folder_To_ZIP('/home/debian/Drug_Detector/standard_curve_data', '/home/debian/Drug_Detector/standard_curve_data/standard_curve_data.zip')
        self.master.back_main_frame(SystemPage)
    
    def Achive_Folder_To_ZIP(self, sFilePath, dest = ""):
        """
        input : Folder path and name
        output: using zipfile to ZIP folder
        """
        if (dest == ""):
            zf = zipfile.ZipFile(sFilePath + '.ZIP', mode='w')
        else:
            zf = zipfile.ZipFile(dest, mode='w')
     
        os.chdir(sFilePath)
        #print sFilePath
        for root, folders, files in os.walk("./"):
            for sfile in files:
                if 'jpg' in sfile:
                    aFile = os.path.join(root, sfile)
                    print(aFile)
                    zf.write(aFile)
        zf.close()
        os.chdir('/home/debian/Drug_Detector')

class AdminLoginPage(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self,master)
        self.configure(height=other_heitht)
        tk.Frame.configure(self,bg=frame_bg)

        tk.Label(self, text=master.conf['system_page_section']['label_adminAccount'], font=master.all_fonts[master.Languagevalue.get()]["general"], bg=frame_bg).pack(pady=10)
        self.admin_account = tk.StringVar()
        accountEntry = tk.Entry(self, font=master.all_fonts[master.Languagevalue.get()]["general"], textvariable=self.admin_account)
        accountEntry.pack()
        accountEntry.bind("<1>", lambda event, entry = accountEntry: self.master.switch_input_frame(entry,master.conf['system_page_section']['label_adminAccount']))
        tk.Label(self, text=master.conf['system_page_section']['label_adminPassword'], font=master.all_fonts[master.Languagevalue.get()]["general"], bg=frame_bg).pack(pady=10)
        self.admin_pwd = tk.StringVar()
        pwdEntry = tk.Entry(self, font=master.all_fonts[master.Languagevalue.get()]["general"], show='*', textvariable=self.admin_pwd)
        pwdEntry.pack()
        pwdEntry.bind("<1>", lambda event, entry = pwdEntry: self.master.switch_input_frame(entry, master.conf['system_page_section']['label_adminPassword']))

        tk.Button(self, text=master.conf['main_page_section']['btn_cancel'], font=master.all_fonts[master.Languagevalue.get()]["general"], bg=button_bg, height=2,
                  command=lambda: master.switch_frame(TestPaperPage)).pack(padx = 10, pady = 10, fill='both', side=tk.BOTTOM)
        tk.Button(self, text=master.conf['system_page_section']['btn_login'], font=master.all_fonts[master.Languagevalue.get()]["general"], bg=button_bg, height=2,
                  command=lambda: self.login(master)).pack(padx = 10, pady = 10, fill='both', side=tk.BOTTOM)

    def login(self,master):
        if(self.admin_account.get() == master.settingConf['Admin']['account'] and self.admin_pwd.get() == master.settingConf['Admin']['password']):
            global ADMIN
            ADMIN = True
            master.switch_frame(TestPaperPreAdjustPage)
        else:
            master.switch_frame(AdminLoginPage)

'''
Search Flow Page
'''
class SearchPage(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        self.configure(height=other_heitht)
        tk.Frame.configure(self,bg=frame_bg)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.data_list = self.get_data()
        self.cur_list = self.data_list
        style = ttk.Style()
        style.configure('Horizontal.TScrollbar', arrowsize=28)
        style.configure('Vertical.TScrollbar', arrowsize=28)
        tk.Label(self, text=master.conf['search_page_section']['label_searchID'], font=master.all_fonts[master.Languagevalue.get()]["small_label"], bg=frame_bg).grid(column=0, row=0, pady=5, sticky="w")
        self.bs = BarcodeScanner(device_name='/dev/ttyS2')
        self.barCodeFlag = 1
        self.idCardButton = tk.Button(self, image=master.images['scan'], bg=frame_bg, command= lambda : self.scan())
        self.idCardButton.grid(column=2, row=0, sticky="e")
        self.search_text = tk.StringVar()
        self.search_text.trace("w", lambda name, index, mode: self.update_list())
        searchEntry = tk.Entry(self, width=15, textvariable=self.search_text)
        searchEntry.grid(column=1, row=0)
        searchEntry.bind("<1>", lambda event, entry = searchEntry: self.master.switch_input_frame(entry, master.conf['search_page_section']['label_searchID']),10)
        self.listbox = tk.Listbox(self, font=master.all_fonts[master.Languagevalue.get()]["middle_label"])
        self.listbox.grid(column=0, row=1, columnspan=2, padx=5, pady=15, sticky="nsew")
        scrollbar = ttk.Scrollbar(self, command=self.listbox.yview)
        scrollbar.grid(row=1,column=2,pady=15, sticky='NSW')
        hscrollbar = ttk.Scrollbar(self, command=self.listbox.xview, orient=tk.HORIZONTAL)
        hscrollbar.grid(column=0, row=2, columnspan=2, sticky='NWE')
        self.listbox.config(yscrollcommand=scrollbar.set,xscrollcommand=hscrollbar.set)
        for item in self.data_list:
            self.listbox.insert(tk.END, item[2]+' - '+item[0])
        select_index = 0
        self.listbox.select_set(select_index)

        
        tk.Button(self, text=master.conf['search_page_section']['btn_readData'], font=master.all_fonts[master.Languagevalue.get()]["general"], bg=button_bg, height=2,
                  command=lambda: self.check_index()).grid(column=0, row=3, columnspan=3, pady=10, padx=10, sticky="nsew")
        tk.Button(self, text=master.conf['main_page_section']['btn_cancel'], font=master.all_fonts[master.Languagevalue.get()]["general"], bg=button_bg, height=2,
                  command=lambda: self.cancel()).grid(column=0, row=4, columnspan=3, pady=10, padx=10,sticky="nsew")
        
    def cancel(self):
        self.bs.close()
        self.master.back_main_frame(WelcomePage)
    def get_data(self):
        try:
            conn = sqlite3.connect(self.master.conf['default']['config_database'])
            cursor = conn.cursor()
            sql = "select test_datetime, did, results.id_card, birth, sex, phone, car, type, expire_date, lot, serial_number, result from results JOIN users on users.id_card = results.id_card ORDER BY test_datetime DESC"
            cursor.execute(sql)
            data_list = cursor.fetchall()
            cursor.close()
            conn.close()
        except ValueError:
            logging.error('Get data error!')
            data_list = []
        return data_list

    def check_index(self):
        try:
            index = self.listbox.get(self.listbox.curselection())
            self.bs.close()
            logger.debug(index)
            self.master.switch_frame(ResultPage, self.cur_list[self.listbox.curselection()[0]])
        except ValueError:
            logging.error('Item can not be found in the list!')

    def update_list(self, *args):
        self.listbox.delete(0,tk.END)
        self.cur_list = []
        try:
            for item in self.data_list:
                if self.search_text.get() in item[2] or self.search_text.get() == "":
                    self.listbox.insert(tk.END, item[2]+' - '+item[0])
                    self.cur_list.append(item)
        except ValueError:
            logging.error('Can not update list!')
    def scan(self):
        if self.barCodeFlag:
            self.barCodeFlag=0
            self.idCardButton.config(state = 'disabled')
            self.update()
            id_card = self.bs.start_capture()
            self.search_text.set(id_card) # scan result
            self.idCardButton.config(state = 'normal')
            self.update()
            self.barCodeFlag=1

class ResultPage(tk.Frame):
    def __init__(self, master, data):
        tk.Frame.__init__(self, master)
        self.configure(height=other_heitht)
        tk.Frame.configure(self,bg=frame_bg)
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=10)
        self.grid_columnconfigure(1, weight=10)
        self.grid_columnconfigure(2, weight=19)
        self.grid_columnconfigure(3, weight=1)
        scrollbar = ttk.Scrollbar(self)
        display_result = tk.Text (self, bg=button_bg,yscrollcommand=scrollbar.set, font=master.all_fonts[master.Languagevalue.get()]["bar_label"])
        display_result.tag_config('negative',foreground='blue')
        display_result.tag_config('positive',foreground = 'red')
        display_result.tag_config('invalid',foreground = 'black')
        style = ttk.Style()
        style.configure('Vertical.TScrollbar', arrowsize=28)
        order = [master.conf['search_page_section']['label_testDatetime'],
                 master.conf['search_page_section']['label_did'],
                 master.conf['search_page_section']['label_idcard'],
                 master.conf['search_page_section']['label_birth'],
                 master.conf['search_page_section']['label_sex'],
                 master.conf['search_page_section']['label_phone'],
                 master.conf['search_page_section']['label_car'],
                 master.conf['search_page_section']['label_type'],
                 master.conf['search_page_section']['label_expireDate'],
                 master.conf['search_page_section']['label_lot'],
                 master.conf['search_page_section']['label_serialNumber'],
                 master.conf['search_page_section']['label_result']]
        tk.Label(self, text=data[2]+' - '+data[0], font=master.all_fonts[master.Languagevalue.get()]["bar_label"], bg='light grey',width=272).grid(column=0, row=0, columnspan=4, sticky="n")
        
        
        all_text = ""
        for title, item in zip(order, data):
            if title ==  master.conf['search_page_section']['label_result']:
                all_text += "\n"+ master.conf['search_page_section']['label_result']+": \n"
                display_result.insert(tk.INSERT, "\n"+ master.conf['search_page_section']['label_result']+": \n")
                test_result = json.loads(item)
                for r in test_result:
                    if r['value'] == "陽性":
                        if master.Languagevalue.get() == "English":
                            r['value'] = "positive"
                        display_result.insert(tk.INSERT, r['item'] + "   "+ r['value'] + "\n", 'positive')
                        
                    elif r['value'] == "陰性":
                        if master.Languagevalue.get() == "English":
                            r['value'] = "negative"
                        display_result.insert(tk.INSERT, r['item'] + "   "+ r['value'] + "\n", 'negative')
                        
                    elif r['value'] == "無效":
                        if master.Languagevalue.get() == "English":
                            r['value'] = "invalid"
                        display_result.insert(tk.INSERT, r['item'] + "   "+ r['value'] + "\n", 'invalid')
                            
                    all_text += r['item'] + "   "+ r['value'] + "\n"

            elif title == master.conf['search_page_section']['label_sex']:
                if item == 1:
                    item = master.conf['search_page_section']['label_boy']
                else:
                    item = master.conf['search_page_section']['label_girl']
                all_text +=title+" : \n"+str(item)+"\n"
                display_result.insert(tk.INSERT, title+" : \n"+str(item)+"\n")
            else:
                all_text +=title+" : \n"+str(item)+"\n"
                display_result.insert(tk.INSERT, title+" : \n"+str(item)+"\n")
        all_text += "\n\n  "
        all_text +=master.conf['search_page_section']['label_subjectName']
        all_text +=": ___________\n\n\n\n"
        all_text += master.conf['search_page_section']['label_operatorName']
        all_text +=": ___________\n\n\n\n    "
        all_text += master.conf['search_page_section']['label_location']
        all_text +=": ___________\n"
        display_result.insert(tk.INSERT, "\n\n  "+
                              master.conf['search_page_section']['label_subjectName']+
                              ": ___________\n\n\n\n"+
                              master.conf['search_page_section']['label_operatorName']+
                              ": ___________\n\n\n\n    "+
                              master.conf['search_page_section']['label_location']+
                              ": ___________\n")
        
        
        
        display_result.config(state=tk.DISABLED)
        display_result.grid(column=0, row=1, columnspan=3, padx=3, pady=5, sticky="n")
        scrollbar.config(command=display_result.yview)
        scrollbar.grid(row=1,column=3,pady=10,sticky='NSW')

        tk.Button(self, text=master.conf['main_page_section']['btn_back'], font=master.all_fonts[master.Languagevalue.get()]["general"], bg=button_bg, height=2,
                  command=lambda: master.back_main_frame(SearchPage)).grid(column=0, columnspan=2, row=2, pady=10)
        tk.Button(self, text=master.conf['main_page_section']['btn_print'], font=master.all_fonts[master.Languagevalue.get()]["general"], bg=button_bg, height=2,
                  command=lambda: self.prints_and_gomain(all_text)).grid(column=2, columnspan=2, row=2, pady=10)

    def prints_and_gomain(self, content):
        content += "\n\n\n"
        printer = Printer('/dev/ttyS1')
        printer.prints(content = content.encode('big5'))
        printer.close()

'''
Export Flow Page
'''
class ExportPage(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        self.configure(height=main_height)
        tk.Frame.configure(self,bg=frame_bg)

        #tk.Button(self, text=master.conf['export_page_section']['btn_export'], font=master.all_fonts[master.Languagevalue.get()]["general"], bg=button_bg, height=2,
        #          command=lambda: master.switch_frame(DataExportPage)).pack(padx = 10, fill='both', anchor='center')
        tk.Button(self, text=master.conf['export_page_section']['btn_update'], font=master.all_fonts[master.Languagevalue.get()]["general"], bg=button_bg, height=2,
                  command=lambda: master.switch_frame(SoftwareUpdatePage)).pack(padx = 10,pady = 30, fill='both')
        tk.Label(self, image=master.images['usb'], bg=frame_bg).pack(padx = 10,pady = 50,fill='both')

class DataExportPage(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        self.configure(height=other_heitht)
        tk.Frame.configure(self,bg=frame_bg)
        tk.Label(self, text=master.conf['export_page_section']['btn_export'], font=master.all_fonts[master.Languagevalue.get()]["general"],bg=frame_bg).pack(pady = 10)
        tk.Label(self, image=master.images['usb'], bg=frame_bg).pack(padx = 10,pady = 50,fill='both')

        tk.Button(self, text=master.conf['main_page_section']['btn_cancel'], font=master.all_fonts[master.Languagevalue.get()]["general"], bg=button_bg, height=2,
                  command=lambda: master.back_main_frame(ExportPage)).pack(padx = 10, pady = 30, fill='both', side=tk.BOTTOM)
        tk.Button(self, text=master.conf['main_page_section']['btn_ok'], font=master.all_fonts[master.Languagevalue.get()]["general"], bg=button_bg, height=2).pack(padx = 10, fill='both', side=tk.BOTTOM)


class SoftwareUpdatePage(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        self.configure(height=other_heitht)
        tk.Frame.configure(self,bg=frame_bg)
        tk.Label(self, text=master.conf['export_page_section']['btn_update'], font=master.all_fonts[master.Languagevalue.get()]["general"],bg=frame_bg).pack(pady = 10)
        tk.Label(self, text=master.conf['export_page_section']['label_version'], font=master.all_fonts[master.Languagevalue.get()]["middle_label"],bg=frame_bg).pack(pady = 15)
        tk.Label(self, text=master.conf['default']['version'], font=master.all_fonts[master.Languagevalue.get()]["general"],bg=frame_bg).pack(pady = 5)
        tk.Label(self, text=master.conf['export_page_section']['label_update'], font=master.all_fonts[master.Languagevalue.get()]["middle_label"],bg=frame_bg).pack(pady = 15)

        tk.Button(self, text=master.conf['main_page_section']['btn_cancel'], font=master.all_fonts[master.Languagevalue.get()]["general"], bg=button_bg, height=2,
                  command=lambda: master.back_main_frame(ExportPage)).pack(padx = 10, pady = 30, fill='both', side=tk.BOTTOM)
        tk.Button(self, text=master.conf['export_page_section']['btn_checkUpdate'], font=master.all_fonts[master.Languagevalue.get()]["general"], bg=button_bg, height=2,
                  command=lambda: self.unzip()).pack(padx = 10, fill='both', side=tk.BOTTOM)

    def unzip(self):
        if os.path.exists('/home/debian/update.zip'):
            with zipfile.ZipFile("/home/debian/update.zip", 'r') as zip_ref:
                os.remove("/home/debian/Drug_Detector/DD.py")
                zip_ref.extractall('/home/debian')
                shutil.move('/home/debian/Drug_Detector/DD_setting.ini', '/home/debian/share/DD_setting.ini')
            os.remove("/home/debian/update.zip")
            os._exit(0) 
            app.destroy()
        self.master.back_main_frame(ExportPage)

'''
Testing Flow Page
'''
class TestingPage(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        self.configure(height=main_height)
        tk.Frame.configure(self,bg=frame_bg)

        tk.Button(self, text=master.conf['testing_page_section']['btn_operator'], font=master.all_fonts[master.Languagevalue.get()]["general"], bg=button_bg, height=2,
                  command=lambda: self.master.switch_frame(OperatorIdPage)).pack(padx = 10,pady = 15, fill='both')
        tk.Button(self, text=master.conf['testing_page_section']['btn_modeOneToOne'], font=master.all_fonts[master.Languagevalue.get()]["general"], bg=button_bg, height=2,
                  command=lambda: self.checkLightAdjust(ONETOONE)).pack(padx = 10, fill='both', anchor='center')
        tk.Button(self, text=master.conf['testing_page_section']['btn_modeOneToMore'], font=master.all_fonts[master.Languagevalue.get()]["general"], bg=button_bg, height=2,
                  command=lambda: self.checkLightAdjust(ONETOMORE)).pack(padx = 10,pady = 30, fill='both')
        tk.Button(self, text=master.conf['testing_page_section']['btn_modeNoWait'], font=master.all_fonts[master.Languagevalue.get()]["general"], bg=button_bg, height=2,
                  command=lambda: self.checkLightAdjust(NOWAIT)).pack(padx = 10, fill='both')
        
        
    
    def checkLightAdjust(self, mode):
        if os.path.exists('dif_array.npy') and (dt.datetime.now() - dt.datetime.fromtimestamp(float(self.master.settingConf['LightAdjust']['adjust_time']))).days < 90:
            self.master.switch_frame(ModeTestingPage, mode)
        else:
            self.master.switch_frame(LigthtPreAdjustPage)

class OperatorIdPage(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        self.configure(height=other_heitht)
        tk.Frame.configure(self,bg=frame_bg)
        tk.Label(self, text=master.conf['testing_page_section']['label_inspectorID'], font=master.all_fonts[master.Languagevalue.get()]["middle_label"],bg=frame_bg).pack(pady = 10)
        self.topTextVar = tk.StringVar()
        self.topTextVar.set(master.inspectorId)
        self.topLevelEntry = tk.Entry(self, font=master.all_fonts[master.Languagevalue.get()]["bar_label"], width=20, textvariable = self.topTextVar)
        self.topLevelEntry.pack()
        tk.Button(self, text=master.conf['main_page_section']['btn_ok'], font=master.all_fonts[master.Languagevalue.get()]["general"], bg=button_bg, height=2,
                  command=lambda: self.save()).pack(padx = 10, pady = 10, fill='both', side=tk.BOTTOM)

        self.create()
    def save(self):
        self.master.inspectorId = self.topLevelEntry.get()
        self.master.back_main_frame(TestingPage)
    def select(self, value):
        if value == "Del":
            self.topLevelEntry.delete(len(self.topLevelEntry.get())-1, 'end')
        else:
            self.topLevelEntry.insert('end', value)
        return
    def create(self):
        alphabets_num = [
        ['1','2','3'],
        ['4','5','6'],
        ['7','8','9'],
        ['','0','Del']
        ]

        self.kb_num = tk.Frame(self)
        for y, row in enumerate(alphabets_num):

            x = 0

            for text in row:
                if self.master.Languagevalue.get()=="English":
                    width=6
                else:
                    width = 7
                height = 2
                columnspan = 1

                tk.Button(self.kb_num, text=text, width=width,height=height,font=self.master.all_fonts[self.master.Languagevalue.get()]["middle_label"],
                          command=lambda value=text: self.select(value),
                          padx=3, pady=3, bd=1,bg="#ebebeb", fg="black", takefocus = False
                         ).grid(row=y, column=x, columnspan=columnspan)
                x+= columnspan

        self.kb_num.pack(fill='x', side=tk.BOTTOM)
# 插入試紙卡匣
class ModeTestingPage(tk.Frame):
    def __init__(self, master, mode=ONETOONE, rounds=0, inspectorId=''):
        tk.Frame.__init__(self, master)
        self.configure(height=other_heitht)
        tk.Frame.configure(self,bg=frame_bg)
        enterTime = dt.datetime.now()
        if mode == ONETOONE:
            tk.Label(self, text=master.conf['testing_page_section']['btn_modeOneToOne'], font=master.all_fonts[master.Languagevalue.get()]["general"],bg=frame_bg).pack()
            tk.Label(self, text=master.conf['testing_page_section']['label_alertOneToOne'].replace('\\n', '\n'), font=master.all_fonts[master.Languagevalue.get()]["middle_label"],bg=frame_bg).pack()
        elif mode == ONETOMORE:
            tk.Label(self, text=master.conf['testing_page_section']['btn_modeOneToMore'], font=master.all_fonts[master.Languagevalue.get()]["general"],bg=frame_bg).pack()
            tk.Label(self, text=master.conf['testing_page_section']['label_alertOneToMore'].replace('\\n', '\n'), font=master.all_fonts[master.Languagevalue.get()]["middle_label"],bg=frame_bg).pack()
        elif mode == NOWAIT:
            tk.Label(self, text=master.conf['testing_page_section']['btn_modeNoWait'], font=master.all_fonts[master.Languagevalue.get()]["general"],bg=frame_bg).pack()
            tk.Label(self, text=master.conf['testing_page_section']['label_alertNoWait'].replace('\\n', '\n'), font=master.all_fonts[master.Languagevalue.get()]["middle_label"],bg=frame_bg).pack()
        tk.Label(self, text=master.conf['testing_page_section']['label_cassetteInsert'], font=master.all_fonts[master.Languagevalue.get()]["middle_label"],bg=frame_bg).pack(pady = 10)

        tk.Button(self, text=master.conf['main_page_section']['btn_cancel'], font=master.all_fonts[master.Languagevalue.get()]["general"], bg=button_bg, height=2,
                  command=lambda: master.back_main_frame(TestingPage)).pack(padx = 10, pady = 10, fill='both', side=tk.BOTTOM)
        tk.Button(self, text=master.conf['main_page_section']['btn_ok'], font=master.all_fonts[master.Languagevalue.get()]["general"], bg=button_bg, height=2,
                  command=lambda: master.switch_frame(ScanCassettePage, mode, rounds, master.inspectorId, enterTime)).pack(padx = 10, fill='both',side=tk.BOTTOM)

# 卡匣掃描
class ScanCassettePage(tk.Frame):
    def __init__(self, master, mode=ONETOONE, rounds=0, inspectorId='', enterTime=0):
        tk.Frame.__init__(self, master)
        self.configure(height=other_heitht)
        tk.Frame.configure(self,bg=frame_bg)
        self.mode = mode
        self.rounds = rounds
        self.inspectorId = inspectorId
        self.enterTime = enterTime
        #self.camera = VideoCapture(0, 720, 1280)
        self.camera = master.camera
        self.camera.open()
        if mode == ONETOONE:
            tk.Label(self, text=master.conf['testing_page_section']['btn_modeOneToOne'], font=master.all_fonts[master.Languagevalue.get()]["general"],bg=frame_bg).pack()
        elif mode == ONETOMORE:
            tk.Label(self, text=master.conf['testing_page_section']['btn_modeOneToMore'], font=master.all_fonts[master.Languagevalue.get()]["general"],bg=frame_bg).pack()
        elif mode == NOWAIT:
            tk.Label(self, text=master.conf['testing_page_section']['btn_modeNoWait'], font=master.all_fonts[master.Languagevalue.get()]["general"],bg=frame_bg).pack()
        tk.Label(self, text=master.conf['testing_page_section']['label_cassetteScan'], font=master.all_fonts[master.Languagevalue.get()]["middle_label"],bg=frame_bg).pack()

        self.cameraAlertLabel = tk.Label(self, text=master.conf['testing_page_section']['label_loadPic'], height=15)
        self.cameraAlertLabel.pack(fill='x')
        
        self.cameraLabel = tk.Label(self, text=master.conf['testing_page_section']['label_loadPic'], height=15)
        self.cameraLabel.pack(fill='x')
        self.cameraLabel.pack_forget()
    
        tk.Button(self, text=master.conf['main_page_section']['btn_cancel'], font=master.all_fonts[master.Languagevalue.get()]["general"], bg=button_bg, height=2,
                  command=lambda: self.cancel()).pack(padx = 10, pady = 10, fill='both', side=tk.BOTTOM)
        self.capture = tk.Button(self, text=master.conf['testing_page_section']['btn_capture'], font=master.all_fonts[master.Languagevalue.get()]["general"], bg=button_bg, height=2,
                  command=lambda: self.recapture())
        self.capture.pack(padx = 10, fill='both', side=tk.BOTTOM)
        self.capture.pack_forget()
        self.after(2000, lambda: self.recapture())

    def cancel(self):
        self.camera.release()
        self.master.back_main_frame(TestingPage)

    def resize(self, w, h, w_box, h_box, pil_image):
      '''
      resize a pil_image object so it will fit into
      a box of size w_box times h_box, but retain aspect ratio
      '''
      f1 = 1.0*w_box/w # 1.0 forces float division in Python2
      f2 = 1.0*h_box/h
      factor = min([f1, f2])
      width = int(w*factor)
      height = int(h*factor)
      return pil_image.resize((width, height), Image.ANTIALIAS)

    def recapture(self):
        success, img = self.camera.read()
        if success != False:
            self.capture.config(state = 'disabled')
            self.capture.update()
            self.cameraLabel.pack_forget()
            self.cameraAlertLabel.pack(fill='x')
            self.update()

            cv2image = cv2.cvtColor(img,cv2.COLOR_BGR2RGBA)
            current_image = Image.fromarray(cv2image)
            w, h = current_image.size
            imgPrint = self.resize(w, h, 272, 260, current_image)
            imgtk = ImageTk.PhotoImage(image=imgPrint)
            self.cameraLabel.imgtk = imgtk
            self.cameraLabel.config(image=imgtk, height=260)
            self.cameraAlertLabel.pack_forget()
            self.cameraLabel.pack(fill='x')

    
            print("capture successful")
            img = cv2.flip(img,-1)
            cv2.imwrite(photoname, img[60:-60,610:])
            self.tiltCorrect(photoname, photoname)
            print('photoname=', photoname)
    
            print("write successful")
            reader = zxing.BarCodeReader()
            QRcode = reader.decode(photoname)
            
            #QRcode = "MED|drugtype001|20221031|20200823|000000002"
            print('QRcode=', QRcode)
            
            if QRcode is not None:
                self.camera.release()
                self.master.switch_frame(InputPage,0,self.mode,self.rounds, self.inspectorId, self.enterTime, QRcode.raw)
                #self.master.switch_frame(InputPage,0,self.mode,self.rounds, self.inspectorId, self.enterTime, QRcode)
            else:
                self.capture.config(state = 'normal')
                self.capture.pack(padx = 10, fill='both', side=tk.BOTTOM)
                self.update()
        else:
            print('else')
            self.camera.release()
            self.master.back_main_frame(TestingPage)
            
    def rotate(self,image,angle,center=None,scale=1.0):
        (w,h) = image.shape[0:2]
        if center is None:
            center = (w//2,h//2)
        wrapMat = cv2.getRotationMatrix2D(center,angle,scale)
        return cv2.warpAffine(image,wrapMat,(h,w))

    def tiltCorrect(self, imgName, saveName):
        src = cv2.imread(imgName)
        gray = cv2.imread(imgName,cv2.IMREAD_GRAYSCALE)
        grayNot = cv2.bitwise_not(gray)
        threImg = cv2.threshold(grayNot,100,255,cv2.THRESH_BINARY_INV)[1]
        fined_Img= cv2.blur(threImg, (5,5))
        coords = np.column_stack(np.where(fined_Img==255))
        coords = np.flip(coords, axis=1)
        print('coords=', coords)

        rect = cv2.minAreaRect(coords)
        bbox = cv2.boxPoints(rect)
        cv2.drawContours(src, [bbox.astype(int)],0,(255,0,0),2)
        cv2.drawContours(fined_Img, [bbox.astype(int)],0,(255,0,0),2)
        angle = cv2.minAreaRect(coords)[-1]

        print('angle=', angle)
        if angle < -45:
            angle = -(angle + 90)
        else:
            angle = -angle
        print('finish_angle=', angle)
        
        dst = self.rotate(src,angle)
        cv2.imwrite(saveName, dst)    
        
        ro_img = self.rotate(fined_Img, angle)
        ro_coords = np.column_stack(np.where(ro_img>0))
        ro_angle = cv2.minAreaRect(ro_coords)[-1]
        print('ro_angle=', ro_angle)
        """
        fig, axes = plt.subplots(nrows=2, ncols=3, figsize=(15,20))
        axes[0][0].imshow(gray, cmap='gray')
        axes[0][0].set_title('gray')
        
        axes[0][1].imshow(grayNot, cmap='gray')
        axes[0][1].set_title('grayNot')

        axes[0][2].imshow(threImg, cmap='gray')
        axes[0][2].set_title('threImg')

        axes[1][0].imshow(src)
        axes[1][0].set_title('src')
        
        axes[1][1].imshow(ro_img, cmap='gray')
        axes[1][1].set_title('ro_img')
        plt.tight_layout()
        plt.show()
        """
            
class InputPage(tk.Frame):
    def __init__(self, master, step, mode, rounds, inspectorId, enterTime, QRcode="",DataObj={} ):
        tk.Frame.__init__(self, master)
        self.configure(height=other_heitht)
        tk.Frame.configure(self,bg=frame_bg)
        self.step = step
        self.mode = mode
        self.rounds = rounds
        self.inspectorId = inspectorId
        self.enterTime = enterTime
        self.QRcode = QRcode
        self.DataObj = DataObj
        self.entry_frame = tk.Frame(self)
        style = ttk.Style()
        style.configure('Vertical.TScrollbar', arrowsize=28)
        if step == 0:
            tk.Label(self, text=master.conf['testing_page_section']['label_subjectID'], font=master.all_fonts[master.Languagevalue.get()]["middle_label"],bg=frame_bg).pack(pady = 10)
        elif step == 1:
            tk.Label(self, text=master.conf['testing_page_section']['label_subjectCar'], font=master.all_fonts[master.Languagevalue.get()]["middle_label"],bg=frame_bg).pack(pady = 10)
        elif step == 2:
            tk.Label(self, text=master.conf['testing_page_section']['label_subjectPhone'], font=master.all_fonts[master.Languagevalue.get()]["middle_label"],bg=frame_bg).pack(pady = 10)
        self.topTextVar = tk.StringVar()
        self.topLevelEntry = tk.Entry(self.entry_frame, font=master.all_fonts[master.Languagevalue.get()]["bar_label"], width=20, textvariable = self.topTextVar)
        self.topLevelEntry.pack(side=tk.LEFT)
        if step==0:
            self.bs = BarcodeScanner(device_name='/dev/ttyS2')
            self.barCodeFlag = 1
            self.idCardButton = tk.Button(self.entry_frame, image=master.images['scan'], bg=frame_bg, command= lambda : self.scan())
            self.idCardButton.pack(side=tk.LEFT)
        self.entry_frame.pack()
        tk.Button(self, text=master.conf['main_page_section']['btn_next'], font=master.all_fonts[master.Languagevalue.get()]["general"], bg=button_bg, height=2,
                  command=lambda: self.save()).pack(padx = 10, pady = 10, fill='both', side=tk.BOTTOM)

        self.create()
    def scan(self):
        if self.barCodeFlag:
            self.barCodeFlag=0
            self.idCardButton.config(state = 'disabled')
            self.update()
            id_card = self.bs.start_capture()
            self.topTextVar.set(id_card) # scan result
            self.idCardButton.config(state = 'normal')
            self.update()
            self.barCodeFlag=1
    def save(self):
        if self.step==2:
            self.DataObj['subject_phone']=self.topLevelEntry.get()
            self.master.switch_frame(SubjectInfoFormPage,self.mode,self.rounds, self.inspectorId, self.enterTime, self.QRcode, self.DataObj)
        elif self.step==1:
            self.DataObj['subject_car']=self.topLevelEntry.get()
            self.master.switch_frame(InputPage,2,self.mode,self.rounds, self.inspectorId, self.enterTime, self.QRcode, self.DataObj)
        elif self.step==0:
            self.DataObj['subject_id']=self.topLevelEntry.get()
            self.bs.close()
            self.master.switch_frame(InputPage,1,self.mode,self.rounds, self.inspectorId, self.enterTime, self.QRcode, self.DataObj)
    def select(self, value):
        if value == "Del":
            self.topLevelEntry.delete(len(self.topLevelEntry.get())-1, 'end')
        elif value =='Eng':
            self.kb_num.pack_forget()
            self.kb_en.pack(fill='x', side=tk.BOTTOM)
        elif value =='123':
            self.kb_en.pack_forget()
            self.kb_num.pack(fill='x', side=tk.BOTTOM)
        else:
            self.topLevelEntry.insert('end', value)
        return
    def create(self):
        if self.step==0:
            alphabets_num = [
                ['1','2','3'],
                ['4','5','6'],
                ['7','8','9'],
                ['Eng','0','Del']
                ]
        elif self.step==1:
            alphabets_num = [
                ['+','1','2','3'],
                ['*','4','5','6'],
                ['/','7','8','9'],
                ['Eng','-','0','Del']
                ]
        elif self.step==2:
            alphabets_num = [
                ['1','2','3'],
                ['4','5','6'],
                ['7','8','9'],
                ['','0','Del']
                ]
       
        alphabets_en = [
            ['A','B','C','D'],
            ['E','F','G','H'],
            ['I','J','K','L'],
            ['M','N','O','P'],
            ['Q','R','S','T'],
            ['U','V','W','X'],
            ['123','Y','Z','Del']
            ]

        self.kb_num = tk.Frame(self)
        self.kb_en = tk.Frame(self)
        for y, row in enumerate(alphabets_num):

            x = 0

            for text in row:
                if self.step==1:
                    width=5
                else:
                    width = 7
                height = 2
                columnspan = 1

                tk.Button(self.kb_num, text=text, width=width,height=height,font=self.master.all_fonts[self.master.Languagevalue.get()]["middle_label"],
                          command=lambda value=text: self.select(value),
                          padx=3, pady=3, bd=1,bg="#ebebeb", fg="black", takefocus = False
                         ).grid(row=y, column=x, columnspan=columnspan)
                x+= columnspan
        for y, row in enumerate(alphabets_en):

            x = 0

            for text in row:

                width = 5
                height = 1
                columnspan = 1

                tk.Button(self.kb_en, text=text, width=width,height=height,font=self.master.all_fonts[self.master.Languagevalue.get()]["middle_label"],
                          command=lambda value=text: self.select(value),
                          padx=3, pady=3, bd=1,bg="#ebebeb", fg="black", takefocus = False
                         ).grid(row=y, column=x, columnspan=columnspan)

                x+= columnspan

        self.kb_num.pack(fill='x', side=tk.BOTTOM)


class SubjectInfoFormPage(tk.Frame):
    def __init__(self, master,mode=ONETOONE, rounds=0, inspectorId='', enterTime=0, QRcode="", DataObj={}):
        tk.Frame.__init__(self, master)
        self.configure(height=other_heitht)
        tk.Frame.configure(self, bg=frame_bg)
        self.grid_propagate(0)
        self.grid_columnconfigure(0, weight=2)
        self.grid_columnconfigure(1, weight=3)
        self.grid_rowconfigure(8, weight=1)
        self.mode = mode
        self.rounds = rounds
        self.enterTime = enterTime
        self.QRcode = QRcode
        self.valid_phone = False
        self.valid_Id = False
        self.valid_date = True
        
        if mode == ONETOONE:
            tk.Label(self, text=master.conf['testing_page_section']['btn_modeOneToOne'], font=master.all_fonts[master.Languagevalue.get()]["general"],bg=frame_bg,height=2).grid(column=0, row=0, columnspan=3)
        elif mode == ONETOMORE:
            tk.Label(self, text=master.conf['testing_page_section']['btn_modeOneToMore'], font=master.all_fonts[master.Languagevalue.get()]["general"],bg=frame_bg,height=2).grid(column=0, row=0, columnspan=3)
        elif mode == NOWAIT:
            tk.Label(self, text=master.conf['testing_page_section']['btn_modeNoWait'], font=master.all_fonts[master.Languagevalue.get()]["general"],bg=frame_bg,height=2).grid(column=0, row=0, columnspan=3)
        self.bs = BarcodeScanner(device_name='/dev/ttyS2')
        self.conf = master.conf
        tk.Label(self, text=master.conf['testing_page_section']['label_inspectorID'], font=master.all_fonts[master.Languagevalue.get()]["bar_label"], bg=frame_bg).grid(column=0, row=1)
        self.inspector_id = tk.StringVar()
        if inspectorId is not None:
            self.inspector_id.set(inspectorId)
        insepectorIdEntry = tk.Entry(self, textvariable=self.inspector_id, width=14)
        insepectorIdEntry.grid(column=1, row=1)
        insepectorIdEntry.bind("<1>", lambda event, entry = insepectorIdEntry: self.master.switch_input_frame(entry, master.conf['testing_page_section']['label_inspectorID']))

        tk.Label(self, text=master.conf['testing_page_section']['label_subjectID'], font=master.all_fonts[master.Languagevalue.get()]["bar_label"], bg=frame_bg).grid(column=0, row=2, pady=10, sticky="e")
        self.subject_id = tk.StringVar()
        self.subject_id.set(DataObj['subject_id'])
        self.subjectIdEntry = tk.Entry(self, textvariable=self.subject_id, width=14)
        
        self.subject_id.trace("w", lambda *args: self.validate_ID())
        self.subjectIdEntry.grid(column=1, row=2)
        self.subjectIdEntry.bind("<1>", lambda event, entry = self.subjectIdEntry: self.master.switch_input_frame(entry, master.conf['testing_page_section']['label_subjectID']))

        self.barCodeFlag = 1
        self.idCardButton = tk.Button(self, image=master.images['scan'], bg=frame_bg, command= lambda : self.scan())
        self.idCardButton.grid(column=2, row=2)

        self.dateTime = master.dateTime
        self.switch_input_frame = master.switch_input_frame
        tk.Label(self, text=master.conf['testing_page_section']['label_subjectBirth'], font=master.all_fonts[master.Languagevalue.get()]["bar_label"], bg=frame_bg).grid(column=0, row=3, pady=10, sticky="e")
        self.entry_frame = DateEntry(self)
        self.entry_frame.grid(column=1,columnspan=2, row=3, pady=15)

        tk.Label(self, text=master.conf['testing_page_section']['label_subjectSex'], font=master.all_fonts[master.Languagevalue.get()]["bar_label"], bg=frame_bg).grid(column=0, row=4, pady=10, sticky="e")
        self.subject_sex = tk.StringVar()
        style = ttk.Style()
        style.configure('TCombobox', arrowsize=30)
        style.configure('Vertical.TScrollbar', arrowsize=28)
        self.option_add('*TCombobox*Listbox.font', master.all_fonts[master.Languagevalue.get()]["time_label"])
        self.SubjectSexBox = ttk.Combobox(self,value=[master.conf['testing_page_section']['label_subjectSexBoy'],master.conf['testing_page_section']['label_subjectSexGirl']], textvariable=self.subject_sex, width=14, justify='center')
        self.SubjectSexBox.current(0)
        self.SubjectSexBox.grid(column=1, row=4)

        tk.Label(self, text=master.conf['testing_page_section']['label_subjectCar'], font=master.all_fonts[master.Languagevalue.get()]["bar_label"], bg=frame_bg).grid(column=0, row=5, pady=10, sticky="e")
        self.subject_car = tk.StringVar()
        self.subject_car.set(DataObj['subject_car'])
        carEntry = tk.Entry(self, textvariable=self.subject_car, width=14)
        carEntry.grid(column=1, row=5)
        carEntry.bind("<1>", lambda event, entry = carEntry: self.master.switch_input_frame(entry, master.conf['testing_page_section']['label_subjectCar']))

        tk.Label(self, text=master.conf['testing_page_section']['label_subjectPhone'], font=master.all_fonts[master.Languagevalue.get()]["bar_label"], bg=frame_bg).grid(column=0, row=6, pady=10, sticky="e")

        self.subject_phone = tk.StringVar()
        self.subject_phone.set(DataObj['subject_phone'])
        self.subject_phone_entry = tk.Entry(self, textvariable=self.subject_phone, width=14)
        
        self.subject_phone.trace("w", lambda *args: self.validate_phone())
        self.subject_phone_entry.grid(column=1, row=6)
        self.subject_phone_entry.bind("<1>", lambda event, entry = self.subject_phone_entry: self.master.switch_input_frame(entry, master.conf['testing_page_section']['label_subjectPhone']))

        self.next_btn = tk.Button(self, text=master.conf['testing_page_section']['btn_inspect'], font=master.all_fonts[master.Languagevalue.get()]["general"], bg=button_bg, height=1,
                                    state=tk.DISABLED, command= lambda: self.nextpage(master))
        self.next_btn.grid(column=0, row=9, columnspan=3, ipadx=90, pady=5, sticky="s")
        tk.Button(self, text=master.conf['main_page_section']['btn_cancel'], font=master.all_fonts[master.Languagevalue.get()]["general"], bg=button_bg, height=1,
                  command=lambda: master.back_main_frame(TestingPage)).grid(column=0, row=10, columnspan=3, ipadx=90, pady=5, sticky="s")
        self.validate_ID()
        self.validate_phone()


    def scan(self):
        if self.barCodeFlag:
            self.barCodeFlag=0
            self.idCardButton.config(state = 'disabled')
            self.update()
            id_card = self.bs.start_capture()
            self.subject_id.set(id_card) # scan result
            self.idCardButton.config(state = 'normal')
            self.update()
            self.barCodeFlag=1

    def validate_phone(self):
        subject_phone_pattern = re.compile("(\d{2,3}-?|\(\d{2,3}\))\d{3,4}-?\d{4}|09\d{2}(\d{6}|-\d{3}-\d{3})")
        phone = self.subject_phone.get()
        if subject_phone_pattern.match(phone) is not None:
            self.subject_phone_entry.configure(bg='#FFFFFF')
            self.valid_phone = True
        else:
            self.subject_phone_entry.configure(bg='#FF5151')
            self.valid_phone = False
        self.switch_button_status()

    def validate_ID(self):
        subject_id_pattern = re.compile("^[A-Z]{1}[1-2]{1}[0-9]{8}$")
        id = self.subject_id.get()
        if subject_id_pattern.match(id) is not None:
            self.subjectIdEntry.configure(bg='#FFFFFF')
            self.valid_Id = True
        else:
            self.subjectIdEntry.configure(bg='#FF5151')
            self.valid_Id = False
        self.switch_button_status()

    def switch_button_status(self):
        if self.valid_Id and self.valid_phone and self.valid_date:
            self.next_btn.config(state=tk.NORMAL)
        else:
            self.next_btn.config(state=tk.DISABLED)

    def nextpage(self, master):
        self.bs.close()
        DataObj = self.composeData()
        master.switch_frame(TestingLoadingPage, self.mode, self.rounds, self.inspector_id.get(), self.enterTime, DataObj, self.QRcode)

    def composeData(self):
        sexInt = 1 if self.subject_sex.get() == '男' else 0
        birth =  self.entry_frame.year.get() + '-' + self.entry_frame.month.get() + '-' + self.entry_frame.day.get()
        obj = {
            'id_card': self.subject_id.get(),
            'sex': sexInt,
            'birth': birth,
            'phone': self.subject_phone.get(),
            'did': self.inspector_id.get(),
            'car': self.subject_car.get(),
            'test_datetime': self.master.dateTime.strftime("%Y-%m-%d %H:%M:%S")
        }
        return obj

# 檢測結果
class TestingLoadingPage(tk.Frame):
    def __init__(self, master,mode=ONETOONE, rounds=0, inspectorId='', enterTime=0, DataObj={}, QRcode=''):
        tk.Frame.__init__(self, master)
        self.configure(height=other_heitht)
        tk.Frame.configure(self,bg=frame_bg)
        if mode == ONETOONE:
            tk.Label(self, text=master.conf['testing_page_section']['btn_modeOneToOne'], font=master.all_fonts[master.Languagevalue.get()]["general"],bg=frame_bg).pack()
        elif mode == ONETOMORE:
            tk.Label(self, text=master.conf['testing_page_section']['btn_modeOneToMore'], font=master.all_fonts[master.Languagevalue.get()]["general"],bg=frame_bg).pack()
        elif mode == NOWAIT:
            tk.Label(self, text=master.conf['testing_page_section']['btn_modeNoWait'], font=master.all_fonts[master.Languagevalue.get()]["general"],bg=frame_bg).pack()
        self.mode = mode
        self.rounds = rounds
        self.inspectorId = inspectorId
        self.res = []
        self.QRcodeobj = {}
        self.DataObj = DataObj
        self.camera = master.camera
        self.camera.open()
        self.temp = 0
        self.flag = 0
        self.textlabel = tk.Label(self, text=master.conf['testing_page_section']['label_inspectPreLoading'].replace('\\n', '\n'), font=master.all_fonts[master.Languagevalue.get()]["middle_label"],bg=frame_bg)
        self.textlabel.pack(pady = 10)
        self.loadlabel = tk.Label(self,bg=frame_bg)
        self.loadlabel.pack(pady = 10)
        self.t1 = threading.Thread(target = lambda: self.drugTesting(DataObj, QRcode))
        timeDelta = dt.datetime.now() - enterTime
        self.maxSecond = TESTLOADINGTIME - timeDelta.seconds
        if rounds > 0 or self.maxSecond < 30 or mode == NOWAIT:
            self.maxSecond = 30
            self.t1.start()
            self.flag=1
             
        self.time = tk.StringVar()
        self.time.set("{:2.1f}%".format(0/self.maxSecond))
        self.timelabel = tk.Label(self, textvariable=self.time, bg=frame_bg, font=master.all_fonts[master.Languagevalue.get()]["bigger_label"])
        self.timelabel.pack(expand=True, fill='both')
        self.after(0, self.update_clock, self.maxSecond)
        self.after(0, self.update, 0)

        tk.Button(self, text=master.conf['main_page_section']['btn_cancel'], font=master.all_fonts[master.Languagevalue.get()]["general"], bg=button_bg, height=2,
                  command=lambda: self.cancel()).pack(padx = 10, pady = 10, fill='both', side=tk.BOTTOM)

    def cancel(self):
        self.camera.release()
        self.master.back_main_frame(TestingPage)

    def update_clock(self,second = 5):
        if second !=0:
            second-=1
        if second < 30 and self.flag==0:
            self.flag=1
            self.t1.start()
            print("algorithm start")
        self.time.set("{:2.1f}%".format(100*(self.maxSecond-second)/self.maxSecond))
        self.after(1000, self.update_clock, second)

    def update(self, ind):
        if self.temp!=2:
            frame = self.master.frames[ind]
            ind += 1
            if ind == 12:
                ind=0
            if ind % 2 == 0:
                dot = "."
                dot = dot*(ind//2)
            self.loadlabel.configure(image=frame)
            self.after(100, self.update, ind)
        else:
            self.loadlabel.destroy()
            self.camera.release()
            self.master.switch_frame(TestingResultPage,self.mode,self.rounds,self.inspectorId, self.res, self.DataObj, self.QRcodeobj)


    def drugTesting(self, DataObj, QRcode):
        #time.sleep(2)
        self.QRcodeobj = self.parseQRcode(QRcode)
        success, img = self.camera.read()
        if success != False:
            conn = sqlite3.connect(self.master.conf['default']['config_database'])
            sql = "SELECT * FROM SQLITE_SEQUENCE"
            imgName = imgdir+str(conn.execute(sql).fetchall()[0][1]+1)+"-"+DataObj['id_card']
            if not os.path.exists(imgName):
               os.mkdir(imgName)
            img = cv2.flip(img, -1)
            cv2.imwrite(imgName+"/0_uncorrect.jpg", img)
            conn.close()
            self.tiltCorrect(imgName+"/0_uncorrect.jpg", imgName+"/0.jpg")
            #time.sleep(5)
            dif_array = np.load('dif_array.npy')
            loc = np.load('line_loc.npy')
            val_line_info = self.QRcodeobj['valid_line_info']
            #val_line_info = [0,1,0,0,1,0,0,1,0]
            
            print('self.QR=', self.QRcodeobj)
            t3 = time.time()
            self.res = MED(imgName+"/0.jpg", dif_array, loc, self.QRcodeobj['threshold'], val_line_info).main('false')
            t4 = time.time()
            print('PN=', self.res)
            print('MED_time=', t4-t3)
            print('algorithm finished')
            self.res = self.parse_result(self.QRcodeobj, self.res)
            self.insertData(DataObj, self.res, self.QRcodeobj)
            self.temp = 2
        else:
            self.camera.release()
            self.master.back_main_frame(TestingPage)

    def rotate(self,image,angle,center=None,scale=1.0):
        (w,h) = image.shape[0:2]
        if center is None:
            center = (w//2,h//2)
        wrapMat = cv2.getRotationMatrix2D(center,angle,scale)
        return cv2.warpAffine(image,wrapMat,(h,w))

    def tiltCorrect(self, imgName, saveName):
        src = cv2.imread(imgName)
        gray = cv2.imread(imgName,cv2.IMREAD_GRAYSCALE)
        grayNot = cv2.bitwise_not(gray)
        threImg = cv2.threshold(grayNot,100,255,cv2.THRESH_BINARY_INV)[1]
        coords = np.column_stack(np.where(threImg>0))
        angle = cv2.minAreaRect(coords)[-1]
        print('angle=', angle)
        
        if angle > -45:
            angle = angle
        else:
            angle = (angle+90)
        print('angle=', angle)
        dst = self.rotate(src,angle)
        cv2.imwrite(saveName, dst)   
        

    def parseQRcode(self, QRcode):
        QRcodeArr = QRcode.split('|')
        threshold_arr, valid_arr, drug_title_arr = self.parse_info(QRcodeArr[1])
        print('QRcode=', QRcode)
        print('threshold_arr=', threshold_arr)
        print('valid_arr=', valid_arr)
        print('drug_title_arr=', drug_title_arr)
        
        return {
            #'line_loc_th': line_loc_th,
            'valid_line_info': valid_arr,
            'drug_title_info': drug_title_arr,
            'threshold': np.array(threshold_arr),
            #'line_loc_th': self.parse_line_loc_info(QRcodeArr[2:15]),
            #'valid_line_info': self.parse_valid_line_info(QRcodeArr[15:24]),
            #'drug_title_info': QRcodeArr[24:33],
            #'threshold': self.parse_threshold_info(QRcodeArr[33:43]),
            'cassette_type': QRcodeArr[1],
            'valid_date': QRcodeArr[2],
            'batch_number': QRcodeArr[3],
            'serial_number': QRcodeArr[4]
        }

    def parse_info(self, dtype):
        conn = sqlite3.connect('./DD.db')
        c = conn.cursor()
        sql = "select T1_A, T2_A, T3_A, T1_B, T2_B, T3_B, T1_C, T2_C, T3_C from cape where type=?"
        all_drugs = c.execute(sql, (dtype,)).fetchone()
        all_drugs = ['NA', 'MET', 'NA', 'NA', 'KET', 'NA', 'NA', 'MOR', 'NA'] ##########################
        threshold_arr = []
        valid_arr = []
        drug_title_arr = []
        for i, drug in enumerate(all_drugs):
            if i % 3==0:
                test_arr = []
            if drug !="NA":
                sql ="select * from drug where name=?"
                thresholds = c.execute(sql, (drug,)).fetchone()
                test_arr.append(thresholds[2])
                valid_arr.append(1)
            else:
                test_arr.append(0)
                valid_arr.append(0)
            drug_title_arr.append(drug)

            if i % 3==2:
                # TODO: C line
                test_arr.append(10)
                threshold_arr.append(test_arr)
        conn.close()
        threshold_arr = [[0, 8, 0, 10], [0, 8, 0, 10], [0, 8, 0, 10]]###################################
        return threshold_arr, valid_arr, drug_title_arr


    def parse_line_loc_info(self, line_loc_info):
        return [
            self.parse_line_loc_row(line_loc_info[1:5], int(line_loc_info[0])),
            self.parse_line_loc_row(line_loc_info[5:9], int(line_loc_info[0])),
            self.parse_line_loc_row(line_loc_info[9:], int(line_loc_info[0])),
        ]

    def parse_line_loc_row(self, row, width):
        for i in range(0, len(row)*2-1):
            if (i%2) == 0:
                row[i] = int(row[i])
                row.insert(i+1, row[i] + width)
            else:
                continue
        return row

    def parse_threshold_info(self, threshold_info):
        threshold_info = [int(item) for item in threshold_info]
        return [
            self.list_append(threshold_info[0:3], threshold_info[9]),
            self.list_append(threshold_info[3:6], threshold_info[9]),
            self.list_append(threshold_info[6:9], threshold_info[9]),
        ]

    def parse_valid_line_info(self, valid_line_info):
        return [int(item) for item in valid_line_info]

    def list_append(self, list, item):
        list.append(item)
        return list

    def parse_result(self, QRcodeobj, result):
        result_list = []
        for index, valid in enumerate(QRcodeobj['valid_line_info']):
            if valid == 1:
                if result[int(index/3)][3] == 'positive':
                    value = '無效'
                else:
                    print(index)
                    value = '陰性' if result[int(index/3)][index%3] == 'negative' else '陽性'

                result_list.append({ 'item': QRcodeobj['drug_title_info'][index], 'value': value })

        return result_list

    def insertData(self, DataObj, result, QRcodeobj):
        try:
            conn = sqlite3.connect(self.master.conf['default']['config_database'])
            sql = """INSERT OR IGNORE INTO users (id_card, sex, birth, phone) VALUES (?,?,?,?);"""
            val = (DataObj['id_card'], DataObj['sex'], DataObj['birth'], DataObj['phone'])
            conn.execute(sql, val)
            sql = """INSERT INTO results (id_card, did, car, test_datetime, type, expire_date, lot, serial_number, result) VALUES (?,?,?,?,?,?,?,?,?);"""
            val = (DataObj['id_card'], DataObj['did'], DataObj['car'], DataObj['test_datetime'], QRcodeobj['cassette_type'], QRcodeobj['valid_date'], QRcodeobj['batch_number'], QRcodeobj['serial_number'], json.dumps(result, ensure_ascii=False))
            conn.execute(sql, val)
            conn.commit()
            conn.close()
            print('Insert DB finished')
        except Exception as e:
            conn.rollback()
            conn.close()
            logger.debug('Insert data error:', e, DataObj)

# 檢測結果
class TestingResultPage(tk.Frame):
    def __init__(self, master,mode=ONETOONE, rounds=0, inspectorId='', res=[], DataObj={}, QRcodeobj={}):
        tk.Frame.__init__(self, master)
        self.configure(height=other_heitht)
        tk.Frame.configure(self,bg=frame_bg)
        if mode == ONETOONE:
            tk.Label(self, text=master.conf['testing_page_section']['btn_modeOneToOne'], font=master.all_fonts[master.Languagevalue.get()]["general"],bg=frame_bg).pack()
        elif mode == ONETOMORE:
            tk.Label(self, text=master.conf['testing_page_section']['btn_modeOneToMore'], font=master.all_fonts[master.Languagevalue.get()]["general"],bg=frame_bg).pack()
        elif mode == NOWAIT:
            tk.Label(self, text=master.conf['testing_page_section']['btn_modeNoWait'], font=master.all_fonts[master.Languagevalue.get()]["general"],bg=frame_bg).pack()
        tk.Label(self, text=master.conf['testing_page_section']['label_inspectResult'], font=master.all_fonts[master.Languagevalue.get()]["middle_label"],bg=frame_bg).pack(pady = 10)
        order = [master.conf['search_page_section']['label_testDatetime'],
                 master.conf['search_page_section']['label_did'],
                 master.conf['search_page_section']['label_idcard'],
                 master.conf['search_page_section']['label_birth'],
                 master.conf['search_page_section']['label_sex'],
                 master.conf['search_page_section']['label_phone'],
                 master.conf['search_page_section']['label_car'],
                 master.conf['search_page_section']['label_type'],
                 master.conf['search_page_section']['label_expireDate'],
                 master.conf['search_page_section']['label_lot'],
                 master.conf['search_page_section']['label_serialNumber'],
                 master.conf['search_page_section']['label_result']]
        rounds+=1
        result_frame = tk.Frame(self, height=100, width=200)
        result_frame.pack_propagate(0)
        style = ttk.Style()
        style.configure('Vertical.TScrollbar', arrowsize=28)
        scrollbar = ttk.Scrollbar(result_frame)
        display_result = tk.Text (result_frame, bg=button_bg,yscrollcommand=scrollbar.set, font=master.all_fonts[master.Languagevalue.get()]["bar_label"])
        display_result.tag_config('negative',foreground='blue')
        display_result.tag_config('positive',foreground = 'red')
        display_result.tag_config('invalid',foreground = 'black')
        content = ""
        # Hutton: 判斷有結果無
        content = content +  order[0] + " : " + DataObj['test_datetime'] + "\n"
        content = content +  order[1]+ " : "  + DataObj['did'] + "\n"
        content = content +  order[2] + " : " + DataObj['id_card'] + "\n"
        content = content +  order[3] + " : " + DataObj['birth'] + "\n"
        if DataObj['sex'] == 1:
            content = content + order[4] + " : " +  master.conf['search_page_section']['label_boy'] + "\n"
        else:
            content = content + order[4] + " : " +  master.conf['search_page_section']['label_girl'] + "\n"
        content = content +  order[5] + " : " + DataObj['phone'] + "\n"
        content = content +  order[6] + " : " + DataObj['car'] + "\n"
        content = content +  order[7] + " : " + QRcodeobj['cassette_type'] + "\n"
        content = content +  order[8] + " : " + QRcodeobj['valid_date'] + "\n"
        content = content +  order[9] + " : " + QRcodeobj['batch_number'] + "\n"
        content = content +  order[10] + " : " + QRcodeobj['serial_number'] + "\n"
        content = content +  order[11] + "\n\n"
        if len(res)>0:
            for result in res:
                if result['value'] == "陽性":
                    if master.Languagevalue.get() == "English":
                        result['value'] = "positive"
                    display_result.insert(tk.INSERT, result['item'] + "   "+ result['value'] + "\n", 'positive')
                        
                elif result['value'] == "陰性":
                    if master.Languagevalue.get() == "English":
                        result['value'] = "negative"
                    display_result.insert(tk.INSERT, result['item'] + "   "+ result['value'] + "\n", 'negative')
                        
                elif result['value'] == "無效":
                    if master.Languagevalue.get() == "English":
                        result['value'] = "invalid"
                    display_result.insert(tk.INSERT, result['item'] + "   "+ result['value'] + "\n", 'invalid')
                result_str = result['item'] + "   "+ result['value']
                content+= result_str + '\n'
        content += "\n\n  "
        content +=master.conf['search_page_section']['label_subjectName']
        content +=": ___________\n\n\n\n"
        content += master.conf['search_page_section']['label_operatorName']
        content +=": ___________\n\n\n\n    "
        content += master.conf['search_page_section']['label_location']
        content +=": ___________\n"
        display_result.pack(side=tk.LEFT)
        scrollbar.pack(side=tk.LEFT)
        result_frame.pack(fill=None,expand=False)

        tk.Button(self, text=master.conf['testing_page_section']['btn_finish'], font=master.all_fonts[master.Languagevalue.get()]["general"], bg=button_bg, height=2,
                  command=lambda: master.back_main_frame(TestingPage)).pack(padx = 10, pady = 10, fill='both', side=tk.BOTTOM)
        tk.Button(self, text=master.conf['testing_page_section']['btn_print'], font=master.all_fonts[master.Languagevalue.get()]["general"], bg=button_bg, height=2,
                  command=lambda: self.prints_and_gomain(content)).pack(padx = 10, fill='both',side=tk.BOTTOM)
        if mode == ONETOMORE or mode == NOWAIT:
            tk.Button(self, text=master.conf['testing_page_section']['btn_continue'], font=master.all_fonts[master.Languagevalue.get()]["general"], bg=button_bg, height=2,
                      command=lambda: master.switch_frame(ModeTestingPage,mode,rounds, inspectorId)).pack(padx = 10, pady = 10, fill='both',side=tk.BOTTOM)
    def prints_and_gomain(self, content):
        content += "\n\n\n"
        printer = Printer('/dev/ttyS1')
        printer.prints(content = content.encode('big5'))
        printer.close()


if __name__ == "__main__":
    logger = logging.root
    logger.setLevel(level=logging.DEBUG)
    logger.basicConfig = logging.basicConfig(level=logging.DEBUG,
                        format = '%(asctime)s %(levelname)s %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S',
                        handlers=[logging.FileHandler('DD.log','w','utf-8'),])

    app = DrugDetectorApp()
    app.attributes('-zoomed',True)
    app.wm_attributes('-fullscreen', 'true')
    app.mainloop()
