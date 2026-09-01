import sys


def main():
    sys.stdout.write("$ ")
    # REPL is achieved using input
    command = input()
    print(f"{command}: command not found")
    
if __name__ == "__main__":
    main()
