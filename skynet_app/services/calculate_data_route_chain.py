from typing import List, Dict, Any
from decimal import Decimal

def calc_route_chain(
    route_chains_ids: List[List[int]],
    route_manager,   # Route.objects
    flight_manager   # Flight.objects
) -> Dict[str, Any]:
    
    itineraries: List[Dict[str, Any]] = []

    for idx, chain_ids in enumerate(route_chains_ids, start=1):
        if not chain_ids:
            continue

        # 1) Traer rutas (no preserva orden)
        routes_qs = (
            route_manager
            .filter(id__in=chain_ids)
            .select_related("origin_airport", "destination_airport")
        )
        # Guardia: si no hay rutas, saltar
        if not routes_qs.exists():
            continue

        # 2) Reordenar según chain_ids (forma “tradicional”)
        route_map = {}
        for r in routes_qs:
            route_map[r.id] = r

        ordered_routes = []
        for rid in chain_ids:
            if rid in route_map:
                ordered_routes.append(route_map[rid])

        # Guardia: si no se pudo reconstruir el orden, saltar
        if not ordered_routes:
            continue

        # 3) Resumen (códigos IATA)
        codes = [r.origin_airport.code for r in ordered_routes]
        codes.append(ordered_routes[-1].destination_airport.code)
        route_summary = " → ".join(codes)

        # 4) Vuelos asociados y sumas
        flights_qs = (
            flight_manager
            .filter(route_id__in=chain_ids)
            .select_related("route")
        )

        duration = 0
        total_price = Decimal(0)  

        for f in flights_qs:
            # Ajustá estos campos a tus modelos reales si difieren
            duration += getattr(getattr(f, "route", None), "estimated_duration", 0) or 0

            price = getattr(f, "base_price", None)
            if price is None:
                price = Decimal(0)
            elif not isinstance(price, Decimal):
                price = Decimal(str(price))
            total_price += price

        itineraries.append({
            "id": idx,
            "route_summary": route_summary,
            "duration": int(duration or 0),
            "total_price": str(total_price),  # <-- seguro para JSON (evitás binarios)
            "route_ids": chain_ids,
        })

    origin = itineraries[0]["route_summary"].split(" → ")[0] if itineraries else None
    destination = itineraries[0]["route_summary"].split(" → ")[-1] if itineraries else None

    return {
        "itineraries": itineraries,
        "origin": origin,
        "destination": destination,
        "route_options": route_chains_ids,
    }
