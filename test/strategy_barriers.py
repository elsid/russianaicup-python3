from unittest import TestCase
from hamcrest import assert_that, equal_to
from model.TileType import TileType
from strategy_barriers import (
    Rectangle,
    Circle,
    make_tile_barriers
)
from strategy_common import Point, Line


class CircleTest(TestCase):
    def test_intersection_with_line_begins_from_circle_position_returns_one_point(self):
        circle = Circle(Point(0, 0), 1)
        line = Line(begin=Point(0, 0), end=Point(2, 0))
        result = circle.intersection_with_line(line)
        assert_that(result, equal_to([Point(1, 0)]))

    def test_intersection_with_line_cross_circle_position_returns_two_points(self):
        circle = Circle(Point(0, 0), 1)
        line = Line(begin=Point(-2, 0), end=Point(2, 0))
        result = circle.intersection_with_line(line)
        assert_that(result, equal_to([Point(-1, 0), Point(1, 0)]))

    def test_intersection_with_line_inside_circle_returns_empty(self):
        circle = Circle(Point(0, 0), 2)
        line = Line(begin=Point(-1, 0), end=Point(1, 0))
        result = circle.intersection_with_line(line)
        assert_that(result, equal_to([]))

    def test_intersection_with_circle_chord_returns_two_points(self):
        circle = Circle(Point(0, 0), 2)
        line = Line(begin=Point(-2, 1), end=Point(2, 1))
        result = circle.intersection_with_line(line)
        assert_that(len(result), equal_to(2))

    def test_intersection_with_circle_tangent_returns_one_points(self):
        circle = Circle(Point(0, 0), 1)
        line = Line(begin=Point(-1, 1), end=Point(1, 1))
        result = circle.intersection_with_line(line)
        assert_that(result, equal_to([Point(0, 1)]))


class RectangleTest(TestCase):
    def test_point_code_inside_returns_inside(self):
        border = Rectangle(left_top=Point(-1, -1), right_bottom=Point(1, 1))
        result = border.point_code(Point(0, 0))
        assert_that(result, equal_to(Rectangle.INSIDE))

    def test_point_code_at_left_returns_left(self):
        border = Rectangle(left_top=Point(-1, -1), right_bottom=Point(1, 1))
        result = border.point_code(Point(-2, 0))
        assert_that(result, equal_to(Rectangle.LEFT))

    def test_point_code_at_right_returns_right(self):
        border = Rectangle(left_top=Point(-1, -1), right_bottom=Point(1, 1))
        result = border.point_code(Point(2, 0))
        assert_that(result, equal_to(Rectangle.RIGHT))

    def test_point_code_at_top_returns_top(self):
        border = Rectangle(left_top=Point(-1, -1), right_bottom=Point(1, 1))
        result = border.point_code(Point(0, -2))
        assert_that(result, equal_to(Rectangle.TOP))

    def test_point_code_at_bottom_returns_bottom(self):
        border = Rectangle(left_top=Point(-1, -1), right_bottom=Point(1, 1))
        result = border.point_code(Point(0, 2))
        assert_that(result, equal_to(Rectangle.BOTTOM))

    def test_point_code_at_left_top_returns_left_top(self):
        border = Rectangle(left_top=Point(-1, -1), right_bottom=Point(1, 1))
        result = border.point_code(Point(-2, -2))
        assert_that(result, equal_to(Rectangle.LEFT | Rectangle.TOP))

    def test_point_code_at_left_bottom_returns_left_bottom(self):
        border = Rectangle(left_top=Point(-1, -1), right_bottom=Point(1, 1))
        result = border.point_code(Point(-2, 2))
        assert_that(result, equal_to(Rectangle.LEFT | Rectangle.BOTTOM))

    def test_point_code_at_right_top_returns_right_top(self):
        border = Rectangle(left_top=Point(-1, -1), right_bottom=Point(1, 1))
        result = border.point_code(Point(2, -2))
        assert_that(result, equal_to(Rectangle.RIGHT | Rectangle.TOP))

    def test_point_code_at_right_bottom_returns_right_bottom(self):
        border = Rectangle(left_top=Point(-1, -1), right_bottom=Point(1, 1))
        result = border.point_code(Point(2, 2))
        assert_that(result, equal_to(Rectangle.RIGHT | Rectangle.BOTTOM))

    def test_clip_line_inside_returns_equal(self):
        rectangle = Rectangle(left_top=Point(0, 0), right_bottom=Point(1, 1))
        line = Line(begin=Point(0.25, 0.25), end=Point(0.75, 0.75))
        result = rectangle.clip_line(line)
        assert_that(result, equal_to(line))

    def test_clip_line_from_inside_to_outside_returns_from_inside_to_border(self):
        rectangle = Rectangle(left_top=Point(0, 0), right_bottom=Point(1, 1))
        line = Line(begin=Point(0.5, 0.5), end=Point(1.5, 0.5))
        result = rectangle.clip_line(line)
        assert_that(result, equal_to(Line(begin=Point(0.5, 0.5),
                                          end=Point(1, 0.5))))

    def test_clip_line_from_outside_returns_equal(self):
        rectangle = Rectangle(left_top=Point(0, 0), right_bottom=Point(1, 1))
        line = Line(begin=Point(0.5, 1.5), end=Point(1.5, 0.5))
        result = rectangle.clip_line(line)
        assert_that(result, equal_to(line))

    def test_1(self):
        line = Line(begin=Point(x=4924.240960182544, y=6227.578604236977),
                    end=Point(x=303.83920535439756, y=5285.014406185436))
        rectangle = Rectangle(left_top=Point(x=800.0, y=4800.0),
                              right_bottom=Point(x=1600.0, y=5600.0))
        result = rectangle.clip_line(line)
        assert_that(result, equal_to(Line(
            begin=Point(x=1600.0, y=5549.431836698775),
            end=Point(x=800.0, y=5386.231448842183),
        )))

    def test_2(self):
        line = Line(begin=Point(x=-2, y=-2), end=Point(x=2, y=2))
        rectangle = Rectangle(left_top=Point(x=-1, y=-1),
                              right_bottom=Point(x=1, y=1))
        result = rectangle.clip_line(line)
        assert_that(result, equal_to(Line(begin=Point(x=-1, y=-1),
                                          end=Point(x=1, y=1))))

    def test_3(self):
        line = Line(begin=Point(x=2, y=2), end=Point(x=-2, y=-2))
        rectangle = Rectangle(left_top=Point(x=-1, y=-1),
                              right_bottom=Point(x=1, y=1))
        result = rectangle.clip_line(line)
        assert_that(result, equal_to(Line(begin=Point(x=1, y=1),
                                          end=Point(x=-1, y=-1))))

    def test_4(self):
        line = Line(begin=Point(x=2, y=1), end=Point(x=-2, y=-1))
        rectangle = Rectangle(left_top=Point(x=-1, y=-1),
                              right_bottom=Point(x=1, y=1))
        result = rectangle.clip_line(line)
        assert_that(result, equal_to(Line(begin=Point(x=1, y=0.5),
                                          end=Point(x=-1, y=-0.5))))


class MakeTileBarriersTest(TestCase):
    def test_for_empty_returns_tile_rectangle(self):
        result = make_tile_barriers(tile_type=TileType.EMPTY,
                                    position=Point(10, 10), margin=1, size=3)
        assert_that(result, equal_to([
            Rectangle(left_top=Point(30, 30), right_bottom=Point(33, 33))
        ]))

    def test_for_vertical_returns_two_rectangles(self):
        result = make_tile_barriers(tile_type=TileType.VERTICAL,
                                    position=Point(10, 20), margin=1, size=3)
        assert_that(result, equal_to([
            Rectangle(left_top=Point(30, 60), right_bottom=Point(31, 63)),
            Rectangle(left_top=Point(32, 60), right_bottom=Point(33, 63)),
        ]))

    def test_for_horizontal_returns_two_rectangles(self):
        result = make_tile_barriers(tile_type=TileType.HORIZONTAL,
                                    position=Point(10, 20), margin=1, size=3)
        assert_that(result, equal_to([
            Rectangle(left_top=Point(30, 60), right_bottom=Point(33, 61)),
            Rectangle(left_top=Point(30, 62), right_bottom=Point(33, 63)),
        ]))

    def test_for_left_top_corner_returns_two_rectangles_and_one_circle(self):
        result = make_tile_barriers(tile_type=TileType.LEFT_TOP_CORNER,
                                    position=Point(10, 20), margin=1, size=3)
        assert_that(result, equal_to([
            Rectangle(left_top=Point(30, 60), right_bottom=Point(31, 63)),
            Rectangle(left_top=Point(30, 60), right_bottom=Point(33, 61)),
            Circle(Point(33, 63), 1),
        ]))

    def test_for_crossroads_returns_four_circles(self):
        result = make_tile_barriers(tile_type=TileType.CROSSROADS,
                                    position=Point(10, 20), margin=1, size=3)
        assert_that(result, equal_to([
            Circle(Point(30, 60), 1), Circle(Point(30, 63), 1),
            Circle(Point(33, 60), 1), Circle(Point(33, 63), 1),
        ]))
