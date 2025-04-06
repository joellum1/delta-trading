import json

# Open the log file and read its content
with open('output.log', 'r') as file:
    content = file.read()

# Split the content into individual JSON objects by separating at each '}\n{'
log_entries = content.strip().split('}\n{')

# Open the same file in write mode to overwrite existing content
with open('formatted_output.log', 'w') as output_file:
    for entry in log_entries:
        # Add curly braces around each log entry to make it valid JSON
        entry = '{' + entry + '}'
        
        try:
            # Parse the JSON
            parsed_entry = json.loads(entry)
            
            # Write the formatted output to the same file
            output_file.write(f"Timestamp: {parsed_entry['timestamp']}\n")
            output_file.write(f"Sandbox Log: {parsed_entry['sandboxLog']}\n")
            output_file.write(f"Lambda Log:\n{parsed_entry['lambdaLog']}\n")
            output_file.write("-" * 40 + "\n")  # Separator line for readability

        except json.JSONDecodeError:
            output_file.write(f"Error decoding JSON for entry:\n{entry}\n")
            output_file.write("-" * 40 + "\n")

print("Formatted log entries have been written to 'your_log_file.log'.")
