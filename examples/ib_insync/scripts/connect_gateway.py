from ib_insync import IB, util, Stock
import os


ibgw_port = os.environ.get('IBGW_PORT', 4002)

if __name__ == "__main__":
    ib = IB()
    ib.connect('127.0.0.1', ibgw_port, clientId=999)
    contract = Stock('AAPL', 'SMART', 'USD')
    bars = ib.reqHistoricalData(
        contract, endDateTime='', durationStr='30 D',
        barSizeSetting='1 day', whatToShow='MIDPOINT', useRTH=True)

    # convert to pandas dataframe:
    df = util.df(bars)
    print(df)
