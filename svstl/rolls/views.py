from django.shortcuts import render
from rest_framework import generics
from .models import Roll
from .serializers import RollSerializer
from rest_framework.filters import SearchFilter
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.response import Response
from rest_framework import status
from django.http import Http404
from django.utils import timezone  # Импортируйте timezone
from django.db.models import Q
from django.utils.dateparse import parse_datetime





class RollApiV(generics.ListAPIView):
    queryset = Roll.objects.all()
    serializer_class = RollSerializer
    # filter_backends = (DjangoFilterBackend, SearchFilter)
    filter_backends = [DjangoFilterBackend] 
    filterset_fields = ['id','length','weight','date_added','date_deletion']

    @swagger_auto_schema(
    operation_description="Список рулонов",
    responses={200: RollSerializer(many=True)},
    manual_parameters=[
        openapi.Parameter('id', openapi.IN_QUERY, description="id рулона", type=openapi.TYPE_STRING),
        openapi.Parameter('length', openapi.IN_QUERY, description="длина рулона", type=openapi.TYPE_STRING),
        openapi.Parameter('weight', openapi.IN_QUERY, description="вес рулона", type=openapi.TYPE_STRING),
        openapi.Parameter('date_added', openapi.IN_QUERY, description="дата добавления рулона", type=openapi.TYPE_STRING),
        openapi.Parameter('date_deletion', openapi.IN_QUERY, description="дата удаления рулона", type=openapi.TYPE_STRING),
        # Добавьте описание для других параметров фильтрации
    ])


    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
    




class CoilListCreateView(generics.ListCreateAPIView):  # Используйте правильный базовый класс
    queryset = Roll.objects.all()
    serializer_class = RollSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['id', 'length', 'weight', 'date_added', 'date_deletion']

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        serializer = RollSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            new_roll_id = serializer.instance.id
            return Response({"id": new_roll_id}, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




class CoilDeleteView(generics.DestroyAPIView):
    queryset = Roll.objects.all()
    serializer_class = RollSerializer

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
        except Roll.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        # Установите дату удаления на текущее время
        instance.date_deletion = timezone.now()  # Используйте timezone.now()
        instance.save()

        return Response(status=status.HTTP_204_NO_CONTENT)





class CoilStatsView(generics.ListAPIView):
    queryset = Roll.objects.all()
    serializer_class = RollSerializer
    # filter_backends = (DjangoFilterBackend, SearchFilter)
    filter_backends = [DjangoFilterBackend] 
    filterset_fields = ['date_added','date_deletion']

    queryset = Roll.objects.all()
    serializer_class = RollSerializer
    filter_backends = [DjangoFilterBackend] 
    filterset_fields = ['start_date','end_date']
    def get(self, request):

        # Получение статистики по рулонам за определенный период
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')

        if not start_date or not end_date:
            raise Http404("Both start_date and end_date are required")

        # Рассчитываем статистику (подставьте свои значения для расчетов)
        stats = {
            'total_added': Roll.objects.filter(date_added__range=(start_date, end_date)).count(),
            'total_deleted': Roll.objects.filter(date_deletion__range=(start_date, end_date)).count(),
            # Добавьте остальные параметры статистики
        }

        return Response(stats)








