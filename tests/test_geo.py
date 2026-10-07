from buska_core.geo import haversine_distance_meters


def test_same_point_is_zero_distance():
    assert haversine_distance_meters(-7.115, -34.861, -7.115, -34.861) == 0


def test_known_distance_joao_pessoa_to_campina_grande():
    # ~120km apart in a straight line; assert within a loose tolerance
    # rather than pinning an exact float.
    distance = haversine_distance_meters(-7.115, -34.861, -7.230, -35.881)
    assert 110_000 < distance < 130_000


def test_accepts_string_coordinates():
    # Callers sometimes pass Decimal/str lat-lon straight from a DB row.
    distance = haversine_distance_meters("-7.115", "-34.861", "-7.115", "-34.861")
    assert distance == 0
