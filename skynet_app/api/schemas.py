from drf_yasg import openapi

# Esquemas de respuesta personalizados para Swagger
airplane_response_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'id': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID único del avión'),
        'model': openapi.Schema(type=openapi.TYPE_STRING, description='Modelo del avión'),
        'enabled': openapi.Schema(type=openapi.TYPE_BOOLEAN, description='Estado del avión'),
        'seats': openapi.Schema(
            type=openapi.TYPE_ARRAY,
            items=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                    'column': openapi.Schema(type=openapi.TYPE_STRING),
                    'row': openapi.Schema(type=openapi.TYPE_INTEGER),
                    'is_available': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                }
            ),
            description='Lista de asientos del avión'
        )
    }
)

error_response_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'error': openapi.Schema(type=openapi.TYPE_STRING, description='Mensaje de error'),
        'detail': openapi.Schema(type=openapi.TYPE_STRING, description='Detalle del error')
    }
)

# Esquemas de autenticación
auth_scheme = openapi.SecurityScheme(
    type=openapi.TYPE_HTTP,
    scheme='bearer',
    bearer_format='JWT',
    description='Token JWT obtenido del endpoint /api/token/'
)

security_definitions = {
    'Bearer': auth_scheme
}
