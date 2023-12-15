import pickle
import pandas as pd

# Replace 'your_file.pickle' with the path to your .pickle file
file_path = 'dma.pickle'

# Open the .pickle file and load data
with open(file_path, 'rb') as file:
    data = pickle.load(file)

# Now 'data' holds the Python object that was stored in the .pickle file
print(data)