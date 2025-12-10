import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from api_client import APIClient
from views.login_view import LoginView
from views.customer_main import CustomerMainView
from views.manager_main import ManagerMainView

class BookstoreApp(tk.Tk):
    
    def __init__(self):
        super().__init__()
        
        self.title("Online Bookstore")
        self.geometry("1100x800")
        
        self.setup_style()
        
        self.api_client = APIClient("http://localhost:5000")
        
        self.current_view = None
        
        self.show_login()
        
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def setup_style(self):
        style = ttk.Style()
        
        available_themes = style.theme_names()
        if 'clam' in available_themes:
            style.theme_use('clam')
        elif 'alt' in available_themes:
            style.theme_use('alt')
        
        style.configure('TButton', padding=6)
        style.configure('TLabel', padding=3)
    
    def clear_view(self):
        if self.current_view:
            self.current_view.destroy()
            self.current_view = None
    
    def show_login(self):
        self.clear_view()
        self.current_view = LoginView(self, self.api_client, self.on_login_success)
    
    def on_login_success(self):
        #show right view based on user role
        if self.api_client.is_manager():
            self.show_manager_view()
        else:
            self.show_customer_view()
    
    def show_customer_view(self):
        self.clear_view()
        self.current_view = CustomerMainView(self, self.api_client, self.show_login)
    
    def show_manager_view(self):
        self.clear_view()
        self.current_view = ManagerMainView(self, self.api_client, self.show_login)
    
    def on_closing(self):
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.destroy()

def main():
    print("Online Bookstore Desktop Client")
 
    app = BookstoreApp()
    app.mainloop()

if __name__ == "__main__":
    main()
