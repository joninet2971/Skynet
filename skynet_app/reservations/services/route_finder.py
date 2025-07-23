from collections import deque
from flight.models import Route, Airport
from typing import List, Optional

def find_route_chain(origin_code: str, destination_code: str) -> Optional[List[Route]]:
    visited = set()
    queue = deque()
    paths = {}

    queue.append(origin_code)
    paths[origin_code] = []

    while queue:
        current_code = queue.popleft()
        if current_code == destination_code:
            return paths[current_code]  # lista de rutas (objetos Route)

        visited.add(current_code)

        # Todas las rutas que salen desde este aeropuerto
        current_routes = Route.objects.select_related('origin_airport', 'destination_airport').filter(
            origin_airport__code=current_code
        )

        for route in current_routes:
            dest_code = route.destination_airport.code
            if dest_code not in visited and dest_code not in queue:
                queue.append(dest_code)
                paths[dest_code] = paths[current_code] + [route]

    return None  # No hay camino
