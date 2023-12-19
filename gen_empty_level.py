# TODO move this to the main file SOMETIME IDK

x = ""

if __name__ == "__main__":
    for i in range(30):
        for i in range(100):
            x += "001"
        x += "\n"

input("Press Enter to continue...\n")

with open("level.txt", "w") as f:
    f.write(x)

print("Task succesful.")
