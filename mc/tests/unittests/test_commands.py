"""
test manage.py commands
"""

from flask.ext.testing import TestCase
from mc.app import create_app
from mc.tests.stubdata import github_commit_payload
from mc.manage import Build
from mc.models import db, Commit
import mock
import httpretty


class TestBuild(TestCase):
    """
    Test the manage.py build command
    """

    def create_app(self):
        app = create_app()
        app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///"
        return app

    def setUp(self):
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    @httpretty.activate
    def test_run(self):
        """
        manage.py build <repo> <commit> should create a new Commit and
        build_docker.delay() should be called
        """
        repo, commit = "unittest-repo", "unittest-hash"

        httpretty.register_uri(
            httpretty.GET,
            self.app.config['GITHUB_COMMIT_API'].format(
                repo=repo, hash=commit
            ),
            body=github_commit_payload.payload,
            content_type="application/json"
        )

        with mock.patch('mc.manage.build_docker') as mocked:
            Build().run(repo, commit, app=self.app)
            c = db.session.query(Commit).filter_by(
                repository=repo, commit_hash=commit
            ).one()
            self.assertIsNotNone(c)
            mocked.delay.assert_called_once_with(c.id)
            Build().run(repo, commit, app=self.app)
            c2 = db.session.query(Commit).filter_by(
                repository=repo, commit_hash=commit
            ).one()
            self.assertEqual(c.id, c2.id)



