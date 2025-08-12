```
  _    _ _       _   _                 
 | |  | (_)     | | (_)                
 | |  | |_  __ _| |_ _  ___  _ __  ___ 
 | |  | | |/ _` | __| |/ _ \| '_ \/ __|
 | |__| | | (_| | |_| | (_) | | | \__ \
  \____/|_|\__,_|\__|_|\___/|_| |_|___/
                                       
        📝 Auto Question Paper Generator
```

---

# 📝 Auto Question Paper Generator

An **automated pipeline** to parse a `.docx` file containing base questions, generate new multiple-choice questions (MCQs) using either **template-based** or **AI-based (ChatGPT)** methods, create related diagrams/images, and assemble everything into a **final formatted Word document**.

---

## ✨ Features
- 📂 **Parse** `.docx` files and extract base questions + embedded images
- 🤖 **Generate MCQs** using:
  - Template mode (offline, deterministic)
  - AI mode (via OpenAI ChatGPT API)
- 🎨 **Auto-generate diagrams** for certain question types (uniform color tables, packed balls, etc.)
- 📄 **Assemble** all into a final, formatted `.docx` document
- ⚡ **One-click execution** via `run_all.py` with smart skipping, timing, and summary reports
- 🎯 Designed for **Mathematics / Quantitative** type problems but can be adapted for others

---

## 📂 Project Structure
```
HighScores_Assignment/
│
├── input/
│   └── base_questions.docx      # Your source questions file
│
├── output/
│   ├── parsed.json              # Extracted raw text & images from .docx
│   ├── questions.json           # Generated MCQs in JSON format
│   ├── images/                  # Auto-generated question diagrams
│   └── result.docx              # Final formatted Word document
│
├── src/
│   ├── utils.py                 # Common helper functions
│   ├── parse_doc.py             # Extract questions & images from .docx
│   ├── generator.py             # Create MCQs from parsed data
│   ├── image_gen.py             # Create diagrams for questions
│   ├── build_doc.py             # Assemble final Word document
│
├── run_all.py                   # Main automation script
└── README.md                    # Project documentation
```

---

## 📦 Dependencies
Make sure you have **Python 3.8+** installed and then install dependencies:

```bash
pip install python-docx Pillow openai
```

If you use AI mode:
```bash
pip install openai
```

---

## 🚀 Step-by-Step Workflow

### **1️⃣ Parse the DOCX**
Extract raw questions + images:
```bash
python src/parse_doc.py --input input/base_questions.docx --out output/parsed.json
```

---

### **2️⃣ Generate Questions**
Using **template mode**:
```bash
python src/generator.py --mode template --input output/parsed.json --out output/questions.json
```

Using **AI (ChatGPT)**:
```bash
python src/generator.py --mode llm --input output/parsed.json --out output/questions.json --openai_key YOUR_API_KEY
```

---

### **3️⃣ Generate Images**
Automatically creates diagrams based on question type:
```bash
python src/image_gen.py --input output/questions.json --out output/images
```

---

### **4️⃣ Build Final DOCX**
Assemble everything into `result.docx`:
```bash
python src/build_doc.py --input output/questions.json --images output/images --out output/result.docx
```

---

## ⚡ One-Click Automation
Run **everything** with one command:
```bash
python run_all.py
```
Features:
- ⏳ Shows **time taken** for each step
- 🔄 Option to **skip steps** if output already exists
- 🛡 Safe overwrite for `result.docx`
- 📊 Final **summary report**

---

## 🖼 Example Output
- **Extracted Questions** → `output/parsed.json`
- **Generated MCQs** → `output/questions.json`
- **Images** → `output/images/uniform_table.png`, `output/images/packed_balls.png`
- **Final Document** → `output/result.docx`

---

## 🔑 Using AI Mode
If you want AI-generated variations:
1. Get an **OpenAI API Key** from [https://platform.openai.com](https://platform.openai.com)
2. Run:
   ```bash
   python src/generator.py --mode llm --input output/parsed.json --out output/questions.json --openai_key YOUR_API_KEY
   ```
3. Or modify `run_all.py` to always use LLM mode.

---

## 📌 Notes
- The template mode is **offline** and free, AI mode requires API key & credits.
- For **diagram generation**, the script currently supports:
  - Uniform/shirt-pants combination table
  - Packed spheres/balls top-view
- Project is easily extensible to handle more question types and diagrams.

---

## 🛠 Future Improvements
- 🧠 More AI prompt engineering for better question quality
- 📊 Graph-based diagrams for statistics problems
- 🌐 Web UI for uploading `.docx` and downloading results
- 🖼 Support for more image templates

---

## 🏆 Credits
- 💻 Developed with **Python** & ❤️
- 📚 Uses:
  - [`python-docx`](https://python-docx.readthedocs.io/)
  - [`Pillow`](https://python-pillow.org/)
  - [`OpenAI API`](https://platform.openai.com/)

---

**🚀 Happy Question Generating!**
