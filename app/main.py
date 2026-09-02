import sys


def main():
    is_shell_running = True;

    while is_shell_running:
        sys.stdout.write("$ ")
        # REPL is achieved using input
        user_input = input();
        command = user_input.split(' ')[0];
        command_args = user_input.split(' ')[1:];
    
        if(command == "exit"):
            is_shell_running = False;
            break;
        elif(command == "echo"):
            print(" ".join(command_args));
        elif(command == "type"):
            arg = "".join(command_args);
            if(arg == 'type' or arg == 'exit' or arg == 'echo'):
                print(f"{arg} is a shell builtin");
            else:    
                print(f"{arg}: not found");    
        else:    
            print(f"{command}: command not found");
    
if __name__ == "__main__":
    main()
