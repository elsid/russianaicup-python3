from enum import Enum
from collections import namedtuple
from itertools import islice, chain
from numpy import array
from scipy.sparse.csgraph import dijkstra
from model.TileType import TileType
from strategy_common import get_current_tile, Point


def adjust_path(path, tile_size):
    if len(path) < 2:
        return (x for x in path)

    def generate():
        typed_path = list(make_typed_path())
        for i, p in islice(enumerate(typed_path), 0, len(typed_path) - 1):
            yield adjust_path_point(p, typed_path[i + 1], tile_size)
        yield path[-1]

    def make_typed_path():
        yield TypedPoint(path[0],
                         PointType(SideType.UNKNOWN,
                                   output_type(path[0], path[1])))
        for i, p in islice(enumerate(path), 1, len(path) - 1):
            yield TypedPoint(p, point_type(path[i - 1], p, path[i + 1]))
        yield TypedPoint(path[-1],
                         PointType(input_type(path[-2], path[-1]),
                                   SideType.UNKNOWN))

    return generate()


TypedPoint = namedtuple('TypedPoint', ('position', 'type'))


def adjust_path_point(current: TypedPoint, following: TypedPoint,
                      tile_size):
    if current.type == following.type:
        return current.position
    shift = Point(0, 0)
    if current.type in {PointType.LEFT_TOP, PointType.TOP_LEFT}:
        shift = Point(- tile_size / 5, - tile_size / 5)
        if current.type.input == following.type.output:
            shift /= 2
    elif current.type in {PointType.LEFT_BOTTOM, PointType.BOTTOM_LEFT}:
        shift = Point(- tile_size / 5, + tile_size / 5)
        if current.type.input == following.type.output:
            shift /= 2
    elif current.type in {PointType.RIGHT_TOP, PointType.TOP_RIGHT}:
        shift = Point(+ tile_size / 5, - tile_size / 5)
        if current.type.input == following.type.output:
            shift /= 2
    elif current.type in {PointType.RIGHT_BOTTOM, PointType.BOTTOM_RIGHT}:
        shift = Point(+ tile_size / 5, + tile_size / 5)
        if current.type.input == following.type.output:
            shift /= 2
    elif current.type in {PointType.LEFT_RIGHT, PointType.RIGHT_LEFT}:
        if following.type.output == SideType.TOP:
            shift = Point(0, + tile_size / 5)
        else:
            shift = Point(0, - tile_size / 5)
    elif current.type in {PointType.TOP_BOTTOM, PointType.BOTTOM_TOP}:
        if following.type.output == SideType.LEFT:
            shift = Point(+ tile_size / 5, 0)
        else:
            shift = Point(- tile_size / 5, 0)
    return current.position + shift


def point_type(previous, current, following):
    return PointType(input_type(previous, current),
                     output_type(current, following))


def input_type(previous, current):
    if previous.y == current.y:
        if previous.x < current.x:
            return SideType.LEFT
        else:
            return SideType.RIGHT
    if previous.x == current.x:
        if previous.y < current.y:
            return SideType.TOP
        else:
            return SideType.BOTTOM
    return SideType.UNKNOWN


def output_type(current, following):
    if current.y == following.y:
        if current.x < following.x:
            return SideType.RIGHT
        else:
            return SideType.LEFT
    if current.x == following.x:
        if current.y < following.y:
            return SideType.BOTTOM
        else:
            return SideType.TOP
    return SideType.UNKNOWN


class SideType(Enum):
    UNKNOWN = 0
    LEFT = 1
    RIGHT = 2
    TOP = 3
    BOTTOM = 4


PointTypeImpl = namedtuple('PointType', ('input', 'output'))


class PointType(PointTypeImpl):
    LEFT_RIGHT = PointTypeImpl(SideType.LEFT, SideType.RIGHT)
    LEFT_TOP = PointTypeImpl(SideType.LEFT, SideType.TOP)
    LEFT_BOTTOM = PointTypeImpl(SideType.LEFT, SideType.BOTTOM)
    RIGHT_LEFT = PointTypeImpl(SideType.RIGHT, SideType.LEFT)
    RIGHT_TOP = PointTypeImpl(SideType.RIGHT, SideType.TOP)
    RIGHT_BOTTOM = PointTypeImpl(SideType.RIGHT, SideType.BOTTOM)
    TOP_LEFT = PointTypeImpl(SideType.TOP, SideType.LEFT)
    TOP_RIGHT = PointTypeImpl(SideType.TOP, SideType.RIGHT)
    TOP_BOTTOM = PointTypeImpl(SideType.TOP, SideType.BOTTOM)
    BOTTOM_LEFT = PointTypeImpl(SideType.BOTTOM, SideType.LEFT)
    BOTTOM_RIGHT = PointTypeImpl(SideType.BOTTOM, SideType.RIGHT)
    BOTTOM_TOP = PointTypeImpl(SideType.BOTTOM, SideType.TOP)


def reduce_diagonal_direct(path):
    return reduce_base_on_three(path, is_diagonal_direct)


def is_diagonal_direct(previous, current, following):
    to_previous = previous - current
    to_following = following - current
    return to_following.x == -to_previous.x and to_following.y == -to_previous.y


def reduce_direct_first_after_me(path):
    if len(path) < 2:
        return (x for x in path)
    following = path[0]
    after_following = path[1]
    if following.x == after_following.x or following.y == after_following.y:
        return islice(path, 1, len(path))
    return (x for x in path)


def reduce_direct(path):
    return reduce_base_on_three(path, is_direct)


def is_direct(previous, current, following):
    return (current.x == previous.x and current.x == following.x or
            current.y == previous.y and current.y == following.y)


def reduce_base_on_three(path, need_reduce):
    if not path:
        return []
    yield path[0]
    if len(path) == 1:
        return
    for i, current in islice(enumerate(path), 1, len(path) - 1):
        if not need_reduce(path[i - 1], current, path[i + 1]):
            yield current
    yield path[-1]


def shift_on_direct(path):
    if len(path) < 2:
        return (x for x in path)
    if path[0].x == path[1].x:
        last = next((i for i, p in islice(enumerate(path), 1, len(path))
                    if p.x != path[i - 1].x), len(path) - 1)
        x = path[last].x
        if x != path[0].x:
            return chain((Point(x, p.y) for p in islice(path, last)),
                         islice(path, last, len(path) - 1))
    elif path[0].y == path[1].y:
        last = next((i for i, p in islice(enumerate(path), 1, len(path))
                    if p.y != path[i - 1].y), len(path) - 1)
        y = path[last].y
        if y != path[0].y:
            return chain((Point(p.x, y) for p in islice(path, last)),
                         islice(path, last, len(path) - 1))
    return (x for x in path)


def shift_to_borders(path):
    if not path:
        return []
    for i, current in islice(enumerate(path), len(path) - 1):
        following = path[i + 1]
        direction = following - current
        yield current + direction * 0.5
    yield path[-1]


def make_tiles_path(start, position, waypoints, next_waypoint_index,
                    tile_size, tiles):
    tile = get_current_tile(position, tile_size)
    matrix = AdjacencyMatrix(tiles)
    tile_index = matrix.index(tile.x, tile.y)
    return make_path(tile_index, next_waypoint_index, matrix,
                     waypoints + [start])


def make_path(start_index, next_waypoint_index, matrix, waypoints):
    graph = array(matrix.values)
    _, predecessors = dijkstra(graph, return_predecessors=True)

    def generate():
        yield path(start_index, matrix.index(*waypoints[next_waypoint_index]))
        for i in range(next_waypoint_index, len(waypoints) - 1):
            src = matrix.index(*waypoints[i])
            dst = matrix.index(*waypoints[i + 1])
            yield path(src, dst)

    def path(src, dst):
        return reversed(list(back_path(src, dst)))

    def back_path(src, dst):
        while src != dst and dst >= 0:
            yield dst
            dst = predecessors.item(src, dst)

    yield Point(matrix.x_position(start_index), matrix.y_position(start_index))
    for v in chain.from_iterable(generate()):
        yield Point(matrix.x_position(v), matrix.y_position(v))


Node = namedtuple('Node', ('x', 'y'))


class AdjacencyMatrix:
    def __init__(self, tiles):
        column_size = len(tiles)
        self.__row_size = len(tiles[0])

        def generate():
            for x, column in enumerate(tiles):
                for y, tile in enumerate(column):
                    yield adjacency_matrix_row(Node(x, y), tile)

        def adjacency_matrix_row(node, tile):
            if tile == TileType.VERTICAL:
                return matrix_row({top(node), bottom(node)})
            elif tile == TileType.HORIZONTAL:
                return matrix_row({left(node), right(node)})
            elif tile == TileType.LEFT_TOP_CORNER:
                return matrix_row({right(node), bottom(node)})
            elif tile == TileType.RIGHT_TOP_CORNER:
                return matrix_row({left(node), bottom(node)})
            elif tile == TileType.LEFT_BOTTOM_CORNER:
                return matrix_row({right(node), top(node)})
            elif tile == TileType.RIGHT_BOTTOM_CORNER:
                return matrix_row({left(node), top(node)})
            elif tile == TileType.LEFT_HEADED_T:
                return matrix_row({left(node), top(node), bottom(node)})
            elif tile == TileType.RIGHT_HEADED_T:
                return matrix_row({right(node), top(node), bottom(node)})
            elif tile == TileType.TOP_HEADED_T:
                return matrix_row({top(node), left(node), right(node)})
            elif tile == TileType.BOTTOM_HEADED_T:
                return matrix_row({bottom(node), left(node), right(node)})
            elif tile == TileType.CROSSROADS:
                return matrix_row({left(node), right(node),
                                   top(node), bottom(node)})
            else:
                return matrix_row({})

        def matrix_row(dst):
            return [1 if x in dst else 0
                    for x in range(self.__row_size * column_size)]

        def left(node):
            return self.index(node.x - 1, node.y)

        def right(node):
            return self.index(node.x + 1, node.y)

        def top(node):
            return self.index(node.x, node.y - 1)

        def bottom(node):
            return self.index(node.x, node.y + 1)

        self.__values = list(generate())

    def index(self, x, y):
        return x * self.__row_size + y

    def x_position(self, index):
        return int(index / self.__row_size)

    def y_position(self, index):
        return index % self.__row_size

    @property
    def values(self):
        return self.__values