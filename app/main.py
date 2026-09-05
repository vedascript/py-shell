
import sys
import os
import subprocess

builtin_commands = ["exit", "echo", "pwd", "type", "cd", "cat"];
 

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

def get_path_type(path):
    if(path[0] == '/'):
        return "absolute";
    elif(path[0] == '~'):
        return 'home_dir';    
    elif(path[1] == '.'):
        return "parent_dir";
    else:
        return "current_dir"   

def handle_input_string(input_str):
    parsed_input_str = "";

    if(input_str.count("'") < 2):
        for i, ch in enumerate(input_str):
            if(not ch == " "):
                parsed_input_str += ch;
            elif(ch == " " and i < input_str.__len__() - 1 and not input_str[i+1] == " "):
                    parsed_input_str += ch;
            else:
                    continue;        
    else:
        parsed_input_str = input_str.replace("'","");

    return parsed_input_str;    

        

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
            input_str = " ".join(command_args);
            string_to_echo = handle_input_string(input_str);

            print(string_to_echo);
        elif(command == "pwd"):
            print(os.getcwd());  

        elif(command == "cd"):
            path_exists = False;
            path = command_args[0];
            path_type =  get_path_type(path);

            if(path_type == 'absolute' and os.path.exists(path)):
                path_exists = True;
                os.chdir(path);

            elif(path_type == 'current_dir'):
                absolute_path = os.getcwd();
                target_path = absolute_path + path[1:];

                if(os.path.exists(path)):
                     path_exists = True;
                     os.chdir(target_path);

            elif(path_type == 'parent_dir'):
                absolute_path = os.getcwd();
                path_arr = path.split('/');
                navigate_back_dir_count = 0;

                for item in path_arr:
                    if(item == '..'):
                        navigate_back_dir_count += 1;

                shortened_path_arr = absolute_path.split('/')[:-navigate_back_dir_count];
                updated_path = "/".join(shortened_path_arr);

                if(os.path.exists(updated_path)):
                    path_exists = True;
                    os.chdir(updated_path)

            elif(path_type == 'home_dir'):
                home_env = os.getenv("HOME");    
                path_exists = True;
                os.chdir(home_env);   

            not path_exists and print(f"cd: {path}: No such file or directory")    

        elif(command == "type"):
            arg = "".join(command_args);
            if(arg in builtin_commands):
                print(f"{arg} is a shell builtin");
            else:
                exec_config = is_command_executable(arg);   
                if(exec_config['is_executable']):
                    print(f"{arg} is {exec_config['file_path']}");
                else:
                 print(f"{arg}: not found");  

        elif(command == "cat"):
          file_contents = '';
          input_str = " ".join(command_args);
          paths_arr = input_str.split("'");

          for file_path_input in paths_arr:
            if(not "'" in file_path_input):
                continue;

            parsed_file_path_input = handle_input_string(file_path_input);
            final_path = os.getcwd() + parsed_file_path_input;

            if(os.path.exists(final_path) and os.path.isfile(final_path)):
                with open(final_path) as file:
                    content = file.read();
                    file_contents += content;    
            else:
                continue; 

          print(f"{file_contents}");       

        else:    
            exec_config = is_command_executable(command);
            if(exec_config['is_executable']):
                subprocess.run([command, *command_args]);
            else:    
                print(f"{command}: command not found");
    
if __name__ == "__main__":
    main()


