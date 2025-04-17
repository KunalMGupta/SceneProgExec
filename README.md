# 🚀 SceneProgExec: Blender Python Script & Package Manager

**SceneProgExec** is a command-line tool and Python module that enables seamless execution of **Blender scripts** and **package management** within Blender's **isolated Python environment**.

## 🔥 Features
✅ **Execute Python scripts inside Blender**  
✅ **Install Python packages in Blender's Python environment**  
✅ **Perform a full reset (remove all third-party packages)**  
✅ **Works both as a CLI tool and a Python module**  
---

## 📥 Installation

### **1️⃣ Install from PyPI**
```bash
pip install sceneprogexec
```

OR **Clone the Repository**
```bash
git clone https://github.com/KunalMGupta/SceneProgExec.git
cd SceneProgExec
pip install .
```

### **2️⃣ Set Environment Variables**
Before using `SceneProgExec`, set the required environment variables:

```bash
export BLENDER_PATH=/Applications/Blender.app/Contents/MacOS/Blender
export BLENDER_PYTHON=/Applications/Blender.app/Contents/Resources/4.3/python/bin/python3.11
```

To make this **permanent**, add the lines to your `~/.bashrc` or `~/.zshrc`:
```bash
echo 'export BLENDER_PATH=/Applications/Blender.app/Contents/MacOS/Blender' >> ~/.zshrc
echo 'export BLENDER_PYTHON=/Applications/Blender.app/Contents/Resources/4.3/python/bin/python3.11' >> ~/.zshrc
source ~/.zshrc
```

### **3️⃣ Run CLI Commands**
Once installed, you can use `sceneprogexec` globally.

---

## 🛠️ Usage

### **🔹 Run a Python Script Inside Blender**
```bash
sceneprogexec run my_script.py --target my_scene.blend
```
✅ Runs `my_script.py` inside **Blender**.

---

### **🔹 Install Packages Inside Blender**
```bash
sceneprogexec install numpy pandas
```
✅ Installs `numpy` and `pandas` inside **Blender’s Python**.

---

### **🔹 Install Packages With a Hard Reset**
```bash
sceneprogexec install numpy pandas --reset
```
✅ **Removes all third-party packages** before installing new ones.

---

### **🔹 Reset Blender's Python (Remove All Third-Party Packages)**
```bash
sceneprogexec reset
```
🗑️ **Deletes all third-party Python packages** in Blender.

---

## 🏗️ **Using as a Python Module**
SceneProgExec can also be **imported and used in Python scripts**:

```python
from sceneprogexec import SceneProgExec

executor = SceneProgExec()
executor.install_packages(["numpy"])
executor.run_script("my_script.py")
executor._delete_all_third_party_packages()  # Hard reset

script = """
import bpy
print("Hello, World!")
"""
executor(script, target="test.blend")
```

---

## 🚀 **Automatic Cleanup**
- **Temporary directory (`blender_tmp`) is deleted** after execution.
- **No leftover logs or scripts clutter your system**.

---

## 🛠️ **Troubleshooting**
❌ **Blender not found?**  
Ensure `BLENDER_PATH` and `BLENDER_PYTHON` are correctly set. Run:
```bash
echo $BLENDER_PATH
echo $BLENDER_PYTHON
```

❌ **Permission denied?**  
Try:
```bash
chmod +x /usr/local/bin/sceneprogexec
```

❌ **Blender script fails to execute?**  
Check the log:
```bash
cat blender_tmp/blender_log.txt
```

---

## 📝 License
This project is licensed under the **MIT License**.

---

## 👨‍💻 Author
Developed by **Kunal Gupta**  
GitHub: [KunalMGupta](https://github.com/KunalMGupta)

---

## ⭐ **Support the Project**
If you find this tool useful, give it a ⭐ on GitHub!