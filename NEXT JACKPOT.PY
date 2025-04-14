import pandas as pd
import numpy as np
import random

# Function to count occurrences of each number and sort them by frequency
def count_ball_frequencies(file_path, white_range, special_range, special_ball_name):
    df = pd.read_excel(file_path)
    df.columns = df.columns.str.strip()

    df['Is_Winner'] = df['Winner'].astype(str).str.contains(r'\*', regex=True, na=False)

    df[['White Ball 1', 'White Ball 2', 'White Ball 3', 'White Ball 4', 'White Ball 5']] = df['White Ball'].str.split(',', expand=True, n=4)
    df[['White Ball 1', 'White Ball 2', 'White Ball 3', 'White Ball 4', 'White Ball 5']] = df[['White Ball 1', 'White Ball 2', 'White Ball 3', 'White Ball 4', 'White Ball 5']].apply(lambda x: x.str.lstrip('0').astype(int))

    white_ball_cols = ['White Ball 1', 'White Ball 2', 'White Ball 3', 'White Ball 4', 'White Ball 5']
    all_white_numbers = df[white_ball_cols].values.flatten()
    special_ball_numbers = df[special_ball_name].astype(str).str.lstrip('0').astype(int).values

    winning_white_numbers = df.loc[df['Is_Winner'], white_ball_cols].values.flatten()
    winning_special_numbers = df.loc[df['Is_Winner'], special_ball_name].astype(str).str.lstrip('0').astype(int).values

    white_counts = np.bincount(all_white_numbers, minlength=white_range+1)
    special_counts = np.bincount(special_ball_numbers, minlength=special_range+1)

    for num in winning_white_numbers:
        white_counts[num] += 2

    for num in winning_special_numbers:
        special_counts[num] += 2

    sorted_white_counts = sorted([(i, count) for i, count in enumerate(white_counts) if count > 0], key=lambda x: x[1], reverse=True)
    sorted_special_counts = sorted([(i, count) for i, count in enumerate(special_counts) if count > 0], key=lambda x: x[1], reverse=True)

    return sorted_white_counts, sorted_special_counts

# Function to generate predictions
def generate_predictions(sorted_white_counts, sorted_special_counts, top_white, top_special, num_white=5, num_predictions=5):
    top_white_balls = [num for num, count in sorted_white_counts[:top_white]]
    top_special_balls = [num for num, count in sorted_special_counts[:top_special]]

    predictions = []
    for _ in range(num_predictions):
        white_balls = random.sample(top_white_balls, num_white)
        special_ball = random.choice(top_special_balls)
        predictions.append((sorted(white_balls), special_ball))

    return predictions

# User input for Mega Millions
print("=== Mega Millions Settings ===")
top_mega_white = int(input("How many of the top white balls should we use for Mega Millions? "))
top_mega_special = int(input("How many of the top Mega Balls should we use? "))
num_mega_predictions = int(input("How many Lines of Mega Millions predictions would you like? "))

# Mega Millions
mega_white_counts, mega_ball_counts = count_ball_frequencies("Mega_Millions_Winning_Numbers.xlsx", 70, 25, "Mega Ball")
print("\nMega Millions Predictions:")
mega_predictions = generate_predictions(mega_white_counts, mega_ball_counts, top_mega_white, top_mega_special, num_predictions=num_mega_predictions)
for prediction in mega_predictions:
    print(f"White Balls: {prediction[0]} | Mega Ball: {prediction[1]}")

# User input for Powerball
print("\n=== Powerball Settings ===")
top_power_white = int(input("How many of the top white balls should we use for Powerball? "))
top_power_special = int(input("How many of the top Powerballs should we use? "))
num_power_predictions = int(input("How many Lines of Powerball predictions would you like? "))

# Powerball
power_white_counts, powerball_counts = count_ball_frequencies("Powerball_Winning_Numbers.xlsx", 69, 26, "Powerball")
print("\nPowerball Predictions:")
power_predictions = generate_predictions(power_white_counts, powerball_counts, top_power_white, top_power_special, num_predictions=num_power_predictions)
for prediction in power_predictions:
    print(f"White Balls: {prediction[0]} | Powerball: {prediction[1]}")