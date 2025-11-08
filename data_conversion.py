# data_conversion.py
# د پښتو بند-کلمو لپاره نړیوال تبدیل کوونکی
# © ۲۰۲۵ IPashto.AI / Spinzar Enterprises

import pandas as pd
import sys
import os
import re # د پرمختللي پاکولو لپاره اړین دی

# --- د فایل لاره ---
# INPUT_FILE_PATH اوس د src جوړښت ته اشاره کوي
INPUT_FILE_PATH = 'src/pashto_stopwords/pashto-stopwords.txt'

def clean_and_normalize(line: str) -> str | None:
    """د کرښې ټول خالي ځایونه، ټیبونه، او ناغوښتل شوي کرکټرونه پاکوي."""
    
    # 1. د Zero-width او BOM کرکټرونو لرې کول
    line = line.replace('\u200b', '').replace('\ufeff', '')
    
    # 2. CRITICAL FIX: د ټولو خالي ځایونو (tabs, multiple spaces) په یو واحد ځای بدلول، او بیا strip()
    line = re.sub(r'\s+', ' ', line).strip()
    
    # 3. د تبصرو، خالي کرښو، او زاړه 'word' سرلیک لرې کول
    if not line or line.startswith('#') or line.lower() == 'word':
        return None
        
    return line

print("پښتو بند-کلمې — د ډاټا بشپړ پاکول او معیاري کول")
print("="*55)

# --- د فایل لوستل ---
print(f"د فایل لوستل: {INPUT_FILE_PATH}")
try:
    with open(INPUT_FILE_PATH, 'r', encoding='utf-8') as f:
        # پر هر کرښې پاکول تطبیق کړئ او None لرې کړئ
        cleaned_words = [clean_and_normalize(line) for line in f]
        cleaned_words = [word for word in cleaned_words if word is not None]

    # **د ډاټا کیفیت ګام**: تکرارونه لرې کړئ او کلمې ترتیب کړئ
    final_words = sorted(list(set(cleaned_words)))
    
    # د ډاټا فریم جوړول
    df = pd.DataFrame(final_words, columns=['word'])
    print(f"پاکې شوې کلمې: {len(df)} (تکرارونه په بریالیتوب سره لرې شول)")
    
except FileNotFoundError:
    print(f"فایل نه موندل شو: {INPUT_FILE_PATH}")
    sys.exit(1)

# --- احصائیه ---
print("\nاحصائیه:")
# د لیست پر ځای د ډاټا فریم څخه اعظمي او لږه کلمه پیدا کړئ
lengths = df['word'].str.len()
max_word = df.loc[lengths.idxmax(), 'word']
min_word = df.loc[lengths.idxmin(), 'word']

print(f"   اوږده کلمه → '{max_word}' ({len(max_word)} توري)")
print(f"   لنډه کلمه → '{min_word}' ({len(min_word)} توري)")

# --- ذخیره کول ---
output_dir = 'stopwords'
os.makedirs(output_dir, exist_ok=True)

formats = {
    'csv': 'pashto-stopwords.csv',
    'json': 'pashto-stopwords.json',
    'xlsx': 'pashto-stopwords.xlsx',
    'pickle': 'pashto-stopwords.pickle',
    'txt': 'pashto-stopwords.txt'
}

for fmt, filename in formats.items():
    path = os.path.join(output_dir, filename)
    if fmt == 'csv':
        df.to_csv(path, index=False, encoding='utf-8')
    elif fmt == 'json':
        # force_ascii=False د پښتو کرکټرونو د سمې ښودنې لپاره اړین دی
        df.to_json(path, orient='records', indent=4, force_ascii=False)
    elif fmt == 'xlsx':
        try:
            df.to_excel(path, index=False, engine='openpyxl')
        except Exception:
            print(f"Excel ذخیره نشوه: (pip install openpyxl)")
            continue
    elif fmt == 'pickle':
        df.to_pickle(path)
    elif fmt == 'txt':
        # د پاکو او ترتیب شویو کلمو ذخیره کول
        with open(path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(final_words))
    print(f"{fmt.upper()} ذخیره شو")

print("\nبشپړ شو! پاک فایلونه دلته دي:", output_dir)

# --- ازموینه ---
# دا ازموینه یوازې هغه وخت کار کوي چې بسته (Package) نصب وي، نو د خطا د مخنیوي لپاره یې په try/except کې شامل کوو.
print("\nد پاکولو ازموینه:")
test_sentence = "دا یو مثال دی چې آیا کار کوي"
try:
    from pashto_stopwords import remove_stopwords
    clean_result = remove_stopwords(test_sentence)
    print(f"   → اصلی جمله: '{test_sentence}'")
    print(f"   → پایله: '{clean_result}' (بند کلمې لیرې شوې)")
except ImportError:
    print("د پښتو بند-کلمو بسته (package) نه ده نصب. ازموینه پریښودل شوه.")