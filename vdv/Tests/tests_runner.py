from unittest import TestLoader, TextTestRunner


TEST_DIRS = [
    './Account/',
    # './Court'
    # './Equipment/',
    # './Extention/',
    # './Location/',
    # './SpecialUsers/Landlord',
    # './SpecialUsers/Simpleuser',
    # './Sport',
    # './Tariff',
]
TEST_FILE_PATTERN = '*Tests.py'


def run_tests(test_dirs=TEST_DIRS, pattern=TEST_FILE_PATTERN):
    loader = TestLoader()
    for test_dir in test_dirs:
        suite = loader.discover(start_dir=test_dir, pattern=pattern)
        runner = TextTestRunner()
        runner.run(suite)


if __name__ == '__main__':
    run_tests()
