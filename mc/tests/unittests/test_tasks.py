"""
Test utilities
"""
from flask.ext.testing import TestCase
from mock import patch
from mc import app
from mc.models import db, Commit, Build
from mc.tasks import register_task_revision, build_docker
import datetime


class TestRegisterTaskDefinition(TestCase):
    """
    Test the register_task_definition task
    """
    def create_app(self):
        app_ = app.create_app()
        app_.config['MC_LOGGING'] = {}
        app_.config['AWS_REGION'] = "unittest-region"
        app_.config['AWS_ACCESS_KEY'] = "unittest-access"
        app_.config['AWS_SECRET_KEY'] = "unittest-secret"
        return app_

    @patch('mc.tasks.Session')
    def test_register_task_definition(self, Session):
        """
        the register_task_definition task should pass a dockerrun.aws.json
        template as kwargs to boto3.ecs.register_task_definition
        """
        session = Session.return_value
        client = session.client.return_value

        with patch('mc.builders.ECSBuilder') as ECSBuilder:
            ecsbuild = ECSBuilder.return_value
            ecsbuild.render_template.return_value = '''{
                "family": "unittest-family",
                "containerDefinitions": [],
                "volumes": []
            }'''
            register_task_revision(ecsbuild)

        Session.assert_called_with(
            aws_access_key_id="unittest-access",
            aws_secret_access_key="unittest-secret",
            region_name="unittest-region",
        )
        session.client.assert_called_with('ecs')
        client.register_task_definition.assert_called_with(
            family="unittest-family",
            containerDefinitions=[],
            volumes=[],
        )


class TestDockerBuildTask(TestCase):
    """
    Test the Build task
    """
    def create_app(self):
        app_ = app.create_app()
        app_.config['SQLALCHEMY_DATABASE_URI'] = "sqlite://"
        app_.config['MC_LOGGING'] = {}
        return app_

    def setUp(self):
        """
        setUp and tearDown are run at the start of each test; ensure
        that a fresh database is used for each test.
        """
        db.create_all()

    def tearDown(self):
        """
        setUp and tearDown are run at the start of each test; ensure
        that a fresh database is used for each test.
        """
        db.session.remove()
        db.drop_all()

    @patch('mc.builders.Client')
    def test_docker_build_task(self, mocked):
        """
        Tests that the docker_build_task adds a Build entry. Assumes the
        underlying builder.run command does not Raise
        """
        commit = Commit(
            repository='adsws',
            commit_hash='test-hash',
        )
        db.session.add(commit)
        db.session.commit()
        commit_id = commit.id

        instance = mocked.return_value
        instance.build.return_value = ['Successfully built']
        instance.push.return_value = ['pushing tag']

        build_docker(commit_id)

        build = db.session.query(Build).first()
        self.assertEqual(build.commit_id, commit_id)
        self.assertAlmostEqual(
            build.timestamp,
            datetime.datetime.now(),
            delta=datetime.timedelta(seconds=1)
        )
        self.assertTrue(build.built)
        self.assertTrue(build.pushed)