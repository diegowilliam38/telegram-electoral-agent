import sys
import os
import site

print("Executable:", sys.executable)
print("Version:", sys.version)
print("\nsys.path:")
for p in sys.path:
    print(p)

print("\nUser Site Packages:", site.getusersitepackages())

print("\nAttempting to import langchain...")
try:
    import langchain
    print("Files:", langchain.__file__)
except ImportError as e:
    print("ImportError:", e)

try:
    import langchain_community
    print("Langchain Community:", langchain_community.__file__)
except ImportError as e:
    print("Langchain Community ImportError:", e)
