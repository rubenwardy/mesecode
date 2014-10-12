import re, sys

# How many spaces in a tab.
# -1 disables support for spaces as tabs (recommended)
# There are usually 4 spaces in a tab
SPACES_PER_TAB = -1

class Node():
	def __init__(self, desc):
		self.desc = desc
		self.name = desc.lower().replace(" ", "_")
		self.groups = []
		self.last_prop = None
		self.type = "node"
		self.eaten = None
		self.drops = []
	def build(self, project):
		name = self.name
		if name.find(":") == -1:
			name = project.modname + ":" + name
		retval = "minetest.register_node(\"" + name + "\", {\n"
		retval += "\tdescription = \"" + self.desc + "\",\n"
		
		if self.eaten is not None:
			retval += "\ton_use = minetest.item_eat(" + self.eaten + "),\n"
		
		is_ground_content = False
		if len(self.groups) > 0:
			retval += "\tgroups = {"
			for group in self.groups:
				if group == "ground":
					is_ground_content = True
					continue
				if group.find("=") == -1:
					group += " = 1"
				retval += group + ", "
			retval += "}\n"
		
		if len(self.drops) == 1:
			retval += "\tdrop = \"" + project.getItemName(self.drops[0]) + "\",\n"
		elif len(self.drops) > 1:
			retval += "\tdrop = {\n"
			for dropped in self.drops:
				retval += "\t\t\"" + project.getItemName(dropped) + "\",\n"
			retval += "\t},"
		
		if is_ground_content:
			retval += "\tis_ground_content = true,\n"
		retval += "})\n"
		return retval

class Script:
	def __init__(self, filename):
		self.filename = filename
		self.type = "script"
	def build(self, project):
		return "dofile(minetest.get_modpath(\"" + project.modname + "\") .. \"" + self.filename + "\")\n"

class ParseError(Exception):
	def __init__(self, value):
		self.value = value
	def __str__(self):
		return self.value
	
def throwParseError(msg):
	print("\033[91mParse Error: " + msg + "\033[0m")
	sys.exit(-1)
	
def parse_list(the_list, line):
	if line == "":
		return
	arr = line.split(",")
	for item in arr:
		item = item.strip()
		if item != "":
			the_list.append(item)

class Project:
	def getItemName(self, desc):
		for item in self.objects:
			if item.type == "node" and item.desc.lower() == desc.lower():
				if item.name.find(":") == -1:
					return self.modname + ":" + item.name
				else:
					return item.name.strip(":")
		return ""
	def __init__(self, filename):
		file = open(filename, "r")

		self.modname = None
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
			
			self.processLine(line, indented, lineno)
			
	def processLine(self, line, indented, lineno):
		if indented > 2 or indented < 0:
			throwParseError("Too many levels of indentation at " + str(lineno))
		elif indented == 0:
			#
			# Top Level Statements
			#
			
			if line.startswith("mod "):
				if self.modname is not None:
					throwParseError("Mod name redefined on line " + str(lineno))
				self.modname = line[4:].strip()
			elif line.startswith("node "):
				self.objects.append(Node(line[5:].strip()))
			elif line.startswith("script "):
				self.objects.append(Script(line[7:].strip()))
			else:				
				throwParseError("Unknown definition on line " + str(lineno))
		else:
			if len(self.objects) == 0:
				throwParseError("Too many levels of indentation at " + str(lineno))
			curobj = self.objects[len(self.objects) - 1]
			
			#
			# Properties
			#
			if indented == 1:
				curobj.last_prop = None
				if line.startswith("is"):
					parse_list(curobj.groups, line[2:].strip())
					curobj.last_prop = curobj.groups
				elif line.startswith("name "):
					curobj.name = line[5:].strip()
				elif line.startswith("eaten "):
					curobj.eaten = line[6:].strip()
				elif curobj.type == "node":
					if line.startswith("drops "):
						parse_list(curobj.drops, line[6:].strip())
						curobj.last_prop = curobj.drops
					else:
						throwParseError("Unknown property in '" + curobj.type + "/" + curobj.name + "' on line " + str(lineno))
				else:
					throwParseError("Unknown property in '" + curobj.type + "/" + curobj.name + "' on line " + str(lineno))
			#
			# Lists
			#
			elif indented == 2:
				curprop = curobj.last_prop
				if curprop is None:
					throwParseError("Too many levels of indentation at " + str(lineno))
				curprop.append(line)
	
	def write(self, directory):
		print("-- Mod namespace: " + self.modname)
		print("-- Generated using the Minetest Readable Modding Format\n")
		for item in self.objects:
			print(item.build(self))
				
				
Project("test.mese").write("test")
