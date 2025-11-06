from rest_framework.views import APIView
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework import status

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from flight.models import Airport, Route, Flight
from api.serializers.flight.serializer import (
    AirportSerializer,
    RouteSerializer,
    FlightSerializer
)

# --------------------------------------------
# AIRPORTS CRUD
# --------------------------------------------

class AirportListCreateAPI(APIView):
    permission_classes = [IsAdminUser]

    @swagger_auto_schema(
        responses={200: AirportSerializer(many=True)}
    )
    def get(self, request):
        airports = Airport.objects.all()
        serializer = AirportSerializer(airports, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        request_body=AirportSerializer,
        responses={201: AirportSerializer}
    )
    def post(self, request):
        serializer = AirportSerializer(data=request.data)
        if serializer.is_valid():
            instance = serializer.save()
            return Response(
                AirportSerializer(instance).data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AirportDetailAPI(APIView):
    permission_classes = [IsAdminUser]

    def get_object(self, pk):
        try:
            return Airport.objects.get(pk=pk)
        except Airport.DoesNotExist:
            return None

    @swagger_auto_schema(responses={200: AirportSerializer, 404: "No encontrado"})
    def get(self, request, pk):
        airport = self.get_object(pk)
        if not airport:
            return Response({"error": "Aeropuerto no encontrado"}, status=status.HTTP_404_NOT_FOUND)
        serializer = AirportSerializer(airport)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(request_body=AirportSerializer, responses={200: AirportSerializer, 404: "No encontrado"})
    def put(self, request, pk):
        airport = self.get_object(pk)
        if not airport:
            return Response({"error": "Aeropuerto no encontrado"}, status=status.HTTP_404_NOT_FOUND)

        serializer = AirportSerializer(airport, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(request_body=AirportSerializer, responses={200: AirportSerializer, 404: "No encontrado"})
    def patch(self, request, pk):
        airport = self.get_object(pk)
        if not airport:
            return Response({"error": "Aeropuerto no encontrado"}, status=status.HTTP_404_NOT_FOUND)

        serializer = AirportSerializer(airport, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(responses={204: "Eliminado", 404: "No encontrado"})
    def delete(self, request, pk):
        airport = self.get_object(pk)
        if not airport:
            return Response({"error": "Aeropuerto no encontrado"}, status=status.HTTP_404_NOT_FOUND)

        airport.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# --------------------------------------------
# ROUTES CRUD
# --------------------------------------------

class RouteListCreateAPI(APIView):
    permission_classes = [IsAdminUser]

    @swagger_auto_schema(
        responses={200: RouteSerializer(many=True)}
    )
    def get(self, request):
        routes = Route.objects.all()
        serializer = RouteSerializer(routes, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        request_body=RouteSerializer,
        responses={201: RouteSerializer}
    )
    def post(self, request):
        serializer = RouteSerializer(data=request.data)
        if serializer.is_valid():
            instance = serializer.save()
            return Response(
                RouteSerializer(instance).data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RouteDetailAPI(APIView):
    permission_classes = [IsAdminUser]

    def get_object(self, pk):
        try:
            return Route.objects.get(pk=pk)
        except Route.DoesNotExist:
            return None

    @swagger_auto_schema(responses={200: RouteSerializer, 404: "No encontrado"})
    def get(self, request, pk):
        route = self.get_object(pk)
        if not route:
            return Response({"error": "Ruta no encontrada"}, status=status.HTTP_404_NOT_FOUND)
        serializer = RouteSerializer(route)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(request_body=RouteSerializer, responses={200: RouteSerializer, 404: "No encontrado"})
    def put(self, request, pk):
        route = self.get_object(pk)
        if not route:
            return Response({"error": "Ruta no encontrada"}, status=status.HTTP_404_NOT_FOUND)

        serializer = RouteSerializer(route, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(request_body=RouteSerializer, responses={200: RouteSerializer, 404: "No encontrado"})
    def patch(self, request, pk):
        route = self.get_object(pk)
        if not route:
            return Response({"error": "Ruta no encontrada"}, status=status.HTTP_404_NOT_FOUND)

        serializer = RouteSerializer(route, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(responses={204: None, 404: "No encontrado"})
    def delete(self, request, pk):
        route = self.get_object(pk)
        if not route:
            return Response({"error": "Ruta no encontrada"}, status=status.HTTP_404_NOT_FOUND)

        route.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# --------------------------------------------
# FLIGHTS CRUD
# --------------------------------------------

class FlightListCreateAPI(APIView):
    permission_classes = [IsAdminUser]

    @swagger_auto_schema(
        responses={200: FlightSerializer(many=True)}
    )
    def get(self, request):
        flights = Flight.objects.all()
        serializer = FlightSerializer(flights, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        request_body=FlightSerializer,
        responses={201: FlightSerializer}
    )
    def post(self, request):
        serializer = FlightSerializer(data=request.data)
        if serializer.is_valid():
            instance = serializer.save()
            return Response(
                FlightSerializer(instance).data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FlightDetailAPI(APIView):
    permission_classes = [IsAdminUser]

    def get_object(self, pk):
        try:
            return Flight.objects.get(pk=pk)
        except Flight.DoesNotExist:
            return None

    @swagger_auto_schema(responses={200: FlightSerializer, 404: "No encontrado"})
    def get(self, request, pk):
        flight = self.get_object(pk)
        if not flight:
            return Response({"error": "Vuelo no encontrado"}, status=status.HTTP_404_NOT_FOUND)
        serializer = FlightSerializer(flight)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(request_body=FlightSerializer, responses={200: FlightSerializer, 404: "No encontrado"})
    def put(self, request, pk):
        flight = self.get_object(pk)
        if not flight:
            return Response({"error": "Vuelo no encontrado"}, status=status.HTTP_404_NOT_FOUND)

        serializer = FlightSerializer(flight, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(request_body=FlightSerializer, responses={200: FlightSerializer, 404: "No encontrado"})
    def patch(self, request, pk):
        flight = self.get_object(pk)
        if not flight:
            return Response({"error": "Vuelo no encontrado"}, status=status.HTTP_404_NOT_FOUND)

        serializer = FlightSerializer(flight, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(responses={204: None, 404: "No encontrado"})
    def delete(self, request, pk):
        flight = self.get_object(pk)
        if not flight:
            return Response({"error": "Vuelo no encontrado"}, status=status.HTTP_404_NOT_FOUND)

        flight.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
