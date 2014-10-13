import re, sys, os

# How many spaces in a tab.
# -1 disables support for spaces as tabs (recommended)
# There are usually 4 spaces in a tab
SPACES_PER_TAB = -1

def throwParseError(msg):
	print("\033[91mParse Error: " + msg + "\033[0m")
	sys.exit(-1)
	
def checkMkDir(directory):
	if not os.path.exists(directory):
		os.makedirs(directory)

class MeseCodeParser:
	class Node:
		def __init__(self, parent, name, value, line, lineno):
			self.line = line
			self.lineno = lineno
			self.name = name
			self.value = value
			self.children = []
		def get(self, name):
			for item in self.children:
				if item.name == name:
					return item
			return None
		def as_list(self):
			retval = []
			for item in self.value.split(","):
				item = item.strip()
				if item != "":
					retval.append(item)
			for item in self.children:
				if item.line != "":
					retval.append(item.line)
			return retval
			
	def parse(self, filename):
		file = open(filename, "r")
		
		self.objects = []
		lineno = 0
		for line in file.readlines():
			lineno += 1
			
			# Remove comments
			if line.find("--") != -1:
				line = line[:line.find("--")]
			if line.strip() == "":
				continue
			
			# Find indentation level
			if SPACES_PER_TAB != -1:
				line = line.replace(SPACES_PER_TAB * " ", "\t")
			indented = 0
			m = re.search('([\\t]+)', line)
			if m:
				indented = len(m.group(1))
				
			# Strip redundant symbols
			line = line.strip()
			
			if indented == 0:
				# Is top level
				self.objects.append(self.createNode(None, line, lineno))
			else:
				count = 1
				if len(self.objects) == 0:
					throwParseError("Unexpected level of indentation on line " + str(lineno))
				node = self.objects[len(self.objects) - 1]
				while count < indented:
					if len(node.children) == 0:
						throwParseError("Unexpected level of indentation on line " + str(lineno))
					node = node.children[len(node.children) - 1]
					count += 1
				node.children.append(self.createNode(node, line, lineno))
				
		return self
		
	def __iter__(self):
		return self.objects.__iter__()
		
	def printOut(self, l, objs):
		for obj in objs:
			print((l*"  ") + obj.name + ": " + obj.value)
			self.printOut(l + 1, obj.children)
					
	def createNode(self, parent, line, lineno):
		return self.Node(parent, line.split(" ")[0], line[len(line.split(" ")[0]) + 1:], line, lineno)
		
class LuaBuilder:
	class Node:
		def __init__(self, name, value):
			self.name   = name
			self.value  = value
			
	def __init__(self):
		self.data = []
	
	def set(self, name, value):
		for item in self.data:
			if item.name == name:
				del item
				break
		self.data.append(self.Node(name, value))
		
	def append(self, name, value):
		for item in self.data:
			if item.name == name:
				item.value.append(value)
				return
		self.data.append(self.Node(name, [value]))
		
	def build(self, header,  indentation):
		retval = header + "{\n"
		for item in self.data:
			retval += (indentation * "\t") + item.name + " = "
			if isinstance(item.value, list):
				retval += "{"
				for i in item.value:
					retval += i + ", "
				retval += "}"
			else:
				retval +=  "\"" + item.value + "\""
			retval += ",\n"
		retval += "})\n"
		return retval
			

def getCode(filename):
	parser = MeseCodeParser().parse(filename)
	modname = None
	index = {}
	for item in parser:
		if item.name == "mod":
			if modname is not None:
				throwParseError("Mod namespace was redefined on line " + str(item.lineno))
			modname = item.value
		elif modname is None:
			throwParseError("Mod namespace was not defined (You missed out 'mod nameofmod' at the beginning of the file)")
			
		if item.name == "node":
			index[item.value] = item
	
	retval = ""
	for item in parser:
		if item.name == "node":
			lb = LuaBuilder()
			lb.set("description", item.value)
			
			groups = item.get("is")
			if groups is not None:
				for group in groups.as_list():
					if group.find("=") == -1:
						lb.append("groups", group + " = 1")
					else:
						lb.append("groups", group)
						
			drops = item.get("drops")
			if drops is not None:
				for drop in drops.as_list():
					try:
						element = index[drop]
						if element.get("name") is not None:
							lb.append("drops", "\"" + element.get("name").value + "\"")
						else:
							lb.append("drops", "\"" + element.value.lower().replace(" ", "_") + "\"")
					except KeyError:
						pass
						
			name = item.get("name")
			if name is None:
				name = item.value.lower().replace(" ", "_")
			else:
				name = name.value
			retval += lb.build("minetest.register_node(\"" + name + "\", ", 1) + "\n"
			
		elif item.name == "script":
			retval += "dofile(minetest.get_modpath(\"" + modname + "\") .. \"" + item.value + "\")\n\n"
			
			
			
	if modname is None:
		throwParseError("Mod namespace was not defined (You missed out 'mod nameofmod' at the beginning of the file)")
		
	print(retval)
	return retval

if __name__ == "__main__":
	if len(sys.argv) == 2:
		Project(sys.argv[1]).write("output")		
	elif len(sys.argv) == 3:
		Project(sys.argv[1]).write(sys.argv[2])
	else:
		print("Usage: mesecode.py path/to/file.mese output/directory")
