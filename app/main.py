import sys
import os


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
                PATH =  os.environ["PATH"]; 
                print(f"PATH: {PATH}")
                dir_path_array = PATH.split(os.pathsep);
                print(f"dir_path_aray {dir_path_array}")
                found_arg = False;
                
                for dir_path in dir_path_array:
                   sub_path_arr = dir_path.split("/")[1:];
                  

                   if(arg in sub_path_arr):
                        does_dir_exists = os.path.exists(dir_path);
                        has_execute_permission = os.access(dir_path, os.X_OK);

                        if(has_execute_permission and does_dir_exists):
                             print(f"{arg} is {dir_path}");
                             found_arg = True;
                             break;
                   else:
                        continue; 
                not found_arg and print(f"{arg}: not found");    
        else:    
            print(f"{command}: command not found");
    
if __name__ == "__main__":
    main()


# traverse through the PATH var. 
# Divide it into separate valid paths (os.pathstep)
# Check if the dir in the path exists on disk
# Check if file is executable