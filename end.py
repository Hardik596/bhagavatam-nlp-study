import os
import mysql.connector
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib import font_manager
from deep_translator import GoogleTranslator
import nltk
from nltk.corpus import wordnet as wn

# Sanskrit Parser imports
from sanskrit_parser.base.sanskrit_base import SanskritObject
from sanskrit_parser.lexical_analyzer.sanskrit_lexical_analyzer import LexicalAnalyzer

# Download WordNet if not already present
nltk.download('wordnet')

# Database Configuration
db_config = {
    "host": "localhost",
    "user": "root",
    "password": "root",
    "database": "sanskrit_wordnet"
}

# Connect to the database
try:
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
except mysql.connector.Error as e:
    print(f"⚠️ Database connection failed: {e}")
    exit()

# 🚀 Input: Sanskrit Sentence
sanskrit_sentence = 'शुद्धं विद्यात् सुखं सदा'  # Example sentence

# Step 1️⃣: Split the Sentence into Words
sanskrit_words = sanskrit_sentence.split()
print(f"Splitting sentence into words: {sanskrit_words}")

# Step 2️⃣: Initialize Graph and Colors
G = nx.Graph()
colors = {
    "synonym": "lightblue",
    "hypernym": "lightgreen",
    "hyponym": "lightcoral",
    "holonym": "plum",
    "meronym": "lightsalmon",
    "root": "#FFB6C1"  # Light Pink for the central node
}

# Step 3️⃣: Lemmatize Sanskrit Words using Sanskrit Parser
lexical_analyzer = LexicalAnalyzer()

def lemmatize_sanskrit_word(word):
    try:
        # Convert to SanskritObject for analysis
        word_obj = SanskritObject(word, encoding='Devanagari')

        # Get lexical analyses (possible root forms)
        analyses = lexical_analyzer.get_lexical_analyzes(word_obj)

        # Extract root words (if available)
        lemmas = [str(analysis.root) for analysis in analyses if analysis.root]

        return lemmas if lemmas else [word]  # Return original word if no lemma found
    except Exception as e:
        print(f"⚠️ Lemmatization error for '{word}': {e}")
        return [word]  # Return original word if lemmatization fails

# Lemmatize all words in the sentence
lemmatized_words_dict = {word: lemmatize_sanskrit_word(word) for word in sanskrit_words}
lemmatized_words = [lemmas[0] for lemmas in lemmatized_words_dict.values()]  # Pick first lemma
print(f"Lemmatized words: {lemmatized_words}")

# Step 4️⃣: Process Each Lemmatized Word
for sanskrit_word in lemmatized_words:
    print(f"\nProcessing word: {sanskrit_word}")

    # Step 5️⃣: Query Sanskrit WordNet for Synonyms
    cursor.execute(f"SELECT synset_id, synset FROM synset_table WHERE synset LIKE '%{sanskrit_word}%';")
    results = cursor.fetchall()

    related_words = {}  # Dictionary to store words and their relationships

    if not results:
        print(f"⚠️ No WordNet data found for: {sanskrit_word}")
    else:
        # Extract synonyms from the synset
        for row in results:
            synset_text = row["synset"]
            if isinstance(synset_text, bytes):
                synset_text = synset_text.decode("utf-8")
            synset_words = synset_text.split(", ")
            
            # Add synonyms (excluding the input word itself)
            for synonym in synset_words:
                if synonym != sanskrit_word:
                    related_words[synonym] = "synonym"

    # Step 6️⃣: Translate Sanskrit to English
    try:
        english_word = GoogleTranslator(source='sa', target='en').translate(sanskrit_word)
        if not english_word:
            raise ValueError("Translation returned None")
        print(f"Translated '{sanskrit_word}' to English: '{english_word}'")
    except Exception as e:
        print(f"⚠️ Translation error (Sanskrit to English): {e}")
        english_word = None

    # Step 7️⃣: Find Relationships Using English WordNet
    if english_word:
        synsets = wn.synsets(english_word)
        if not synsets:
            print(f"⚠️ No English WordNet synsets found for: {english_word}")
        else:
            # Use the first synset (most common sense)
            synset = synsets[0]
            print(f"Using English synset: {synset.name()} - {synset.definition()}")

            # Define relationships to extract
            relationships = {
                "hypernym": synset.hypernyms(),
                "hyponym": synset.hyponyms(),
                "holonym": synset.part_holonyms() + synset.member_holonyms() + synset.substance_holonyms(),
                "meronym": synset.part_meronyms() + synset.member_meronyms() + synset.substance_meronyms()
            }

            # Limit the number of related words per relationship to avoid clutter
            max_per_relation = 5

            # Process each relationship type
            for rel_type, rel_synsets in relationships.items():
                count = 0
                for rel_synset in rel_synsets:
                    if count >= max_per_relation:
                        break
                    # Take the first lemma from each related synset
                    lemma = rel_synset.lemma_names()[0]
                    try:
                        sanskrit_rel_word = GoogleTranslator(source='en', target='sa').translate(lemma)
                        if sanskrit_rel_word and sanskrit_rel_word != sanskrit_word:
                            # Verify if the translated word exists in the database
                            cursor.execute(f"SELECT synset_id FROM synset_table WHERE synset LIKE '%{sanskrit_rel_word}%';")
                            if cursor.fetchone():
                                related_words[sanskrit_rel_word] = rel_type
                                count += 1
                    except Exception as e:
                        print(f"⚠️ Translation error (English to Sanskrit) for '{lemma}': {e}")

    # Step 8️⃣: Build the Graph for the Current Word
    G.add_node(sanskrit_word, category="root")
    for rel_word, rel_type in related_words.items():
        G.add_node(rel_word, category=rel_type)
        G.add_edge(sanskrit_word, rel_word, relation=rel_type)

# Close database connection
cursor.close()
conn.close()

# Step 9️⃣: Select Top Nodes (if needed)
node_degrees = dict(G.degree())
top_100_nodes = sorted(node_degrees, key=node_degrees.get, reverse=True)[:100]
subgraph = G.subgraph(top_100_nodes) if len(G) > 100 else G

# Step 🔟: Visualize Graph
plt.figure(figsize=(14, 7))
font_path = "./font/NotoSansDevanagari-VariableFont_wdth,wght.ttf"  
if os.path.exists(font_path):
    font_manager.fontManager.addfont(font_path)
    prop = font_manager.FontProperties(fname=font_path)
else:
    prop = None  # Use default font if custom font is missing

# Layout
pos = nx.spring_layout(subgraph, k=0.5, iterations=50)

# Draw the graph
nx.draw(subgraph, pos, node_color="lightblue", with_labels=True, font_size=12, font_family="Noto Sans Devanagari" if prop else "Arial")
plt.title(f"Semantic Graph for Sentence: {sanskrit_sentence}", fontproperties=prop)
plt.show()
