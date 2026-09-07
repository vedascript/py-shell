
import sys
import os
import subprocess

builtin_commands = ["exit", "echo", "pwd", "type", "cd"];
 

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

def parse_input_str(input_str, get_str_arr = False):
    if('"' in input_str):
        str_arr = input_str.split('"');
        
        if(get_str_arr):
            return str_arr;

        parsed_str = handle_double_quotes_str(str_arr);
    else:
        str_arr = input_str.split("'"); 

        if(get_str_arr):
            return str_arr;

        parsed_str =  handle_single_quote_str(str_arr)

    return parsed_str;     

def handle_double_quotes_str(str_arr):
    parsed_input_str = '';

    for str in str_arr:
        if(not str.strip() and len(str)):
            parsed_input_str += " ";
        elif(len(str) and str[0] == " "):
            striped_str = str.lstrip();
            parsed_input_str+= f'{" " + striped_str}'    
        else:    
            parsed_input_str += str.strip();

    return parsed_input_str;

def handle_single_quote_str(str_arr):
    parsed_input_str = '';
    is_empty_quoted_str = len(str_arr) and not str_arr[0] == '';

    for str in str_arr:
        if(str == " "):
            parsed_input_str += " ";
        elif(str.count("'") >= 2):
            parsed_input_str += str;    
        elif(len(str) and str[0] == " "):
            parsed_input_str += str;
        elif(len(str) and str[len(str)-1] == " "):
            parsed_input_str += str;
        elif(is_empty_quoted_str):
            # print(f"split arr: {str.split("\\")}")
            parsed_input_str += ' '.join(str.split());
        else:
            parsed_input_str += str    
        
    return parsed_input_str.replace("'","");   

def get_single_quotes_occurrence_after_backticks(input_str):
    print(f"input str: {input_str}")
    back_ticks_count = 0;
    back_ticks_before_quote = [];

    for index, char in enumerate(input_str):
        char = input_str[index];
        if(not index == len(input_str) - 1 and char=="\\" and input_str[index + 1] == "'"):
            back_ticks_count += 1;
            back_ticks_before_quote.append(back_ticks_count);    
        elif(char == '\\'):
            back_ticks_count += 1;   

    return back_ticks_before_quote;            

def parse_back_ticks(input_str, back_ticks_before_quotes):
    parsed_str = "";
    index = 0;
    back_ticks_count = 0;

    while index < len(input_str):
        char = input_str[index];

        if(char == "\\"):
            back_ticks_count += 1;

            if(back_ticks_count in back_ticks_before_quotes):
                char = input_str[index + 1] if not index == len(input_str) - 1 else ''; 
                parsed_str +=  f"'{char}"
                index += 2;
            elif(index == len(input_str) - 1):
                index += 1;
                continue; 
            else:          
                parsed_str += input_str[index + 1];
                index += 2;
        else:
            parsed_str += char;  
            index +=1;  

    return parsed_str;

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
            # back_ticks_parsed_str = parse_back_ticks(input_str)
            # parsed_input_str = parse_input_str(back_ticks_parsed_str);
            back_ticks_before_quotes = get_single_quotes_occurrence_after_backticks(input_str);
            parsed_input_str = parse_input_str(input_str);
            back_ticks_parsed_str = parse_back_ticks(parsed_input_str, back_ticks_before_quotes);
            print(back_ticks_parsed_str);
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
          back_ticks_before_quotes = get_single_quotes_occurrence_after_backticks(input_str);
          parsed_input_arr = parse_input_str(input_str, True);
          back_ticks_parsed_str = parse_back_ticks(parsed_input_arr, back_ticks_before_quotes)
       
          for file_path_input in back_ticks_parsed_str:
            if(not file_path_input.strip()):
                continue;

            if(os.path.exists(file_path_input) and os.path.isfile(file_path_input)):
                with open(file_path_input) as file:
                    content = file.read();
                    file_contents += content;   
            else:
                continue; 

          sys.stdout.write(f"{file_contents}");       

        else:    
            exec_config = is_command_executable(command);
            if(exec_config['is_executable']):
                subprocess.run([command, *command_args]);
            else:    
                print(f"{command}: command not found");
    
if __name__ == "__main__":
    main()


