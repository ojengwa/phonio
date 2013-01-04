from unittest import TestSuite

def load_tests(loader, tests, pattern):
    suite = TestSuite()
    names = ('phonio.test.softphone_test',
            'phonio.test.dialer_test' )
    for name in names:
        tests = loader.loadTestsFromName(name)
        suite.addTests(tests)
    return suite
