# WSU Archive Search Tool

Welcome to the WSU Archive Search Tool! This program helps you search through archival collection files (in XML format) to find materials related to your research questions. 

## What You'll Need

- A Windows computer (Windows 10 or 11 recommended)
- At least 16 GB of RAM (32 GB is better)
- 50 GB of free disk space
- An internet connection
- An OpenAI API key (we'll help you get this)
- A folder containing your XML collection files

## Step-by-Step Setup Guide

### Step 1: Install Python

1. Download Python:
   - Go to [python.org/downloads](https://www.python.org/downloads/)
   - **Important**: Download Python 3.10.x (e.g., Python 3.10.11)
   - Scroll down to find Python 3.10.x if it's not the default download
   - Save the installer to your computer

2. Install Python:
   - Double-click the downloaded file
   - **Important**: Check the box that says "Add Python to PATH"
   - Click "Install Now"
   - Wait for the installation to complete
   - Click "Close" when done

3. Verify Python version:
   - Open PowerShell (press Windows key + X, then press I)
   - Run this command:
     ```powershell
     python --version
     ```
   - You should see "Python 3.10.x" (where x is the minor version number)
   - If you see a different version, you may need to uninstall other Python versions or adjust your PATH

**Note**: This program requires Python 3.10 specifically. Other versions (including newer ones) may cause compatibility issues with the required packages.

### Step 2: Download the Project from GitHub

1. **Get the Project Files**:
   - From the project's repo on GitHub, click the green "Code" button near the top of the page
   - Click "Download ZIP" from the dropdown menu
   - Save the ZIP file to your computer (e.g., in your Downloads folder)

2. **Extract the Files**:
   - Navigate to where you saved the ZIP file
   - Right-click the ZIP file and select "Extract All..."
   - Choose a location to extract to (e.g., `C:\Users\YourUsername\Documents\`)
   - Click "Extract"
   - The extracted folder will be named `WSU_Archive_Search_Tool-master`

3. **Rename the Folder (Optional but Recommended)**:
   - Right-click the extracted folder
   - Select "Rename"
   - Type `WSU_Archive_Search_Tool` and press Enter
   - This makes the folder name simpler and matches the instructions below

4. **Verify the Contents**:
   - Open the folder
   - You should see these important files:
     - `main.py`
     - `requirements.txt`
     - `README.md`
     - `ead_parser.py`
   - If any of these files are missing, you may need to download the project again

### Step 3: Get an OpenAI API Key

**Option A: Get an API Key from the Program Owner (Recommended)**
- Contact the program owner to request an API key
- This is the easiest option and ensures you get a key that's already set up for the program

**Option B: Get Your Own API Key**
1. Create an OpenAI account:
   - Go to [platform.openai.com](https://platform.openai.com/)
   - Click "Sign Up" and create an account
   - Verify your email address

2. Get your API key:
   - Log in to your OpenAI account
   - Click on your profile picture
   - Select "View API keys"
   - Click "Create new secret key"
   - Copy the key and save it somewhere safe

3. Set up the API key as an environment variable:
   - Open PowerShell (press Windows key + X, then press I)
   - Run this command (replace YOUR_API_KEY with your actual key):
     ```powershell
     [System.Environment]::SetEnvironmentVariable('OPENAI_API_KEY', 'YOUR_API_KEY', 'User')
     ```
   - Close and reopen PowerShell for the changes to take effect
   - To verify it worked, run:
     ```powershell
     $env:OPENAI_API_KEY
     ```
     You should see your API key displayed

### Step 4: Set Up the Program

1. Download the program:
   - Download the program files from the repository
   - Extract them to a folder on your computer (e.g., `C:\Users\YourName\Documents\WSU_Archive_Search_Tool`)

2. Install required software:
   - Open PowerShell (press Windows key + X, then press I)
   - Navigate to your program folder:
     ```powershell
     cd "C:\Users\YourName\Documents\WSU_Archive_Search_Tool"
     ```
   - Install the required packages:
     ```powershell
     pip install -r requirements.txt
     ```

3. Add your XML files:
   - Create a folder called `collections` in your program directory
   - Copy your XML files into this folder. This should be the entire WSU collection fileset.

### Step 5: Run the Program

1. First-time setup:
   - Open PowerShell
   - Navigate to your program folder:
     ```powershell
     cd "C:\Users\YourName\Documents\WSU_Archive_Search_Tool"
     ```
   - Run the program with the rebuild flag:
     ```powershell
     python main.py --rebuild
     ```
   - This will process all your XML files and create a search index (this may take some time -- as in 2+ hours)
   - **Note**: You only need to use `--rebuild` the first time you run the program, or if you add new XML files to the collections folder

2. Normal usage (after first-time setup):
   - Open PowerShell
   - Navigate to your program folder
   - Run the program:
     ```powershell
     python main.py
     ```
   - The program will load the existing index and be ready for queries

3. Additional options:
   - To see the documents that were retrieved for your query:
     ```powershell
     python main.py --show_retrieved
     ```
   - To rebuild the index (if you've added new XML files):
     ```powershell
     python main.py --rebuild
     ```
   - To combine both options:
     ```powershell
     python main.py --rebuild --show_retrieved
     ```

4. Searching the archives:
   - Once the program is ready, you can enter your search queries
   - For example:
     - "What collections have information about early Washington State history?"
     - "Find documents related to student life in the 1960s"
     - "Search for materials about agricultural research"
   - Type 'exit' when you want to quit

## Example Queries

Here are some example queries you can try:

1. "Find collections related to World War II at Washington State."
2. "Search for documents about early campus buildings in the 1800s."
3. "What materials exist about student protests in the 1970s?"
4. "Find information about agricultural research in the 1950s."
5. "Search for letters or diaries from early faculty  from 1850-1870."

## Troubleshooting

If you encounter any issues:

1. **Python not found error**:
   - Make sure Python is installed correctly
   - Restart your computer
   - Try running `python --version` in PowerShell to verify installation

2. **Missing files error**:
   - Check that your XML files are in the `collections` folder
   - Make sure the folder name is spelled exactly as "collections"

3. **API key issues**:
   - Verify your OpenAI API key is set correctly:
     ```powershell
     $env:OPENAI_API_KEY
     ```
   - If nothing shows up, you need to set the environment variable again
   - Make sure you have sufficient credits in your OpenAI account

4. **Memory errors**:
   - Close other programs to free up memory
   - Consider using a computer with more RAM

## Tips for Better Searches

1. Be specific in your queries
2. Use natural language (like you're asking a question)
3. Include relevant time periods when possible
4. Try different phrasings if you don't find what you're looking for
5. The program works best with detailed, focused questions

## Need Help?

If you're having trouble with the program:
1. Check the troubleshooting section above
2. Make sure you've followed all setup steps
3. Contact technical support with any error messages you see

Happy searching! 