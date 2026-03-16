from time import strftime
from tkinter import *
#time 
def time():
    string=strftime('%I:%M:%S %p %a %y')
    rootl.configure(text=string)
    root.after(1000,time)
#window
root=Tk()
root.title('CLOCK')
rootl=Label(text='',font=('times new roman',75),background='black',foreground='white')
rootl.pack(fill='x')
time()
mainloop()
