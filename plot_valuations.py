# plot_valuations.py

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from fund_manager.db import get_session
from fund_manager.models import Fund, FundValuation

def plot_valuations_curve():
    session = get_session()
    try:
        funds = session.query(Fund).all()
        if not funds:
            print("No funds available to plot.")
            return
        
        plt.figure(figsize=(12, 6))
        
        # Plot each fund's valuation curve
        for fund in funds:
            valuations = session.query(FundValuation)\
                                .filter_by(fund_id=fund.id)\
                                .order_by(FundValuation.valuation_date)\
                                .all()
            if not valuations:
                continue
            
            dates = [val.valuation_date for val in valuations]
            values = [val.total_value for val in valuations]
            
            plt.plot(dates, values, marker='o', linestyle='-', label=fund.name)
        
        plt.xlabel('Date')
        plt.ylabel('Total Value ($)')
        plt.title('Fund Valuations Over Time')
        plt.legend()
        
        # Format x-axis to display dates nicely.
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M:%S'))
        plt.gcf().autofmt_xdate()  # Auto-rotate date labels
        
        plt.tight_layout()
        plt.show()
    finally:
        session.close()

if __name__ == '__main__':
    plot_valuations_curve()
