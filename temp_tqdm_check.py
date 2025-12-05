import sys
import os

print("--- sys.path ---")
for p in sys.path:
    print(p)
print("--- os.environ['PATH'] ---")
print(os.environ.get('PATH'))
print("--- Attempting to import tqdm ---")
try:
    import tqdm
    print("tqdm imported successfully from:", tqdm.__file__)
except ImportError as e:
    print(f"ImportError: {e}")
print("--- End of script ---")