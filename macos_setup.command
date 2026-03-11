#!/bin/bash

# Get the directory where the script is located and navigate there
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"

echo "=========================================="
echo "      MineSync macOS Setup & Launcher      "
echo "=========================================="

# Check if Homebrew is installed
if ! command -v brew &> /dev/null; then
    echo "Homebrew is not installed. Installing Homebrew now..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    
    # Add Homebrew to PATH for the current session (Apple Silicon & Intel paths)
    if [[ -x /opt/homebrew/bin/brew ]]; then
        eval "$(/opt/homebrew/bin/brew shellenv)"
    elif [[ -x /usr/local/bin/brew ]]; then
        eval "$(/usr/local/bin/brew shellenv)"
    fi
else
    echo "Homebrew is already installed. Perfect!"
fi

echo "Checking and installing dependencies (this might take a minute)..."
# Install all required GTK4/Adwaita libraries, Python, and Rclone
brew install rclone python gtk4 libadwaita pygobject3

echo "Starting MineSync..."
# PyGObject installed via Homebrew is bound to Homebrew's Python 3
python3 -m mc_sync_setup.main
