
from re import L
import stat
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

def parse_input_str(input_str):
    is_double_quotes_str = input_str and input_str[0] == '"' and input_str[len(input_str) - 1] == '"';

    if(is_double_quotes_str):
        str_arr = input_str.split('"');
        parsed_str = handle_double_quotes_str(str_arr);
    else:
        str_arr = input_str.split("'");  
        parsed_str = handle_single_quote_str(str_arr)

    return parsed_str;  



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
            parsed_input_str += ' '.join(str.split());
        else:
            parsed_input_str += str    
        
    return parsed_input_str.replace("'","");         

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

def track_back_slash_chars(input_str):
    back_slash_chars = [];
    index = 0;
    is_str_wrapped_in_single_quotes = input_str and input_str[0] == "'" and input_str[len(input_str) - 1] == "'";

    if(is_str_wrapped_in_single_quotes):
        return [];

    while(index < len(input_str)):
        char = input_str[index];
        if(char == "\\" and not index == len(input_str) - 1):
            back_slash_chars.append(input_str[index + 1]);
            index += 2
        else:
            index += 1;    

    return back_slash_chars;        




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

def parse_back_slash_str(input_str, back_slash_char_arr):
    index = 0;
    parsed_str = "";

    if(not len(back_slash_char_arr)):
        return input_str;

    while(index < len(input_str)):
        char = input_str[index];

        if(char == "\\" and not index == len(input_str) - 1):
            back_slash_char = back_slash_char_arr.pop(0);
            parsed_str += back_slash_char; 
            next_char_in_str = input_str[index + 1];

            if((back_slash_char == "'" or back_slash_char == '"' ) and not next_char_in_str == back_slash_char):
                index += 1;
            else:    
                index += 2;
        else:
            parsed_str += char;
            index += 1;

    if(len(back_slash_char_arr)):
       parsed_str = parsed_str[:-1];
       parsed_str += back_slash_char_arr.pop(0);         

    return parsed_str;            

# 3 state normal. single. double
# default is normal => if char == " " end of string, append it [];
# state => normal and char== " ' " then state => single
# keep adding chars until char == " ' "
# then state=> normal , add that string to [] wrapped in single quotes.

# state => normal and char == '"' then state => double
# keep adding chars until char == '"' then append it 
# state => normal , parsed-str = "";

def get_cat_string_arr(input_str):
    cat_str_arr = [];
    index = 0;
    state = "normal";
    parsed_str = "";

    while(index < len(input_str)):
        char = input_str[index];

        if(state == "normal"):
            if(char == " "):
                cat_str_arr.append(parsed_str);
                parsed_str = "";
            elif(char == "'"):
                state = "single_quote";  
            elif(char == '"'):
                state = "double_quote";         
            else:
                parsed_str += char;

        elif(state == "single_quote"):
            # end of single quote str
            if(char == "'"):
                cat_str_arr.append(f"'{parsed_str}'");
                parsed_str = "";
                state = "normal";
            else:
                parsed_str += char 

        elif(state == 'double_quote'):
            #end of double quote
            if(char == '"'):
                cat_str_arr.append(f'"{parsed_str}');
                parsed_str = "";
                state = "normal";
            else:
                parsed_str += char               

        index += 1;  

    # any pending last str
    if(parsed_str):
        cat_str_arr.append(parsed_str);     

    return list(filter(None, cat_str_arr));         



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
            back_slash_chars = track_back_slash_chars(input_str);
            parsed_input_str = parse_input_str(input_str);
            back_ticks_parsed_str = parse_back_slash_str(parsed_input_str, back_slash_chars);

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
          cat_str_arr = get_cat_string_arr(input_str);

          for file_path_input in cat_str_arr:
            back_slash_chars = track_back_slash_chars(file_path_input);
            parsed_input_str = parse_input_str(file_path_input);
            back_slash_parsed_file_path = parse_back_slash_str(parsed_input_str, back_slash_chars);

            if(not back_slash_parsed_file_path.strip()):
                continue;

            if(os.path.exists(back_slash_parsed_file_path) and os.path.isfile(back_slash_parsed_file_path)):
                with open(back_slash_parsed_file_path) as file:
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




