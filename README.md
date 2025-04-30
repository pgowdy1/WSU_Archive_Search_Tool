# WSU Archive Search Tool

Welcome to the WSU Archive Search Tool! This program helps you search through archival collection files (in XML format) to find materials related to your research questions. It uses advanced AI technology to understand your queries and find relevant documents from the archives.

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
   - Click the big yellow "Download Python" button
   - Save the installer to your computer

2. Install Python:
   - Double-click the downloaded file
   - **Important**: Check the box that says "Add Python to PATH"
   - Click "Install Now"
   - Wait for the installation to complete
   - Click "Close" when done

### Step 2: Get an OpenAI API Key

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

### Step 3: Set Up the Program

1. Download the program:
   - Download the program files from the repository
   - Extract them to a folder on your computer (e.g., `C:\Users\YourName\Documents\WSU_Archive_Search_Tool`)

2. Install required software:
   - Open Command Prompt (press Windows key + R, type `cmd`, press Enter)
   - Navigate to your program folder:
     ```
     cd C:\Users\YourName\Documents\WSU_Archive_Search_Tool
     ```
   - Install the required packages:
     ```
     pip install -r requirements.txt
     ```

3. Add your XML files:
   - Create a folder called `collections` in your program directory
   - Copy your XML files into this folder

### Step 4: Run the Program

1. First-time setup:
   - Open Command Prompt
   - Navigate to your program folder
   - Run the program:
     ```
     python main.py
     ```
   - When prompted, enter your OpenAI API key
   - The program will process your XML files (this may take some time)

2. Searching the archives:
   - Once the program is ready, you can enter your search queries
   - For example:
     - "What collections have information about early Washington State history?"
     - "Find documents related to student life in the 1960s"
     - "Search for materials about agricultural research"
   - Type 'exit' when you want to quit

## Example Queries

Here are some example queries you can try:

1. "Find collections related to World War II at Washington State"
2. "Search for documents about early campus buildings"
3. "What materials exist about student protests in the 1970s?"
4. "Find information about agricultural research in the 1950s"
5. "Search for letters or diaries from early faculty members"

## Troubleshooting

If you encounter any issues:

1. **Python not found error**:
   - Make sure Python is installed correctly
   - Restart your computer
   - Try running `python --version` in Command Prompt to verify installation

2. **Missing files error**:
   - Check that your XML files are in the `collections` folder
   - Make sure the folder name is spelled exactly as "collections"

3. **API key issues**:
   - Verify your OpenAI API key is correct
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