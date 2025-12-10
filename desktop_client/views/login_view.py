import tkinter as tk
from tkinter import ttk, messagebox
import threading

class LoginView(tk.Frame):
    
    def __init__(self, parent, api_client, on_login_success):
        super().__init__(parent)
        self.api_client = api_client
        self.on_login_success = on_login_success
        
        self.pack(fill=tk.BOTH, expand=True)
        self.create_widgets()
    
    def create_widgets(self):
        main_frame = ttk.Frame(self, padding="40")
        main_frame.pack(expand=True)
        
        title_label = ttk.Label(
            main_frame,
            text=" Online Bookstore",
            font=('Arial', 24, 'bold')
        )
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 30))
        
        notebook = ttk.Notebook(main_frame)
        notebook.grid(row=1, column=0, columnspan=2, sticky='nsew')
        
        #login tab
        login_frame = ttk.Frame(notebook, padding="20")
        notebook.add(login_frame, text="Login")
        self.create_login_tab(login_frame)
        
        #register tab
        register_frame = ttk.Frame(notebook, padding="20")
        notebook.add(register_frame, text="Register")
        self.create_register_tab(register_frame)
    
    def create_login_tab(self, parent):
        ttk.Label(parent, text="Username:", font=('Arial', 10)).grid(
            row=0, column=0, sticky='w', pady=5
        )
        self.login_username = ttk.Entry(parent, width=30, font=('Arial', 10))
        self.login_username.grid(row=0, column=1, pady=5, padx=5)
        
        ttk.Label(parent, text="Password:", font=('Arial', 10)).grid(
            row=1, column=0, sticky='w', pady=5
        )
        self.login_password = ttk.Entry(parent, width=30, show='*', font=('Arial', 10))
        self.login_password.grid(row=1, column=1, pady=5, padx=5)
        
        self.login_button = ttk.Button(
            parent,
            text="Login",
            command=self.handle_login
        )
        self.login_button.grid(row=2, column=0, columnspan=2, pady=20)
        
        self.login_status = ttk.Label(parent, text="", foreground="blue")
        self.login_status.grid(row=3, column=0, columnspan=2)
        
        #Bind Enter key
        self.login_password.bind('<Return>', lambda e: self.handle_login())
    
    def create_register_tab(self, parent):
        ttk.Label(parent, text="Username:", font=('Arial', 10)).grid(
            row=0, column=0, sticky='w', pady=5
        )
        self.reg_username = ttk.Entry(parent, width=30, font=('Arial', 10))
        self.reg_username.grid(row=0, column=1, pady=5, padx=5)
        
        ttk.Label(parent, text="Email:", font=('Arial', 10)).grid(
            row=1, column=0, sticky='w', pady=5
        )
        self.reg_email = ttk.Entry(parent, width=30, font=('Arial', 10))
        self.reg_email.grid(row=1, column=1, pady=5, padx=5)
        
        ttk.Label(parent, text="Password:", font=('Arial', 10)).grid(
            row=2, column=0, sticky='w', pady=5
        )
        self.reg_password = ttk.Entry(parent, width=30, show='*', font=('Arial', 10))
        self.reg_password.grid(row=2, column=1, pady=5, padx=5)
        
        self.register_button = ttk.Button(
            parent,
            text="Register",
            command=self.handle_register
        )
        self.register_button.grid(row=3, column=0, columnspan=2, pady=20)
        
        self.reg_status = ttk.Label(parent, text="", foreground="blue")
        self.reg_status.grid(row=4, column=0, columnspan=2)
        
        self.reg_password.bind('<Return>', lambda e: self.handle_register())
    
    def handle_login(self):
        username = self.login_username.get().strip()
        password = self.login_password.get()
        
        if not username or not password:
            messagebox.showerror("Error", "Please fill in all fields")
            return
        
        self.login_button.config(state='disabled')
        self.login_status.config(text="Logging in...", foreground="blue")
        
        def login_thread():
            success, message = self.api_client.login(username, password)
            self.after(0, lambda: self.handle_login_response(success, message))
        
        threading.Thread(target=login_thread, daemon=True).start()
    
    def handle_login_response(self, success, message):
        self.login_button.config(state='normal')
        
        if success:
            self.login_status.config(text=message, foreground="green")
            self.after(500, self.on_login_success)
        else:
            self.login_status.config(text=message, foreground="red")
            messagebox.showerror("Login Failed", message)
    
    def handle_register(self):
        username = self.reg_username.get().strip()
        email = self.reg_email.get().strip()
        password = self.reg_password.get()
        
        if not username or not email or not password:
            messagebox.showerror("Error", "Please fill in all fields")
            return
        
        self.register_button.config(state='disabled')
        self.reg_status.config(text="Registering...", foreground="blue")
        
        def register_thread():
            success, message = self.api_client.register(username, email, password)
            self.after(0, lambda: self.handle_register_response(success, message))
        
        threading.Thread(target=register_thread, daemon=True).start()
    
    def handle_register_response(self, success, message):
        self.register_button.config(state='normal')
        
        if success:
            self.reg_status.config(text=message, foreground="green")
            messagebox.showinfo("Success", message)
            self.reg_username.delete(0, tk.END)
            self.reg_email.delete(0, tk.END)
            self.reg_password.delete(0, tk.END)
        else:
            self.reg_status.config(text=message, foreground="red")
            messagebox.showerror("Registration Failed", message)
