from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from api.serializers.airplane.serializer import AirplaneSerializer
from airplane.models import Airplane
from airplane.services import airplane_service
from django.core.exceptions import ValidationError


class AirplaneViewSet(viewsets.ViewSet):
    """
    API ViewSet para manejar CRUD de aviones.
    Usa los servicios existentes del módulo airplane.
    """

    def list(self, request):
        airplanes = airplane_service.get_all_airplanes_service()
        serializer = AirplaneSerializer(airplanes, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        airplane = airplane_service.get_airplane(pk)
        serializer = AirplaneSerializer(airplane)
        return Response(serializer.data)

    def create(self, request):
        serializer = AirplaneSerializer(data=request.data)
        if serializer.is_valid():
            try:
                airplane_service.create_airplane_service(serializer.validated_data)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            except ValidationError as e:
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        serializer = AirplaneSerializer(data=request.data)
        if serializer.is_valid():
            try:
                airplane_service.update_airplane_service(pk, serializer.validated_data)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except ValidationError as e:
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        try:
            airplane_service.delete_airplane_service(pk)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except ValidationError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'])
    def seats(self, request, pk=None):
        """Devuelve los asientos del avión"""
        seats = airplane_service.get_airplane_seats(pk)
        serializer = AirplaneSerializer(seats, many=True)
        return Response(serializer.data)
