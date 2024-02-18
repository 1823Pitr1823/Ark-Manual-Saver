#!venv/bin/python
import os
import gc
import pyautogui
import shutil
import subprocess
from tkinter import *
from tkinter import ttk
from PyQt5 import Qt
from pynput.keyboard import Key, Listener
import threading
import shutil
from datetime import datetime
from notifypy import Notify
import time
import platform
import multiprocessing
from Xlib import display
from tkinter.messagebox import showinfo, askyesno
from tkinter import simpledialog
import sys
gui_active=False
file_copy=""
source_dir=""
nw_pos=(0,0)
dest_dir=""
current_platform=""
app_window=None
selected_save=None
Save_name=None
csv_saves =""
save_list=None
Continue_rewrite=False
def status_notify(title, message):
    notification = Notify()
    notification.title = title
    notification.message = message
    notification.send()

def action(type, src, target):
    global current_platform
    global csv_saves
    global Save_name
    global selected_save
    global new_folder_name
    global save_list
    global Save_name
    global app_window
    global Continue_load
    global Continue_rewrite
    if type == "load" and selected_save!=None:
        if os.path.isdir(src) == True:
            app_window.withdraw()
            Continue_load=askyesno(title="Load save",message="Do you want to overwrite game loaded save?")
            app_window.deiconify()
            app_window.lift()
            if Continue_load==True:
                if current_platform == "Windows":
                    status_notify("ARK SAVER", "Loading...")
                    os.popen("xcopy '"+ src+"' "+"'"+target+"'")
                    print("windows triggered")
                    status_notify("ARK SAVER", "Save loaded!")
                    reload_saves()

                if current_platform == "Linux":
                    status_notify("ARK SAVER", "Loading...")
                    print("cp -R '"+ src+"/'* "+"'"+target+"'")
                    os.popen("cp -R '"+ src+"/'* "+"'"+target+"'")
                    status_notify("ARK SAVER", "Save loaded!")
                    reload_saves()

    if type == "save":
        app_window.withdraw()
        new_folder_name="ARK-"+datetime.now().strftime("%d-%m-%Y-%H-%M")
        app_window.deiconify()
        app_window.lift()
        if os.path.isdir(target+"/"+new_folder_name) == True:
            app_window.withdraw()
            Continue_rewrite=askyesno(title="Rewrite save",message="Save with duplicate timestamp exist rewrite?")
            app_window.deiconify()
            app_window.lift()
        else:
            Save_name=simpledialog.askstring(title="New save",prompt="Name/description:")
            Continue_rewrite=False
        reload_saves()

        if os.path.isdir(target+"/"+new_folder_name) == True and Continue_rewrite==True or os.path.isdir(target+"/"+new_folder_name) == False:

            if Save_name!=None and Save_name!="":
                if current_platform == "Windows":
                    status_notify("ARK SAVER", "Saving...")
                    os.popen("xcopy '"+ src+"' "+"'"+target+"/"+new_folder_name+"'")
                    csv_saves=csv_saves+target+"/"+new_folder_name+";"+Save_name+"\n"
                    file=open('saves.csv', 'w')
                    file.write(csv_saves)
                    file.close()
                    print("windows triggered")
                    status_notify("ARK SAVER", "Game saved!")
                if current_platform == "Linux":
                    status_notify("ARK SAVER", "Saving...")
                    os.popen("cp -R '"+ src+"' "+"'"+target+"/"+new_folder_name+"'")
                    if Continue_rewrite == False:
                        csv_saves=csv_saves+target+"/"+new_folder_name+";"+Save_name+"\n"
                        file=open('saves.csv', 'w')
                        file.write(csv_saves)
                        file.close()
                        status_notify("ARK SAVER", "Game saved!")
                reload_saves()

    if type == "delete" and selected_save!=None:
        new_list_csv=""
        print(csv_saves)
        shutil.rmtree(csv_saves.split("\n")[selected_save].split(";")[0])
        for i in range(0,len(csv_saves.split("\n"))-1):
            if selected_save!=i:
                print(str(i)+":"+str(selected_save)+":"+new_list_csv+csv_saves.split("\n")[i])
                new_list_csv=new_list_csv+csv_saves.split("\n")[i]+"\n"
        csv_saves = new_list_csv
        print(csv_saves)
        print(new_list_csv)
        print(selected_save)
        file=open('saves.csv', 'w')
        file.write(csv_saves)
        file.close()
        reload_saves()




def init():
    global app_window
    global dest_dir
    global source_dir
    global current_platform
    global csv_saves
    current_platform=platform.system()
    if current_platform!="Linux" and current_platform!="Windows":
        status_notify("ARK Saver", "Unsupported platform: "+str(platform.system())+"\n"+"Supported platforms:[Linux, Windows]")
        sys.exit()

    app = Qt.QApplication([])
    if os.path.isfile("saves.csv") == True:
        csv_save_file=open('saves.csv', 'r+', encoding="utf-8")
        csv_saves = csv_save_file.read()

    print("File exists?:"+str(os.path.isfile("saver.cfg")))
    if os.path.isfile("saver.cfg") == True:
        cfg_file = open('saver.cfg', 'r+', encoding="utf-8")
        cfg_file_copy = cfg_file.read()

        source_dir = cfg_file_copy.split("\n")[0].split("'")[1]
        dest_dir= cfg_file_copy.split("\n")[1].split("'")[1]
        status_notify("ARK SAVER", "Source="+source_dir+"\n"+"Dest="+dest_dir)
        cfg_file.close()
        app.quit()
        with Listener(
                on_press=on_press,
                on_release=on_release) as listener:
            listener.join()

    else:
        cfg_file = open('saver.cfg', 'at', encoding="utf-8")
        status_notify("ARK SAVER", "Select ARK saves folder")
        showinfo("ARK SAVER", "Select ARK saves folder")
        cfg_file.write("source_dir='"+Qt.QFileDialog.getExistingDirectoryUrl(None,'choose ARK saves folder').toString().replace("file://","")+"'\n")
        status_notify("ARK SAVER", "Select manual saves folder")
        showinfo("ARK SAVER", "Select your manual saves folder")
        cfg_file.write("dest_dir='"+Qt.QFileDialog.getExistingDirectoryUrl(None,'choose manual saves folder').toString().replace("file://","")+"'\n")
        cfg_file.close()
        app.quit()
        init()



def on_select(event):
    global selected_save
    if len(event.widget.curselection())>0:
        index=event.widget.curselection()[0]
        selected_save=index





def reload_saves():
    global save_list
    global csv_saves
    if save_list.size()>0:
        save_list.delete(0,END)
    if csv_saves!="":
        for i in range(0,len(csv_saves.split("\n"))-1):
            save_list.insert(i,csv_saves.split("\n")[i].split(";")[1]+"     "+csv_saves.split("\n")[i].split(";")[0])

def start_gui():
    global nw_pos
    global app_window
    global current_platform
    global dest_dir
    global source_dir
    global selected_save
    global save_list



    if current_platform == "Windows":
        import pygetwindow as gw
        nw_pos=(gw.getActiveWidow().top-400,gw.getActiveWidow().left-300)
        pass
    if current_platform == "Linux":
        focus_id = subprocess.check_output('xdotool getwindowfocus', shell=True).decode('utf-8').strip().split('\n')[0]
        nw_pos=(int(subprocess.check_output('xwininfo -id '+focus_id+"| grep X:", shell=True).decode('utf-8').strip().split('\n')[0].split("X:")[1])+((pyautogui.size()[0]/4)-400),int(subprocess.check_output('xwininfo -id '+focus_id+"| grep Y:", shell=True).decode('utf-8').strip().split('\n')[0].split("Y:")[1])+((pyautogui.size()[1]/2)-300))


    if app_window == None:
        app_window = Tk()
        app_window.geometry("800x600+"+str(nw_pos[0]).replace(".0","")+"+"+str(nw_pos[1]).replace(".0",""))
        app_window.overrideredirect(True)
        app_window.configure(background='#20396b')
        app_window.configure(bg='#20396b')
        app_window.tk_setPalette(background='#20396b', foreground='White',activeBackground='#1c3360', activeForeground="White")
        app_window.wm_attributes("-topmost", True)
        app_window.wait_visibility(app_window)
        app_window.attributes('-alpha', 0.9)
        title=Label(app_window, text="ARK Save Manager", font="Calibry 12", bg='#20396b', fg="White")




        title.pack()
        control_box = Frame(app_window, bg="White",height=500,width=50)
        list_box = Frame(app_window, height=500,width=50)
        list_box.pack(side = LEFT, pady=50, padx=50)
        save_list=Listbox(list_box, height=500,width=50, bd=0, font="Calibry 12",fg="White", bg="#265c99")
        yscrollbar = Scrollbar(list_box, bg="White")
        yscrollbar.pack(side = RIGHT, fill= Y)
        xscrollbar = Scrollbar(list_box, orient='horizontal', bg="White")
        xscrollbar.pack(side = BOTTOM, fill= X)
        save_list.config(yscrollcommand = yscrollbar.set)
        save_list.config(xscrollcommand = xscrollbar.set)
        yscrollbar.config(command = save_list.yview)
        xscrollbar.config(command = save_list.xview)
        control_box.pack(side=RIGHT, padx=50)
        save_list.bind('<<ListboxSelect>>', on_select)
        save_list.pack(side = LEFT)
        btn_save = Button(control_box, width=8, text="New save", font="Calibry 12",fg="White", bg="#265c99", command= lambda:action("save",source_dir, dest_dir))
        btn_load = Button(control_box, width=8, text="Load", font="Calibry 12",fg="White", bg="#265c99",command= lambda: action("load",csv_saves.split("\n")[selected_save].split(";")[0],source_dir))
        btn_edit = Button(control_box, width=8, text="Edit", font="Calibry 12",fg="White", bg="#265c99",command= lambda: action("edit",dest_dir,csv_saves[selected_save].split(";")[0]))
        btn_delete = Button(control_box, width=8, text="Delete", font="Calibry 12",fg="White", bg="#265c99",command= lambda: action("delete","",""))
        btn_save.pack()
        btn_load.pack()
        btn_edit.pack()
        btn_delete.pack()
        reload_saves()
        app_window.mainloop()

    else:
        app_window.deiconify()



def stop_gui():
    global gui_active
    global app_window
    gui_active = False
    app_window.withdraw()


def on_press(key):
    pass



def on_release(key):
    global gui_active
    try:
        if key==key.f5 and gui_active == False:
            gui_active = True
            threading.Thread(target=start_gui, args=()).start()


        if key ==Key.esc:
            if gui_active == True:
               stop_gui()
               gui_active = False



    except:
        pass




if __name__ == '__main__':
    gc.enable()
    init()
