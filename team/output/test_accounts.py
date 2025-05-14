import unittest
from unittest.mock import patch
import accounts

class TestSharePriceFunction(unittest.TestCase):
    def test_get_existing_share_price(self):
        # Test that existing symbols return the correct price
        self.assertEqual(accounts.get_share_price('AAPL'), 150.0)
        self.assertEqual(accounts.get_share_price('TSLA'), 800.0)
        self.assertEqual(accounts.get_share_price('GOOGL'), 2500.0)
    
    def test_get_nonexistent_share_price(self):
        # Test that non-existent symbols return 0.0
        self.assertEqual(accounts.get_share_price('NONEXISTENT'), 0.0)
        self.assertEqual(accounts.get_share_price(''), 0.0)


class TestAccountClass(unittest.TestCase):
    def setUp(self):
        # Create a fresh Account instance for each test
        self.account = accounts.Account('test_user')
    
    def test_initialization(self):
        # Test that a new account has the expected initial values
        self.assertEqual(self.account.user_id, 'test_user')
        self.assertEqual(self.account.balance, 0.0)
        self.assertEqual(self.account.initial_deposit, 0.0)
        self.assertEqual(self.account.holdings, {})
        self.assertEqual(self.account.transactions, [])
    
    def test_deposit_funds_positive_amount(self):
        # Test depositing positive amount
        self.account.deposit_funds(1000.0)
        self.assertEqual(self.account.balance, 1000.0)
        self.assertEqual(self.account.initial_deposit, 1000.0)
        self.assertEqual(len(self.account.transactions), 1)
        self.assertEqual(self.account.transactions[0]['type'], 'deposit')
        self.assertEqual(self.account.transactions[0]['amount'], 1000.0)
        self.assertEqual(self.account.transactions[0]['balance_after'], 1000.0)
        
        # Second deposit should not update initial_deposit
        self.account.deposit_funds(500.0)
        self.assertEqual(self.account.balance, 1500.0)
        self.assertEqual(self.account.initial_deposit, 1000.0)
        self.assertEqual(len(self.account.transactions), 2)
    
    def test_deposit_funds_negative_amount(self):
        # Test that depositing negative amount raises ValueError
        with self.assertRaises(ValueError):
            self.account.deposit_funds(-100.0)
    
    def test_deposit_funds_zero_amount(self):
        # Test that depositing zero raises ValueError
        with self.assertRaises(ValueError):
            self.account.deposit_funds(0.0)
    
    def test_withdraw_funds_valid(self):
        # Setup account with funds
        self.account.deposit_funds(1000.0)
        
        # Test withdrawal
        self.account.withdraw_funds(300.0)
        self.assertEqual(self.account.balance, 700.0)
        self.assertEqual(len(self.account.transactions), 2)
        self.assertEqual(self.account.transactions[1]['type'], 'withdrawal')
        self.assertEqual(self.account.transactions[1]['amount'], 300.0)
        self.assertEqual(self.account.transactions[1]['balance_after'], 700.0)
    
    def test_withdraw_funds_negative_amount(self):
        self.account.deposit_funds(1000.0)
        with self.assertRaises(ValueError):
            self.account.withdraw_funds(-100.0)
    
    def test_withdraw_funds_zero_amount(self):
        self.account.deposit_funds(1000.0)
        with self.assertRaises(ValueError):
            self.account.withdraw_funds(0.0)
    
    def test_withdraw_funds_insufficient_balance(self):
        self.account.deposit_funds(1000.0)
        with self.assertRaises(ValueError):
            self.account.withdraw_funds(1100.0)
    
    def test_buy_shares_valid(self):
        self.account.deposit_funds(10000.0)
        self.account.buy_shares('AAPL', 10)
        
        # Check balance is reduced
        self.assertEqual(self.account.balance, 10000.0 - (150.0 * 10))
        
        # Check holdings are updated
        self.assertEqual(self.account.holdings['AAPL'], 10)
        
        # Check transaction is recorded
        self.assertEqual(len(self.account.transactions), 2)
        self.assertEqual(self.account.transactions[1]['type'], 'buy')
        self.assertEqual(self.account.transactions[1]['symbol'], 'AAPL')
        self.assertEqual(self.account.transactions[1]['quantity'], 10)
        self.assertEqual(self.account.transactions[1]['price'], 150.0)
        self.assertEqual(self.account.transactions[1]['total'], 1500.0)
    
    def test_buy_shares_invalid_symbol(self):
        self.account.deposit_funds(10000.0)
        with self.assertRaises(ValueError):
            self.account.buy_shares('INVALID', 10)
    
    def test_buy_shares_negative_quantity(self):
        self.account.deposit_funds(10000.0)
        with self.assertRaises(ValueError):
            self.account.buy_shares('AAPL', -5)
    
    def test_buy_shares_zero_quantity(self):
        self.account.deposit_funds(10000.0)
        with self.assertRaises(ValueError):
            self.account.buy_shares('AAPL', 0)
    
    def test_buy_shares_insufficient_funds(self):
        self.account.deposit_funds(100.0)
        with self.assertRaises(ValueError):
            self.account.buy_shares('AAPL', 10)  # Costs 1500.0
    
    def test_sell_shares_valid(self):
        # Setup account with shares
        self.account.deposit_funds(10000.0)
        self.account.buy_shares('AAPL', 10)
        initial_balance = self.account.balance
        
        # Sell some shares
        self.account.sell_shares('AAPL', 5)
        
        # Check balance is increased
        self.assertEqual(self.account.balance, initial_balance + (150.0 * 5))
        
        # Check holdings are updated
        self.assertEqual(self.account.holdings['AAPL'], 5)
        
        # Check transaction is recorded
        self.assertEqual(len(self.account.transactions), 3)
        self.assertEqual(self.account.transactions[2]['type'], 'sell')
        self.assertEqual(self.account.transactions[2]['symbol'], 'AAPL')
        self.assertEqual(self.account.transactions[2]['quantity'], 5)
        self.assertEqual(self.account.transactions[2]['price'], 150.0)
        self.assertEqual(self.account.transactions[2]['total'], 750.0)
    
    def test_sell_shares_all(self):
        # Setup account with shares
        self.account.deposit_funds(10000.0)
        self.account.buy_shares('AAPL', 10)
        
        # Sell all shares
        self.account.sell_shares('AAPL', 10)
        
        # Check holdings - the symbol should be removed
        self.assertNotIn('AAPL', self.account.holdings)
    
    def test_sell_shares_insufficient(self):
        self.account.deposit_funds(10000.0)
        self.account.buy_shares('AAPL', 5)
        
        with self.assertRaises(ValueError):
            self.account.sell_shares('AAPL', 10)
    
    def test_sell_shares_nonexistent_symbol(self):
        self.account.deposit_funds(10000.0)
        
        with self.assertRaises(ValueError):
            self.account.sell_shares('GOOGL', 5)  # Never bought GOOGL
    
    def test_sell_shares_negative_quantity(self):
        self.account.deposit_funds(10000.0)
        self.account.buy_shares('AAPL', 10)
        
        with self.assertRaises(ValueError):
            self.account.sell_shares('AAPL', -5)
    
    def test_sell_shares_zero_quantity(self):
        self.account.deposit_funds(10000.0)
        self.account.buy_shares('AAPL', 10)
        
        with self.assertRaises(ValueError):
            self.account.sell_shares('AAPL', 0)
    
    def test_calculate_portfolio_value(self):
        # Setup account with various holdings
        self.account.deposit_funds(10000.0)
        self.account.buy_shares('AAPL', 10)  # 10 * 150.0 = 1500.0
        self.account.buy_shares('TSLA', 5)   # 5 * 800.0 = 4000.0
        
        expected_value = self.account.balance + (10 * 150.0) + (5 * 800.0)
        self.assertEqual(self.account.calculate_portfolio_value(), expected_value)
    
    def test_calculate_portfolio_value_empty(self):
        self.account.deposit_funds(10000.0)
        self.assertEqual(self.account.calculate_portfolio_value(), 10000.0)
    
    def test_calculate_profit_loss(self):
        initial_deposit = 10000.0
        self.account.deposit_funds(initial_deposit)
        
        # Buy shares that will increase total value
        self.account.buy_shares('AAPL', 10)  # 1500.0
        self.account.buy_shares('TSLA', 5)   # 4000.0
        
        # Calculate expected profit
        portfolio_value = self.account.calculate_portfolio_value()
        expected_profit = portfolio_value - initial_deposit
        
        self.assertEqual(self.account.calculate_profit_loss(), expected_profit)
        self.assertEqual(self.account.get_profit_loss(), expected_profit)
    
    def test_get_holdings(self):
        self.account.deposit_funds(10000.0)
        self.account.buy_shares('AAPL', 10)
        self.account.buy_shares('TSLA', 5)
        
        holdings = self.account.get_holdings()
        self.assertEqual(holdings, {'AAPL': 10, 'TSLA': 5})
        
        # Verify that the returned dictionary is a copy
        holdings['AAPL'] = 20
        self.assertEqual(self.account.holdings['AAPL'], 10)
    
    def test_list_transactions(self):
        self.account.deposit_funds(10000.0)
        self.account.buy_shares('AAPL', 10)
        self.account.sell_shares('AAPL', 5)
        
        transactions = self.account.list_transactions()
        self.assertEqual(len(transactions), 3)
        
        # Verify types are correct
        self.assertEqual(transactions[0]['type'], 'deposit')
        self.assertEqual(transactions[1]['type'], 'buy')
        self.assertEqual(transactions[2]['type'], 'sell')
        
        # Verify that the returned list is a copy
        transactions.append({'fake': 'transaction'})
        self.assertEqual(len(self.account.transactions), 3)


if __name__ == '__main__':
    unittest.main()