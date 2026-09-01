import sys


def main():
    sys.stdout.write("$ ")
    command = sys.argv[0]
    print(f"{command}: command not found")
    
if __name__ == "__main__":
    main()
