import mysql.connector
import re

# ✅ STEP 1: Database Configuration
db_config = {
    "host": "localhost",
    "user": "root",
    "password": "root",
    "database": "sanskrit_wordnet"
}

# ✅ STEP 2: Query WordNet Table for Lemma
def get_lemma_from_wordnet(word, cursor):
    query = "SELECT head FROM synset_table WHERE synset LIKE %s LIMIT 1"
    cursor.execute(query, (f"%{word}%",))
    result = cursor.fetchone()
    
    print(f"🔍 Searching '{word}' in WordNet... Found:", result)  # Debugging
    
    return result["head"] if result and result["head"] else None

# ✅ STEP 3: Improved Root Extraction (Fixed "विद्यात्" → "विद्या")
def refine_root(word):
    patterns = [
        (r'(.+)त्$', r'\1'),  # Remove 'त्' first ('विद्यात्' → 'विद्या')
        (r'(.+)', r'\1ा'),    # Then add 'ा' ('विद्या' → 'विद्या') but not duplicate
        (r'(.+)ं$', r'\1'),   # 'शुद्धं' → 'शुद्ध'
        (r'(.+)ः$', r'\1'),   # 'सुखः' → 'सुख'
    ]
    
    for pattern, replacement in patterns:
        if re.search(pattern, word):
            new_word = re.sub(pattern, replacement, word)
            print(f"🔄 Applying Rule: {pattern} → {replacement} on '{word}' → '{new_word}'")
            return new_word  # Return after first successful match

    print(f"⚠️ No rule matched for '{word}', keeping it unchanged.")
    return word  # Return unchanged if no pattern matches



# ✅ STEP 4: Lemmatization Pipeline
def lemmatize_words(words):
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)

    lemmatized_words = []
    for word in words:
        print("\n🔹 Processing:", word)  # Debugging

        lemma = get_lemma_from_wordnet(word, cursor)
        if not lemma:
            print("⚠️ No lemma found in WordNet, applying regex rules.")
            lemma = refine_root(word)
        else:
            print(f"✅ WordNet Lemma Found: {lemma}")

        lemmatized_words.append(lemma)

    cursor.close()
    conn.close()
    return lemmatized_words

# ✅ STEP 5: Test with Your Words
words_to_lemmatize = ["विद्यात्", "शुद्धं", "सुखं", "सदा"]
lemmatized = lemmatize_words(words_to_lemmatize)
print("\n🔹 Original:", words_to_lemmatize)
print("🔹 Lemmatized:", lemmatized)
# token for hugging face : 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









