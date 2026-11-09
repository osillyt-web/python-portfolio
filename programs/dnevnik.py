import sys, os
if sys.platform == 'win32':
    os.system('chcp 65001 > nul')
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stdin.reconfigure(encoding='utf-8')

while True:
    print("--- Дневник заметок ---")
    print("1. Добавить заметку")
    print("2. Показать все")
    print("3. Удалить заметку")
    print("4. Выход")
    выбор = input("Что делаем? ")

    if выбор == "4":
        print("Пока!")
        break

    elif выбор == "1":
        заметка = input("Твоя заметка: ")
        файл = open("заметки.txt", "a", encoding="utf-8")
        файл.write(заметка + "\n")
        файл.close()
        print("Заметка сохранена!")
    elif выбор == "2":
        блокнот = open("заметки.txt", "r", encoding="utf-8")
        номер = 1
        for строка in блокнот:
            строка = строка.rstrip()
            print(номер, ". ", строка, sep="")
            номер = номер + 1
        блокнот.close()
    elif выбор == "3":
        блокнот = open("заметки.txt", "r", encoding="utf-8")
        строки = блокнот.readlines()
        блокнот.close()

        какой = input("Какую удалить (номер)? ")
        номер = int(какой)
        индекс = номер - 1

        строки.pop(индекс)

        файл = open("заметки.txt", "w", encoding="utf-8")
        файл.writelines(строки)
        файл.close()
        print("Удалено!")
    else:
        print("Нет такого пункта!")