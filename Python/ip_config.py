import tkinter as tk
from tkinter import ttk

class IPConfigurator:
    def __init__(self):
        # Standard IP-adresse
        self.clientAddress = None
        self.standard_ip = "100"
        self.closed = False
        # Global variabel for å holde styr på om vinduet allerede er åpent
        self.window_open = False   
        
    # Funksjon som oppdaterer IP-adressen når brukeren velger en verdi fra rullegardinmenyen
    def updateIP(self):
        self.clientAddress = f"192.168.10.{str(self.var1.get())}{str(self.var2.get())}{str(self.var3.get())}"
        self.root.destroy()
        self.window_open = False

    def on_close(self):
        self.closed = True
        self.root.destroy()
        
    # Funksjon som åpner et vindu for å velge en IP-adresse
    def selectIP(self, invalid_ip = None):
        if self.window_open:
            return
        self.window_open = True

        self.root = tk.Tk()
        self.root.style = ttk.Style()
        self.root.style.configure(".", font=("Arial", 20, "bold"))
        self.root.option_add("*Font", "Arial 20 bold")

        
        self.root.title("IP Address Configuration")
        self.root.attributes('-fullscreen', True)
        self.root.resizable(False, False)
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        
        self.frame = ttk.Frame(self.root)
        self.frame.pack(pady=15)
        
        self.label = ttk.Label(self.frame, text="192.168.10.")
        self.label.pack(side=tk.LEFT)
        
        self.var1 = tk.StringVar(self.root)
        self.var2 = tk.StringVar(self.root)
        self.var3 = tk.StringVar(self.root)
        
        
        self.dropdown1 = ttk.OptionMenu(self.frame, self.var1, *range(-1,3))
        self.dropdown1.pack(side=tk.LEFT)
        
        self.dropdown2 = ttk.OptionMenu(self.frame, self.var2, *range(-1,6))
        self.dropdown2.pack(side=tk.LEFT)
        
        self.dropdown3 = ttk.OptionMenu(self.frame, self.var3, *range(-1,6))
        self.dropdown3.pack(side=tk.LEFT)
        self.var1.set(self.standard_ip[0])
        self.var2.set(self.standard_ip[1])
        self.var3.set(self.standard_ip[2])

        

        if invalid_ip != None:
            invalid = tk.Label(self.root, text=f"Feil ip: {invalid_ip}", fg="red")
            invalid.pack(pady=15)
        
        self.ok_button = ttk.Button(self.root, text="Ok", command=self.updateIP, padding=(0,10))
        self.ok_button.pack(pady=15)
        
        self.cancel_button = ttk.Button(self.root, text="Avbryt", command=self.on_close, padding=(0,10))
        self.cancel_button.pack()
        
        self.root.mainloop()
