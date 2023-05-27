import numpy as np
from enchant.checker import SpellChecker
from enchant.checker.CmdLineChecker import color  # только для изменения цвета текста в терминале


def reading_replacement(cmd, error_word):
    if cmd.isdigit():
        replacement_idx = int(cmd)
        if replacement_idx >= len(suggestions) or replacement_idx < 0:
            print(color("Нет исправления с таким номером"))
            return False
        rpl = error_word.suggest()[replacement_idx]
        print(color("Исправление: ", color="bold") + "\"" + error_word.word + "\" на \"" + rpl + "\"")
        error_word.replace(rpl)
        return True
    else:
        if cmd.lower() == "ignore" or cmd.lower() == "i":
            print("Игнорирование ошибки")
            return True
        else:
            return False


def create_context_for_word(checker):
    text = checker.get_text()
    start = text.rfind(" ", 0, max(checker.wordpos - 40, 0))
    end = text.find(" ", min(checker.wordpos + len(checker.word) + 40, len(text)))
    # пофиксить замену слова
    return color("Контекст: ", color="bold") + text[start + 1: end].replace(checker.word, color(checker.word, color="red"))


def levenshtaine_distance(str1, str2) -> int:
    insert_cost = 1
    delete_cost = 1
    replace_cost = 1
    N = len(str1)
    M = len(str2)
    D = np.empty((N+1, M+1))
    D[0][0] = 0
    for j in range(1, M + 1):
        D[0][j] = D[0][j-1] + insert_cost
    for i in range(1, N + 1):
        D[i][0] = D[i - 1][0] + delete_cost
        for j in range(1, M+1):
            if str1[i-1] != str2[j-1]:
                D[i][j] = min(D[i-1][j] + delete_cost, D[i][j-1] + insert_cost, D[i-1][j-1] + replace_cost)
            else:
                D[i][j] = D[i-1][j-1]
    return D[N][M]


checker = SpellChecker("en_US")
print("Введите текст для исправления:")
print()
text = input()
checker.set_text(text)
errors_count = 0
for error in checker:
    errors_count += 1
    print()
    # вывод ошибки, контекст ошибки и варианты исправления
    print(color("Ошибка в слове: ", color="bold") + color(error.word, color="red"))
    # Вывод контекста
    print(create_context_for_word(error))
    # Варианты исправления
    suggestions = error.suggest()
    result_line = ""
    for idx, sugg in enumerate(suggestions):
        if idx == 0:
            result_line = (
                    result_line
                    + color(str(idx), color="yellow")
                    + ": "
                    + color(sugg, color="bold")
                    + " ("
                    + str(levenshtaine_distance(error.word, sugg))
                    + ")"
            )
        else:
            result_line = (
                result_line
                + " | "
                + color(str(idx), color="yellow")
                + ": "
                + color(sugg, color="bold")
                + " ("
                + str(levenshtaine_distance(error.word, sugg))
                + ")"
            )
    print(color("Варианты исправления: ", color="bold") + result_line)
    # Выбор варианта
    status = False
    while not status:
        print("Выберите вариант исправления ("+color("\"ignore\"", color="green")+" или "+color("\"i\"", color="green")+" для пропуска)")
        command = input(">> ")
        command = command.strip()
        status = reading_replacement(command, error)

if errors_count == 0:
    print(color("Ошибок не найдено", color="green"))
else:
    print("Количество найденных ошибок: "+str(errors_count))
    print("Исправленный текст:")
    print(checker.get_text())
    print()
