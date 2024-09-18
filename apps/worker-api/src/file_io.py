import os


def save_files(directory_path, file_names, extracted_files):
    for filename in file_names:
        save_file(directory_path, filename, extracted_files)


def save_file(directory_path, filename, extracted_files):
    if filename in extracted_files:
        with open(os.path.join(directory_path, filename), "w") as f:
            f.write(extracted_files[filename])
        print(f"{filename} saved successfully.")
    else:
        print(f"{filename} not found in the output.")
