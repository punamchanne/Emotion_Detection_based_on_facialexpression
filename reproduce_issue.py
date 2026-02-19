import sys
print(f"Python version: {sys.version}")

try:
    print("Importing numpy...")
    import numpy
    print(f"numpy version: {numpy.__version__}")
except ImportError as e:
    print(f"Failed to import numpy: {e}")

try:
    print("Importing scipy...")
    import scipy
    print(f"scipy version: {scipy.__version__}")
except ImportError as e:
    print(f"Failed to import scipy: {e}")

try:
    print("Importing sklearn...")
    import sklearn
    print(f"sklearn version: {sklearn.__version__}")
except ImportError as e:
    print(f"Failed to import sklearn: {e}")

try:
    print("Importing tensorflow...")
    import tensorflow as tf
    print(f"tensorflow version: {tf.__version__}")
except ImportError as e:
    print(f"Failed to import tensorflow: {e}")

try:
    print("Importing tensorflow.keras.models...")
    from tensorflow.keras.models import Sequential
    print("Success: Imported Sequential")
except ImportError as e:
    print(f"Failed to import tensorflow.keras.models: {e}")
