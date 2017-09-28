from tkinter import *
import serial

root = Tk()
root.iconbitmap(default='icon.ico')
root.title("North Robotics Navigator 1.0")
root.geometry("1000x500")
ser = serial.Serial('COM4', baudrate=115200, timeout=1)

myVar1 = '0'
myVar2 = '0'
element = []


def leftClick1(event):

    myVar1 = str(entry1.get())
    stringvar = ">BLNK V1[" + myVar1 + "]\r"

    ser.write(stringvar.encode('utf-8'))
def leftClick2(event):

    stringvar = ">AN01 V1[" + myVar2 + "]\r"

    ser.write(stringvar.encode('utf-8'))

    propData = ser.readline().decode('ascii')
    entry2.delete(0, END)
    entry2.insert(0, propData)

def leftClick3(event):
    myVar3 = '1'
    stringvar = ">AN01 V1[" + myVar3 + "]\r"

    ser.write(stringvar.encode('utf-8'))

    propData = ser.readline().decode('ascii')
    element.append(propData)


    #textbox.insert(END, element[i])

def leftClick4(event):
    print(element[:])


mp = PhotoImage(file= 'robot app background.gif')
label1=Label(root, text = "hello", image = mp )
label1.place(x = 0, y = 0)

button1 = Button(root, text="SEND", relief = RAISED, font=("Helvetica", 15), bg = 'GREY', foreground = 'WHITE', height  = 3, width = 8 )
button1.grid(row  = 1, column = 1, padx = 10, pady = 10)
button1.bind("<Button-1>", leftClick1)

button2 = Button(root, text="READ", relief = RAISED, font=("Helvetica", 15), bg ='#89B0C1', foreground = 'WHITE', height  = 3, width = 8 )
button2.grid(row  = 2, column = 1)
button2.bind("<Button-1>", leftClick2)

button3 = Button(root, text="DATA", relief = RAISED, font=("Helvetica", 15), bg ='#89B0C1', foreground = 'WHITE', height  = 3, width = 8 )
button3.grid(row  = 3, column = 1, padx = 10, pady = 10)
button3.bind("<Button-1>", leftClick3)

button4 = Button(root, text="PRINT", relief = RAISED, font=("Helvetica", 15), bg ='#89B0C1', foreground = 'WHITE', height  = 3, width = 8 )
button4.grid(row  = 4, column = 1, padx = 10, pady = 10)
button4.bind("<Button-1>", leftClick4)



entry1 = Entry(root, font = ("Helvetica", 20))
entry1.grid (row = 1, column = 2)

entry2 = Entry(root, font = ("Helvetica", 20))
entry2.grid (row = 2, column = 2)

textbox = Text(root, width = 35, height = 10)
textbox.grid(row = 3, column = 2)



mainloop()