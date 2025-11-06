from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.core.exceptions import ValidationError
from airplane.models import Airplane
from airplane.services import airplane_service
from api.serializers.airplane.serializer import AirplaneSerializer, SeatSerializer
from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

class AirplaneAPIView(APIView):
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_summary="Listar aviones",
        operation_description="Obtiene la lista de todos los aviones disponibles",
        responses={
            200: AirplaneSerializer(many=True),
            401: "No autorizado",
            400: "Error de validación"
        },
        security=[{"Bearer": []}]
    )
    def get(self, request, pk=None):
        if pk:
            airplane = get_object_or_404(Airplane, id=pk, enabled=True)
            serializer = AirplaneSerializer(airplane)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            try:
                airplanes = airplane_service.get_all_airplanes_service()
                serializer = AirplaneSerializer(airplanes, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except ValidationError as e:
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_summary="Crear avión",
        operation_description="Crea un nuevo avión en el sistema",
        request_body=AirplaneSerializer,
        responses={
            201: AirplaneSerializer,
            400: "Datos inválidos",
            401: "No autorizado"
        },
        security=[{"Bearer": []}]
    )
    def post(self, request):
        serializer = AirplaneSerializer(data=request.data)
        if serializer.is_valid():
            try:
                airplane = airplane_service.create_airplane_service(serializer.validated_data)
                response_serializer = AirplaneSerializer(airplane)
                return Response(response_serializer.data, status=status.HTTP_201_CREATED)
            except ValidationError as e:
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_summary="Actualizar avión completo",
        operation_description="Actualiza todos los campos de un avión específico",
        request_body=AirplaneSerializer,
        responses={
            200: AirplaneSerializer,
            400: "Datos inválidos",
            401: "No autorizado",
            404: "Avión no encontrado"
        },
        security=[{"Bearer": []}]
    )
    def put(self, request, pk):
        airplane = get_object_or_404(Airplane, id=pk, enabled=True)
        serializer = AirplaneSerializer(airplane, data=request.data)
        if serializer.is_valid():
            try:
                airplane = airplane_service.update_airplane_service(pk, serializer.validated_data)
                response_serializer = AirplaneSerializer(airplane)
                return Response(response_serializer.data, status=status.HTTP_200_OK)
            except ValidationError as e:
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_summary="Actualizar avión parcial",
        operation_description="Actualiza campos específicos de un avión",
        request_body=AirplaneSerializer,
        responses={
            200: AirplaneSerializer,
            400: "Datos inválidos",
            401: "No autorizado",
            404: "Avión no encontrado"
        },
        security=[{"Bearer": []}]
    )
    def patch(self, request, pk):
        airplane = get_object_or_404(Airplane, id=pk, enabled=True)
        serializer = AirplaneSerializer(airplane, data=request.data, partial=True)
        if serializer.is_valid():
            try:
                airplane = airplane_service.update_airplane_service(pk, serializer.validated_data)
                response_serializer = AirplaneSerializer(airplane)
                return Response(response_serializer.data, status=status.HTTP_200_OK)
            except ValidationError as e:
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_summary="Eliminar avión",
        operation_description="Elimina un avión del sistema (soft delete)",
        responses={
            200: "Avión eliminado correctamente",
            401: "No autorizado",
            404: "Avión no encontrado"
        },
        security=[{"Bearer": []}]
    )
    def delete(self, request, pk):
        airplane = get_object_or_404(Airplane, id=pk)
        try:
            airplane_service.delete_airplane_service(pk)
            return Response(
                {'detail': f'Avión {airplane.model} eliminado correctamente'},
                status=status.HTTP_200_OK
            )
        except ValidationError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_summary="Obtener asientos del avión",
        operation_description="Obtiene la lista de asientos de un avión específico",
        responses={
            200: SeatSerializer(many=True),
            401: "No autorizado",
            404: "Avión no encontrado"
        },
        security=[{"Bearer": []}]
    )
    def get_seats(self, request, pk):
        try:
            seats = airplane_service.get_airplane_seats(pk)
            serializer = SeatSerializer(seats, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except ValidationError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
