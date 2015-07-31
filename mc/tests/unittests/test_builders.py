"""
Test builders
"""
import unittest
import io
import mock
from mc.builders import DockerImageBuilder, DockerRunner
from mc.models import Commit


class TestDockerImageBuilder(unittest.TestCase):
    """
    Test the DockerImageBuilder
    """
    def setUp(self):
        self.commit = Commit(
            commit_hash='master',
            repository="adsws"
        )
        self.builder = DockerImageBuilder(self.commit)

    def test_get_templates(self):
        """
        Test that the builder grabs the expected templates.
        This uses "live" templates.
        """
        self.builder.render_templates()
        self.assertGreater(len(self.builder.files), 0)
        self.assertEqual(self.builder.files[0]['name'], 'Dockerfile')
        self.assertIn(self.commit.commit_hash, self.builder.files[0]['content'])

    def test_create_docker_context(self):
        """
        Test that the docker context is created in-memory and that it has
        a non zero size. This uses "live" templates.
        """
        self.builder.render_templates()
        self.builder.create_docker_context()
        self.assertIsInstance(self.builder.tarfile, io.BytesIO)
        self.assertGreater(len(self.builder.tarfile.readlines()), 0)

    @mock.patch('mc.builders.Client')
    def test_docker_build(self, mocked):
        """
        Tests that docker build (using a mocked docker client) returns
        as expected
        """
        instance = mocked.return_value
        instance.build.return_value = ['Successfully built']
        self.builder.build()
        self.assertTrue(self.builder.built)

    @mock.patch('mc.builders.Client')
    def test_docker_push(self, mocked):
        """
        Tests that docker push (using a mocked docker client) returns
        as expected
        """
        instance = mocked.return_value
        instance.push.return_value = ['pushing tag']
        self.builder.push()
        self.assertTrue(self.builder.pushed)


class TestDockerRunner(unittest.TestCase):
    """
    Test the docker runner
    """

    @mock.patch('mc.builders.Client')
    def setUp(self, mocked):
        instance = mocked.return_value
        instance.create_container.return_value = {'Id': 'mocked'}
        self.instance = instance
        self.builder = DockerRunner(
            image='redis',
            name='redis',
            mem_limit="100m",
            network_mode="host"
        )

    def test_initialization(self):
        """
        the Dockerrunner.setup() method should modify its container
        attribute, and client.create_container should be called with the
        expected kwargs
        """
        self.assertEqual(self.builder.container,  {'Id': 'mocked'})
        self.instance.create_container.assert_called_with(
            host_config={'NetworkMode': 'host', "Memory": 104857600},
            name='redis',
            image='redis'
        )
        self.instance.pull.assert_called_with('redis')

    def test_start(self):
        """
        the start() method should run an option callback after calling
        docker.Client.start with the expected container id
        """
        def cb(container):
            self.assertEqual(container, {'Id': 'mocked'})
        self.builder.start(callback=cb)
        self.instance.start.assert_called_with(container='mocked')

    def test_teardown(self):
        """
        the teardown() method should be called with the correct container id
        """
        self.builder.teardown()
        self.instance.stop.assert_called_with(container='mocked')
        self.instance.remove_container.assert_called_with(container='mocked')
