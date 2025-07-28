from collections import deque
from flight.models import Route
from typing import List, Optional

def find_route_chain(origin_code: str, destination_code: str) -> Optional[List[List[Route]]]:
    queue = deque()
    all_paths = []

    queue.append((origin_code, []))  # origen y ruta acumulada

    while queue:
        current_code, current_path = queue.popleft()

        # Si llegamos al destino, guardamos el camino completo
        if current_code == destination_code:
            all_paths.append(current_path)
            continue  # ¡No cortamos! Queremos seguir buscando más rutas

        # Buscamos todas las rutas que salen desde el aeropuerto actual
        current_routes = Route.objects.select_related('origin_airport', 'destination_airport').filter(
            origin_airport__code=current_code
        )

        for route in current_routes:
            next_code = route.destination_airport.code

            # Prevenimos ciclos: no volver a pasar por el mismo aeropuerto del camino actual
            if next_code in [r.origin_airport.code for r in current_path] or \
               next_code in [r.destination_airport.code for r in current_path]:
                continue

            queue.append((next_code, current_path + [route]))

    return all_paths if all_paths else None

