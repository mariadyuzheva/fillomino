#!/usr/bin/env python3

import collections
import random
import copy


class Field:
    def __init__(self, size):
        self.check_size(size)
        self._size = size

    @staticmethod
    def check_size(size):
        if type(size) is not int:
            raise TypeError('Field size should be integer')

        if size <= 1:
            raise ValueError('Minimum field size is 2')

    def size(self):
        return self._size

    def get_all_cells(self):
        row_length = self._size

        for x in range(self._size * 2 - 1):
            for y in range(row_length):
                yield (x, y)
            if x < self._size - 1:
                row_length += 1
            else:
                row_length -= 1

    def get_neighbour_cells(self, cell):
        for x in range(-1, 2):
            for y in range(-1, 2):
                if (cell[0] < self._size - 1 and x == -y
                        or cell[0] == self._size - 1 and abs(x) == y
                        or cell[0] > self._size - 1 and x == y):
                    continue

                neighbour_cell = tuple(map(sum, zip((x, y), cell)))
                if (neighbour_cell in list(self.get_all_cells())
                        and neighbour_cell != cell):
                    yield neighbour_cell


class FieldState:
    COLORS = [
        '\033[31m',
        '\033[32m',
        '\033[33m',
        '\033[34m'
    ]

    def __init__(self, field):
        self.field = field
        self._state = collections.defaultdict(lambda: 0)
        self._colored_cells = {}
        self._colored_state = {}

    def __str__(self):
        result = ""
        row_length = self.field.size()

        max_value = 0
        for value in self._state.values():
            if value > max_value:
                max_value = value
        max_value_len = len(str(max_value))

        first_gap_length = self.field.size() * max_value_len

        for x in range(self.field.size() * 2 - 1):
            row = ''
            if x < self.field.size():
                first_gap_length -= max_value_len
            else:
                first_gap_length += max_value_len
            row += ' ' * first_gap_length

            for y in range(row_length):
                if self._colored_state:
                    cell_state = self._colored_state[(x, y)]
                else:
                    cell_state = self._state[(x, y)]

                row += ''.join((
                    ' ' * (max_value_len - len(str(self._state[(x, y)]))),
                    str(cell_state),
                    ' ' * max_value_len))

            if x < self.field.size() - 1:
                row_length += 1
            else:
                row_length -= 1

            result += row + '\n'

        return result

    @staticmethod
    def from_string_to_state(string_state):
        rows = string_state.strip().split('\n')
        size = len(rows[0].split())
        if size * 2 - 1 != len(rows):
            raise ValueError('Wrong format of field state')

        field = Field(size)
        state = FieldState(field)
        row_length = size

        for row_number, row in enumerate(rows):
            row = row.split()
            if len(row) != row_length:
                raise ValueError('Wrong format of field state')

            for value_number, value in enumerate(row):
                state.set_state((row_number, value_number), int(value))

            if row_number < size - 1:
                row_length += 1
            else:
                row_length -= 1
        return state

    def set_state(self, coords, value):
        if value < 0:
            raise ValueError('Value should be non-negative')

        if type(value) is not int:
            raise TypeError('Value should be integer')
        self._state[coords] = value

    def get_state(self, coords):
        return self._state[coords]

    def get_full_state(self):
        return self._state

    def clear_state(self):
        for cell in self.field.get_all_cells():
            self._state[cell] = 0

    def neighbours_differ(self, cell, prev_cells, number):
        for cell in self.field.get_neighbour_cells(cell):
            if (cell not in prev_cells
                    and self.get_state(cell) == number):
                return False

        return True

    def get_involved(self, cell):
        involved = [cell]
        value = self._state[cell]
        not_checked = [cell]

        while not_checked:
            cell = not_checked.pop()

            for neighbour in self.field.get_neighbour_cells(cell):
                if (neighbour not in involved
                        and self._state[neighbour] == value):
                    involved.append(neighbour)
                    not_checked.append(neighbour)

        return involved

    def color_state(self):
        self.get_cells_colors()

        for cell in self._state.keys():
            self._colored_state[cell] = ''.join((
                self._colored_cells[cell],
                str(self._state[cell]),
                '\033[0m'))

    def get_cells_colors(self):
        next_cells = [(0, 0)]
        previous_cells = []
        possible_colors = collections.defaultdict(lambda: list(self.COLORS))
        same_group_cells = {}
        other_group_cells = {}

        while next_cells:
            cell = next_cells.pop()
            if cell not in self._colored_cells:
                same_group_cells[cell] = self.get_involved(cell)
                other_group_cells[cell] = []

                for group_cell in same_group_cells[cell]:
                    for neighbour in filter(
                            lambda n: n not in same_group_cells[cell],
                            self.field.get_neighbour_cells(group_cell)):
                        other_group_cells[cell].append(neighbour)
                        if neighbour not in next_cells:
                            next_cells.append(neighbour)

                if self.color_selected(same_group_cells[cell],
                                       other_group_cells[cell],
                                       possible_colors[cell]):
                    previous_cells.append(cell)
                else:
                    previous_cell = previous_cells.pop()
                    possible_colors[previous_cell].remove(
                        self._colored_cells[previous_cell])
                    for g_cell in same_group_cells[previous_cell]:
                        del self._colored_cells[g_cell]
                    next_cells.append(cell)
                    next_cells.append(previous_cell)
                    possible_colors[cell] = list(self.COLORS)

    def color_selected(self, same_group_cells, other_group_cells,
                       possible_colors):
        for color in filter(
                lambda x: x in possible_colors, self.COLORS):
            if (all(not self.has_the_same_color(color, n)
                    for n in other_group_cells)):
                for group_cell in same_group_cells:
                    self._colored_cells[group_cell] = color
                return True
            possible_colors.remove(color)
        return False

    def has_the_same_color(self, color, cell):
        if cell not in self._colored_cells:
            return False

        return self._colored_cells[cell] == color


class CellsGroup:
    def __init__(self, value, initial_cells):
        self.value = value
        self.initial_cells = initial_cells
        self.possible_cells = []
        self.possible_connection_cells = []

    def get_value(self):
        return self.value

    def get_possible_length(self):
        return (len(self.initial_cells) + len(self.possible_cells)
                + len(self.possible_connection_cells))

    def add_possible_cell(self, cell):
        if cell not in self.possible_cells:
            self.possible_cells.append(cell)

    def add_connection(self, cell):
        if cell not in self.possible_connection_cells:
            self.possible_connection_cells.append(cell)


class PuzzleGenerator:
    def __init__(self, size, max_value=9):
        self.size = size
        self.field = Field(self.size)
        self.field_state = FieldState(self.field)
        self.game_field = None
        self.groups = []
        self.max_value = max_value

    def generate_filled_field(self):
        while not self._field_generated():
            self.field_state.clear_state()
            self.groups = []

    def _field_generated(self):
        all_cells = list(self.field.get_all_cells())
        random.shuffle(all_cells)

        for cell in filter(lambda x: self.field_state.get_state(x) == 0,
                           all_cells):
            number = random.randint(2, self.max_value)

            while not self._cells_involved(cell, number):
                number -= 1
                if number == 0:
                    return False

        return True

    def _find_next_cells(self, cell, value):
        for next_cell in self.field.get_neighbour_cells(cell):
            if (self.field_state.get_state(next_cell) == 0
                    and self.field_state.neighbours_differ(
                        next_cell, [cell], value)):
                yield next_cell

    def _cells_involved(self, cell, value):
        if not self.field_state.neighbours_differ(cell, [], value):
            return False

        self.field_state.set_state(cell, value)
        involved_cells = [cell]

        while len(involved_cells) != value:
            next_cells = list(self._find_next_cells(involved_cells[-1], value))

            if not next_cells:
                for cell in involved_cells:
                    self.field_state.set_state(cell, 0)
                return False

            for cell in next_cells:
                self.field_state.set_state(cell, value)
                involved_cells.append(cell)

        self.groups.append(CellsGroup(value, involved_cells))
        return True

    def generate_field_for_game(self, unity, percent=50):
        self.game_field = copy.deepcopy(self.field_state)

        if not unity:
            groups = list(filter(lambda g: g.get_value() != 1, self.groups))
        else:
            groups = self.groups

        max_empty = int(len(list(self.field.get_all_cells())) * percent / 100)
        total_empty = 0

        for group in groups:
            group_empty = int(group.get_value() * percent / 100)

            if ((group.get_value() == 1 or group_empty + 1 < group.get_value())
                    and total_empty + group_empty < max_empty
                    and group_empty < group.get_value()):
                group_empty += random.randint(0, 1)
            if total_empty + group_empty > max_empty:
                break

            total_empty += group_empty
            random_group_cells = random.sample(
                group.initial_cells, group_empty)

            for cell in random_group_cells:
                self.game_field.set_state(cell, 0)


class PuzzleSolver:
    def __init__(self, string_state, unity=False, strict=False):
        self.field_state = FieldState.from_string_to_state(string_state)
        self.involved = []
        self.possible_values = collections.defaultdict(lambda: [])
        self.unfilled_groups = {}
        self.state_changed = True
        self.unity = unity
        self.strict = strict

    def solve(self):
        self._refresh_state()

        while self.state_changed:
            self.state_changed = False
            self._join_groups_if_one_connection()
            self._fill_group_if_no_other_variants()
            self._fill_cells_with_one_value()

        self._try_fill_empty_cells()

    def _fill_cells_with_one_value(self):
        for cell in filter(lambda c: self.field_state.get_state(c) == 0,
                           self.field_state.field.get_all_cells()):
            if len(self.possible_values[cell]) == 1:
                self.field_state.set_state(
                    cell, self.possible_values[cell].pop())
                self._refresh_state()

    def _join_groups_if_one_connection(self):
        for group in self.unfilled_groups.values():
            if (group.get_possible_length() < group.get_value()
                    and len(group.possible_connection_cells) == 1):
                self.field_state.set_state(
                    group.possible_connection_cells[0], group.get_value())
                self._refresh_state()

    def _fill_group_if_no_other_variants(self):
        for group in self.unfilled_groups.values():
            if (group.get_possible_length() == group.get_value()
                    and not group.possible_connection_cells):
                for cell in group.possible_cells:
                    self.field_state.set_state(cell, group.get_value())
                    self._refresh_state()

    def _refresh_state(self):
        self._find_unfilled_groups()
        for cell in filter(lambda c: self.field_state.get_state(c) != 0
                           and c in self.unfilled_groups,
                           self.field_state.field.get_all_cells()):
            self._find_possible_values(cell)

        empty_cells = list(filter(lambda c: self.field_state.get_state(c) == 0,
                                  self.field_state.field.get_all_cells()))

        involved_empty = set()
        for cell in empty_cells:
            if self.unity and all(
                    self.field_state.get_state(n) != 1
                    for n in self.field_state.field.get_neighbour_cells(cell)):
                self._add_possible_value(cell, 1)

            if not self.strict and cell not in involved_empty:
                empty_group = self.field_state.get_involved(cell)
                involved_empty = involved_empty.union(empty_group)
                self._find_additional_values(empty_group)

        self.state_changed = True

    def _find_additional_values(self, empty_group):
        for value in range(
                2, min(len(empty_group) + 1, 10)):
            involved_for_value = set(empty_group)
            not_possible_cells = set()

            for involved in involved_for_value:
                if any(self.field_state.get_state(n) == value
                       for n in self.field_state.field.get_neighbour_cells(
                       involved)):
                    not_possible_cells.add(involved)
            involved_for_value -= not_possible_cells

            if value <= len(involved_for_value):
                for cell in involved_for_value:
                    self._add_possible_value(cell, value)

    def _find_unfilled_groups(self):
        self.unfilled_groups = {}
        self.involved = []
        self.possible_values = collections.defaultdict(lambda: [])

        for cell in filter(lambda x: self.field_state.get_state(x) != 0,
                           self.field_state.field.get_all_cells()):
            if cell not in self.involved:
                initial_cells = self.field_state.get_involved(cell)
                self.involved += initial_cells
                value = self.field_state.get_state(cell)

                if len(initial_cells) < value:
                    new_group = CellsGroup(value, initial_cells)
                    for c in initial_cells:
                        self.unfilled_groups[c] = new_group

                if len(initial_cells) > value:
                    raise ValueError('Wrong group size')

    def _find_possible_values(self, cell):
        next_cells = [(cell, 0)]
        value = self.field_state.get_state(cell)
        previous_cells = []
        group = self.unfilled_groups[cell]

        while next_cells:
            current_cell, current_length = next_cells.pop()
            previous_cells.append(current_cell)

            way_length = current_length + len(group.initial_cells)

            if way_length < value and current_cell != cell:
                self._add_possible_value(current_cell, value)
                group.add_possible_cell(current_cell)

            elif way_length == value:
                self._add_possible_value(current_cell, value)
                group.add_possible_cell(current_cell)
                continue

            free_neighbours = filter(
                lambda n: self.field_state.get_state(n) == 0
                and n not in previous_cells,
                self.field_state.field.get_neighbour_cells(current_cell))

            for neighbour in free_neighbours:
                if any(self._connection_cells_found(n, neighbour, group)
                       for n in self.field_state.field.get_neighbour_cells(
                        neighbour)):
                    continue

                next_cells.append((neighbour, current_length + 1))

    def _add_possible_value(self, cell, value):
        if value not in self.possible_values[cell]:
            self.possible_values[cell].append(value)

    def _connection_cells_found(self, neighbour, cell, group):
        value = group.get_value()

        if (self.field_state.get_state(neighbour) == value
                and neighbour not in group.initial_cells
                and neighbour not in group.possible_cells):
            self.field_state.set_state(cell, value)
            intersection_length = len(self.field_state.get_involved(cell))
            self.field_state.set_state(cell, 0)

            if intersection_length <= value:
                group.add_connection(cell)
                self._add_possible_value(cell, value)
            return True

        return False

    def _try_fill_empty_cells(self):
        filled_cells = []
        prev_cell = None
        free_cells = list(filter(lambda c: self.field_state.get_state(c) == 0,
                                 self.field_state.field.get_all_cells()))
        possible_values = self.possible_values

        while free_cells:
            self._refresh_state()
            cell = prev_cell
            if not prev_cell:
                cell = free_cells.pop()
                possible_values[cell] = self.possible_values[cell]
            wrong_values = set()

            for value in possible_values[cell]:
                self.field_state.set_state(cell, value)
                try:
                    self._check_group_size()
                    filled_cells.append(cell)
                    prev_cell = None
                    break

                except ValueError:
                    wrong_values.add(value)

            possible_values[cell] = list(
                set(possible_values[cell]) - wrong_values)

            if not possible_values[cell]:
                free_cells.append(cell)
                if not filled_cells:
                    raise ValueError('Puzzle is unsolvable')
                prev_cell = filled_cells.pop()
                possible_values[prev_cell] = list(
                    set(possible_values[prev_cell])
                    - {self.field_state.get_state(prev_cell)})
                self.field_state.set_state(cell, 0)
                self.field_state.set_state(prev_cell, 0)

    def _check_group_size(self):
        self._refresh_state()
        if any(group.get_possible_length() < group.get_value()
               and not group.possible_connection_cells
               for group in self.unfilled_groups.values()):
            raise ValueError('Wrong group size')
