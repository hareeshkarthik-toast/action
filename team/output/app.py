import gradio as gr
from accounts import Account, get_share_price

# Initialize the account for a single user
account = Account("user1")

def create_account(initial_deposit):
    """Create an account with initial deposit"""
    try:
        account.deposit_funds(float(initial_deposit))
        return f"Account created with initial deposit of ${initial_deposit}."
    except ValueError as e:
        return f"Error: {str(e)}"

def deposit(amount):
    """Deposit funds to the account"""
    try:
        account.deposit_funds(float(amount))
        return f"Successfully deposited ${amount}. New balance: ${account.balance:.2f}"
    except ValueError as e:
        return f"Error: {str(e)}"

def withdraw(amount):
    """Withdraw funds from the account"""
    try:
        account.withdraw_funds(float(amount))
        return f"Successfully withdrew ${amount}. New balance: ${account.balance:.2f}"
    except ValueError as e:
        return f"Error: {str(e)}"

def buy_shares(symbol, quantity):
    """Buy shares of a stock"""
    try:
        account.buy_shares(symbol, int(quantity))
        return f"Successfully bought {quantity} shares of {symbol}. New balance: ${account.balance:.2f}"
    except ValueError as e:
        return f"Error: {str(e)}"

def sell_shares(symbol, quantity):
    """Sell shares of a stock"""
    try:
        account.sell_shares(symbol, int(quantity))
        return f"Successfully sold {quantity} shares of {symbol}. New balance: ${account.balance:.2f}"
    except ValueError as e:
        return f"Error: {str(e)}"

def get_account_info():
    """Get account information"""
    portfolio_value = account.calculate_portfolio_value()
    profit_loss = account.calculate_profit_loss()
    holdings = account.get_holdings()
    
    info = f"Account Balance: ${account.balance:.2f}\n"
    info += f"Portfolio Value: ${portfolio_value:.2f}\n"
    info += f"Profit/Loss: ${profit_loss:.2f} ({'profit' if profit_loss >= 0 else 'loss'})\n\n"
    
    if holdings:
        info += "Current Holdings:\n"
        for symbol, quantity in holdings.items():
            price = get_share_price(symbol)
            value = price * quantity
            info += f"- {symbol}: {quantity} shares @ ${price:.2f} = ${value:.2f}\n"
    else:
        info += "No holdings.\n"
    
    return info

def get_transactions():
    """Get transaction history"""
    transactions = account.list_transactions()
    if not transactions:
        return "No transactions yet."
    
    result = "Transaction History:\n"
    for i, transaction in enumerate(transactions, 1):
        result += f"\n{i}. Type: {transaction['type'].upper()}\n"
        
        if transaction['type'] == 'deposit':
            result += f"   Amount: ${transaction['amount']:.2f}\n"
        elif transaction['type'] == 'withdrawal':
            result += f"   Amount: ${transaction['amount']:.2f}\n"
        elif transaction['type'] in ['buy', 'sell']:
            result += f"   Symbol: {transaction['symbol']}\n"
            result += f"   Quantity: {transaction['quantity']}\n"
            result += f"   Price: ${transaction['price']:.2f}\n"
            result += f"   Total: ${transaction['total']:.2f}\n"
        
        result += f"   Balance After: ${transaction['balance_after']:.2f}\n"
    
    return result

def get_stock_price(symbol):
    """Get the current price of a stock"""
    try:
        price = get_share_price(symbol)
        if price == 0.0:
            return f"Error: Invalid symbol {symbol}"
        return f"Current price of {symbol}: ${price:.2f}"
    except Exception as e:
        return f"Error: {str(e)}"

# Create the Gradio interface
with gr.Blocks(title="Trading Account Simulator") as demo:
    gr.Markdown("# Trading Account Simulator")
    gr.Markdown("Create an account, deposit/withdraw funds, and trade stocks")
    
    with gr.Tab("Account Management"):
        with gr.Group():
            gr.Markdown("## Create Account")
            with gr.Row():
                initial_deposit = gr.Number(label="Initial Deposit ($)")
                create_btn = gr.Button("Create Account")
            create_output = gr.Textbox(label="Result")
            create_btn.click(create_account, inputs=initial_deposit, outputs=create_output)
        
        with gr.Group():
            gr.Markdown("## Deposit/Withdraw Funds")
            with gr.Row():
                deposit_amount = gr.Number(label="Amount ($)")
                deposit_btn = gr.Button("Deposit")
            deposit_output = gr.Textbox(label="Result")
            deposit_btn.click(deposit, inputs=deposit_amount, outputs=deposit_output)
            
            with gr.Row():
                withdraw_amount = gr.Number(label="Amount ($)")
                withdraw_btn = gr.Button("Withdraw")
            withdraw_output = gr.Textbox(label="Result")
            withdraw_btn.click(withdraw, inputs=withdraw_amount, outputs=withdraw_output)
    
    with gr.Tab("Trading"):
        with gr.Group():
            gr.Markdown("## Check Stock Price")
            with gr.Row():
                price_symbol = gr.Textbox(label="Stock Symbol (e.g., AAPL, TSLA, GOOGL)")
                price_btn = gr.Button("Get Price")
            price_output = gr.Textbox(label="Result")
            price_btn.click(get_stock_price, inputs=price_symbol, outputs=price_output)
        
        with gr.Group():
            gr.Markdown("## Buy Shares")
            with gr.Row():
                buy_symbol = gr.Textbox(label="Stock Symbol")
                buy_quantity = gr.Number(label="Quantity", precision=0)
            buy_btn = gr.Button("Buy")
            buy_output = gr.Textbox(label="Result")
            buy_btn.click(buy_shares, inputs=[buy_symbol, buy_quantity], outputs=buy_output)
        
        with gr.Group():
            gr.Markdown("## Sell Shares")
            with gr.Row():
                sell_symbol = gr.Textbox(label="Stock Symbol")
                sell_quantity = gr.Number(label="Quantity", precision=0)
            sell_btn = gr.Button("Sell")
            sell_output = gr.Textbox(label="Result")
            sell_btn.click(sell_shares, inputs=[sell_symbol, sell_quantity], outputs=sell_output)
    
    with gr.Tab("Account Information"):
        with gr.Group():
            gr.Markdown("## Account Summary")
            account_info_btn = gr.Button("Refresh Account Information")
            account_info_output = gr.Textbox(label="Account Information", lines=10)
            account_info_btn.click(get_account_info, inputs=None, outputs=account_info_output)
        
        with gr.Group():
            gr.Markdown("## Transaction History")
            transactions_btn = gr.Button("View Transactions")
            transactions_output = gr.Textbox(label="Transactions", lines=20)
            transactions_btn.click(get_transactions, inputs=None, outputs=transactions_output)

if __name__ == "__main__":
    demo.launch()