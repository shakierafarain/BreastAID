# 📁 Project Structure

Your BreastAID project is now organized in a modular, scalable structure:

```
PSM 2/
├── app.py                          # Main entry point (clean & simple!)
├── firebase_key.json               # Firebase credentials
│
├── config/
│   ├── __init__.py
│   └── firebase_config.py          # Firebase setup & initialization
│
├── pages/
│   ├── __init__.py
│   ├── login.py                    # Login page logic
│   ├── register.py                 # Registration page logic
│   ├── dashboard.py                # Dashboard with assessment history
│   ├── survey.py                   # Multi-step survey form
│   └── result.py                   # Assessment result & recommendations
│
├── utils/
│   ├── __init__.py
│   ├── scoring.py                  # Risk score calculation
│   ├── validators.py               # Form validation & helpers
│   └── firebase_helper.py           # Firebase CRUD operations
│
└── styles/
    ├── __init__.py
    └── theme.py                    # Theme colors & CSS styling
```

## 📋 File Descriptions

### Core Files
- **app.py** - Main router that loads the right page based on user state. Very clean!
  
### Configuration
- **config/firebase_config.py** - Handles Firebase initialization without duplicates

### Pages (User Interface)
- **pages/login.py** - User login with database verification
- **pages/register.py** - New user registration
- **pages/dashboard.py** - Home page + assessment history
- **pages/survey.py** - 4-part survey form + question logic
- **pages/result.py** - Risk score result + recommendations

### Utilities (Business Logic)
- **utils/scoring.py** - Calculate risk score from answers (max 40)
- **utils/validators.py** - Check missing questions, get section headers
- **utils/firebase_helper.py** - Save/load data to/from Firestore

### Styles
- **styles/theme.py** - Pink/coral/yellow theme + CSS classes

---

## ✨ Benefits of This Structure

✅ **Clean & Organized** - Each file has one responsibility  
✅ **Easy to Maintain** - Find code quickly  
✅ **Scalable** - Add new features without cluttering existing files  
✅ **Reusable** - Import functions from utils in any page  
✅ **Testable** - Easy to test individual modules  
✅ **Readable** - No more 700+ line files!  

---

## 🚀 How to Run

```bash
streamlit run app.py
```

That's it! Streamlit will automatically use the modular structure.

---

## 📊 Line Count Comparison

**Before:** app.py = ~600 lines 😫  
**After:** 
- app.py = ~70 lines ✨
- Each page = ~50-150 lines (focused)
- Total still ~600 lines, but organized!
