import tkinter as tk
from tkinter import ttk, messagebox
import threading

class CustomerMainView(tk.Frame):
    
    def __init__(self, parent, api_client, on_logout):
        super().__init__(parent)
        self.api_client = api_client
        self.on_logout = on_logout
        self.cart = []
        
        self.pack(fill=tk.BOTH, expand=True)
        self.create_widgets()
        
        self.load_all_books()
    
    def create_widgets(self):
        #Top bar
        top_frame = ttk.Frame(self, padding="10")
        top_frame.pack(fill=tk.X)
        
        ttk.Label(
            top_frame,
            text=f"Welcome, {self.api_client.user['username']}!",
            font=('Arial', 14, 'bold')
        ).pack(side=tk.LEFT)
        
        ttk.Button(
            top_frame,
            text="Logout",
            command=self.handle_logout
        ).pack(side=tk.RIGHT)
        
        content_frame = ttk.Frame(self, padding="10")
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        left_frame = ttk.Frame(content_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        search_frame = ttk.Frame(left_frame)
        search_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(search_frame, text="Search:", font=('Arial', 10)).pack(side=tk.LEFT, padx=(0, 5))
        
        self.search_entry = ttk.Entry(search_frame, font=('Arial', 10))
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.search_entry.bind('<Return>', lambda e: self.search_books())
        
        self.search_button = ttk.Button(
            search_frame,
            text="Search",
            command=self.search_books
        )
        self.search_button.pack(side=tk.LEFT)
        
        self.status_label = ttk.Label(left_frame, text="", foreground="blue")
        self.status_label.pack(fill=tk.X, pady=(0, 5))
        
        books_frame = ttk.Frame(left_frame)
        books_frame.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(books_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.books_tree = ttk.Treeview(
            books_frame,
            columns=('ID', 'Title', 'Author', 'Buy Price', 'Rent Price'),
            show='headings',
            yscrollcommand=scrollbar.set
        )
        scrollbar.config(command=self.books_tree.yview)
        
        #Column headings
        self.books_tree.heading('ID', text='ID')
        self.books_tree.heading('Title', text='Title')
        self.books_tree.heading('Author', text='Author')
        self.books_tree.heading('Buy Price', text='Buy Price')
        self.books_tree.heading('Rent Price', text='Rent Price')
        
        #Column widths
        self.books_tree.column('ID', width=40)
        self.books_tree.column('Title', width=200)
        self.books_tree.column('Author', width=150)
        self.books_tree.column('Buy Price', width=80)
        self.books_tree.column('Rent Price', width=80)
        
        self.books_tree.pack(fill=tk.BOTH, expand=True)
        
        button_frame = ttk.Frame(left_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(
            button_frame,
            text="Add to Buy Cart",
            command=lambda: self.add_to_cart('buy')
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            button_frame,
            text="Add to Rent Cart",
            command=lambda: self.add_to_cart('rent')
        ).pack(side=tk.LEFT)
        
        right_frame = ttk.LabelFrame(content_frame, text="Shopping Cart", padding="10")
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH)
        right_frame.config(width=300)
        
        cart_frame = ttk.Frame(right_frame)
        cart_frame.pack(fill=tk.BOTH, expand=True)
        
        cart_scrollbar = ttk.Scrollbar(cart_frame)
        cart_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.cart_listbox = tk.Listbox(
            cart_frame,
            yscrollcommand=cart_scrollbar.set,
            font=('Arial', 9)
        )
        cart_scrollbar.config(command=self.cart_listbox.yview)
        self.cart_listbox.pack(fill=tk.BOTH, expand=True)
        
        cart_button_frame = ttk.Frame(right_frame)
        cart_button_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(
            cart_button_frame,
            text="Remove Selected",
            command=self.remove_from_cart
        ).pack(fill=tk.X, pady=(0, 5))
        
        ttk.Button(
            cart_button_frame,
            text="Clear Cart",
            command=self.clear_cart
        ).pack(fill=tk.X, pady=(0, 5))
        
        self.total_label = ttk.Label(
            right_frame,
            text="Total: $0.00",
            font=('Arial', 12, 'bold')
        )
        self.total_label.pack(pady=(10, 0))
        
        self.checkout_button = ttk.Button(
            right_frame,
            text="Place Order",
            command=self.checkout,
            state='disabled'
        )
        self.checkout_button.pack(fill=tk.X, pady=(10, 0))
    
    def load_all_books(self):
        self.status_label.config(text="Loading books...", foreground="blue")
        
        def load_thread():
            success, data = self.api_client.search_books("")
            self.after(0, lambda: self.handle_books_response(success, data))
        
        threading.Thread(target=load_thread, daemon=True).start()
    
    def handle_books_response(self, success, data):
        if success:
            books = data
            self.status_label.config(
                text=f"Loaded {len(books)} book(s)",
                foreground="green"
            )
            self.display_books(books)
        else:
            self.status_label.config(text=f"Error: {data}", foreground="red")
            messagebox.showerror("Load Failed", data)
    
    def search_books(self):
        keyword = self.search_entry.get().strip()
        
        self.search_button.config(state='disabled')
        self.status_label.config(text="Searching...", foreground="blue")
        
        def search_thread():
            success, data = self.api_client.search_books(keyword)
            self.after(0, lambda: self.handle_search_response(success, data))
        
        threading.Thread(target=search_thread, daemon=True).start()
    
    def handle_search_response(self, success, data):
        self.search_button.config(state='normal')
        
        if success:
            books = data
            self.status_label.config(
                text=f"Found {len(books)} book(s)",
                foreground="green"
            )
            self.display_books(books)
        else:
            self.status_label.config(text=f"Error: {data}", foreground="red")
            messagebox.showerror("Search Failed", data)
    
    def display_books(self, books):
        for item in self.books_tree.get_children():
            self.books_tree.delete(item)
        
        for book in books:
            self.books_tree.insert('', tk.END, values=(
                book['id'],
                book['title'],
                book['author'],
                f"${book['price_buy']:.2f}",
                f"${book['price_rent']:.2f}"
            ))
    
    def add_to_cart(self, item_type):
        selection = self.books_tree.selection()
        
        if not selection:
            messagebox.showwarning("No Selection", "Please select a book first")
            return
        
        item = self.books_tree.item(selection[0])
        values = item['values']
        
        book_id = values[0]
        title = values[1]
        author = values[2]
        price = float(values[3][1:]) if item_type == 'buy' else float(values[4][1:])
        
        self.cart.append({
            'book_id': book_id,
            'title': title,
            'author': author,
            'type': item_type,
            'price': price
        })
        
        self.update_cart_display()
        
        messagebox.showinfo("Added", f"Added '{title}' to {item_type} cart")
    
    def update_cart_display(self):
        self.cart_listbox.delete(0, tk.END)
        
        total = 0
        for item in self.cart:
            text = f"[{item['type'].upper()}] {item['title']} - ${item['price']:.2f}"
            self.cart_listbox.insert(tk.END, text)
            total += item['price']
        
        self.total_label.config(text=f"Total: ${total:.2f}")
        
        self.checkout_button.config(state='normal' if self.cart else 'disabled')
    
    def remove_from_cart(self):
        selection = self.cart_listbox.curselection()
        
        if not selection:
            messagebox.showwarning("No Selection", "Please select an item to remove")
            return
        
        index = selection[0]
        self.cart.pop(index)
        
        self.update_cart_display()
    
    def clear_cart(self):
        if self.cart and messagebox.askyesno("Confirm", "Clear all items from cart?"):
            self.cart.clear()
            self.update_cart_display()
    
    def checkout(self):
        if not self.cart:
            return
        
        total = sum(item['price'] for item in self.cart)
        if not messagebox.askyesno(
            "Confirm Order",
            f"Place order for {len(self.cart)} item(s)?\nTotal: ${total:.2f}"
        ):
            return
        
        items = [
            {'book_id': item['book_id'], 'type': item['type']}
            for item in self.cart
        ]
        
        self.checkout_button.config(state='disabled')
        self.status_label.config(text="Placing order...", foreground="blue")
        
        def order_thread():
            success, data = self.api_client.create_order(items)
            self.after(0, lambda: self.handle_order_response(success, data))
        
        threading.Thread(target=order_thread, daemon=True).start()
    
    def handle_order_response(self, success, data):
        self.checkout_button.config(state='normal')
        
        if success:
            order_id = data['order_id']
            total = data['total_amount']
            email_sent = data.get('email_sent', False)
            
            message = f"Order #{order_id} placed successfully!\n\n"
            message += f"Total: ${total:.2f}\n\n"
            if email_sent:
                message += "Bill has been sent to your email."
            else:
                message += "Note: Email not sent (SMTP not configured)"
            
            messagebox.showinfo("Order Successful", message)
            
            self.cart.clear()
            self.update_cart_display()
            self.status_label.config(text="Order placed successfully!", foreground="green")
        else:
            self.status_label.config(text="Order failed", foreground="red")
            messagebox.showerror("Order Failed", data)
    
    def handle_logout(self):
        if messagebox.askyesno("Logout", "Are you sure you want to logout?"):
            self.cart.clear()
            self.api_client.logout()
            self.destroy()
            self.on_logout()
