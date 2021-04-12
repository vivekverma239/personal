# from core.models import *
# from rest_framework import serializers

# class ConstantSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Constant
#         fields = '__all__'

# class StockDataSerializer(serializers.ModelSerializer):
#     time = serializers.SerializerMethodField()
#     class Meta:
#         model = StockData
#         fields = '__all__'

#     def get_time(self, obj):
#         return int(obj.datetime.strftime('%s'))


# class StrategySignalSerializer(serializers.ModelSerializer):
#     time = serializers.SerializerMethodField()

#     class Meta:
#         model = StrategySignal
#         fields = ['res', 'time', 'datetime', 'score']

#     def get_time(self, obj):
#         return int(obj.datetime.strftime('%s'))

# class SearchFileSerializer(serializers.ModelSerializer):

#     class Meta:
#         model = SearchFile
#         fields = "__all__"