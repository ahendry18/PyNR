from tkinter import *
import serial

import matplotlib .pyplot as plt
root = Tk()
root.iconbitmap(default='icon.ico')
root.title("North Robotics Navigator 1.0")
root.geometry("1000x500")
ser = serial.Serial('COM4', baudrate=115200, timeout=1)

propData = '0'
myVar1 = '0'
myVar2 = '0'


def leftClick1(event): #graph

    myVar1 = str(entry1.get())
    stringvar = ">AN01 V1[" + myVar1 + "]\r"
    ser.write(stringvar.encode('utf-8'))

    readprop()

def leftClick2(event): #programming box

    myVar2 = str(entry2.get())
    stringvar = ">AN02 V1[" + myVar2 + "]\r"
    ser.write(stringvar.encode('utf-8'))

    readprop()

def readprop():
    propData = ser.readline().decode('ascii')
    print(propData)
    textbox1.insert(1.0, propData)

mp = PhotoImage(file= 'robot app background.gif')
label1=Label(root, text = "hello", image = mp )
label1.place(x = 0, y = 0)

button1 = Button(root, text="AN01", relief = RAISED, font=("Helvetica", 10), bg = 'GREY', foreground = 'WHITE', height  = 3, width = 5 )
button1.place(x = 10, y =10, width=100, height=50)
button1.bind("<Button-1>", leftClick1)

button2 = Button(root, text="AN02", relief = RAISED, font=("Helvetica", 10), bg = 'GREY', foreground = 'WHITE', height  = 3, width = 5 )
button2.place(x = 10, y =70, width=100, height=50)
button2.bind("<Button-1>", leftClick2)

button3 = Button(root, text="AN03", relief = RAISED, font=("Helvetica", 10), bg = 'GREY', foreground = 'WHITE', height  = 3, width = 5 )
button3.place(x = 10, y =130, width=100, height=50)
#button3.bind("<Button-1>", leftClick3)

entry1 = Entry(root, font = ("Helvetica", 20))
entry1.place(x = 125, y =15, width=120, height=40)

entry2 = Entry(root, font = ("Helvetica", 20))
entry2.place(x = 125, y =75, width=120, height=40)

entry3 = Entry(root, font = ("Helvetica", 20))
entry3.place(x = 125, y =135, width=120, height=40)


textbox1 = Text(root, width = 35, height = 10)
textbox1.place(x = 260, y =15, width=200, height=400)

textbox2 = Text(root, width = 35, height = 10)
textbox2.place(x = 475, y =15, width=200, height=400)

mainloop()