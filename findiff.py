#!/usr/bin/env python
#encoding=utf-8


import os
import sys
import time
import filecmp
import shutil
import cmd
from timeit import Timer
from datetime import datetime

#dir =  os.path.dirname(os.path.abspath(__file__))
def visit(find_path):
    if not os.path.exists(find_path):
        print  "path not existed: %s" %find_path
        "visit() takes exactly 1 argument (0 given) "
        sys.exit()
    sep = os.path.sep
    dir_results=list()
    file_results=list()
    for nowpath,dirs,files in os.walk(find_path):
        dir_results.extend([nowpath +sep+ i for i in dirs])
        file_results.extend([nowpath +sep+ i for i in files])
    return {"root":find_path,"dir":dir_results,"file":file_results}
   
   
def filediff(pathA, pathB):
    file_pathA = [path[len(pathA["root"]):] for path in pathA["file"] if path] 
    file_pathB = [path[len(pathB["root"]):] for path in pathB["file"] if path]
    rootA = pathA["root"]
    rootB = pathB["root"]
    setA = set(file_pathA)
    setB = set(file_pathB)
    onlyA = list(setA - setB)
    onlyB = list(setB - setA)
    AandB = setA&setB
    diffAB = [file for file in AandB if not filecmp.cmp(rootA + file, rootB + file)]
    return {"rootA":rootA,"rootB":rootB,\
    "onlyA":onlyA, "onlyB":onlyB, "diffAB":diffAB}
   
   
def movefile(diff_result, path_out = None):
    if not diff_result:
        print  "path not existed\
        \nmovefile() takes exactly 1 argument (0 given) "
        sys.exit()
    sep = os.path.sep
    differents = []
    new_file = []
    will_change_file = []
    differents.extend(diff_result["diffAB"])
    differents.extend(diff_result["onlyA"])
    for diff in differents:
        file_A = diff_result["rootA"] + diff
        file_B = diff_result["rootB"] + diff
        dir_B = os.path.dirname(file_B)
        if path_out:
            file_out = path_out + diff
            dir_out = os.path.dirname(file_out)
        else:
            file_out = file_B
            dir_out = dir_B
        if os.path.exists(file_out): 
            #print file_out
            #备份后复制
            os.rename(file_out, file_out + r".bak_%s"\
            %datetime.now().strftime("%Y%m%d_%H%M%S"))
        elif not os.path.exists(dir_out):
            #创建目录复制
            os.makedirs(dir_out)
        shutil.copyfile(file_A, file_out)
        new_file.append(file_A)
        will_change_file.append(file_out)
    return [new_file,will_change_file]
            

def diffmain(root_a, root_b, path_out = None):
    sep = os.path.sep
    root_a = root_a.replace("\\",sep).replace("/",sep)
    root_b = root_b.replace("\\",sep).replace("/",sep)
    if root_a[-1] != sep:
        root_a += sep 
    if root_b[-1] != sep:
        root_b += sep
    if path_out:
        path_out = path_out.replace("\\",sep).replace("/",sep)
        if path_out[-1] != sep:
            path_out += sep
    pathA = visit(root_a)#用raw获取的路径已经转义，可以识别中文路径，但是直接输如字符串的话可能由于没有转译好导致不能识别中文路径问题
    pathB = visit(root_b)#r"C:\Users\Gary\Desktop\project\polo_ad_app_new")#r"C:\Users\Gary\Desktop\tt")
    diffs = filediff(pathA,pathB)
    chage_str = "%s\n"%datetime.now()
    for key in ["rootA", "rootB", "onlyA", "onlyB", "diffAB"]:
        chage_str += "\n%s:\n"%key +"="*75 
        if key not in ["rootA","rootB"]:
            for value in diffs[key]:
                if key == "onlyA":
                    if value[0] in ["\\","/"]:
                        chage_str += "\n" + diffs["rootA"]+value[1:]  
                    else:
                        chage_str += "\n" + diffs["rootA"]+value
                elif key == "onlyB":
                    if value[0] in [r"\\",r"/"]:
                        chage_str += "\n" + diffs["rootB"]+value[1:]
                    else:
                        chage_str += "\n" + diffs["rootB"]+value
                elif key == "diffAB":
                    chage_str += "\n" + value
        else:
            chage_str += "\n" +  diffs[key]
    print chage_str
    if "y" == raw_input("do you want replace[y/n](n)\n> "):
        new_file,will_change_file = movefile(diffs, path_out)
        move_str = ""
        if len(new_file)==len(will_change_file) != 0:
            move_str += "\nchanged:\n" +"="*75 
            for  num in range(len(new_file)):
                move_str += '\n' + new_file[num] +"-->"+will_change_file[num]
            print move_str
        if path_out:
            log_content = path_out
        else:
            log_content = os.path.dirname(os.path.abspath(__file__))+sep
        print "log content:",log_content
        f = open(log_content + "changed.log","a")
        f.write(chage_str+move_str)
        f.close()
            
class Command(cmd.Cmd):
    def do_help(self,line):
        print "\npython findiff.py [-f path_of_you_changed path_of_you_need_replace [-out path_out]]\
        \nif no path_out the file will replace path_you_need_replace\
        \nelse under path_out\
        \nwarning : don't create path_out;all path are abspath;\
        "
        
if __name__ == "__main__":  
    if len(sys.argv) ==6 and sys.argv[1].lower() == "-f" and sys.argv[4].lower() == "-out" :
        path_a = sys.argv[2]
        path_b = sys.argv[3]
        path_out = sys.argv[5]
        diffmain(path_a,path_b,path_out)
    elif len(sys.argv) ==4 and sys.argv[1].lower() == "-f":
        path_a = sys.argv[2]
        path_b = sys.argv[3]
        diffmain(path_a,path_b)    
    else:
        Command().onecmd("help")
