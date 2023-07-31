import pytest
import os
import subprocess
import time
from ib_insync import IB, util, Forex
import asyncio
import time

IMAGE_NAME = os.environ['IMAGE_NAME']
account = os.environ['IB_ACCOUNT']
password = os.environ['IB_PASSWORD']
trade_mode = os.environ['TRADE_MODE']
ib_port = os.environ.get('IB_PORT', 4001)
ibgw_port = os.environ.get('IBGW_PORT', 4002)
ib_logging_level = os.environ.get('IB_LOGGING_LEVEL', 'DEBUG')
watchdog_app_startup_time = os.environ.get('IBGW_WATCHDOG_APP_STARTUP_TIME', 60)
watchdog_app_timeout = os.environ.get('IBGW_WATCHDOG_APP_TIMEOUT', 30)
watchdog_connect_timeout = os.environ.get('IBGW_WATCHDOG_CONNECT_TIMEOUT', 60)
watchdog_probe_timeout = os.environ.get('IBGW_WATCHDOG_PROBE_TIMEOUT', 10)
watchdog_readonly = os.environ.get('IBGW_WATCHDOG_READONLY', True)
watchdog_retry_delay = os.environ.get('IBGW_WATCHDOG_RETRY_DELAY', 5)


@pytest.fixture(scope='function')
def ib_docker():
    # run a container
    docker_id = subprocess.check_output(
        ['docker', 'run', 
        '-e', 'IB_ACCOUNT={}'.format(account),
        '-e', 'IB_PASSWORD={}'.format(password),
        '-e', 'TRADE_MODE={}'.format(trade_mode),
        '-e', 'IB_PORT={}'.format(ib_port),
        '-e', 'IBGW_PORT={}'.format(ibgw_port),
        '-e', 'IB_LOGGING_LEVEL={}'.format(ib_logging_level),
        '-e', 'IBGW_WATCHDOG_APP_STARTUP_TIME={}'.format(watchdog_app_startup_time),
        '-e', 'IBGW_WATCHDOG_APP_TIMEOUT={}'.format(watchdog_app_timeout),
        '-e', 'IBGW_WATCHDOG_CONNECT_TIMEOUT={}'.format(watchdog_connect_timeout),
        '-e', 'IBGW_WATCHDOG_PROBE_TIMEOUT={}'.format(watchdog_probe_timeout),
        '-e', 'IBGW_WATCHDOG_READONLY={}'.format(watchdog_readonly),
        '-e', 'IBGW_WATCHDOG_RETRY_DELAY={}'.format(watchdog_retry_delay),
        '-p', '{}:{}'.format(ibgw_port, ibgw_port),
        '-d', IMAGE_NAME, 
        "tail", "-f", "/dev/null"]).decode().strip()
    yield docker_id
    subprocess.check_call(['docker', 'rm', '-f', docker_id])
    time.sleep(15)


def test_ibgw_interactive(ib_docker):
    ib = IB()
    wait = 120
    while not ib.isConnected():
        try:
            IB.sleep(1)
            ib.connect('127.0.0.1', ibgw_port, clientId=999)
        except:
            pass
        wait -= 1
        if wait <= 0:
            break
    
    contract = Forex('EURUSD')
    bars = ib.reqHistoricalData(
        contract, endDateTime='', durationStr='30 D',
        barSizeSetting='1 hour', whatToShow='MIDPOINT', useRTH=True)

    # convert to pandas dataframe:
    df = util.df(bars)
    print(df)
    
def test_ibgw_restart(ib_docker):

    subprocess.check_output(
        ['docker', 'container', 'stop', ib_docker]).decode().strip()
    subprocess.check_output(
        ['docker', 'container', 'start', ib_docker]).decode().strip()
    
    ib = IB()
    wait = 120
    while not ib.isConnected():
        try:
            IB.sleep(1)
            ib.connect('127.0.0.1', ibgw_port, clientId=999)
        except:
            pass
        wait -= 1
        if wait <= 0:
            break
    
    contract = Forex('EURUSD')
    bars = ib.reqHistoricalData(
        contract, endDateTime='', durationStr='30 D',
        barSizeSetting='1 hour', whatToShow='MIDPOINT', useRTH=True)

    # convert to pandas dataframe:
    df = util.df(bars)
    print(df)
