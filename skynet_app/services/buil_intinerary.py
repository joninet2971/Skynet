import uuid

def build_itinerary_options(route_chains, route_qs, flight_qs):
    """
    route_chains: iterable de cadenas, p.ej [[12], [4,7], [5,9,11]] (IDs de Route)
    Devuelve lista de dicts serializables con un ID estable por opción.
    """
    # Asegurar listas (no tuplas)
    chains = [list(chain) for chain in route_chains]

    options = []
    for idx, chain in enumerate(chains, start=1):
        # podés enriquecer cada segmento con datos del vuelo
        segments = []
        for route_id in chain:
            r = route_qs.get(pk=route_id)
            f = flight_qs.get(route=r)  # ajustá si tu relación es distinta
            segments.append({
                "route_id": r.id,
                "flight_id": f.id,
                "origin": r.origin.code,
                "destination": r.destination.code,
                "departure": f.departure_time.isoformat(),
                "arrival": f.arrival_time.isoformat(),
            })
        options.append({
            "itinerary_id": idx,      # o str(uuid.uuid4())
            "segments": segments,
            # podés sumar precio, duraciones, etc.
        })
    return options
