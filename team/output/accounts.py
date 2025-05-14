from typing import Dict, List

def get_share_price(symbol: str) -> float:
    """Returns the current price of a share. This is a test implementation."""
    prices = {
        'AAPL': 150.0,
        'TSLA': 800.0,
        'GOOGL': 2500.0
    }
    return prices.get(symbol, 0.0)

class Account:
    def __init__(self, user_id: str):
        """Initializes a new account with the given user_id."""
        self.user_id = user_id
        self.initial_deposit = 0.0
        self.balance = 0.0
        self.holdings = {}
        self.transactions = []

    def deposit_funds(self, amount: float) -> None:
        """Increases the account's balance by the given amount."""
        if amount <= 0:
            raise ValueError("Deposit amount must be positive")
        
        # If this is the first deposit, set it as the initial deposit
        if self.initial_deposit == 0.0:
            self.initial_deposit = amount
        
        self.balance += amount
        
        # Record the transaction
        transaction = {
            'type': 'deposit',
            'amount': amount,
            'balance_after': self.balance
        }
        self.transactions.append(transaction)

    def withdraw_funds(self, amount: float) -> None:
        """Decreases the account's balance by the given amount if the balance is sufficient."""
        if amount <= 0:
            raise ValueError("Withdrawal amount must be positive")
        
        if amount > self.balance:
            raise ValueError(f"Insufficient funds. Current balance: {self.balance}")
        
        self.balance -= amount
        
        # Record the transaction
        transaction = {
            'type': 'withdrawal',
            'amount': amount,
            'balance_after': self.balance
        }
        self.transactions.append(transaction)

    def buy_shares(self, symbol: str, quantity: int) -> None:
        """Records the purchase of quantity shares of symbol."""
        if quantity <= 0:
            raise ValueError("Quantity must be positive")
        
        price = get_share_price(symbol)
        if price == 0.0:
            raise ValueError(f"Invalid symbol: {symbol}")
        
        total_cost = price * quantity
        
        if total_cost > self.balance:
            raise ValueError(f"Insufficient funds. Cost: {total_cost}, Balance: {self.balance}")
        
        # Update balance
        self.balance -= total_cost
        
        # Update holdings
        if symbol in self.holdings:
            self.holdings[symbol] += quantity
        else:
            self.holdings[symbol] = quantity
        
        # Record the transaction
        transaction = {
            'type': 'buy',
            'symbol': symbol,
            'quantity': quantity,
            'price': price,
            'total': total_cost,
            'balance_after': self.balance
        }
        self.transactions.append(transaction)

    def sell_shares(self, symbol: str, quantity: int) -> None:
        """Records the sale of quantity shares of symbol."""
        if quantity <= 0:
            raise ValueError("Quantity must be positive")
        
        if symbol not in self.holdings or self.holdings[symbol] < quantity:
            raise ValueError(f"Insufficient shares. Owned: {self.holdings.get(symbol, 0)}, Requested: {quantity}")
        
        price = get_share_price(symbol)
        total_earned = price * quantity
        
        # Update balance
        self.balance += total_earned
        
        # Update holdings
        self.holdings[symbol] -= quantity
        if self.holdings[symbol] == 0:
            del self.holdings[symbol]
        
        # Record the transaction
        transaction = {
            'type': 'sell',
            'symbol': symbol,
            'quantity': quantity,
            'price': price,
            'total': total_earned,
            'balance_after': self.balance
        }
        self.transactions.append(transaction)

    def calculate_portfolio_value(self) -> float:
        """Calculates the total value of all holdings based on current share prices."""
        total_value = self.balance
        
        for symbol, quantity in self.holdings.items():
            price = get_share_price(symbol)
            total_value += price * quantity
        
        return total_value

    def calculate_profit_loss(self) -> float:
        """Calculates the net profit or loss by comparing the current total value of the account with the initial deposit."""
        return self.calculate_portfolio_value() - self.initial_deposit

    def get_holdings(self) -> Dict[str, int]:
        """Returns a copy of the current holdings dictionary."""
        return self.holdings.copy()

    def get_profit_loss(self) -> float:
        """Returns the current profit or loss of the user."""
        return self.calculate_profit_loss()

    def list_transactions(self) -> List[Dict]:
        """Returns a list of all transactions made by the user."""
        return self.transactions.copy()