"""
Run coverall report if have config
"""
import os

if os.getenv('COVERAGE_ENABLE', None):
    os.system('coverage combine')
    os.system('coveralls')
    os.system('coverage report')
    os.system('coverage html -d $CIRCLE_ARTIFACTS')
