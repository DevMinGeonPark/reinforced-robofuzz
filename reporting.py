import os
import glob

def read_error_files(directory):
    error_files = glob.glob(os.path.join(directory, 'error-*'))
    errors = set()
    
    for file_path in error_files:
        with open(file_path, 'r') as file:
            for line in file:
                errors.add(line.strip())
    
    return errors

def write_error_report(errors, output_file):
    with open(output_file, 'w') as file:
        for error in sorted(errors):
            file.write(f"{error}\n")

if __name__ == "__main__":
    directory = './'
    output_file = 'error-report'
    
    errors = read_error_files(directory)
    write_error_report(errors, output_file)
    
    print(f"Error report generated: {output_file}")
