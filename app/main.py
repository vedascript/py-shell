
import sys
import os
import subprocess
import token

builtin_commands = ["exit", "echo", "pwd", "type", "cd"];
file_overwrite_modes = {">": "w" , "1>":"w"};
file_descriptor_dic = {} 
 

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

def push_reset_token(tokens_arr,curr_token):
    tokens_arr.append(curr_token);
    return "", False

def tokenize(input_str):
    tokens = [];
    current_token = "";
    has_token = False;
    state = "normal";
    index = 0;
    overwrite_mode = "";
    file_descriptor = None;

    while(index < len(input_str)):
        char = input_str[index];
        next_char = input_str[index + 1 : index + 2];

        if(state == "normal"):
            if(char == " "):
                if(has_token):
                    current_token, has_token = push_reset_token(tokens, current_token);
            elif(char == "'"):
                state = "single_quote";
                has_token = True;
            elif(char == '"'):
                state = "double_quote";
                has_token = True;
            elif(char == "\\" and next_char):
                current_token += next_char;
                has_token = True;
                index += 1;
            elif(char == ">"):
                if(has_token):
                    current_token, has_token = push_reset_token(tokens, current_token);
                overwrite_mode = file_overwrite_modes[char];
                file_descriptor = "OUTPUT";
            elif(char == "1" and next_char == ">"):
                if(has_token):
                    current_token, has_token = push_reset_token(tokens, current_token);
                overwrite_mode = file_overwrite_modes["1>"]; 
                file_descriptor = "OUTPUT"; 
                index +=1 ; 
            elif(char == "2" and next_char == ">"):
                if(has_token):
                    current_token, has_token = push_reset_token(tokens, current_token); 
                overwrite_mode = file_overwrite_modes[">"];  
                file_descriptor = "ERROR";
                index += 1;
            else:
                current_token += char;
                has_token = True;

        elif(state == "single_quote"):
            # backslash carries no meaning inside single quotes
            if(char == "'"):
                state = "normal";
            else:
                current_token += char;

        elif(state == "double_quote"):
            if(char == '"'):
                state = "normal";
            elif(char == "\\" and next_char in ("\\", '"', "$", "`")):
                current_token += next_char;
                index += 1;
            else:
                current_token += char;

        index += 1;

    # an unterminated quote still yields whatever was collected
    if(has_token):
        tokens.append(current_token);

    return {"tokens": tokens, "overwrite_mode": overwrite_mode, "file_descriptor": file_descriptor};    
           

def main():
    is_shell_running = True;
    output = sys.stdout;
    error_output = sys.stderr;

    while is_shell_running:
        try:      
            sys.stdout.write("$ ")
            # REPL is achieved using input
            file_to_write_output = None;
            tokens_config = tokenize(input());

            tokens = tokens_config["tokens"];
            overwrite_mode = tokens_config["overwrite_mode"];
            file_descriptor = tokens_config["file_descriptor"]

            if(not tokens):
                continue;

            command = tokens[0];

            if(file_descriptor):
                command_args = tokens[1:-1];
                file_to_write_output = tokens.pop();
            else:
                command_args = tokens[1:];    
      
         
            if(file_descriptor):
                try:
                    if(file_descriptor == "OUTPUT"):
                        output = open(file_to_write_output, overwrite_mode);
                    else:
                        error_output = open(file_to_write_output, overwrite_mode);    
                except OSError as e:
                    print(f"shell: {file_to_write_output}: {e.strerror}", file=sys.stderr);  
                    continue;    

            if(command == "exit"):
                is_shell_running = False;
                break;

            elif(command == "echo"):
                command_args_str = " ".join(command_args);
                print(command_args_str, file=output)
        

            elif(command == "pwd"):
                print(os.getcwd(), file=output);  

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

                not path_exists and print(f"cd: {path}: No such file or directory", file = error_output)    

            elif(command == "type"):
                arg = "".join(command_args)
                if(arg in builtin_commands):
                    print(f"{arg} is a shell builtin", file=output);
                else:
                    exec_config = is_command_executable(arg);   
                    if(exec_config['is_executable']):
                        print(f"{arg} is {exec_config['file_path']}", file=output);
                    else:
                        print(f"{arg}: not found", file = error_output);       

            else:  
                exec_config = is_command_executable(command);

                if(exec_config['is_executable']): 
                    subprocess.run([command, *command_args], stdout = output, stderr = error_output);     
                else:    
                    print(f"{command}: command not found", file = error_output);
        finally:
            if(output is not sys.stdout):
                output.close();
                output = sys.stdout;
            if(error_output is not sys.stderr):
                error_output.close();
                error_output = sys.stderr;    

            
if __name__ == "__main__":
    main()




