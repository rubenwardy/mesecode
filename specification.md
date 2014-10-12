Minetest Readable Modding Format
================================

(Just a specification, a converter has not been written)

Here is the definition of default:stone:

```
mod default

node Stone
	is ground, cracky, stone
	drops Cobble
```

This is translated into the following code:

```Lua
minetest.register_node("default:stone", {
	description = "Stone",
	tiles = {"default_stone.png"},
	is_ground_content = true,
	groups = {cracky=3, stone=1},
	drop = 'default:cobble'
})
```

Line 1 in the script file declares the name of this mod.

Line 3 is the start of the definition of a node.
The description is just the phrase after 'node'.
The node's name is a decapitalised version of the description,
with underscores instead of spaces.
The tile is in the form modname_itemname.png.

Overwriting description and name
--------------------------------

It is possible to overwrite the name of a node or item.
For example:

```
mod some_foods

node Milk Chocolate Bar
	name chocolate_milk
	eaten 2
```

Lists
-----

Some properties require lists.
These two code snippets do exactly the same thing:

```
node test
	is one, two, three
```


```
node test
	is
		one
		two
		three
```
Tiles
-----

Sometimes you want to give a node multiple tiles.

```
mod compass

node Compass
	6 tiles
	is cracky, oddly_breakable_by_hand
```

Allows compass_compass_top.png, compass_compass_left.png, compass_compass_back.png, etc to be used.

You can use the tiles property as a list, like this:

```
mod special_grass

node grass
	tiles
		top.png
		bottom.png
		right.png
		left.png
		back.png
		front.png
```

Lua Scripting
-------------

```
script script1.lua
```

```
node furnace
	on right click: function
	on punch: script2.lua
```

```
!! Lua



!! End Lua
```
