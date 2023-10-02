import sys


def translate(start):
    end = ""
    arr = start.split(" ")
    problem = ""
    prev = 0;
    for x in arr:
        y = x.lower()
        num = 0
        # .len()
        # check for problem numbers
        if problem != "":
            if "," in y:
                y = x[0:-1]

            # check its a number
            try:
                # print("no")
                num = float(y)

                # check to make sure it has a decimal
                try :
                    y.index(".") 
                    prev = int(num)
                except ValueError:   
                    print(prev)
                    y = str(prev) + "." + y
                    print(y)

                num = float(y)

            # print(num)
            except ValueError:
                # print("whoops")
                pass

            # reformat numbers
            if num != 0 and len(y) < 4:
                # print("hi")
                i = y.index(".") + 1
                z = (y[0:i] + "0" + y[i])
                num = float(z)
            # print(num)
        print("y equals " + y)   
        # add translated problem to string
        if problem == "sc" and y != "ex":
            # print("Hi")
            end += ("Self-Check " + str(num) + "\n")
        if problem == "ex" and y != "sc":
            # print("Hi")
            end += ("Exercise " + str(num) + "\n")

        # determine problem type
        if y == "sc":
            problem = "sc"
        if y == "ex":
            problem = "ex"

    return end


def main():
    # write translated text to questions?
    if len(sys.argv) == 2:
        start = sys.argv[1]
    else:
        f = open("raw.txt", "r")
        start = f.read()

    # print(start)
    end = translate(start)
    print(end)

    w = open("questions.txt", "w")
    w.write(end)
    w.close()


if __name__ == '__main__':
    main()
