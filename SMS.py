import tkinter as tk
from tkinter import filedialog
from twilio.rest import Client
import pandas as pd
import time

# Find your Account SID and Auth Token at twilio.com/console
account_sid = ''
auth_token = ''
client = Client(account_sid, auth_token)

def fetch_carrier_info(csv_path):
    # Read the CSV file into a DataFrame
    df = pd.read_csv(csv_path)

    # Remove parentheses and dashes from phone numbers
    df['Phone Number'] = df['Phone Number'].str.replace(r'[() ]', '', regex=True)
    df['Phone Number'] = df['Phone Number'].str.replace('-', '')

    results = []

    # Iterate through the rows and fetch carrier information
    for phone_number in df['Phone Number']:
        if pd.notna(phone_number) and str(phone_number).strip() != "":
            phone_info = client.lookups.v1.phone_numbers(phone_number).fetch(type=['carrier'])
            carrier_info = phone_info.carrier
            carrier_name = carrier_info.get('name', '')

            # Map the carrier information to an email domain
            if carrier_name == "T-Mobile USA, Inc.":
                carrier_email = "tmomail.net"
            elif carrier_name == "Verizon Wireless":
                carrier_email = "vtext.com"
            elif carrier_name == "AT&T Wireless":
                carrier_email = "txt.att.net"
            # Add more carrier mappings as needed
            else:
                carrier_email = "Unknown Carrier"

            result = f"{phone_info.phone_number[2:]}@{carrier_email}"
            results.append(result)

    return results

def save_to_csv(results, original_file):
    # Filter out NaN results
    results = [result for result in results if result != 'NaN or Empty']

    # Create a DataFrame from the results
    result_df = pd.DataFrame(results, columns=['Alternate_Emails'])

    # Extract the original file name (excluding the path and extension)
    original_file_name = filedialog.asksaveasfilename(filetypes=[("CSV Files", "*.csv")])
    original_file_name = original_file_name.split("/")[-1].split(".")[0]

    # Measure the time it takes to save the DataFrame to a new CSV file
    start_time = time.time()
    output_file = f"{original_file_name}_Edited.csv"
    result_df.to_csv(output_file, index=False)
    end_time = time.time()

    print(f"Time taken to create the new CSV file: {end_time - start_time} seconds")

def open_file_dialog():
    # Open a file dialog to select the CSV file
    file_path = filedialog.askopenfilename(title="Select CSV File", filetypes=[("CSV Files", "*.csv")])
    if file_path:
        results = fetch_carrier_info(file_path)

        # Save results to a new CSV file
        save_to_csv(results, file_path)

        # Close the tkinter UI
        root.destroy()

# Create the main window
root = tk.Tk()
root.title("SMS Conversion")

# Set window size and position
window_width = 400
window_height = 300
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
x_position = (screen_width - window_width) // 2
y_position = (screen_height - window_height) // 2
root.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")

# Create a header label
header_label = tk.Label(root, text="Select CSV", font=("Helvetica", 16))
header_label.pack(pady=20)

# Create a "Browse" button
browse_button = tk.Button(root, text="Browse", command=open_file_dialog, width=15, height=2)
browse_button.pack()

# Start the main loop
root.mainloop()
