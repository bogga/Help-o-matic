from random import shuffle

def split(names : str, num : int):
    avg = len(names) / float(num)
    out = []
    last = 0.0

    shuffle(names)
    while last < len(names):
        out.append(names[int(last):int(last + avg)])
        last += avg

    for i in range(num):
        printable = "Team " + str(i + 1) + ": "
        for j in range(len(out[i])):
            printable += out[i][j]
            if j < (len(out[i]) - 1):
                printable += ", "
        print(printable)

while True:
    split(input("> "), int(input("num:\n> ")))