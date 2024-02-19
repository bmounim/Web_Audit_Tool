# Check existing remotes
git remote -v

# Change remote URL if necessary
git remote set-url origin https://github.com/bmounim/Web-Image-Analysis-App.git

# Install Git LFS (follow installation instructions on the Git LFS website)
# Initialize Git LFS
git lfs install

# Track large files
git lfs track "*.png"

# Add the .gitattributes file and re-add large files
git add .gitattributes
git add .

# Commit and push your changes
git commit -m "Configure Git LFS and add large files"
git push origin main
