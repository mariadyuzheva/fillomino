#!/usr/bin/env python3

import os
import sys
import unittest

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             os.path.pardir))
from fillomino_logic import Field, FieldState, PuzzleGenerator, PuzzleSolver


class FieldTest(unittest.TestCase):
    def test_init_field(self):
        field = Field(5)
        self.assertEqual(5, field.size())

    def test_init_errors(self):
        for size in (-5, 0, 1):
            with self.assertRaises(ValueError):
                Field(size)

        for size in ((2, 3), 5.5, '4'):
            with self.assertRaises(TypeError):
                Field(size)

    def test_get_all_cells(self):
        field = Field(2)
        cells = field.get_all_cells()
        self.assertSetEqual(
            set(cells),
            {(0, 0), (0, 1), (1, 0), (1, 2), (1, 1), (2, 0), (2, 1)})

    def test_get_neighbour_cells(self):
        field = Field(3)

        for (cell, neighbours) in (((0, 0), {(0, 1), (1, 1), (1, 0)}),
                                   ((1, 2), {(0, 1), (0, 2), (1, 3), (2, 3),
                                             (2, 2), (1, 1)}),
                                   ((2, 2), {(1, 1), (1, 2), (2, 3), (3, 2),
                                             (3, 1), (2, 1)}),
                                   ((2, 4), {(1, 3), (2, 3), (3, 3)}),
                                   ((3, 1), {(2, 1), (2, 2), (3, 2), (4, 1),
                                             (4, 0), (3, 0)}),
                                   ((4, 1), {(4, 0), (3, 1), (3, 2), (4, 2)})):
            self.assertSetEqual(
                neighbours, set(field.get_neighbour_cells(cell)))


class FieldStateTest(unittest.TestCase):
    def test_init_state(self):
        field = Field(3)
        state = FieldState(field)

        for cell in field.get_all_cells():
            self.assertEqual(state.get_state(cell), 0)

    def test_field_to_string(self):
        generator = PuzzleGenerator(4)
        generator.generate_filled_field()
        state = generator.field_state
        state_to_string = str(state)
        state_from_string = FieldState.from_string_to_state(state_to_string)

        self.assertDictEqual(state_from_string.get_full_state(),
                             state.get_full_state())

    def test_set_state(self):
        field = Field(3)
        state = FieldState(field)
        state.set_state((2, 4), 5)

        self.assertEqual(state.get_state((2, 4)), 5)

    def test_set_state_errors(self):
        field = Field(3)
        state = FieldState(field)

        with self.assertRaises(ValueError):
            state.set_state((1, 1), -5)

        for cell, value in (((1, 0), 2.5), ((2, 2), '10'), ((4, 2), (1, 5))):
            with self.assertRaises(TypeError):
                state.set_state(cell, value)

    def test_get_full_state(self):
        field = Field(3)
        state = FieldState(field)
        state.set_state((2, 4), 1)

        self.assertEqual(state.get_full_state(), state._state)

    def test_clear_state(self):
        field = Field(3)
        state = FieldState(field)

        for cell, value in (((1, 1), 2), ((2, 3), 4), ((3, 1), 7)):
            state.set_state(cell, value)

        state.clear_state()

        for cell in field.get_all_cells():
            self.assertEqual(state.get_state(cell), 0)

    def test_neighbours_differ(self):
        string = '''
          3 5 1
         1 3 5 5
        2 0 0 5 5
         3 4 4 4
          3 0 4
        '''

        generator = PuzzleGenerator(3)
        generator.field_state = FieldState.from_string_to_state(string)

        for cell, prev_cell in (((2, 2), (1, 1)),
                                ((2, 1), (2, 0)),
                                ((4, 1), (4, 0))):
            self.assertTrue(generator.field_state.neighbours_differ(
                cell, [prev_cell], generator.field_state.get_state(prev_cell)))

        for cell, prev_cell in (((2, 1), (1, 1)),
                                ((2, 1), (3, 0))):
            self.assertFalse(generator.field_state.neighbours_differ(
                cell, [prev_cell], generator.field_state.get_state(prev_cell)))

    def test_color_state(self):
        generator = PuzzleGenerator(5)
        generator.generate_filled_field()
        generator.field_state.color_state()

        for cell in generator.field_state.field.get_all_cells():
            self.assertTrue(generator.field_state._colored_cells[cell]
                            in generator.field_state.COLORS)

    def test_get_involved(self):
        string = '''
          3 5 1
         2 3 5 5
        2 3 1 5 0
         0 4 4 4
          0 0 4
        '''

        field_state = FieldState.from_string_to_state(string)

        for cell, involved in (((0, 2), [(0, 2)]),
                               ((2, 0), [(2, 0), (1, 0)]),
                               ((4, 1), [(4, 1), (4, 0), (3, 0)])):
            self.assertListEqual(field_state.get_involved(cell), involved)


class PuzzleGeneratorTest(unittest.TestCase):
    def test_generate_filled_field(self):
        generator = PuzzleGenerator(3)
        generator.generate_filled_field()

        for number in generator.field_state.get_full_state().values():
            self.assertNotEqual(number, 0)

    def test_find_next_cells(self):
        string = '''
          3 5 1
         3 3 5 5
        2 0 5 4 4
         3 5 1 4
          3 0 4
        '''

        generator = PuzzleGenerator(3)
        generator.field_state = FieldState.from_string_to_state(string)

        for cell, next_cells in (((0, 0), []),
                                 ((2, 0), [(2, 1)]),
                                 ((3, 0), []),
                                 ((4, 0), [(4, 1)])):
            self.assertEqual(next_cells, list(generator._find_next_cells(
                cell, generator.field_state.get_state(cell))))

    def test_cells_involved(self):
        string = '''
          3 5 1
         2 3 5 5
        2 3 1 5 5
         0 4 4 4
          0 0 4
        '''

        generator = PuzzleGenerator(3)
        generator.field_state = FieldState.from_string_to_state(string)

        for number in (3, 4, 6):
            self.assertFalse(generator._cells_involved((3, 0), number))

        self.assertTrue(generator._cells_involved((4, 1), 2))
        self.assertTrue(generator._cells_involved((3, 0), 1))

    def test_generate_field_for_game_empty_unities(self):
        percent = 50
        unity = True

        generator = PuzzleGenerator(4)
        generator.generate_filled_field()
        generator.generate_field_for_game(unity, percent)

        empty_cells = list(filter(
            lambda cell: generator.game_field.get_state(cell) == 0,
            generator.field.get_all_cells()))

        min_empty_count = 0
        for group in generator.groups:
            min_empty_count += int(group.get_value() * percent / 100)

        max_empty_count = min_empty_count + len(generator.groups)
        self.assertTrue(min_empty_count <= len(empty_cells) <= max_empty_count)

        for group in filter(lambda g: g.get_value() != 1, generator.groups):
            self.assertTrue(any(generator.field_state.get_state(cell) != 0
                                for cell in group.initial_cells))

    def test_generate_field_for_game_with_unities(self):
        generator = PuzzleGenerator(4)
        generator.generate_filled_field()
        generator.generate_field_for_game(False)

        for cell, value in filter(
                lambda cell_state: cell_state[1] == 1,
                generator.field_state.get_full_state().items()):
            self.assertTrue(generator.game_field.get_state(cell) == 1)


class PuzzleSolverTest(unittest.TestCase):
    def test_error_from_string_to_state(self):
        string = '''
          3 5 1
         2 3 5 5
        2 3 1 5 0
         0 4 4 4
        '''

        with self.assertRaises(ValueError):
            PuzzleSolver(string)

        string = '''
          3 5 1
         2 3 5
        2 3 1 5 0
         0 4 4 4
          0 0 4
        '''

        with self.assertRaises(ValueError):
            PuzzleSolver(string)

    def test_find_possible_values_strict(self):
        string = '''
          3 3 0
         5 0 5 5
        3 0 4 5 1
         0 1 4 4
          3 2 2
        '''

        solver = PuzzleSolver(string, False, True)
        solver._refresh_state()

        for cell, values in (((0, 2), {3, 5}), ((1, 1), {3, 4, 5})):
            self.assertSetEqual(set(solver.possible_values[cell]), values)

    def test_find_possible_values_with_unities_strict(self):
        string = '''
          3 3 0
         5 0 5 5
        3 0 4 5 1
         0 1 4 4
          3 2 2
        '''

        solver = PuzzleSolver(string, True, True)
        solver._refresh_state()

        for cell, values in (((0, 2), {1, 3, 5}), ((1, 1), {1, 3, 4, 5}),
                             ((2, 1), {3, 4, 5}), ((3, 0), {3, 5})):
            self.assertSetEqual(set(solver.possible_values[cell]), values)

    def test_find_additional_values(self):
        string = '''
          3 3 0
         5 0 5 5
        0 4 4 5 1
         0 1 4 4
          0 2 2
        '''

        solver = PuzzleSolver(string, True, False)
        solver._refresh_state()

        for cell, values in (((0, 2), {1, 3, 5}), ((1, 1), {1, 3, 5}),
                             ((2, 0), {1, 2, 3, 5}), ((3, 0), {2, 3, 5}),
                             ((4, 0), {3, 5})):
            self.assertSetEqual(set(solver.possible_values[cell]), values)

    def test_solve(self):
        string = '''
          0 0 0
         2 3 5 5
        1 0 3 5 1
         3 4 4 4
          3 3 4
        '''

        solver = PuzzleSolver(string)
        solver.solve()

        for cell, value in (((0, 1), 5), ((0, 2), 5), ((2, 1), 2),
                            ((0, 0), 3)):
            self.assertEqual(solver.field_state.get_state(cell), value)

        string = '''
          3 0 0
         5 0 5 5
        3 0 4 5 1
         0 1 4 4
          3 2 2
        '''

        solver = PuzzleSolver(string)
        solver.solve()

        for cell, value in (((0, 1), 3), ((0, 2), 3), ((1, 1), 5),
                            ((2, 1), 4), ((3, 0), 3)):
            self.assertEqual(solver.field_state.get_state(cell), value)

    def test_solve_and_try_fill_empty_cells(self):
        string = '''
          3 0 0
         5 0 0 5
        3 0 0 5 1
         0 1 4 4
          3 2 2
        '''

        solver = PuzzleSolver(string, True)
        solver.solve()

        for cell in solver.field_state.field.get_all_cells():
            self.assertNotEqual(solver.field_state.get_state(cell), 0)

    def test_check_group_size(self):
        string = '''
          3 0 5
         5 5 5 5
        6 6 0 0 1
         0 1 4 4
          6 4 4
        '''

        solver = PuzzleSolver(string)

        with self.assertRaises(ValueError):
            solver._check_group_size()

        string = '''
          2 0 5
         5 5 5 5
        6 6 0 0 5
         0 1 4 4
          6 4 4
        '''

        solver = PuzzleSolver(string)

        with self.assertRaises(ValueError):
            solver._find_unfilled_groups()

    def test_unsolvable_puzzle(self):
        string = '''
          3 0 0
         5 5 5 5
        6 6 0 6 1
         0 1 4 4
          6 4 4
        '''
        solver = PuzzleSolver(string)

        with self.assertRaises(ValueError):
            solver._try_fill_empty_cells()

    def solve_puzzle_without_some_values(self):
        string = '''
          0 0 0
         4 4 4 0
        6 6 0 6 1
         0 1 4 4
          6 4 4
        '''

        solver = PuzzleSolver(string, False, True)
        with self.assertRaises(ValueError):
            solver.solve()

        solver = PuzzleSolver(string, False, False)
        solver.solve()
        for value in solver.field_state.get_full_state().values():
            self.assertNotEqual(value, 0)


if __name__ == '__main__':
    unittest.main()
