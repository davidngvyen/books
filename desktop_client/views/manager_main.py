import tkinter as tk
from tkinter import ttk, messagebox
import threading

class ManagerMainView(tk.Frame):
    
    def __init__(self, parent, api_client, on_logout):
        super().__init__(parent)
        self.api_client = api_client
        self.on_logout = on_logout
        
        self.pack(fill=tk.BOTH, expand=True)
        self.create_widgets()
        
        self.load_orders()
        self.load_books()
    
    def create_widgets(self):
        #Top bar
        top_frame = ttk.Frame(self, padding="10")
        top_frame.pack(fill=tk.X)
        
        ttk.Label(
            top_frame,
            text=f"Manager Dashboard - {self.api_client.user['username']}",
            font=('Arial', 14, 'bold')
        ).pack(side=tk.LEFT)
        
        ttk.Button(
            top_frame,
            text="Logout",
            command=self.handle_logout
        ).pack(side=tk.RIGHT)
        
        self.notebook = ttk.Notebook(self, padding="10")
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        orders_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(orders_frame, text="Orders Management")
        self.create_orders_tab(orders_frame)
        
        books_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(books_frame, text="Books Management")
        self.create_books_tab(books_frame)
    
    def create_orders_tab(self, parent):
        #Top controls
        controls_frame = ttk.Frame(parent)
        controls_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(
            controls_frame,
            text="Refresh Orders",
            command=self.load_orders
        ).pack(side=tk.LEFT, padx=5)
        
        self.orders_status = ttk.Label(controls_frame, text="", foreground="blue")
        self.orders_status.pack(side=tk.LEFT, padx=10)
        
        #Orders tree
        tree_frame = ttk.Frame(parent)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(tree_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.orders_tree = ttk.Treeview(
            tree_frame,
            columns=('ID', 'Customer', 'Email', 'Total', 'Status', 'Date'),
            show='headings',
            yscrollcommand=scrollbar.set
        )
        scrollbar.config(command=self.orders_tree.yview)
        
        #Column headings
        self.orders_tree.heading('ID', text='Order ID')
        self.orders_tree.heading('Customer', text='Customer')
        self.orders_tree.heading('Email', text='Email')
        self.orders_tree.heading('Total', text='Total')
        self.orders_tree.heading('Status', text='Status')
        self.orders_tree.heading('Date', text='Date')
        
        #Column widths
        self.orders_tree.column('ID', width=60)
        self.orders_tree.column('Customer', width=100)
        self.orders_tree.column('Email', width=150)
        self.orders_tree.column('Total', width=80)
        self.orders_tree.column('Status', width=80)
        self.orders_tree.column('Date', width=150)
        
        self.orders_tree.pack(fill=tk.BOTH, expand=True)
        
        #Action buttons
        action_frame = ttk.Frame(parent)
        action_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(
            action_frame,
            text="View Order Details",
            command=self.view_order_details
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            action_frame,
            text="Mark as Paid",
            command=lambda: self.update_status('Paid')
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            action_frame,
            text="Mark as Pending",
            command=lambda: self.update_status('Pending')
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            action_frame,
            text="Cancel Order",
            command=lambda: self.update_status('Cancelled')
        ).pack(side=tk.LEFT, padx=5)
    
    def load_orders(self):
        """Load all orders from API"""
        self.orders_status.config(text="Loading orders...", foreground="blue")
        
        def load_thread():
            success, data = self.api_client.get_all_orders()
            self.after(0, lambda: self.handle_orders_response(success, data))
        
        threading.Thread(target=load_thread, daemon=True).start()
    
    def handle_orders_response(self, success, data):
        """Handle orders response"""
        if success:
            orders = data
            self.orders_status.config(
                text=f"Loaded {len(orders)} order(s)",
                foreground="green"
            )
            self.display_orders(orders)
        else:
            self.orders_status.config(text=f"Error: {data}", foreground="red")
            messagebox.showerror("Load Failed", data)
    
    def display_orders(self, orders):
        """Display orders in tree"""
        #Clear existing
        for item in self.orders_tree.get_children():
            self.orders_tree.delete(item)
        
        #Add orders
        for order in orders:
            #Format date
            date_str = order.get('created_at', 'N/A')
            if isinstance(date_str, str) and len(date_str) > 19:
                date_str = date_str[:19]  #Trim to YYYY-MM-DD HH:MM:SS
            
            self.orders_tree.insert('', tk.END, values=(
                order['id'],
                order['username'],
                order['email'],
                f"${order['total_amount']:.2f}",
                order['payment_status'],
                date_str
            ))
    
    def view_order_details(self):
        """View detailed order information"""
        selection = self.orders_tree.selection()
        
        if not selection:
            messagebox.showwarning("No Selection", "Please select an order first")
            return
        
        # Get order ID
        item = self.orders_tree.item(selection[0])
        order_id = item['values'][0]
        
        #Fetch details
        success, data = self.api_client.get_order_details(order_id)
        
        if success:
            order = data['order']
            items = data['items']
            
            #Create details window
            details_window = tk.Toplevel(self)
            details_window.title(f"Order #{order_id} Details")
            details_window.geometry("600x400")
            
            #Order info
            info_frame = ttk.LabelFrame(details_window, text="Order Information", padding="10")
            info_frame.pack(fill=tk.X, padx=10, pady=10)
            
            ttk.Label(info_frame, text=f"Order ID: {order['id']}").pack(anchor='w')
            ttk.Label(info_frame, text=f"Customer: {order['username']} ({order['email']})").pack(anchor='w')
            ttk.Label(info_frame, text=f"Total: ${order['total_amount']:.2f}").pack(anchor='w')
            ttk.Label(info_frame, text=f"Status: {order['payment_status']}").pack(anchor='w')
            ttk.Label(info_frame, text=f"Date: {order.get('created_at', 'N/A')}").pack(anchor='w')
            
            #Items
            items_frame = ttk.LabelFrame(details_window, text="Order Items", padding="10")
            items_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            #Items tree
            items_tree = ttk.Treeview(
                items_frame,
                columns=('Book', 'Author', 'Type', 'Price'),
                show='headings'
            )
            
            items_tree.heading('Book', text='Book')
            items_tree.heading('Author', text='Author')
            items_tree.heading('Type', text='Type')
            items_tree.heading('Price', text='Price')
            
            for item in items:
                items_tree.insert('', tk.END, values=(
                    item['title'],
                    item['author'],
                    item['item_type'].upper(),
                    f"${item['price']:.2f}"
                ))
            
            items_tree.pack(fill=tk.BOTH, expand=True)
            
        else:
            messagebox.showerror("Error", data)
    
    def update_status(self, new_status):
        """Update order payment status"""
        selection = self.orders_tree.selection()
        
        if not selection:
            messagebox.showwarning("No Selection", "Please select an order first")
            return
        
        # Get order ID
        item = self.orders_tree.item(selection[0])
        order_id = item['values'][0]
        current_status = item['values'][4]
        
        #Confirm
        if not messagebox.askyesno(
            "Confirm Update",
            f"Update order #{order_id} status from '{current_status}' to '{new_status}'?"
        ):
            return
        
        self.orders_status.config(text="Updating...", foreground="blue")
        
        def update_thread():
            success, data = self.api_client.update_payment_status(order_id, new_status)
            self.after(0, lambda: self.handle_update_response(success, data))
        
        threading.Thread(target=update_thread, daemon=True).start()
    
    def handle_update_response(self, success, data):
        """Handle status update response"""
        if success:
            self.orders_status.config(text="Status updated!", foreground="green")
            messagebox.showinfo("Success", data)
            self.load_orders()  #Refresh
        else:
            self.orders_status.config(text="Update failed", foreground="red")
            messagebox.showerror("Update Failed", data)
    
    #Books Tab
    
    def create_books_tab(self, parent):
        """Create books management tab"""
        #Top controls
        controls_frame = ttk.Frame(parent)
        controls_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(
            controls_frame,
            text="Refresh Books",
            command=self.load_books
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            controls_frame,
            text="Add New Book",
            command=self.add_book
        ).pack(side=tk.LEFT, padx=5)
        
        self.books_status = ttk.Label(controls_frame, text="", foreground="blue")
        self.books_status.pack(side=tk.LEFT, padx=10)
        
        #Books tree
        tree_frame = ttk.Frame(parent)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(tree_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.books_tree = ttk.Treeview(
            tree_frame,
            columns=('ID', 'Title', 'Author', 'Buy Price', 'Rent Price', 'Available'),
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
        self.books_tree.heading('Available', text='Available')
        
        #Column widths
        self.books_tree.column('ID', width=40)
        self.books_tree.column('Title', width=200)
        self.books_tree.column('Author', width=150)
        self.books_tree.column('Buy Price', width=80)
        self.books_tree.column('Rent Price', width=80)
        self.books_tree.column('Available', width=80)
        
        self.books_tree.pack(fill=tk.BOTH, expand=True)
        
        #Action buttons
        action_frame = ttk.Frame(parent)
        action_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(
            action_frame,
            text="Edit Selected Book",
            command=self.edit_book
        ).pack(side=tk.LEFT, padx=5)
    
    def load_books(self):
        """Load all books from API"""
        self.books_status.config(text="Loading books...", foreground="blue")
        
        def load_thread():
            success, data = self.api_client.get_all_books_manager()
            self.after(0, lambda: self.handle_books_response(success, data))
        
        threading.Thread(target=load_thread, daemon=True).start()
    
    def handle_books_response(self, success, data):
        """Handle books response"""
        if success:
            books = data
            self.books_status.config(
                text=f"Loaded {len(books)} book(s)",
                foreground="green"
            )
            self.display_books(books)
        else:
            self.books_status.config(text=f"Error: {data}", foreground="red")
            messagebox.showerror("Load Failed", data)
    
    def display_books(self, books):
        """Display books in tree"""
        #Clear existing
        for item in self.books_tree.get_children():
            self.books_tree.delete(item)
        
        #Add books
        for book in books:
            self.books_tree.insert('', tk.END, values=(
                book['id'],
                book['title'],
                book['author'],
                f"${book['price_buy']:.2f}",
                f"${book['price_rent']:.2f}",
                'Yes' if book['available'] else 'No'
            ))
    
    def add_book(self):
        """Open dialog to add new book"""
        dialog = BookDialog(self, "Add New Book")
        
        if dialog.result:
            data = dialog.result
            
            self.books_status.config(text="Adding book...", foreground="blue")
            
            def add_thread():
                success, message = self.api_client.create_book(
                    data['title'],
                    data['author'],
                    data['price_buy'],
                    data['price_rent']
                )
                self.after(0, lambda: self.handle_book_action_response(success, message, "add"))
            
            threading.Thread(target=add_thread, daemon=True).start()
    
    def edit_book(self):
        """Edit selected book"""
        selection = self.books_tree.selection()
        
        if not selection:
            messagebox.showwarning("No Selection", "Please select a book first")
            return
        
        #Get book data
        item = self.books_tree.item(selection[0])
        values = item['values']
        
        book_data = {
            'id': values[0],
            'title': values[1],
            'author': values[2],
            'price_buy': float(values[3][1:]),
            'price_rent': float(values[4][1:]),
            'available': values[5] == 'Yes'
        }
        
        dialog = BookDialog(self, "Edit Book", book_data)
        
        if dialog.result:
            data = dialog.result
            
            self.books_status.config(text="Updating book...", foreground="blue")
            
            def update_thread():
                success, message = self.api_client.update_book(
                    book_data['id'],
                    data['title'],
                    data['author'],
                    data['price_buy'],
                    data['price_rent'],
                    data['available']
                )
                self.after(0, lambda: self.handle_book_action_response(success, message, "update"))
            
            threading.Thread(target=update_thread, daemon=True).start()
    
    def handle_book_action_response(self, success, message, action):
        """Handle book add/update response"""
        if success:
            self.books_status.config(text=f"Book {action}ed!", foreground="green")
            messagebox.showinfo("Success", message)
            self.load_books()  #Refresh
        else:
            self.books_status.config(text=f"Book {action} failed", foreground="red")
            messagebox.showerror("Failed", message)
    
    def handle_logout(self):
        """Handle logout"""
        if messagebox.askyesno("Logout", "Are you sure you want to logout?"):
            #Logout from API
            self.api_client.logout()
            #Destroy current view first
            self.destroy()
            #Then show login
            self.on_logout()


class BookDialog(tk.Toplevel):
    """Dialog for adding/editing books"""
    
    def __init__(self, parent, title, book_data=None):
        """
        Args:
            parent: Parent widget
            title: Dialog title
            book_data: Existing book data for editing (None for new book)
        """
        super().__init__(parent)
        self.title(title)
        self.geometry("400x300")
        self.resizable(False, False)
        
        self.result = None
        
        #Create form
        form_frame = ttk.Frame(self, padding="20")
        form_frame.pack(fill=tk.BOTH, expand=True)
        
        #Title
        ttk.Label(form_frame, text="Title:").grid(row=0, column=0, sticky='w', pady=5)
        self.title_entry = ttk.Entry(form_frame, width=30)
        self.title_entry.grid(row=0, column=1, pady=5, padx=5)
        
        #Author
        ttk.Label(form_frame, text="Author:").grid(row=1, column=0, sticky='w', pady=5)
        self.author_entry = ttk.Entry(form_frame, width=30)
        self.author_entry.grid(row=1, column=1, pady=5, padx=5)
        
        #Buy Price
        ttk.Label(form_frame, text="Buy Price:").grid(row=2, column=0, sticky='w', pady=5)
        self.buy_price_entry = ttk.Entry(form_frame, width=30)
        self.buy_price_entry.grid(row=2, column=1, pady=5, padx=5)
        
        #Rent Price
        ttk.Label(form_frame, text="Rent Price:").grid(row=3, column=0, sticky='w', pady=5)
        self.rent_price_entry = ttk.Entry(form_frame, width=30)
        self.rent_price_entry.grid(row=3, column=1, pady=5, padx=5)
        
        #Available (only for edit)
        if book_data:
            ttk.Label(form_frame, text="Available:").grid(row=4, column=0, sticky='w', pady=5)
            self.available_var = tk.BooleanVar(value=book_data.get('available', True))
            ttk.Checkbutton(form_frame, variable=self.available_var).grid(row=4, column=1, sticky='w', pady=5, padx=5)
        else:
            self.available_var = tk.BooleanVar(value=True)
        
        #Fill in existing data
        if book_data:
            self.title_entry.insert(0, book_data['title'])
            self.author_entry.insert(0, book_data['author'])
            self.buy_price_entry.insert(0, str(book_data['price_buy']))
            self.rent_price_entry.insert(0, str(book_data['price_rent']))
        
        #Buttons
        button_frame = ttk.Frame(form_frame)
        button_frame.grid(row=5, column=0, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="Save", command=self.save).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=self.destroy).pack(side=tk.LEFT, padx=5)
        
        #Make modal
        self.transient(parent)
        self.grab_set()
        self.wait_window()
    
    def save(self):
        """Validate and save"""
        title = self.title_entry.get().strip()
        author = self.author_entry.get().strip()
        
        if not title or not author:
            messagebox.showerror("Error", "Title and author are required")
            return
        
        try:
            price_buy = float(self.buy_price_entry.get())
            price_rent = float(self.rent_price_entry.get())
            
            if price_buy <= 0 or price_rent <= 0:
                raise ValueError("Prices must be positive")
        except ValueError as e:
            messagebox.showerror("Error", "Invalid price values")
            return
        
        self.result = {
            'title': title,
            'author': author,
            'price_buy': price_buy,
            'price_rent': price_rent,
            'available': self.available_var.get()
        }
        
        self.destroy()
