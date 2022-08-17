from os import path
import sys
path_name = path.dirname(path.dirname(__file__))
if path_name not in sys.path:
    sys.path.insert(0, path_name)
import pygine

print("#### Full help on pygine ####")
print(help(pygine))
print("#######################################################################")

for obj in dir(pygine):
    if obj and not obj.startswith("__") and obj.upper() != obj:
        print("#######################################################################")
        print(eval(f"help(pygine.{obj})"))