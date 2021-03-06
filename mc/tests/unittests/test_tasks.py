"""
Test utilities
"""
from flask.ext.testing import TestCase
from mock import patch, call, Mock
from mc import app
from mc.models import db, Commit, Build
from mc.tasks import register_task_revision, build_docker, update_service, \
    start_test_environment, stop_test_environment, run_test_in_environment, \
    run_ci_test, run_task

import datetime


class TestTestEnvironment(TestCase):
    """
    Test the start_test_environment task
    """
    def create_app(self):
        return app.create_app()

    @patch('mc.builders.SolrDockerRunner')
    @patch('mc.builders.RegistratorDockerRunner')
    @patch('mc.builders.GunicornDockerRunner')
    @patch('mc.builders.PostgresDockerRunner')
    @patch('mc.builders.ConsulDockerRunner')
    @patch('mc.builders.RedisDockerRunner')
    def test_containers_are_built(self,
                                  mocked_redis_runner,
                                  mocked_consul_runner,
                                  mocked_postgres_runner,
                                  mocked_gunicorn_runner,
                                  mocked_registrator_runner,
                                  mocked_solr_runner
                                  ):
        """
        Tests that the containers relevant for the test environment are started
        """

        config = {}
        services = config.setdefault('services', [
                {
                    'name': 'adsws',
                    'repository': 'adsabs',
                    'tag': '0596971c755855ff3f9caed2f96af7f9d5792cc2'
                }
            ])

        dependencies = config.setdefault('dependencies', [
            {
                "name": "redis",
                "image": "redis:2.8.9",
            },
            {
                "name": "postgres",
                "image": "postgres:9.3",
            },
            {
                "name": "registrator",
                "image": "gliderlabs/registrator:latest"
            },
            {
                "name": "solr",
                "image": "adsabs/montysolr:v48.1.0.3"
            },
            {
                "name": "consul",
                "image": "adsabs/consul:v1.0.0",
            }
        ])

        instance_gunicorn_runner = mocked_gunicorn_runner.return_value
        instance_redis_runner = mocked_redis_runner.return_value
        instance_consul_runner = mocked_consul_runner.return_value
        instance_postgres_runner = mocked_postgres_runner.return_value
        instance_registrator_runner = mocked_registrator_runner.return_value
        instance_solr_runner = mocked_solr_runner.return_value

        instance_list = [
            instance_gunicorn_runner,
            instance_redis_runner,
            instance_consul_runner,
            instance_postgres_runner,
            instance_registrator_runner,
            instance_solr_runner
        ]

        for instance in instance_list:
            instance.start.return_value = None
            instance.provision.return_value = None

        instance_registrator_runner.start.return_value = None
        instance_registrator_runner.provision.return_value = None

        start_test_environment(test_id=None, config=config)

        for instance in instance_list:

            self.assertTrue(
                instance.start.called,
                msg='Instance {} was not called'.format(instance)
            )
            instance.provision.has_calls(
                [call(callback=s['name']) for s in services]
            )

    @patch('mc.tasks.Client')
    def test_containers_are_stopped(self, mocked):
        """
        Test that we have the opportunity to stop containers based on an id
        """
        instance = mocked.return_value
        instance.containers.return_value = [
            {
                u'Command': u'/entrypoint.sh redis-server',
                u'Created': 1443632967,
                u'Id': u'mocked',
                u'Image': u'redis',
                u'Labels': {},
                u'Names': [u'/livetest-redis-tLJpZ'],
                u'Ports': [{u'PrivatePort': 6379, u'Type': u'tcp'}],
                u'Status': u'Up About a minute'
            }
        ]
        instance.stop.return_value = None
        instance.remove_container.return_value = None

        stop_test_environment(test_id='livetest')

        instance.stop.assert_has_calls([
            call(container=u'mocked')
        ])

        instance.remove_container.assert_has_calls([
            call(container=u'mocked')
        ])

    @patch('mc.tasks.TestRunner.service_provisioner')
    def test_can_start_tests_that_run_in_environment(self, mocked):
        """
        Test that we can start running the tests in the environment
        """
        instance = mocked.return_value

        run_test_in_environment(test_id='livetest')

        # Check provisioned
        instance.assert_has_calls([
            call(),
        ])

    @patch('mc.tasks.TestRunner.service_provisioner')
    @patch('mc.builders.SolrDockerRunner')
    @patch('mc.builders.RegistratorDockerRunner')
    @patch('mc.builders.GunicornDockerRunner')
    @patch('mc.builders.PostgresDockerRunner')
    @patch('mc.builders.ConsulDockerRunner')
    @patch('mc.builders.RedisDockerRunner')
    def test_can_start_run_stop_all(self,
                                    mocked_redis_runner,
                                    mocked_consul_runner,
                                    mocked_postgres_runner,
                                    mocked_gunicorn_runner,
                                    mocked_registrator_runner,
                                    mocked_solr_runner,
                                    mocked_test_runner
                                    ):
        """
        Tests the spin up, running of tests, and tear down of the test environment

        This test is a bit overkill, but just in case the running task changes differently to the sub commands, the full
        test is included here.
        """

        # START THE DEPENDENCIES AND SERVICES
        config = {}
        services = config.setdefault('services', [
                {
                    'name': 'adsws',
                    'repository': 'adsabs',
                    'tag': '0596971c755855ff3f9caed2f96af7f9d5792cc2'
                }
            ])

        config.setdefault('dependencies', [
            {
                "name": "redis",
                "image": "redis:2.8.9",
            },
            {
                "name": "postgres",
                "image": "postgres:9.3",
            },
            {
                "name": "registrator",
                "image": "gliderlabs/registrator:latest"
            },
            {
                "name": "solr",
                "image": "adsabs/montysolr:v48.1.0.3"
            },
            {
                "name": "consul",
                "image": "adsabs/consul:v1.0.0",
            }
        ])

        config.setdefault('tests', [
            'adsrex'
        ])

        instance_gunicorn_runner = mocked_gunicorn_runner.return_value
        instance_redis_runner = mocked_redis_runner.return_value
        instance_consul_runner = mocked_consul_runner.return_value
        instance_postgres_runner = mocked_postgres_runner.return_value
        instance_registrator_runner = mocked_registrator_runner.return_value
        instance_solr_runner = mocked_solr_runner.return_value

        instance_list = [
            instance_gunicorn_runner,
            instance_redis_runner,
            instance_consul_runner,
            instance_postgres_runner,
            instance_registrator_runner,
            instance_solr_runner
        ]

        for instance in instance_list:
            instance.start.return_value = None
            instance.provision.return_value = None
            instance.teardown.return_value = None

        run_ci_test(test_id='unittests', config=config)

        for instance in instance_list:

            self.assertTrue(
                instance.start.called,
                msg='Instance {} was not called'.format(instance)
            )
            instance.provision.has_calls(
                [call(callback=s['name']) for s in services]
            )

        # RUN TESTS
        mocked_test_runner.assert_has_calls([
            call(services=['adsrex']), call()()
        ])

        # STOP AND REMOVE CONTAINERS
        for instance in instance_list:
            self.assertTrue(
                instance.teardown.called
            )


class TestRegisterTaskDefinition(TestCase):
    """
    Test the register_task_definition task
    """
    def create_app(self):
        return app.create_app()

    @patch('mc.tasks.get_boto_session')
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

        session.client.assert_called_with('ecs')
        client.register_task_definition.assert_called_with(
            family="unittest-family",
            containerDefinitions=[],
            volumes=[],
        )
        register_task_revision('{"valid": "json"}')
        client.register_task_definition.assert_called_with(valid="json")


class TestUpdateService(TestCase):
    """
    Test the update service task
    """
    def create_app(self):
        return app.create_app()

    @patch('mc.tasks.get_boto_session')
    def test_update_service(self, Session):
        """
        the update_service task should pass call the boto3 task after
        establishing a session
        """
        session = Session.return_value
        client = session.client.return_value
        kwargs = dict(
            cluster="unittest-cluster",
            service="unittest-service",
            desiredCount=5,
            taskDefinition='{"valid": "json"}',
        )
        update_service(**kwargs)
        session.client.assert_called_with('ecs')
        client.update_service.assert_called_with(**kwargs)


class TestRunTask(TestCase):
    """
    Test the run task
    """
    def create_app(self):
        return app.create_app()

    @patch('mc.tasks.get_boto_session')
    def test_run_task(self, Session):
        """
        the run_task task should pass call the boto3 task after
        establishing a session
        """
        session = Session.return_value
        client = session.client.return_value
        kwargs = dict(
            cluster="unittest-cluster",
            count=1,
            taskDefinition='{"valid": "json"}',
        )
        run_task(**kwargs)
        session.client.assert_called_with('ecs')
        client.run_task.assert_called_with(**kwargs)


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
