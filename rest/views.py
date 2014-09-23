from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render_to_response, get_object_or_404
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_control
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.base import View
from django.http import HttpResponse

from judge.models import Submission, Result, Problem
from models import Node, NodeSession, NodeInfo, Language
from sendfile import sendfile

from xmltodict import parse


class SessionGetView(View):
    """Create a new session for the node if it authorizes properly."""

    template_name = "session.xml"

    def get(self, request, *args, **kwargs):
        name = kwargs['nodeName']
        key = kwargs['nodeKey']

        # Search for node in DB
        try:
            node = Node.objects.get(name=name, key=key)
        except ObjectDoesNotExist:

            # Create if doesn't exist
            node = Node(name=name, key=key)
            node.save()

            # Return error
            return HttpResponse(status=401)

        # If found check if authorized
        if not node.authorized:
            return HttpResponse(status=401)
        else:
            # Check if node has an active session
            session = NodeSession.objects.filter(node=node,
              expiration_time__gte=timezone.now(), active=True)

            if session:
                session = session[0]

            if not session or session.is_expired or not session.active:
                # Create a new session
                session = NodeSession(node=node)
                session.save()

            # Return the details to the node
            return render_to_response(self.template_name, {
                'id': session.id,
                'expires': session.expiration_time.strftime('%s'),
            }, content_type='application/xml')

    @method_decorator(cache_control(no_cache=True))
    def dispatch(self, *args, **kwargs):
        return super(SessionGetView, self).dispatch(*args, **kwargs)


class SessionEndView(View):
    """Disable the session with the given ID."""

    template_name = "session.xml"

    def get(self, request, *args, **kwargs):
        sessionId = kwargs['sessionId']

        session = get_object_or_404(NodeSession, id=sessionId)

        session.active = False
        session.save()

        return HttpResponse(status=200)

    @method_decorator(cache_control(no_cache=True))
    def dispatch(self, *args, **kwargs):
        return super(SessionEndView, self).dispatch(*args, **kwargs)


class RESTView(View):

    @method_decorator(cache_control(no_cache=True))
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        # Check authorization
        sessionId = kwargs['sessionId']

        # Check if user has an active session
        try:
            session = NodeSession.objects.get(id=sessionId)
        except ObjectDoesNotExist:
            return HttpResponse(status=401)

        if session.is_expired or not session.active:
            return HttpResponse(status=401)

        # Identify the node
        self.node = session.node

        # Check if node is authorized to use webservices
        if not self.node.authorized:
            return HttpResponse(status=401)

        # If it is a POST request and has a XML body
        if request.method == 'POST' and request.body and \
          request.META['CONTENT_TYPE'] == 'application/xml':
            try:
                self.data = parse(request.body)
            except:
                return HttpResponse(status=400)
        else:
            HttpResponse(status=400)

        return super(RESTView, self).dispatch(request, *args, **kwargs)


class ReportView(RESTView):
    """Report the nodes status to the supervisor."""

    template_name = "report.xml"

    def post(self, request, *args, **kwargs):
        try:
            ip = request.META['REMOTE_ADDR']
            version = self.data['report']['version']
            memory = self.data['report']['memory']
            disk = self.data['report']['disk']
            frequency = self.data['report']['frequency']
            languages = []
            for language in self.data['report']['languages']['language']:
                languages.append(language)
        except (KeyError, AttributeError):
            return HttpResponse(status=400)

        try:
            self.node.info
        except ObjectDoesNotExist:
            self.node.info = NodeInfo(node=self.node, ip=ip, version=version,
              memory=memory, frequency=frequency, disk=disk)
        else:
            self.node.info = NodeInfo(ip=ip, version=version,
              memory=memory, frequency=frequency, disk=disk)
        self.node.info.save()

        for langName in languages:
            try:
                lang = Language.objects.get(name=langName)
            except ObjectDoesNotExist:
                lang = Language(name=langName)
                lang.save()
            self.node.info.languages.add(lang)

        self.node.info.save()

        return HttpResponse(status=200)


class SubmissionView(RESTView):
    """Get a submission to test or post the testing results."""

    template_name = "submission.xml"

    def get(self, request, *args, **kwargs):
        try:
            submission = Submission.objects.select_for_update().filter(
              status=Submission.WAITING_STATUS)[0]
        except IndexError:
            return HttpResponse(status=404)

        submission.remove_results()  # In case of rejudging
        submission.status = submission.JUDGING_STATUS
        submission.active = int(submission.contest.is_active)
        submission.node = self.node
        submission.save()

        return render_to_response(self.template_name, {
            'submission': submission,
        }, content_type='application/xml')

    def post(self, request, *args, **kwargs):
        try:
            sid = self.kwargs['submissionId']
            status = int(self.data['submission']['status'])
        except:
            return HttpResponse(status=400)

        submission = get_object_or_404(
          Submission.objects.select_for_update(), pk=sid)

        if not bool(status):
            submission.status = submission.WAITING_STATUS
            submission.save()
            return HttpResponse(status=200)

        try:
            compilelog = self.data['submission']['compilelog']
            results = self.data['submission']['results']
        except:
            return HttpResponse(status=400)

        submission.compilelog = compilelog
        submission.remove_results()

        if 'returncode' in results['result']:
            result = results['result']
            returncode = result['returncode']
            mark = bool(int(result['mark']))
            time = float(result['time'])
            res = Result(returncode=returncode, mark=mark,
                time=time, submission=submission)
            res.save()
        else:
            for result in results['result']:
                returncode = int(result['returncode'])
                mark = bool(int(result['mark']))
                time = float(result['time'])
                res = Result(returncode=returncode, mark=mark,
                    time=time, submission=submission)
                res.save()

        num_good_results = submission.results.all().filter(mark=True).count()
        num_results = submission.results.all().count()

        try:
            submission.score = int((float(num_good_results)
             / float(num_results)) * 100)
        except ZeroDivisionError:
            submission.score = 0

        submission.status = submission.JUDGED_STATUS
        submission.save()
        return HttpResponse(status=200)


class TestView(RESTView):
    """Get the tests or the test timestamp for the problem
    with the given id."""

    template_name = "test.xml"

    def get(self, request, *args, **kwargs):
        what = kwargs['type']
        problemId = kwargs['problemId']

        problem = get_object_or_404(Problem, codename=problemId)

        try:
            inpt = problem.tests.input
            out = problem.tests.output
            conf = problem.tests.config
        except ObjectDoesNotExist:
            return HttpResponse(status=404)

        if what == 'in':
            return sendfile(inpt.file.path)
        elif what == 'out':
            return sendfile(out.file.path)
        elif what == 'conf':
            return sendfile(conf.file.path)
        elif what == 'timestamp':
            return render_to_response(self.template_name, {
                'input': inpt.timestamp.strftime('%s'),
                'output': out.timestamp.strftime('%s'),
                'config': conf.timestamp.strftime('%s'),
            }, content_type='application/xml')
