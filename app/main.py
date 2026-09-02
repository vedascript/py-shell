
import sys
import os
import subprocess

def is_command_executable(command_to_run):
    PATH =  os.environ["PATH"]; 
    dir_path_array = PATH.split(os.pathsep);

    for dir_path in dir_path_array:
        file_path = os.path.join(dir_path, command_to_run);
        does_file_exists = os.path.isfile(file_path);
        has_execute_permission = os.access(file_path, os.X_OK);

        if(does_file_exists and has_execute_permission):
           return {'is_executable':True, 'file_path': file_path};

    return {'is_executable':False, 'file_path': None};       

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
                exec_config = is_command_executable(arg);   
                if(exec_config['is_executable']):
                    print(f"{arg} is {exec_config['file_path']}");
                    break;

                print(f"{arg}: not found");    
        else:    
            exec_config = is_command_executable(command);
            if(exec_config['is_executable']):
                # subprocess.run(['mkdir','abc']);
                print(f"arr: {user_input}")
            else:    
                print(f"{command}: command not found");
    
if __name__ == "__main__":
    main()


# traverse through the PATH var. 
# Divide it into separate valid paths (os.pathstep)
# Check if the dir in the path exists on disk
# Check if file is executable