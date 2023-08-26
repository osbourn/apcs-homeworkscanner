def Translate(start):
    end = ""
    arr = start.split(" ")
    problem = ""
    for x in arr:
        y = x.lower()
        num = 0
        # .len()
        # check for problem numbers
        if problem != "":
            if "," in y:
                y = x[0:-1]

            # print(y)
            try:
                # print("no")
                num = float(y)
            # print(num)
            except:
                # print("whoops")
                pass

            # reformat numbers
            if num != 0 and len(y) < 4:
                # print("hi")
                i = y.index(".") + 1
                z = (y[0:i] + "0" + y[i])
                num = float(z)
            # print(num)

        # add translated problem to string
        if problem == "sc" and y != "ex":
            # print("Hi")
            end += ("Self-Check " + str(num) + " \n")
        if problem == "ex" and y != "sc":
            # print("Hi")
            end += ("Exercise " + str(num) + " \n")

        # determine problem type
        if y == "sc":
            problem = "sc"
        if y == "ex":
            problem = "ex"

    return end


def main():
    # write translated text to questions?
    end = ""
    f = open("raw.txt", "r")
    start = f.read()

    # print(start)
    end = Translate(start)
    print(end)

    w = open("questions.txt", "a")
    w.write(end)
    w.close()


if __name__ == '__main__':
    main()
