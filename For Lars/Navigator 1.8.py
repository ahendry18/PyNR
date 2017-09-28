from tkinter import *
import serial

import matplotlib .pyplot as plt
root = Tk()
root.iconbitmap(default='icon.ico')
root.title("North Robotics Navigator 1.0")
root.geometry("1000x500")
ser = serial.Serial('COM4', baudrate=115200, timeout=1)

lineA = 1
propData = '0'
myVar1 = '0'
myVar2 = '0'


def buttonPress1(event): #graph


    global lineA

    lineA +=1

    #myVar1 = str(textbox2.get(2.0, 2.15))
    myVar1 = str(textbox2.get("%d.%d" % (lineA, 0), "%d.%d" % (lineA, 20)))


    stringvar = ">AN02 V1[" + myVar1 + "]\r"
    ser.write(stringvar.encode('utf-8'))
    print(myVar1)
    readprop()

def buttonPress2(event): #programming box

    myVar2 = str(entry2.get())
    stringvar = ">AN02 V1[" + myVar2 + "]\r"
    ser.write(stringvar.encode('utf-8'))

    readprop()

def buttonPress3(event): #programming box

    myVar2 = str(entry2.get())
    stringvar = ">AN02 V1[" + myVar2 + "]\r"
    ser.write(stringvar.encode('utf-8'))

    readprop()

def buttonPress4(event): #programming box

    readprop()

def buttonPress5(event): #programming box

    northfile = open("Code.txt", 'r')
    textbox2.insert(1.0,northfile.read())

def readprop():

    propData = ser.readline().decode('ascii')
    print(propData)
    textbox1.insert(1.0, propData)

mp = PhotoImage(file= 'robot app background.gif')
label1=Label(root, text = "hello", image = mp )
label1.place(x = 0, y = 0)

button1 = Button(root, text="read", relief = RAISED, font=("Helvetica", 10), bg = 'GREY', foreground = 'WHITE', height  = 3, width = 5 )
button1.place(x = 10, y =10, width=100, height=50)
button1.bind("<Button-1>", buttonPress1)

button2 = Button(root, text="Axis0-", relief = RAISED, font=("Helvetica", 10), bg = 'GREY', foreground = 'WHITE', height  = 3, width = 5 )
button2.place(x = 10, y =70, width=100, height=50)
button2.bind("<Button-1>", buttonPress2)

button3 = Button(root, text="Axis1+", relief = RAISED, font=("Helvetica", 10), bg = 'GREY', foreground = 'WHITE', height  = 3, width = 5 )
button3.place(x = 10, y =130, width=100, height=50)
button3.bind("<Button-1>", buttonPress3)

button4 = Button(root, text="Axis1-", relief = RAISED, font=("Helvetica", 10), bg = 'GREY', foreground = 'WHITE', height  = 3, width = 5 )
button4.place(x = 10, y =190, width=100, height=50)
button4.bind("<Button-1>", buttonPress4)

button5 = Button(root, text="Open", relief = RAISED, font=("Helvetica", 10), bg = 'GREY', foreground = 'WHITE', height  = 3, width = 5 )
button5.place(x = 10, y =250, width=100, height=50)
button5.bind("<Button-1>", buttonPress5)


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

textfile = open("Code.txt")





mainloop()