"""Analytical and adversarial checks of geometry-to-candidate conversion."""
from dataclasses import replace

import numpy as np
from shapely.geometry import GeometryCollection, LineString, box

from fea.config import load_config
from fea.geometry.unit import Unit
from fea.geometry.raster import rasterize, fixed_service_doors, STORAGE_ONLY, KEEPOUT
from fea.furniture.library import library, rectangles
from fea.furniture.candidates import generate_candidates


def empty_room(width=3., depth=4.):
    room = box(0, 0, width, depth)
    return Unit("toy", "test", "test", {"furnishable": room, "storage_only": GeometryCollection(),
        "walkable_only": GeometryCollection(), "fixed_service": GeometryCollection()}, room.boundary,
        [], [], None, width*depth, 1)


def test_service_target_ignores_balcony_opening_but_keeps_interior_approach():
    """A door polygon added to circulation must not count as a room by itself."""
    room = empty_room(4, 4)
    indoor = box(1.9, 1, 2.1, 2)
    balcony = box(2.7, 3.9, 3.7, 4.1)
    room = replace(room, doors=[indoor, balcony], classes={**room.classes,
        "furnishable": box(0, 0, 2, 4), "fixed_service": box(2.1, 0, 4, 3.9),
        "walkable_only": indoor.union(balcony), "excluded": box(2.1, 4.1, 4, 5)})
    targets = fixed_service_doors(room)
    assert len(targets) == 1 and targets[0].equals(indoor)
    assert len(rasterize(room).service_targets) == 1


def test_desk_count_in_3_by_4_room_is_analytical():
    grid = rasterize(empty_room())
    desk = library(load_config("config/project.yaml")["furniture"])["desk"]
    poses = generate_candidates(grid, {"desk": desk})["desk"]
    # 1.2 m along-wall width: 19 positions on each 3 m wall and 29 on each 4 m wall.
    assert len(poses) == 2*(30-12+1)+2*(40-12+1) == 96
    x0, y0 = (int(round(-v/grid.resolution)) for v in grid.origin)
    for x, y, angle in poses:
        if angle == 0: assert y == y0
        elif angle == 90: assert x == x0+30
        elif angle == 180: assert y == y0+40
        else: assert x == x0


def test_storage_only_can_hold_storage_but_not_desk():
    room = empty_room()
    room = replace(room, classes={**room.classes, "storage_only": room.classes["furnishable"], "furnishable": GeometryCollection()})
    grid = rasterize(room)
    items = library(load_config("config/project.yaml")["furniture"])
    poses = generate_candidates(grid, {k: items[k] for k in ("desk", "wardrobe", "shelving")})
    assert np.count_nonzero(grid.labels == STORAGE_ONLY) == 1200
    assert len(poses["desk"]) == 0
    assert len(poses["wardrobe"]) > 0 and len(poses["shelving"]) > 0


def test_door_swing_excludes_bodies_and_clearances():
    door = LineString([(0, 0), (1, 0)])
    room = empty_room()
    grid = rasterize(replace(room, doors=[door], entrance=door, walls=room.walls.difference(door)))
    assert np.count_nonzero(grid.labels == KEEPOUT) == 100
    items = library(load_config("config/project.yaml")["furniture"])
    for name, poses in generate_candidates(grid, items).items():
        for x, y, angle in poses:
            for state in items[name].states:
                body, strips, _ = rectangles(state, grid.resolution, int(angle))
                for dx, dy, w, h in [body, *strips]:
                    assert not np.any(grid.labels[y+dy:y+dy+h, x+dx:x+dx+w] == KEEPOUT)


def test_tall_items_do_not_back_onto_a_full_window_wall():
    room = empty_room()
    grid = rasterize(replace(room, windows=[LineString([(0, 0), (3, 0)])]))
    wardrobe = library(load_config("config/project.yaml")["furniture"])["wardrobe"]
    poses = generate_candidates(grid, {"wardrobe": wardrobe})["wardrobe"]
    assert len(poses) > 0
    assert 0 not in poses[:, 2]


def test_shared_anchor_rejects_a_pose_when_deployed_state_does_not_fit():
    grid = rasterize(empty_room(1.8, 1.8))
    item = library(load_config("config/project.yaml")["furniture"])["wall_bed_single"]
    assert len(generate_candidates(grid, {item.name: replace(item, states=(item.states[0],))})[item.name]) > 0
    assert len(generate_candidates(grid, {item.name: item})[item.name]) == 0
