
---

# WSU Archive Search Tool README

Welcome to the **WSU Archive Search Tool**! This program helps archivists search through over 4,000 archival collection files (in XML format) to find materials related to their questions—like “What collections have information on Washington State's involvement in the Spanish-American war?” It’s easy to use once set up, and this guide will walk you through everything on a Windows computer, even if you’ve never programmed before.

## What You’ll Need
- A Windows computer (Windows 10 or 11 recommended) with at least **16 GB of RAM** (32 GB is better) and **50 GB of free disk space**.
- An **internet connection** for setup.
- A folder with your XML collection files (e.g., `collections` folder containing files like `NTE2sc014.xml`).
- About **1-2 hours** for setup (depending on your internet speed).

## Step-by-Step Setup Instructions

### Step 1: Install Python
Python is the tool that runs this program. Let’s get it installed.

1. **Download Python**:
   - Open your web browser (e.g., Chrome, Edge) and go to [python.org/downloads](https://www.python.org/downloads/).
   - Click the big yellow button that says **Download Python 3.11.x** (or the latest 3.x version).
   - Save the file (e.g., `python-3.11.x.exe`) to your Downloads folder.

2. **Install Python**:
   - Double-click the downloaded file to run it.
   - **Important**: Check the box that says **Add Python to PATH** at the bottom of the installer window.
   - Click **Install Now** and wait (it’ll take a few minutes).
   - When it says “Setup was successful,” click **Close**.

3. **Check It Worked**:
   - Press `Windows Key + S`, type `cmd`, and hit Enter to open the Command Prompt.
   - Type `python --version` and press Enter.
   - You should see something like `Python 3.11.x`. If you do, great! If not, restart your computer and try again.

### Step 2: Set Up a Project Folder
Let’s organize everything in one place.

1. **Create a Folder**:
   - Open File Explorer (`Windows Key + E`).
   - Go to `C:\Users\YourUsername\Documents` (replace `YourUsername` with your actual username).
   - Right-click, select **New > Folder**, and name it `WSU_Archive_Search`.

2. **Add Your XML Files**:
   - Inside `WSU_Archive_Search`, create a subfolder called `collections`.
   - Copy your 4,000+ XML files (e.g., `NTE2sc014.xml`) into the `collections` folder. You can drag and drop them from wherever they are.

3. **Save the Program**:
   - Copy the code from this project (e.g., `main.py`, provided separately) into a file:
     - Open Notepad (`Windows Key + S`, type `notepad`, hit Enter).
     - Paste the code.
     - Click **File > Save As**, set “Save as type” to **All Files (*.*)**, name it `main.py`, and save it in `C:\Users\YourUsername\Documents\WSU_Archive_Search`.

### Step 3: Install Required Tools
The program needs some extra pieces to work. We’ll install them using the Command Prompt.

1. **Open Command Prompt**:
   - Press `Windows Key + S`, type `cmd`, and hit Enter.

2. **Install Dependencies**:
   - Type each command below, press Enter, and wait for it to finish (it’ll download stuff from the internet):
     - `pip install lxml`
     - `pip install sentence-transformers`
     - `pip install faiss-cpu` *(use `faiss-gpu` if you have an NVIDIA GPU—ask IT if unsure)*
     - `pip install transformers`
     - `pip install torch`
     - `pip install bitsandbytes`
   - Each might take 1-5 minutes depending on your internet speed. You’ll see text scrolling; when it stops and shows a new line like `C:\>`, it’s done.

### Step 4: Get a Hugging Face Token
The program uses a smart language model (Llama) that requires a special key from Hugging Face.

1. **Sign Up**:
   - Open your browser and go to [huggingface.co](https://huggingface.co/).
   - Click **Sign Up** (top right), enter your email, a username, and a password, then click **Create Account**.
   - Check your email for a verification link, click it, and log in.

2. **Request Model Access**:
   - Go to [meta-llama/Meta-Llama-3.1-8B-Instruct](https://huggingface.co/meta-llama/Meta-Llama-3.1-8B-Instruct) (we’ll use the 8B version—it’s lighter).
   - If it says “Gated model,” click **Request Access**, fill out the form (e.g., “Purpose: Archival search tool”), and submit. Approval usually comes within a day.

3. **Get Your Token**:
   - After logging in, click your profile picture (top right) > **Settings** > **Access Tokens**.
   - Click **New Token**, name it (e.g., “ArchiveTool”), select **Read**, and click **Generate**.
   - Copy the token (e.g., `hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`) and save it in a text file (e.g., `token.txt` in your project folder).

### Step 5: Update the Program with Your Token
You need to add your token to the code.

1. **Open the Code**:
   - Open `main.py` in Notepad (right-click `main.py` > **Open with** > **Notepad**).

2. **Find and Replace**:
   - Look for the line `hf_token = "your_hf_token_here"`.
   - Replace `"your_hf_token_here"` with your token (e.g., `hf_token = "hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"`).
   - Save the file (**File > Save**).

### Step 6: Prepare the Search Data (First-Time Setup)
Before searching, the program needs to process your XML files.

1. **Open Command Prompt**:
   - Press `Windows Key + S`, type `cmd`, right-click **Command Prompt**, and select **Run as administrator**.

2. **Navigate to Your Folder**:
   - Type `cd C:\Users\YourUsername\Documents\WSU_Archive_Search` (replace `YourUsername`) and press Enter.

3. **Run the Processing**:
   - Type `python main.py "test query" --process --generate-embeddings` and press Enter.
   - This reads all XML files in the `collections` folder, breaks them into chunks, and builds a search index. It’ll take **1-4 hours** depending on your computer and file count.
   - You’ll see progress messages like “Processing NTE2sc014.xml...” and a progress bar. When it’s done, it’ll save `processed_chunks.json` and `ead_index.faiss` in your folder.

### Step 7: Search the Archives
Now you’re ready to search!

1. **Run a Search**:
   - In the same Command Prompt (still in your project folder), type:
     ```cmd
     python main.py "What collections have information on Washington State's involvement in the Spanish-American war?"

2. **Try Other Queries**:
    - Replace the query with anything you're looking for, like:
    python main.py "What collections might relate to the history of queer students at WSU?"
    python main.py "Where can I look to find letters or diaries written by women between 1750-1754?"

## Troubleshooting
- **Error “Python not found”**: Restart your computer and ensure “Add Python to PATH” was checked during install.
- **Memory Error**: Your computer might not handle the big Llama model. Edit `main.py`, change `llm_model_name` to `"meta-llama/Meta-Llama-3.1-8B-Instruct"`, and rerun Step 6.
- **“Access Denied”**: Double-check your token and model approval. Wait for Hugging Face approval if needed.
- **Still Stuck?**: Ask someone tech-savvy to help, or note the exact error and seek assistance.

## Tips
- **First Run**: Step 6 is only needed once unless you add new XML files.
- **Speed**: If you have a gaming PC with an NVIDIA GPU, install `faiss-gpu` and `torch` with CUDA support for faster processing—ask IT for help.
- **Output**: Results show collections and why they match, making it easy to decide what to pull from the archives.

Enjoy searching the WSU archives with this tool! 