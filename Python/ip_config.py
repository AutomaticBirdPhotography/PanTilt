import tkinter as tk
from tkinter import ttk

class IPConfigurator:
    def __init__(self):
        # Standard IP-adresse
        self.clientAddress = None
        self.standard_group = "4"
        self.standard_ip = "100"
        self.valid_var2_range = range(0, 10)
        self.valid_var3_range = range(0, 10)
        self.closed = False
        # Global variabel for å holde styr på om vinduet allerede er åpent
        self.window_open = False
        
        # Initialize dropdown attributes
        self.dropdown1 = None
        self.dropdown2 = None
        self.dropdown3 = None
        
    # Funksjon som oppdaterer IP-adressen når brukeren velger en verdi fra rullegardinmenyen
    def updateIP(self):
        self.clientAddress = f"192.168.{str(self.var0.get())}.{str(self.var1.get())}{str(self.var2.get())}{str(self.var3.get())}"
        self.root.destroy()
        self.window_open = False

    def on_close(self):
        self.closed = True
        self.root.destroy()
    
    def get_valid_range(self, *args):
        var1_value = self.var1.get()
        var2_value = self.var2.get()
        var3_value = self.var3.get()

        if var1_value in ['0', '1']:
            self.valid_var2_range = range(0, 10)
            self.valid_var3_range = range(0, 10)
        elif var1_value == "2":
            self.valid_var2_range = range(0, 6)
            if int(var2_value) >= 5:
                self.var2.set('5')
                self.valid_var3_range = range(0, 6)
                if int(var3_value) > 5:
                    self.var3.set('5')
            else:
                self.valid_var3_range = range(0, 10)

        self.update_dropdown_options()
    
    def update_dropdown_options(self):
        if self.dropdown2 is not None:
            self.dropdown2['menu'].delete(0, 'end')
            for value in self.valid_var2_range:
                self.dropdown2['menu'].add_command(label=value, command=lambda v=value: self.var2.set(v))
        
        if self.dropdown3 is not None:
            self.dropdown3['menu'].delete(0, 'end')
            for value in self.valid_var3_range:
                self.dropdown3['menu'].add_command(label=value, command=lambda v=value: self.var3.set(v))

        
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
        
        self.label = ttk.Label(self.frame, text="192.168.")
        self.label.pack(side=tk.LEFT)
        
        self.var0 = tk.StringVar(self.root)
        self.var1 = tk.StringVar(self.root)
        self.var2 = tk.StringVar(self.root)
        self.var3 = tk.StringVar(self.root)
        
        self.var1.trace("w", self.get_valid_range)  # Lytter for endringer i var1
        self.var2.trace("w", self.get_valid_range)
        
        self.dropdown0 = ttk.OptionMenu(self.frame, self.var0, *["0", "4", "10"])
        self.dropdown0.pack(side=tk.LEFT)
        
        self.dot_label = ttk.Label(self.frame, text=".")
        self.dot_label.pack(side=tk.LEFT)
        
        self.dropdown1 = ttk.OptionMenu(self.frame, self.var1, *range(-1,3))
        self.dropdown1.pack(side=tk.LEFT)
        
        self.dropdown2 = ttk.OptionMenu(self.frame, self.var2, *self.valid_var2_range)
        self.dropdown2.pack(side=tk.LEFT)
        
        self.dropdown3 = ttk.OptionMenu(self.frame, self.var3, *self.valid_var3_range)
        self.dropdown3.pack(side=tk.LEFT)
        self.var0.set(self.standard_group)
        self.var1.set(self.standard_ip[0])
        self.var2.set(self.standard_ip[1])
        self.var3.set(self.standard_ip[2])
        self.get_valid_range()

        

        if invalid_ip != None:
            invalid = tk.Label(self.root, text=f"Feil ip: {invalid_ip}", fg="red")
            invalid.pack(pady=15)
        
        self.ok_button = ttk.Button(self.root, text="Ok", command=self.updateIP, padding=(0,10))
        self.ok_button.pack(pady=15)
        
        self.cancel_button = ttk.Button(self.root, text="Avbryt", command=self.on_close, padding=(0,10))
        self.cancel_button.pack()
        
        self.root.mainloop()
