import pytest
import subprocess
import testinfra
import os
import time

IMAGE_NAME = os.environ['IMAGE_NAME']
ib_port = os.environ.get('IB_PORT', 4001)
ibgw_port = os.environ.get('IBGW_PORT', 4002)
ib_logging_level = os.environ.get('IB_LOGGING_LEVEL', 'DEBUG')
watchdog_app_startup_time = os.environ.get('IBGW_WATCHDOG_APP_STARTUP_TIME', 60)
watchdog_app_timeout = os.environ.get('IBGW_WATCHDOG_APP_TIMEOUT', 30)
watchdog_connect_timeout = os.environ.get('IBGW_WATCHDOG_CONNECT_TIMEOUT', 60)
watchdog_probe_timeout = os.environ.get('IBGW_WATCHDOG_PROBE_TIMEOUT', 10)
watchdog_readonly = os.environ.get('IBGW_WATCHDOG_READONLY', True)
watchdog_retry_delay = os.environ.get('IBGW_WATCHDOG_RETRY_DELAY', 5)

# scope='session' uses the same container for all the tests;
# scope='function' uses a new container per test function.
@pytest.fixture(scope='session')
def host(request):
    account = 'test'
    password = 'test'
    trade_mode = 'paper'

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
    # return a testinfra connection to the container
    yield testinfra.get_host("docker://" + docker_id)
    # at the end of the test suite, destroy the container
    subprocess.check_call(['docker', 'rm', '-f', docker_id])
    time.sleep(15)

def test_ib_connect_fail(host):
    script = """
from ib_insync import *
IB.sleep(120)
ib = IB()
ib.connect('127.0.0.1', {port}, clientId=1)
ib.disconnect()
""".format(port=ibgw_port)
    cmd = host.run("python -c \"{}\"".format(script))
    assert cmd.rc != 0
