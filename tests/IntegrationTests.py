from dash.react import Dash
from dash.react import Dash
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import dash
import dash_core_components
import dash_core_components as dcc
import dash_html_components as html
import importlib
import multiprocessing
import percy
import time
import unittest


class IntegrationTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        super(IntegrationTests, cls).setUpClass()
        cls.driver = webdriver.Chrome()

        loader = percy.ResourceLoader(
          webdriver=cls.driver
        )
        cls.percy_runner = percy.Runner(loader=loader)

        cls.percy_runner.initialize_build()

    @classmethod
    def tearDownClass(cls):
        super(IntegrationTests, cls).tearDownClass()
        cls.driver.quit()
        cls.percy_runner.finalize_build()

    def setUp(s):
        pass

    def tearDown(s):
        s.server_process.terminate()

    def startServer(s, dash):
        def run():
            dash.run_server(
                port=8050,
                debug=False,
                component_suites=[
                    'dash_core_components',
                    'dash_html_components'
                ],
                threaded=True
            )

        # Run on a separate process so that it doesn't block
        s.server_process = multiprocessing.Process(target=run)
        s.server_process.start()
        time.sleep(0.5)

        # Visit the dash page
        s.driver.get('http://localhost:8050')

        # Inject an error and warning logger
        logger = '''
        window.tests = {};
        window.tests.console = {error: [], warn: [], log: []};

        var _log = console.log;
        var _warn = console.warn;
        var _error = console.error;

        console.log = function() {
            window.tests.console.log.push({method: 'log', arguments: arguments});
            return _log.apply(console, arguments);
        };

        console.warn = function() {
            window.tests.console.warn.push({method: 'warn', arguments: arguments});
            return _warn.apply(console, arguments);
        };

        console.error = function() {
            window.tests.console.error.push({method: 'error', arguments: arguments});
            return _error.apply(console, arguments);
        };
        '''
        s.driver.execute_script(logger)