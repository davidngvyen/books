import requests
from typing import Dict, List, Optional, Tuple

class APIClient:
    
    def __init__(self, base_url: str = "http://localhost:5000"):
        self.base_url = base_url
        self.token: Optional[str] = None
        self.user: Optional[Dict] = None
    
    def _get_headers(self) -> Dict[str, str]:
        headers = {'Content-Type': 'application/json'}
        if self.token:
            headers['Authorization'] = f'Bearer {self.token}'
        return headers
    
    def _handle_response(self, response: requests.Response) -> Tuple[bool, any]:
        try:
            data = response.json()
        except:
            data = {'error': 'Invalid response from server'}
        
        if response.status_code in [200, 201]:
            return True, data
        else:
            error_msg = data.get('error', f'Request failed with status {response.status_code}')
            return False, error_msg
    
    def register(self, username: str, email: str, password: str) -> Tuple[bool, str]:
        try:
            response = requests.post(
                f'{self.base_url}/api/auth/register',
                json={'username': username, 'email': email, 'password': password},
                timeout=10
            )
            success, data = self._handle_response(response)
            
            if success:
                return True, "Registration successful! Please log in."
            else:
                return False, data
                
        except requests.exceptions.ConnectionError:
            return False, "Cannot connect to server. Is it running?"
        except Exception as e:
            return False, f"Registration failed: {str(e)}"
    
    def login(self, username: str, password: str) -> Tuple[bool, str]:
        try:
            response = requests.post(
                f'{self.base_url}/api/auth/login',
                json={'username': username, 'password': password},
                timeout=10
            )
            success, data = self._handle_response(response)
            
            if success:
                self.token = data['token']
                self.user = data['user']
                return True, f"Welcome, {self.user['username']}!"
            else:
                return False, data
                
        except requests.exceptions.ConnectionError:
            return False, "Cannot connect to server. Is it running?"
        except Exception as e:
            return False, f"Login failed: {str(e)}"
    
    def logout(self):
        self.token = None
        self.user = None
    
    def is_logged_in(self) -> bool:
        return self.token is not None
    
    def is_manager(self) -> bool:
        return self.user and self.user.get('role') == 'manager'
    
    #book stuff
    def search_books(self, keyword: str = "") -> Tuple[bool, any]:
        try:
            url = f'{self.base_url}/api/books'
            if keyword:
                url += f'?q={keyword}'
            
            response = requests.get(url, timeout=10)
            success, data = self._handle_response(response)
            
            if success:
                return True, data['books']
            else:
                return False, data
                
        except requests.exceptions.ConnectionError:
            return False, "Cannot connect to server"
        except Exception as e:
            return False, f"Search failed: {str(e)}"
    
    def create_order(self, items: List[Dict]) -> Tuple[bool, any]:
        try:
            response = requests.post(
                f'{self.base_url}/api/orders',
                headers=self._get_headers(),
                json={'items': items},
                timeout=10
            )
            success, data = self._handle_response(response)
            return success, data
            
        except requests.exceptions.ConnectionError:
            return False, "Cannot connect to server"
        except Exception as e:
            return False, f"Order failed: {str(e)}"
    
    #manager stuff
    def get_all_orders(self) -> Tuple[bool, any]:
        try:
            response = requests.get(
                f'{self.base_url}/api/manager/orders',
                headers=self._get_headers(),
                timeout=10
            )
            success, data = self._handle_response(response)
            
            if success:
                return True, data['orders']
            else:
                return False, data
                
        except requests.exceptions.ConnectionError:
            return False, "Cannot connect to server"
        except Exception as e:
            return False, f"Failed to get orders: {str(e)}"
    
    def get_order_details(self, order_id: int) -> Tuple[bool, any]:
        try:
            response = requests.get(
                f'{self.base_url}/api/manager/orders/{order_id}',
                headers=self._get_headers(),
                timeout=10
            )
            return self._handle_response(response)
            
        except requests.exceptions.ConnectionError:
            return False, "Cannot connect to server"
        except Exception as e:
            return False, f"Failed to get order details: {str(e)}"
    
    def update_payment_status(self, order_id: int, status: str) -> Tuple[bool, any]:
        try:
            response = requests.patch(
                f'{self.base_url}/api/manager/orders/{order_id}/payment-status',
                headers=self._get_headers(),
                json={'payment_status': status},
                timeout=10
            )
            success, data = self._handle_response(response)
            
            if success:
                return True, data['message']
            else:
                return False, data
                
        except requests.exceptions.ConnectionError:
            return False, "Cannot connect to server"
        except Exception as e:
            return False, f"Update failed: {str(e)}"
    
    def get_all_books_manager(self) -> Tuple[bool, any]:
        try:
            response = requests.get(
                f'{self.base_url}/api/manager/books',
                headers=self._get_headers(),
                timeout=10
            )
            success, data = self._handle_response(response)
            
            if success:
                return True, data['books']
            else:
                return False, data
                
        except requests.exceptions.ConnectionError:
            return False, "Cannot connect to server"
        except Exception as e:
            return False, f"Failed to get books: {str(e)}"
    
    def create_book(self, title: str, author: str, price_buy: float, price_rent: float) -> Tuple[bool, any]:
        try:
            response = requests.post(
                f'{self.base_url}/api/manager/books',
                headers=self._get_headers(),
                json={
                    'title': title,
                    'author': author,
                    'price_buy': price_buy,
                    'price_rent': price_rent
                },
                timeout=10
            )
            success, data = self._handle_response(response)
            
            if success:
                return True, data['message']
            else:
                return False, data
                
        except requests.exceptions.ConnectionError:
            return False, "Cannot connect to server"
        except Exception as e:
            return False, f"Failed to create book: {str(e)}"
    
    def update_book(self, book_id: int, title: str, author: str, 
                   price_buy: float, price_rent: float, available: bool) -> Tuple[bool, any]:
        try:
            response = requests.put(
                f'{self.base_url}/api/manager/books/{book_id}',
                headers=self._get_headers(),
                json={
                    'title': title,
                    'author': author,
                    'price_buy': price_buy,
                    'price_rent': price_rent,
                    'available': available
                },
                timeout=10
            )
            success, data = self._handle_response(response)
            
            if success:
                return True, data['message']
            else:
                return False, data
                
        except requests.exceptions.ConnectionError:
            return False, "Cannot connect to server"
        except Exception as e:
            return False, f"Failed to update book: {str(e)}"
