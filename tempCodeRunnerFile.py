def refine_root(word):
    patterns = [
        (r'(.+[^ा])त्$', r'\1ा'),  # Fix: Prevents double "ा"
        (r'(.+)ं$', r'\1'),        # 'शुद्धं' → 'शुद्ध'
        (r'(.+)ः$', r'\1'),        # 'सुखः' → 'सुख'
    ]
    
    for pattern, replacement in patterns:
        if re.match(pattern, word):
            print(f"🔄 Applying Rule: {pattern} → {replacement} on '{word}'")  # Debugging
            return re.sub(pattern, replacement, word)

    print(f"⚠️ No rule matched for '{word}', keeping it unchanged.")  # Debugging
    return word  # Return unchanged if no pattern matches
