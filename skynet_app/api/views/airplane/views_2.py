from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny

from api.serializers.airplane.serializer import AirplaneSerializer, SeatSerializer
from airplane.models import Airplane
from airplane.services import airplane_service
from django.core.exceptions import ValidationError


class AirplaneViewSet(viewsets.ModelViewSet):
    """
    ViewSet completo para manejar CRUD de aviones.

    - GET    /api/airplane/airplanes/          -> Lista todos los aviones
    - POST   /api/airplane/airplanes/          -> Crea un nuevo avión
    - GET    /api/airplane/airplanes/{id}/     -> Obtiene un avión específico
    - PUT    /api/airplane/airplanes/{id}/     -> Actualiza completamente un avión
    - PATCH  /api/airplane/airplanes/{id}/     -> Actualización parcial de un avión
    - DELETE /api/airplane/airplanes/{id}/     -> Elimina un avión (soft delete)
    - GET    /api/airplane/airplanes/{id}/seats/ -> Obtiene los asientos de un avión
    """
    permission_classes = [AllowAny]
    queryset = Airplane.objects.filter(enabled=True).order_by('id')
    serializer_class = AirplaneSerializer

    def perform_create(self, serializer):
        """Crea un avión"""
        try:
            airplane = airplane_service.create_airplane_service(serializer.validated_data)
            serializer.instance = airplane
        except ValidationError as e:
            raise ValidationError(str(e))

    def perform_update(self, serializer):
        """Actualiza un avión"""
        try:
            airplane = airplane_service.update_airplane_service(
                self.get_object().id, 
                serializer.validated_data
            )
            serializer.instance = airplane
        except ValidationError as e:
            raise ValidationError(str(e))

    def perform_destroy(self, instance):
        """Elimina un avión"""
        try:
            airplane_service.delete_airplane_service(instance.id)
        except ValidationError as e:
            raise ValidationError(str(e))

    def destroy(self, request, *args, **kwargs):
        """Elimina un avión y devuelve mensaje de confirmación"""
        instance = self.get_object()
        self.perform_destroy(instance=instance)
        return Response(
            {
                "detail": f'Avion {instance.model} eliminado correctamente'
            }, 
            status=status.HTTP_200_OK
        )

    @action(detail=True, methods=['get'])
    def seats(self, request, pk=None):
        """Devuelve los asientos de un avión específico"""
        try:
            seats = airplane_service.get_airplane_seats(pk)
            serializer = SeatSerializer(seats, many=True)
            return Response(serializer.data)
        except ValidationError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)