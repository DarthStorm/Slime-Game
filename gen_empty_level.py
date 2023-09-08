# TODO move this to the main file SOMETIME IDK

x = ""

if __name__ == '__main__':
    for i in range(30):
        for i in range(100):
            x += "002"
        x += "\n"

input("Press any key to continue...\n")

with open("level.txt", "w") as f:
    f.write(x)

print("Task succesful.")