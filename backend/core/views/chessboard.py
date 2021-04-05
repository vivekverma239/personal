from django.shortcuts import render
import os
import json 
import requests
from uuid import UUID
import re

import pandas as pd 
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import viewsets, renderers, views
from rest_framework import filters , status
from rest_framework.response import Response as RestResponse
from django.http import HttpResponse
from rest_framework.parsers import FileUploadParser
from django.http import FileResponse
from core.projects.chessboard.app import recognize_board
from rest_framework.decorators import action

class PassthroughRenderer(renderers.BaseRenderer):
    """
        Return data as-is. View should supply a Response.
    """
    media_type = ''
    format = ''
    def render(self, data, accepted_media_type=None, renderer_context=None):
        return data


class ChessBoardViewSet(views.APIView):
    """
    """
    # permission_classes = (IsAuthenticated,)
    permission_classes = (AllowAny,)
    parser_class = (FileUploadParser,)
    basename = 'chessboard'

    def __init__(self, **kwargs):
        # Required to identify in permission module 
        super().__init__(**kwargs)

    def post(self, request, **kwargs): 
        random = request.data.get("random")
        if random: 
            file_name = None
        else:
            file = request.FILES['file']
            file_name = "./media/{}".format(file.name)
            with open(file_name, "wb+") as file_: 
                for chunk in file.chunks():
                    file_.write(chunk)
        res = recognize_board(file_name)
        return RestResponse(res)

class ChessImageViewSet(views.APIView):
    """
    """
    # permission_classes = (IsAuthenticated,)
    permission_classes = (AllowAny,)

    def __init__(self, **kwargs):
        # Required to identify in permission module 
        super().__init__(**kwargs)

    def get(self, request, **kwargs): 
        file = self.request.query_params['file']
        file = open(file, "rb")
        # send file
        response = HttpResponse(file.read(), content_type='whatever')
        response['Content-Disposition'] = 'attachment; filename="%s"' % file.name

        return response

    # @action(methods=['get'], detail=False, renderer_classes=(PassthroughRenderer,))
    # def download(self,  **kwargs):
