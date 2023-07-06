import random
import sys
import os
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)
from datetime import datetime, timedelta
from .balance_sheet import generate_fake_balance_sheet
from .income import generate_fake_income_statement
from .cash_flow import generate_fake_cash_flow


class PublicCompany:
    """
    Runs all public companies as a process Generating financial reports, distributing dividends, and issuing shares
    """
    def __init__(self, name, initial_price, initial_cash, startdate, requester, exchange_channel = 5570):
        self.name = name
        self.symbol = name[:3].upper()
        self.price = initial_price
        self.cash = initial_cash
        self.startdate = startdate
        self.currentdate = startdate 
        self.shareholders = []
        self.outstanding_shares = 0
        self.ex_dividend_date = None
        self.requests = requester

    async def issue_shares(self, shares, price):
        self.cash += shares * price
        self.price = price
        self.requests.create_asset(self.symbol, shares, price, price * 0.99, price * 1.01)

    async def generate_financial_report(self, date, period, symbol):
        balance_sheet = generate_fake_balance_sheet(date, symbol, period)
        income_statement = generate_fake_income_statement(date, symbol, period)
        cash_flow = generate_fake_cash_flow(balance_sheet['retainedEarnings'], date, symbol, period)
    
    async def distribute_dividends(self, dividends_paid):
        total_shares = sum(sum(shareholder["shares"]) for shareholder in self.shareholders)
        eligible_shareholders = []
        for shareholder in self.shareholders:
            shares = sum(shareholder["shares"])
            if len(shareholder["shares"]) > 0 and (self.startdate <= self.ex_dividend_date or any(date is None or date >= self.ex_dividend_date for date in shareholder["sold_date"])):
                eligible_shareholders.append(shareholder)
        
        for shareholder in eligible_shareholders:
            shares = sum(shareholder["shares"])
            dividend = (shares / total_shares) * dividends_paid
            shareholder["dividend"] = dividend
            self.cash -= dividend
            print(f"Dividends distributed to {shareholder['name']} - {self.currentdate}: {dividend}")
    
    async def calculate_ex_dividend_date(self, dividend_payment_date):
        # Subtracting 2 days from the dividend payment date to determine the ex-dividend date
        self.ex_dividend_date = dividend_payment_date - timedelta(days=2)
    
    async def add_shareholder(self, name, shares=[], sold_date=[]):
        self.shareholders.append({"name": name, "shares": shares, "sold_date": sold_date})
    
    async def remove_shareholder(self, name):
        self.shareholders.remove(shareholder for shareholder in self.shareholders if shareholder['name'] == name )

    async def next(self, date, dividends_paid, dividend_payment_date):
        self.shareholders = await self.requests.get_agents_holding(self.symbol)
        self.calculate_ex_dividend_date(dividend_payment_date)
        while self.currentdate < date:
            self.currentdate += timedelta(days=1) # TODO: pull this from the clock process
            if self.currentdate.month % 3 == 0 and self.currentdate.day == 1:
                self.generate_financial_report()
            if self.currentdate.month % 3 == 0 and self.currentdate.day == 15:
                #TODO: get eligible shareholders from shareholders 
                self.distribute_dividends(dividends_paid)

# # Example usage
# start_date = datetime(2023, 1, 1)
# end_date = datetime(2023, 12, 31)
# dividends_paid = random.randint(-40, -10) * -1
# dividend_payment_date = datetime(2023, 3, 15)

# company = PublicCompany("ABC Corporation", 100, 1000000, start_date)
# company.shareholders = [
#     {"name": "Shareholder A", "shares": [1000, 2000, 3000], "sold_date": [datetime(2023, 1, 15), datetime(2023, 3, 15), None]},
#     {"name": "Shareholder B", "shares": [2000], "sold_date": [datetime(2023, 3, 15)]},
#     {"name": "Shareholder C", "shares": [3000], "sold_date": [None]},
# ]

# company.next(end_date, dividends_paid, dividend_payment_date)
