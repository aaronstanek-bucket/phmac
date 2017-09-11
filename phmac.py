from phmac_compiler import py_html_macro_node as node
from phmac_compiler import my_custom
from phmac_compiler import load as file_to_tree
import sys

def make_dict(ins):
    lookin = []
    libs = []
    comp = []
    macros = []
    for x in ins.subs:
        if x.text=="look-in":
            for y in x.subs:
                lookin.append(y.text)
        elif x.text=="libs":
            for y in x.subs:
                libs.append(y.text)
        elif x.text=="compile":
            for y in x.subs:
                comp.append([y.text,y.subs[0].text])
        elif x.text=="macro-files":
            for y in x.subs:
                macros.append(y.text)
        else:
            raise Exception("Command ("+str(x.text)+") not recognized")
    ou = dict()
    ou["look-in"] = lookin
    ou["libs"] = libs
    ou["compile"] = comp
    ou["macros"] = macros
    return ou

def addString(b,s):
    w = s.encode("utf8")
    for x in w:
        b.append(x)

def make_python(d):
    ou = []
    addString(ou,"import sys\n")
    for x in d["look-in"]:
        addString(ou,"sys.path.append(\"")
        addString(ou,x)
        addString(ou,"\")\n")
    addString(ou,"from phmac_compiler import load_and_run as MACRO_THE_STUFF\n")
    addString(ou,"from phmac_compiler import main as DO_THE_STUFF\n")
    for x in d["libs"]:
        addString(ou,"import phmac_stdlib\n")
    for x in d["macros"]:
        addString(ou,"MACRO_THE_STUFF(\"")
        addString(ou,x)
        addString(ou,"\")\n")
    for x in d["compile"]:
        addString(ou,"DO_THE_STUFF(\"")
        addString(ou,x[0])
        addString(ou,"\",\"")
        addString(ou,x[1])
        addString(ou,"\")\n")
    return ou

def save(data):
    outfile = open("make.py","wb")
    outfile.truncate(0)
    outfile.seek(0,0)
    outfile.write(bytes(data))
    outfile.close()

def main():
    ins = file_to_tree(sys.argv[1])
    d = make_dict(ins)
    del(ins)
    py = make_python(d)
    del(d)
    save(py)

main()
