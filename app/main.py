
import sys
import os
import subprocess

builtin_commands = ["exit", "echo", "pwd", "type", "cd"];
file_overwrite_modes = {">": "w" , "1>":"w"};
 

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

def tokenize(input_str):
    tokens = [];
    current_token = "";
    has_token = False;
    state = "normal";
    index = 0;
    should_overwrite_stdout = False;
    overwrite_mode = "";


    while(index < len(input_str)):
        char = input_str[index];
        next_char = input_str[index + 1 : index + 2];

        if(state == "normal"):
            if(char == " "):
                if(has_token):
                    tokens.append(current_token);
                    current_token = "";
                    has_token = False;
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
            elif(char == ">" or char == "1>"):
                should_overwrite_stdout = True;
                overwrite_mode = file_overwrite_modes[char];
                current_token += char;
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

    return {"tokens": tokens, "should_overwrite_stdout": should_overwrite_stdout, "overwrite_mode": overwrite_mode};


def parse_redirection_str(command_args):
    try:
        index =  command_args.index(">");
    except ValueError:
        index = command_args.index("1>");

    updated_command_args = command_args[:-index-1];
    file_to_write_output = command_args[index+1:];

    return {"updated_command_args": updated_command_args, "file_to_write_output": file_to_write_output};       
           

def main():
    is_shell_running = True;
    output = sys.stdout;

    while is_shell_running:
        try:      
            sys.stdout.write("$ ")
            # REPL is achieved using input
            file_to_write_output = None;
            tokens_config = tokenize(input());

            tokens = tokens_config["tokens"];
            should_overwrite_stdout = tokens_config["should_overwrite_stdout"];
            overwrite_mode = tokens_config["overwrite_mode"];

            if(not tokens):
                continue;

            command = tokens[0];
            command_args = tokens[1:];

            if(should_overwrite_stdout):
                parse_config = parse_redirection_str(command_args);
                command_args = parse_config['updated_command_args'];
                file_to_write_output = parse_config['file_to_write_output'];

                try:
                    output = open(file_to_write_output, overwrite_mode);
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

                not path_exists and print(f"cd: {path}: No such file or directory")    

            elif(command == "type"):
                arg = "".join(command_args);
                if(arg in builtin_commands):
                    print(f"{arg} is a shell builtin", file=output);
                else:
                    exec_config = is_command_executable(arg);   
                    if(exec_config['is_executable']):
                        print(f"{arg} is {exec_config['file_path']}", file=output);
                    else:
                        print(f"{arg}: not found");       

            else:  
                exec_config = is_command_executable(command, );

                if(exec_config['is_executable']): 
                    subprocess.run([command, *command_args],stdout=output);     
                else:    
                    print(f"{command}: command not found");
        finally:
            if(not output == sys.stdout):
                output.close();
            
if __name__ == "__main__":
    main()




