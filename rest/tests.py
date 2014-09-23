from django.test import TestCase, Client

from models import Node, NodeSession, NodeInfo
from judge.models import Submission

from xmltodict import parse, unparse


class SessionTest(TestCase):

    def setUp(self):
        self.c = Client()
        self.url = '/rest/getsession/nodename/{}/nodekey/{}/'

    def test_getsession(self):
        response = self.c.get(self.url.format('testname', 'testkey'))
        self.assertEqual(response.status_code, 401)
        nodes = Node.objects.filter(name='testname')
        self.assertEqual(nodes.count(), 1)

        node = nodes[0]
        node.authorized = True
        node.save()

        response = self.c.get(self.url.format('testname', 'testkey'))
        self.assertEqual(response.status_code, 200)
        nodes = Node.objects.filter(name='testname')
        self.assertEqual(nodes.count(), 1)

    def test_multiple_getsessions_for_same_node(self):
        response = self.c.get(self.url.format('testname', 'testkey'))
        self.assertEqual(response.status_code, 401)
        self.assertEqual(Node.objects.filter(name='testname').count(), 1)

        response = self.c.get(self.url.format('testname', 'testkey'))
        self.assertEqual(response.status_code, 401)
        self.assertEqual(Node.objects.filter(name='testname').count(), 1)

    def test_multiple_getsessions_for_different_nodes(self):
        response = self.c.get(self.url.format('testname', 'testkey'))
        self.assertEqual(response.status_code, 401)
        self.assertEqual(Node.objects.filter().count(), 1)

        response = self.c.get(self.url.format('testname2', 'testkey2'))
        self.assertEqual(response.status_code, 401)
        self.assertEqual(Node.objects.filter().count(), 2)

    def test_endsession(self):
        response = self.c.get(self.url.format('testname', 'testkey'))
        self.assertEqual(response.status_code, 401)
        nodes = Node.objects.filter(name='testname')
        self.assertEqual(nodes.count(), 1)

        node = nodes[0]
        node.authorized = True
        node.save()

        response = self.c.get(self.url.format('testname', 'testkey'))
        self.assertEqual(response.status_code, 200)

        response = parse(response.content)

        sid = response['session']['id']

        response = self.c.get('/rest/endsession/sessionid/' + sid + '/')
        self.assertEqual(response.status_code, 200)
        session = NodeSession.objects.get(id=sid)
        self.assertEqual(session.active, False)

        response = self.c.get('/rest/getsubmission/sessionid/' + sid + '/')
        print response.content
        self.assertEqual(response.status_code, 401)


class ReportTest(TestCase):

    def setUp(self):
        self.c = Client()
        self.nurl = '/rest/getsession/nodename/{}/nodekey/{}/'

        response = self.c.get(self.nurl.format('testname', 'testkey'))
        self.assertEqual(response.status_code, 401)
        nodes = Node.objects.filter(name='testname')
        self.assertEqual(nodes.count(), 1)

        node = nodes[0]
        node.authorized = True
        node.save()

        response = self.c.get(self.nurl.format('testname', 'testkey'))
        self.assertEqual(response.status_code, 200)

        response = parse(response.content)

        sid = response['session']['id']
        self.url = '/rest/postreport/sessionid/' + sid + '/'

    def test_report_creation(self):
        response = self.c.post(self.url,
                               data="""<report>
                               <version>1.0</version>
                               <memory>12</memory>
                               <disk>13</disk>
                               <frequency>100</frequency>
                               <languages>
                               <language>Python</language>
                               </languages>
                               </report>""", content_type='application/xml')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(NodeInfo.objects.get(ip='127.0.0.1').version, '1.0')

    def test_invalid_content_type(self):
        response = self.c.post(self.url,
                               data="""<report>
                               <version>1.0</version>
                               <memory>12</memory>
                               <disk>13</disk>
                               <frequency>100</frequency>
                               <languages>
                               <language>Python</language>
                               </languages>
                               </report>""", content_type='application/abc')

        self.assertEqual(response.status_code, 400)

    def test_invalid_xml(self):
        response = self.c.post(self.url,
                               data="""<repor
                               <version>1.0</version>
                               <memory>12</memory>
                               <disk>13</disk>
                               <frequency>100</frequency>
                               <languages>
                               <language>Python</language>
                               </languages>
                               </report>""", content_type='application/xml')

        self.assertEqual(response.status_code, 400)


class SubmissionTest(TestCase):

    def setUp(self):
        self.c = Client()
        self.nurl = '/rest/getsession/nodename/{}/nodekey/{}/'

        response = self.c.get(self.nurl.format('testname', 'testkey'))
        self.assertEqual(response.status_code, 401)
        nodes = Node.objects.filter(name='testname')
        self.assertEqual(nodes.count(), 1)

        node = nodes[0]
        node.authorized = True
        node.save()

        response = self.c.get(self.nurl.format('testname', 'testkey'))
        self.assertEqual(response.status_code, 200)

        response = parse(response.content)

        sid = response['session']['id']
        self.gurl = '/rest/getsubmission/sessionid/' + sid + '/'
        self.purl = '/rest/postsubmission/sessionid/' + sid \
                + '/submissionid/{}/'

    def test_getsubmission(self):
        response = self.c.get(self.gurl)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.items().index(('Content-Type', 'application/xml')))

        response = parse(response.content)
        self.assertEqual(response['submission']['pid'], 'HELLO')

    def test_postsubmission(self):
        response = self.c.get(self.gurl)
        response = parse(response.content)
        subid = response['submission']['sid']

        res = """<submission>
            <status>1</status>
            <compilelog>alalla</compilelog>
            <results>
                <result>
                    <returncode>10</returncode>
                    <mark>1</mark>
                    <time>13</time>
                </result>
                <result>
                    <returncode>2</returncode>
                    <mark>0</mark>
                    <time>13</time>
                </result>
            </results>
        </submission>"""

        response = self.c.post(self.purl.format(subid), data=res,
                              content_type='application/xml')
        self.assertEqual(response.status_code, 200)

        s = Submission.objects.get(id=subid)
        self.assertEqual(s.score, 50)
        self.assertEqual(s.status, s.JUDGED_STATUS)


class TestsTest(TestCase):

    def setUp(self):
        self.c = Client()
        self.nurl = '/rest/getsession/nodename/{}/nodekey/{}/'

        response = self.c.get(self.nurl.format('testname', 'testkey'))
        self.assertEqual(response.status_code, 401)
        nodes = Node.objects.filter(name='testname')
        self.assertEqual(nodes.count(), 1)

        node = nodes[0]
        node.authorized = True
        node.save()

        response = self.c.get(self.nurl.format('testname', 'testkey'))
        self.assertEqual(response.status_code, 200)

        response = parse(response.content)

        sid = response['session']['id']
        self.url = '/rest/gettests/sessionid/' + sid + '/problemid/HELLO/{}/'

    def test_gettests_timestamp(self):
        response = self.c.get(self.url.format('timestamp'))
        self.assertEqual(response.status_code, 200)
        response = parse(response.content)
        self.assertEqual(response['test']['in'], '1338729402')


    def test_gettests_files(self):
        response = self.c.get(self.url.format('in'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.has_header('X-Sendfile'))

        response = self.c.get(self.url.format('out'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.has_header('X-Sendfile'))

        response = self.c.get(self.url.format('conf'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.has_header('X-Sendfile'))
