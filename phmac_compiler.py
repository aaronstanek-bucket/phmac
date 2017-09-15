import sys

if sys.version_info.major!=3:
    raise Exception("This software was written for Python 3. Using other versions of Python may cause bugs. Please use Python 3.")

class py_html_macro_node:
    def __init__(self):
        self.mode = 0
        self.ty= "?"
        self.text = ""
        self.tag = ""
        self.args = ""
        self.subs = []
    def addSub(self):
        self.subs.append(py_html_macro_node())
        return self.subs[-1]
    def convert(self):
        self.mode = 1
        if self.text[0]=="<":
            self.ty = "b"
        elif self.text[0]==">":
            self.ty = "u"
        else:
            self.ty = "t"
            return
        u = ""
        i = 1
        while i < len(self.text):
            if self.text[i]==" ":
                break
            i = i+1
        self.tag = self.text[1:i]
        self.args = self.text[i+1:]

def readfile(filename):
    infile = open(filename,"rb")
    indata = list(infile.read())
    indata.append(10)
    infile.close()
    return indata

def parsefiledata(filedata):
    ou = []
    k = []
    foundText = False
    count = 0
    for x in filedata:
        if x==13:
            continue
        if x==10:
            if foundText:
                ou.append([count,bytes(k).decode("utf8")])
            k = []
            foundText = False
            count = 0
            continue
        if foundText==False:
            if x==32:
                count = count+1
                continue
            if x==9:
                count = count+1
                continue
            foundText = True
        k.append(x)
    return ou

def assemble(par):
    ou = py_html_macro_node()
    ou.text = "<html"
    ou.convert()
    j = [[-1,ou]]
    for x in par:
        while j[-1][0]>=x[0]:
            j.pop()
        j.append([x[0],j[-1][1].addSub()])
        j[-1][1].text = x[1]
        j[-1][1].convert()
    return ou

def load(filename):
    raw = readfile(filename)
    par = parsefiledata(raw)
    del(raw)
    ou = assemble(par)
    return ou

auto = {"area","base","br","col","command","embed","hr","img","input","keygen","link","meta","param","source","track","wbr"}

class custom_tag_block:
    def __init__(self):
        self.lookup = dict()
    def add(self,tag_name,func):
        self.lookup[tag_name] = func

my_custom =  custom_tag_block()

class HTML_encoder:
    def addString(self,s):
        w = s.encode("utf8")
        for x in w:
            self.html.append(x)
    def node_text(self,node):
        self.addString(node.text)
    def node_open(self,node):
        if node.ty=="t":
            self.node_text(node)
        elif node.ty=="b":
            self.addString("<")
            self.addString(node.tag)
            if node.args!="":
                self.addString(" ")
                self.addString(node.args)
            self.addString(">")
        else:
            if node.tag not in my_custom.lookup:
                raise Exception("Unknown custom tag: "+node.tag)
            f = my_custom.lookup[node.tag]
            n = f(node)
            if ((n.ty!="t") and (n.ty!="b")):
                raise Exception("Custom tag failed: "+node.tag)
            self.p[-1][1] = n
            self.p[-2][1].subs[self.p[-1][0]] = n
            self.node_open(n)
    def node_close(self,node):
        if node.ty=="b":
            if node.tag not in auto:
                self.addString("</")
                self.addString(node.tag)
                self.addString(">")
    def goto_next(self):
        if len(self.p[-1][1].subs)!=0:
            self.p.append([0,self.p[-1][1].subs[0]])
            self.node_open(self.p[-1][1])
            return
        while True:
            self.node_close(self.p[-1][1])
            if len(self.p)==1:
                self.p = []
                return
            if (self.p[-1][0]+1)<len(self.p[-2][1].subs):
                self.p[-1] = [self.p[-1][0]+1,self.p[-2][1].subs[self.p[-1][0]+1]]
                self.node_open(self.p[-1][1])
                return
            self.p.pop()
    def __call__(self,root):
        self.html = []
        self.addString("<!DOCTYPE html>")
        self.p = [[0,root]]
        self.node_open(root)
        while len(self.p)!=0:
            self.goto_next()
        ou = bytes(self.html).decode("utf8")
        del(self.html)
        del(self.p)
        return ou

def encode(node,filename):
    my_encoder = HTML_encoder()
    s = my_encoder(node)
    outfile = open(filename,"w")
    outfile.truncate(0)
    outfile.seek(0,0)
    outfile.write(s)
    outfile.close()

def main(input_filename,output_filename):
    node = load(input_filename)
    encode(node,output_filename)

def load_and_run(input_filename):
    node = load(input_filename)
    my_encoder = HTML_encoder()
    my_encoder(node)

def partial(input_filename,output_filename):
    node = load(input_filename)
    my_encoder = HTML_encoder()
    s = my_encoder(node)
    s = s[21:-7]
    outfile = open(output_filename,"w")
    outfile.truncate(0)
    outfile.seek(0,0)
    outfile.write(s)
    outfile.close()

if __name__=="__main__":
    main(sys.argv[1],sys.argv[2])
