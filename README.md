# Головоломка "Fillomino"

Автор: Дюжева Мария (mdyuzheva@gmail.com)


## Описание
Данное приложение является реализацией генератора полей и алгоритма решения 
для головоломки "Fillomino" с шестиугольным полем.


## Требования
* Python версии не ниже 3.6


## Состав
* Консольная версия генератора полей: "fillomino_generator.py"
* Консольная версия решателя головоломки: "filllomino_solver.py"
* Логика головоломки: "fillomino_logic.py"
* Тесты: "fillomino_test.py"


## Консольная версия
Справка по запуску: "./fillomino_generator.py --help"
					"./fillomino_solver.py --help"

Пример запуска: "./fillomino_generator.py -s SIZE -e PERCENT -u -p FILENAME -l FILENAME -c -m MAXVALUE"
				"./filllomino_solver.py -s FILENAME -u -w FILENAME -c -r"

## Подробности реализации
В основе всего лежат класс "fillomino_logic.Field", реализующий хранение поля,
класс "fillomino_logic.FieldState", реализующий хранение и изменение состояния поля,
класс "fillomino_logic.CellsGroup", реализующий хранение групп клеток поля,
класс "fillomino_logic.PuzzleGenerator", генерирующий поле для головоломки,
класс "fillomino_logic.PuzzleSolver", реализующий алгоритм решения.

На модуль "fillomino_logic" написаны тесты, их можно найти в "fillomino_test.py".
Покрытие тестами по строкам составляет 98%.

	fillomino_logic.py         367      9    98%   85, 205-212, 224

