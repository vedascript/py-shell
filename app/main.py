import sys


def main():
    is_shell_running = True;

    while is_shell_running:
        sys.stdout.write("$ ")
        # REPL is achieved using input
        command = input()
        if(command == "exit"):
            is_shell_running = False
            break;
        print(f"{command}: command not found")
    
if __name__ == "__main__":
    main()
