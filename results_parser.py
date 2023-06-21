import pandas as pd

data = []

# Read the input text file
with open('results_parsed.txt', 'r') as file:
    lines = file.readlines()

# Parse the lines and extract the relevant information
for i in range(len(lines)):
    line = lines[i].strip()
    if line.startswith("GAME:"):
        game_name = line.split(':')[1].strip()
        game_name = game_name.replace('-', '')
    elif line.startswith("iter details"):
        details = line.split(':')[1].strip().split(', ')
        std_w = float(details[0].split('-')[1])
        std_func = details[1].split('-')[1]
        func_param = details[2].split('-')[1]
        iter1 = int(details[3].split('-')[1])
        iter2 = int(details[4].split('-')[1])        
        results_mean = float(lines[i + 2].split(':')[1].strip())
        results_std = float(lines[i + 3].split(':')[1].strip())

        game_name_to_write = f'{game_name}_{func_param}' if func_param != 'None' else game_name
        # Append the extracted information as a dictionary
        data.append({'game': game_name_to_write, 'std_w': std_w, 'std_func': std_func,
                     'iter1': iter1, 'iter2': iter2,
                     'results_mean': results_mean,
                     'results_std': results_std})

# Create a DataFrame from the extracted data
df = pd.DataFrame(data)

# Write the DataFrame into a CSV file
df.to_csv('output.csv', index=False)