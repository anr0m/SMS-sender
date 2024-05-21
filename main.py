import tkinter as tk
from tkinter import ttk
import pages

class SMSApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("SMS App")
        self.geometry("555x600")
        self.create_widgets()

    def create_widgets(self):
        self.tabControl = ttk.Notebook(self)

        self.page1 = ttk.Frame(self.tabControl)
        self.page2 = ttk.Frame(self.tabControl)
        self.page3 = ttk.Frame(self.tabControl)
        self.page4 = ttk.Frame(self.tabControl)

        self.tabControl.add(self.page1, text="Sending an SMS")
        self.tabControl.add(self.page2, text="Group management")
        self.tabControl.add(self.page3, text="Recipient management")
        self.tabControl.add(self.page4, text="Administration of Groups")

        self.tabControl.pack(expand=1, fill="both")

        pages.Page1(self.page1)
        pages.Page2(self.page2)
        pages.Page3(self.page3)
        pages.Page4(self.page4)

if __name__ == "__main__":
    app = SMSApp()
    app.mainloop()
