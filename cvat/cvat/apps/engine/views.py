# Copyright (C) 2018 Intel Corporation
#
# SPDX-License-Identifier: MIT

import os
import re
import traceback
from ast import literal_eval
import shutil
from datetime import datetime

from django.http import HttpResponseBadRequest
from django.shortcuts import redirect, render
from django.conf import settings
from sendfile import sendfile
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer
from rest_framework import status
from rest_framework import viewsets
from rest_framework import serializers
from rest_framework.decorators import action
from rest_framework import mixins
from django_filters import rest_framework as filters
import django_rq
from django.db import IntegrityError


from . import annotation, task, models
from cvat.settings.base import JS_3RDPARTY, CSS_3RDPARTY
from cvat.apps.authentication.decorators import login_required
import logging
from .log import slogger, clogger
from cvat.apps.engine.models import StatusChoice, Task, Job, Plugin
from cvat.apps.engine.serializers import (TaskSerializer, UserSerializer,
   ExceptionSerializer, AboutSerializer, JobSerializer, ImageMetaSerializer,
   RqStatusSerializer, TaskDataSerializer, LabeledDataSerializer,
   PluginSerializer, FileInfoSerializer, LogEventSerializer)
from django.contrib.auth.models import User
from cvat.apps.authentication import auth
from rest_framework.permissions import SAFE_METHODS

# Server REST API
@login_required
def dispatch_request(request):
    """An entry point to dispatch legacy requests"""
    if request.method == 'GET' and 'id' in request.GET:
        return render(request, 'engine/annotation.html', {
            'css_3rdparty': CSS_3RDPARTY.get('engine', []),
            'js_3rdparty': JS_3RDPARTY.get('engine', []),
            'status_list': [str(i) for i in StatusChoice]
        })
    else:
        return redirect('/dashboard/')

class ServerViewSet(viewsets.ViewSet):
    serializer_class = None

    # To get nice documentation about ServerViewSet actions it is necessary
    # to implement the method. By default, ViewSet doesn't provide it.
    def get_serializer(self, *args, **kwargs):
        pass

    @staticmethod
    @action(detail=False, methods=['GET'], serializer_class=AboutSerializer)
    def about(request):
        from cvat import __version__ as cvat_version
        about = {
            "name": "Computer Vision Annotation Tool",
            "version": cvat_version,
            "description": "CVAT is completely re-designed and re-implemented " +
                "version of Video Annotation Tool from Irvine, California " +
                "tool. It is free, online, interactive video and image annotation " +
                "tool for computer vision. It is being used by our team to " +
                "annotate million of objects with different properties. Many UI " +
                "and UX decisions are based on feedbacks from professional data " +
                "annotation team."
        }
        serializer = AboutSerializer(data=about)
        if serializer.is_valid(raise_exception=True):
            return Response(data=serializer.data)

    @staticmethod
    @action(detail=False, methods=['POST'], serializer_class=ExceptionSerializer)
    def exception(request):
        serializer = ExceptionSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            additional_info = {
                "username": request.user.username,
                "name": "Send exception",
            }
            message = JSONRenderer().render({**serializer.data, **additional_info}).decode('UTF-8')
            jid = serializer.data.get("job_id")
            tid = serializer.data.get("task_id")
            if jid:
                clogger.job[jid].error(message)
            elif tid:
                clogger.task[tid].error(message)
            else:
                clogger.glob.error(message)

            return Response(serializer.data, status=status.HTTP_201_CREATED)

    @staticmethod
    @action(detail=False, methods=['POST'], serializer_class=LogEventSerializer)
    def logs(request):
        serializer = LogEventSerializer(many=True, data=request.data)
        if serializer.is_valid(raise_exception=True):
            user = { "username": request.user.username }
            for event in serializer.data:
                message = JSONRenderer().render({**event, **user}).decode('UTF-8')
                jid = event.get("job_id")
                tid = event.get("task_id")
                if jid:
                    clogger.job[jid].info(message)
                elif tid:
                    clogger.task[tid].info(message)
                else:
                    clogger.glob.info(message)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

    @staticmethod
    @action(detail=False, methods=['GET'], serializer_class=FileInfoSerializer)
    def share(request):
        param = request.query_params.get('directory', '/')
        if param.startswith("/"):
            param = param[1:]
        directory = os.path.abspath(os.path.join(settings.SHARE_ROOT, param))

        if directory.startswith(settings.SHARE_ROOT) and os.path.isdir(directory):
            data = []
            content = os.scandir(directory)
            for entry in content:
                entry_type = None
                if entry.is_file():
                    entry_type = "REG"
                elif entry.is_dir():
                    entry_type = "DIR"

                if entry_type:
                    data.append({"name": entry.name, "type": entry_type})

            serializer = FileInfoSerializer(many=True, data=data)
            if serializer.is_valid(raise_exception=True):
                return Response(serializer.data)
        else:
            return Response("{} is an invalid directory".format(param),
                status=status.HTTP_400_BAD_REQUEST)

class TaskFilter(filters.FilterSet):
    name = filters.CharFilter(field_name="name", lookup_expr="icontains")
    owner = filters.CharFilter(field_name="owner__username", lookup_expr="icontains")
    mode = filters.CharFilter(field_name="mode", lookup_expr="icontains")
    status = filters.CharFilter(field_name="status", lookup_expr="icontains")
    assignee = filters.CharFilter(field_name="assignee__username", lookup_expr="icontains")

    class Meta:
        model = Task
        fields = ("id", "name", "owner", "mode", "status", "assignee")

class TaskViewSet(auth.TaskGetQuerySetMixin, viewsets.ModelViewSet):
    queryset = Task.objects.all().prefetch_related(
            "label_set__attributespec_set",
            "segment_set__job_set",
        ).order_by('-id')
    serializer_class = TaskSerializer
    search_fields = ("name", "owner__username", "mode", "status")
    filterset_class = TaskFilter
    ordering_fields = ("id", "name", "owner", "status", "assignee")

    def get_permissions(self):
        http_method = self.request.method
        permissions = [IsAuthenticated]

        if http_method in SAFE_METHODS:
            permissions.append(auth.TaskAccessPermission)
        elif http_method in ["POST"]:
            permissions.append(auth.TaskCreatePermission)
        elif http_method in ["PATCH", "PUT"]:
            permissions.append(auth.TaskChangePermission)
        elif http_method in ["DELETE"]:
            permissions.append(auth.TaskDeletePermission)
        else:
            permissions.append(auth.AdminRolePermission)

        return [perm() for perm in permissions]

    def perform_create(self, serializer):
        if self.request.data.get('owner', None):
            serializer.save()
        else:
            serializer.save(owner=self.request.user)

    def perform_destroy(self, instance):
        task_dirname = instance.get_task_dirname()
        super().perform_destroy(instance)
        shutil.rmtree(task_dirname, ignore_errors=True)

    @staticmethod
    @action(detail=True, methods=['GET'], serializer_class=JobSerializer)
    def jobs(request, pk):
        queryset = Job.objects.filter(segment__task_id=pk)
        serializer = JobSerializer(queryset, many=True,
            context={"request": request})

        return Response(serializer.data)

    @action(detail=True, methods=['POST'], serializer_class=TaskDataSerializer)
    def data(self, request, pk):
        db_task = self.get_object()
        serializer = TaskDataSerializer(db_task, data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            task.create(db_task.id, serializer.data)
            return Response(serializer.data, status=status.HTTP_202_ACCEPTED)

    @action(detail=True, methods=['GET', 'DELETE', 'PUT', 'PATCH'],
        serializer_class=LabeledDataSerializer)
    def annotations(self, request, pk):
        if request.method == 'GET':
            data = annotation.get_task_data(pk, request.user)
            serializer = LabeledDataSerializer(data=data)
            if serializer.is_valid(raise_exception=True):
                return Response(serializer.data)
        elif request.method == 'PUT':
            serializer = LabeledDataSerializer(data=request.data)
            if serializer.is_valid(raise_exception=True):
                data = annotation.put_task_data(pk, request.user, serializer.data)
                return Response(data)
        elif request.method == 'DELETE':
            annotation.delete_task_data(pk, request.user)
            return Response(status=status.HTTP_204_NO_CONTENT)
        elif request.method == 'PATCH':
            action = self.request.query_params.get("action", None)
            if action not in annotation.PatchAction.values():
                raise serializers.ValidationError(
                    "Please specify a correct 'action' for the request")
            serializer = LabeledDataSerializer(data=request.data)
            if serializer.is_valid(raise_exception=True):
                try:
                    data = annotation.patch_task_data(pk, request.user, serializer.data, action)
                except (AttributeError, IntegrityError) as e:
                    return Response(data=str(e), status=status.HTTP_400_BAD_REQUEST)
                return Response(data)

    @action(detail=True, methods=['GET'], serializer_class=None,
        url_path='annotations/(?P<filename>[^/]+)')
    def dump(self, request, pk, filename):
        filename = re.sub(r'[\\/*?:"<>|]', '_', filename)
        queue = django_rq.get_queue("default")
        username = request.user.username
        db_task = self.get_object()
        timestamp = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
        file_ext = request.query_params.get("format", "xml")
        action = request.query_params.get("action")
        if action not in [None, "download"]:
            raise serializers.ValidationError(
                "Please specify a correct 'action' for the request")

        file_path = os.path.join(db_task.get_task_dirname(),
            filename + ".{}.{}.".format(username, timestamp) + "xml")

        rq_id = "{}@/api/v1/tasks/{}/annotations/{}".format(username, pk, filename)
        rq_job = queue.fetch_job(rq_id)

        if rq_job:
            if rq_job.is_finished:
                if not rq_job.meta.get("download"):
                    if action == "download":
                        rq_job.meta[action] = True
                        rq_job.save_meta()
                        return sendfile(request, rq_job.meta["file_path"], attachment=True,
                            attachment_filename=filename + "." + file_ext)
                    else:
                        return Response(status=status.HTTP_201_CREATED)
                else: # Remove the old dump file
                    try:
                        os.remove(rq_job.meta["file_path"])
                    except OSError:
                        pass
                    finally:
                        rq_job.delete()
            elif rq_job.is_failed:
                rq_job.delete()
                return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            else:
                return Response(status=status.HTTP_202_ACCEPTED)

        rq_job = queue.enqueue_call(func=annotation.dump_task_data,
            args=(pk, request.user, file_path, request.scheme,
                request.get_host(), request.query_params),
            job_id=rq_id)
        rq_job.meta["file_path"] = file_path
        rq_job.save_meta()

        return Response(status=status.HTTP_202_ACCEPTED)

    @action(detail=True, methods=['GET'], serializer_class=RqStatusSerializer)
    def status(self, request, pk):
        response = self._get_rq_response(queue="default",
            job_id="/api/{}/tasks/{}".format(request.version, pk))
        serializer = RqStatusSerializer(data=response)

        if serializer.is_valid(raise_exception=True):
            return Response(serializer.data)

    @staticmethod
    def _get_rq_response(queue, job_id):
        queue = django_rq.get_queue(queue)
        job = queue.fetch_job(job_id)
        response = {}
        if job is None or job.is_finished:
            response = { "state": "Finished" }
        elif job.is_queued:
            response = { "state": "Queued" }
        elif job.is_failed:
            response = { "state": "Failed", "message": job.exc_info }
        else:
            response = { "state": "Started" }
            if 'status' in job.meta:
                response['message'] = job.meta['status']

        return response

    @staticmethod
    @action(detail=True, methods=['GET'], serializer_class=ImageMetaSerializer,
        url_path='frames/meta')
    def data_info(request, pk):
        try:
            db_task = models.Task.objects.get(pk=pk)
            meta_cache_file = open(db_task.get_image_meta_cache_path())
        except OSError:
            task.make_image_meta_cache(db_task)
            meta_cache_file = open(db_task.get_image_meta_cache_path())

        data = literal_eval(meta_cache_file.read())
        serializer = ImageMetaSerializer(many=True, data=data['original_size'])
        if serializer.is_valid(raise_exception=True):
            return Response(serializer.data)

    @action(detail=True, methods=['GET'], serializer_class=None,
        url_path='frames/(?P<frame>\d+)')
    def frame(self, request, pk, frame):
        """Get a frame for the task"""

        try:
            # Follow symbol links if the frame is a link on a real image otherwise
            # mimetype detection inside sendfile will work incorrectly.
            db_task = self.get_object()
            path = os.path.realpath(db_task.get_frame_path(frame))
            return sendfile(request, path)
        except Exception as e:
            slogger.task[pk].error(
                "cannot get frame #{}".format(frame), exc_info=True)
            return HttpResponseBadRequest(str(e))

class JobViewSet(viewsets.GenericViewSet,
    mixins.RetrieveModelMixin, mixins.UpdateModelMixin):
    queryset = Job.objects.all().order_by('id')
    serializer_class = JobSerializer

    def get_permissions(self):
        http_method = self.request.method
        permissions = [IsAuthenticated]

        if http_method in SAFE_METHODS:
            permissions.append(auth.JobAccessPermission)
        elif http_method in ["PATCH", "PUT", "DELETE"]:
            permissions.append(auth.JobChangePermission)
        else:
            permissions.append(auth.AdminRolePermission)

        return [perm() for perm in permissions]


    @action(detail=True, methods=['GET', 'DELETE', 'PUT', 'PATCH'],
        serializer_class=LabeledDataSerializer)
    def annotations(self, request, pk):
        if request.method == 'GET':
            data = annotation.get_job_data(pk, request.user)
            return Response(data)
        elif request.method == 'PUT':
            serializer = LabeledDataSerializer(data=request.data)
            if serializer.is_valid(raise_exception=True):
                try:
                    data = annotation.put_job_data(pk, request.user, serializer.data)
                except (AttributeError, IntegrityError) as e:
                    return Response(data=str(e), status=status.HTTP_400_BAD_REQUEST)
                return Response(data)
        elif request.method == 'DELETE':
            annotation.delete_job_data(pk, request.user)
            return Response(status=status.HTTP_204_NO_CONTENT)
        elif request.method == 'PATCH':
            action = self.request.query_params.get("action", None)
            if action not in annotation.PatchAction.values():
                raise serializers.ValidationError(
                    "Please specify a correct 'action' for the request")
            serializer = LabeledDataSerializer(data=request.data)
            if serializer.is_valid(raise_exception=True):
                try:
                    data = annotation.patch_job_data(pk, request.user,
                        serializer.data, action)
                except (AttributeError, IntegrityError) as e:
                    return Response(data=str(e), status=status.HTTP_400_BAD_REQUEST)
                return Response(data)


class UserViewSet(viewsets.GenericViewSet, mixins.ListModelMixin,
    mixins.RetrieveModelMixin, mixins.UpdateModelMixin):
    queryset = User.objects.all().order_by('id')
    serializer_class = UserSerializer

    def get_permissions(self):
        permissions = [IsAuthenticated]

        if self.action in ["self"]:
            pass
        else:
            user = self.request.user
            if self.action != "retrieve" or int(self.kwargs.get("pk", 0)) != user.id:
                permissions.append(auth.AdminRolePermission)

        return [perm() for perm in permissions]

    @staticmethod
    @action(detail=False, methods=['GET'], serializer_class=UserSerializer)
    def self(request):
        serializer = UserSerializer(request.user, context={ "request": request })
        return Response(serializer.data)

class PluginViewSet(viewsets.ModelViewSet):
    queryset = Plugin.objects.all()
    serializer_class = PluginSerializer

    # @action(detail=True, methods=['GET', 'PATCH', 'PUT'], serializer_class=None)
    # def config(self, request, name):
    #     pass

    # @action(detail=True, methods=['GET', 'POST'], serializer_class=None)
    # def data(self, request, name):
    #     pass

    # @action(detail=True, methods=['GET', 'DELETE', 'PATCH', 'PUT'],
    #     serializer_class=None, url_path='data/(?P<id>\d+)')
    # def data_detail(self, request, name, id):
    #     pass


    @action(detail=True, methods=['GET', 'POST'], serializer_class=RqStatusSerializer)
    def requests(self, request, name):
        pass

    @action(detail=True, methods=['GET', 'DELETE'],
        serializer_class=RqStatusSerializer, url_path='requests/(?P<id>\d+)')
    def request_detail(self, request, name, rq_id):
        pass

def rq_handler(job, exc_type, exc_value, tb):
    job.exc_info = "".join(
        traceback.format_exception_only(exc_type, exc_value))
    job.save()
    if "tasks" in job.id.split("/"):
        return task.rq_handler(job, exc_type, exc_value, tb)

    return True
