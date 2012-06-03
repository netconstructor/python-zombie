from unittest import TestCase
import cStringIO

try:
    from json import loads, dumps
except ImportError:
    from simplejson import loads, dumps  # noqa
import fudge

from pythonzombie.proxy.server import ZombieProxyServer
from pythonzombie.proxy.client import ZombieProxyClient


class FakeNode(object):
    def __json__(self):
        return 'ENCODED'


class FakePopen(object):

    stdin = cStringIO.StringIO()
    stdout = cStringIO.StringIO()


class TestServerCommunication(TestCase):

    def setUp(self):
        super(TestServerCommunication, self).setUp()
        self.server = ZombieProxyServer()
        self.client = ZombieProxyClient(self.server.socket)

    def tearDown(self):
        super(TestServerCommunication, self).tearDown()
        fudge.clear_expectations()

    def test_encode(self):
        foo = {
            'foo': 'bar'
        }
        self.client.encode(foo) == dumps(foo)

        self.client.encode(FakeNode()) == 'ENCODED'

    def test_decode(self):
        foo = dumps({
            'foo': 'bar'
        })
        self.client.__decode__(foo) == loads(foo)

    def test_simple_send(self):
        self.client.__send__(
            "stream.end()"
        )

    def test_simple_json(self):
        obj = {
            'foo': 'bar',
            'test': 500
        }
        assert self.client.json(obj) == obj

    @fudge.with_fakes
    def test_simple_wait(self):

        js = """
        try {
            browser.visit("%s",  function(err, browser){
                if (err)
                    stream.end(JSON.stringify(err.message));
                else
                    stream.end();
            });
        } catch (err) {
            stream.end(JSON.stringify(err.message));
        }
        """ % 'http://example.com'

        with fudge.patched_context(
            ZombieProxyClient,
            '__send__',
            (fudge.Fake('__send__', expect_call=True).
                with_args(js)
            )):

            self.client.wait('visit', 'http://example.com')

    @fudge.with_fakes
    def test_wait_without_arguments(self):

        js = """
        try {
            browser.wait(null, function(err, browser){
                if (err)
                    stream.end(JSON.stringify(err.message));
                else
                    stream.end();
            });
        } catch (err) {
            stream.end(JSON.stringify(err.message));
        }
        """

        with fudge.patched_context(
            ZombieProxyClient,
            '__send__',
            (fudge.Fake('__send__', expect_call=True).
                with_args(js)
            )):

            self.client.wait('wait')
