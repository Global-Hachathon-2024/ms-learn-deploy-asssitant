import os


def process_and_save_files(root_dir, required_files, output_dir):
    """
    Process folders containing the required files and save the formatted content to the output directory.

    Args:
        root_dir (str): The root directory to search for folders.
        required_files (list): List of required files that must be present in the folder.
        output_dir (str): The directory where the formatted files will be saved.
    """
    folder_count = 0
    for subdir, _, files in os.walk(root_dir):
        if all(file in files for file in required_files):
            formatted_content = format_file_content(subdir)
            save_formatted_content(formatted_content, output_dir, folder_count)
            folder_count += 1
    return folder_count


def format_file_content(subdir):
    """
    Format the content of the README.md file in the given directory.

    Args:
        subdir (str): The directory containing the README.md file.

    Returns:
        list: The formatted content of the README.md file.
    """
    with open(os.path.join(subdir, "README.md"), "r", encoding="utf-8") as f:
        content = f.readlines()

    # Remove lines starting with ![ or [![
    content = [x for x in content if not x.startswith("![") and not x.startswith("[![")]

    # Add directory path to the file content
    content.insert(0, f"path: {subdir.replace(os.sep, '/')[3:]}\n")

    # Reduce consecutive empty lines to a single empty line
    content = [x for i, x in enumerate(content) if i == 0 or x != content[i - 1] or x != "\n"]
    return content


def save_formatted_content(content, output_dir, count):
    """
    Save the formatted content to a file in the output directory.

    Args:
        content (list): The formatted content to be saved.
        output_dir (str): The directory where the formatted file will be saved.
        count (int): The count used to generate the file name.
    """
    os.makedirs(output_dir, exist_ok=True)
    output_file_path = os.path.join(output_dir, f"{count:03}.txt")
    with open(output_file_path, "w", encoding="utf-8") as f:
        f.writelines(content)


if __name__ == "__main__":
    root_directory = "../quickstarts"
    required_files = [
        "README.md",
        "main.bicep",
        "azuredeploy.json",
        "azuredeploy.parameters.json",
    ]
    output_directory = "ai_search_index"

    matching_folders_count = process_and_save_files(root_directory, required_files, output_directory)
    print(f"Number of folders matching the criteria: {matching_folders_count}")
