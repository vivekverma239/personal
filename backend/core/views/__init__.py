from django.shortcuts import render
import os
import json 
import requests
from uuid import UUID
import re

import pandas as pd 
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import viewsets, renderers
from rest_framework import filters , status
from rest_framework.response import Response as RestResponse
from django.http import HttpResponse
from django.forms import model_to_dict 
from django.contrib.auth.models import User
from django.db.models import Q
from rest_framework.parsers import FileUploadParser
from django.db import transaction
from django.http import FileResponse

from core.models import * 
from core.serializers import *
from core.es import search_files, search_sections
from core.search import extract_answer, search_classifier
from .chessboard import ChessBoardViewSet, ChessImageViewSet

class ConstantViewSet(viewsets.ModelViewSet):
    """
    """
    pagination_class = None
    queryset = Constant.objects.all().order_by('name')
    serializer_class = ConstantSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['key']

    def __init__(self, **kwargs):
        # Required to identify in permission module 
        super().__init__(**kwargs)
        self.name = "constant"

    def get_queryset(self):
        queryset = Constant.objects.all().order_by('-createdAt')
        key = self.request.query_params.get("key")
        if key :
            queryset = queryset.filter(key=key)
        return queryset


class StockDataViewSet(viewsets.ModelViewSet):
    """
    """
    pagination_class = None
    queryset = StockData.objects.all().order_by('-createdAt')
    serializer_class = StockDataSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['stock_symbol']

    def __init__(self, **kwargs):
        # Required to identify in permission module 
        super().__init__(**kwargs)
        self.name = "stock_data"

    def get_queryset(self):
        queryset = StockData.objects.all().order_by('-createdAt')
        stock = self.request.query_params.get("stock")
        res = self.request.query_params.get("res", '1d').lower()
        queryset = queryset.filter(res=res)
        if stock :
            queryset = queryset.filter(stock_symbol=stock)
        return queryset


class StrategyViewSet(viewsets.ModelViewSet):
    """
    """
    pagination_class = None
    queryset = StrategySignal.objects.all().order_by('name')
    serializer_class = StrategySignalSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']

    def __init__(self, **kwargs):
        # Required to identify in permission module 
        super().__init__(**kwargs)
        self.name = "project"

    def get_queryset(self):
        queryset = StrategySignal.objects.all().order_by('-createdAt')
        stock = self.request.query_params.get("stock")
        res = self.request.query_params.get("res", '1d').lower()
        queryset = queryset.filter(res=res)
        if stock :
            queryset = queryset.filter(stock_symbol=stock)
        return queryset


class PassthroughRenderer(renderers.BaseRenderer):
    """
        Return data as-is. View should supply a Response.
    """
    media_type = ''
    format = ''
    def render(self, data, accepted_media_type=None, renderer_context=None):
        return data


class SearchFileViewSet(viewsets.ModelViewSet):
    """
    """
    # permission_classes = (IsAuthenticated,)
    permission_classes = (AllowAny,)
    parser_class = (FileUploadParser,)
    queryset = SearchFile.objects.all().order_by('-createdAt')
    serializer_class = SearchFileSerializer

    filter_backends = [filters.SearchFilter]
    search_fields = ['name']

    def __init__(self, **kwargs):
        # Required to identify in permission module 
        super().__init__(**kwargs)
        self.name = "maintenance_message"

    def get_queryset(self):
        queryset = SearchFile.objects.all().order_by('-createdAt')
        project_id =  self.request.query_params.get("project_id")
        if project_id:
            queryset = queryset.filter(metadata__project_id=project_id)
        return queryset

    def update(self, *args,  **kwargs):
        res = super().update(*args, **kwargs)
        instance = self.get_object()
        return res

    def create(self, *args, **kwargs): 
        print(args[0].data)
        res = super().create(*args, **kwargs)
        return res

    @action(methods=['get'], detail=True, renderer_classes=(PassthroughRenderer,))
    def download(self, *args, **kwargs):
        instance = self.get_object()

        # get an open file handle (I'm just using a file attached to the model for this example):
        file_handle = instance.file.open()

        # send file
        response = FileResponse(file_handle, content_type='whatever')
        response['Content-Length'] = instance.file.size
        response['Content-Disposition'] = 'attachment; filename="%s"' % instance.file.name

        return response


class SearchFileMethod(viewsets.ViewSet):

    def retrieve(self, request):
        query = request.query_params.get("query")
        project_id = request.query_params.get("project_id")
        results = search_files(query, {"project_id": project_id})
        results = search_sections(query=query, params={"project_id": "f6da25c7-8275-4b2c-bbab-cc4f8ec5e029"})
        responses = [i['_source']['text'] for i in results]
        scores = search_classifier(query, responses)
        for idx, response in enumerate(responses): 
            results[idx]['ml_score'] = scores[idx]
        return RestResponse(results, status=status.HTTP_200_OK)

    def retrieve_section(self, request):
        query = request.query_params.get("query")
        project_id = request.query_params.get("project_id")
        results = search_sections(query, {"project_id": project_id})
        responses = [i['_source']['text'] for i in results]
        scores = search_classifier(query, responses)
        for idx, response in enumerate(responses): 
            results[idx]['ml_score'] = scores[idx]
        return RestResponse(results, status=status.HTTP_200_OK)

    def highlight(self, request):
        query = request.query_params.get("query")
        file_id = request.query_params.get("file_id")
        page = request.query_params.get("page")
        file = SearchFile.objects.get(id=file_id)
        answers = file.parsed_data['pages'][page]
        results = extract_answer(query, answers)
        return RestResponse(results, status=status.HTTP_200_OK)
