# -*- coding: utf-8 -*-
import os
import sys
import coverage
import unittest

from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager

from config import setup_logging, running_config
from app import create_app, add_api_support

setup_logging()
flask_app = create_app(running_config)
flask_app = add_api_support(flask_app)

from app import db

migrate = Migrate(flask_app, db)

manager = Manager(flask_app)
manager.add_command("db", MigrateCommand)

COV = None
if os.environ.get('FLASK_COVERAGE'):
    COV = coverage.coverage(branch=True, include='app/*')
    COV.start()


@manager.command
# The flask script can be used for some cli command which should access database.
def test(enable_cov=True):
    """Run the unit tests."""
    if enable_cov and not os.environ.get('FLASK_COVERAGE'):
        os.environ['FLASK_COVERAGE'] = '1'
        os.execvp(sys.executable, [sys.executable] + sys.argv)

    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)
    if COV:
        COV.stop()
        COV.save()
        print('Coverage Summary:')
        COV.report()
        basedir = os.path.abspath(os.path.dirname(__file__))
        covdir = os.path.join(basedir, 'tmp/coverage')
        COV.html_report(directory=covdir)
        print('HTML version: file://%s/index.html' % covdir)
        COV.erase()


@flask_app.route("/")
def index():
    return "hello from manager"


if __name__ == '__main__':
    manager.run()
