import mysql.connector
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib import font_manager
import stanza
from googletrans import Translator
import numpy as np
from nltk.corpus import stopwords
import nltk
nltk.download("stopwords")

stop_words = set(stopwords.words("english"))


# Initialize Stanza
stanza.download("en")
nlp = stanza.Pipeline("en", processors="tokenize,pos,lemma")

# Initialize Google Translator
translator = Translator()

# Database Connection
db_config = {
    "host": "localhost",
    "user": "root",
    "password": "root",
    "database": "sanskrit_wordnet"
}
conn = mysql.connector.connect(**db_config)
cursor = conn.cursor(dictionary=True)

# 🚀 INPUT: Sanskrit Sentence
sanskrit_sentence = "कृष्णः यः प्रियः सर्वः आकर्षकः"

# Step 1️⃣: Translate Sanskrit to English using Google Translate
translated_sentence = translator.translate(sanskrit_sentence, src="auto", dest="en").text


# Step 2️⃣: Text Preprocessing
doc = nlp(translated_sentence)
old_lemmas = [word.lemma for sent in doc.sentences for word in sent.words]
lemmas = [word for word in old_lemmas if word.lower() not in stop_words]

print(lemmas)

# Step 3️⃣: Translate Back to Sanskrit using Google Translate
import time

sanskrit_lemmas = []
for word in lemmas:
    try:
        translation = translator.translate(word, src="en", dest="hi")
        if translation and translation.text:  # Ensure translation is valid
            sanskrit_lemmas.append(translation.text)
        else:
            print(f"⚠️ Translation failed for: {word}, skipping...")
    except Exception as e:
        print(f"⚠️ Error translating '{word}': {e}")
        time.sleep(1)  # Wait 1 second before retrying

print("sanskrit = ",sanskrit_lemmas)


# Step 4️⃣: Query WordNet for Relations and Construct Graph
G = nx.Graph()
main_nodes = set()

for word in sanskrit_lemmas:
    cursor.execute(f"SELECT synset, gloss, category FROM synset_table WHERE synset LIKE '%{word}%';")
    results = cursor.fetchall()
    
    if not results:
        print(f"⚠️ No WordNet data found for: {word}")
        continue

    G.add_node(word, category="MainWord")
    main_nodes.add(word)
    
    relation_weights = {}
    
    for row in results:
        synset_words = row["synset"].decode("utf-8").split(", ")
        gloss_words = row["gloss"].decode("utf-8").split()
        
        # Synonyms
        for synonym in synset_words:
            if synonym != word:
                relation_weights[synonym] = relation_weights.get(synonym, 0) + 1
        
        # Hypernyms & Hyponyms (Extract from Gloss)
        for gloss_word in gloss_words:
            if gloss_word in sanskrit_lemmas and gloss_word != word:
                relation_weights[gloss_word] = relation_weights.get(gloss_word, 0) + 2
    
    # Select top 20 highest weighted relations
    top_20_relations = sorted(relation_weights.items(), key=lambda x: x[1], reverse=True)[:20]
    
    for related_word, weight in top_20_relations:
        G.add_node(related_word, category="Related")
        G.add_edge(word, related_word, weight=weight)
        
cursor.close()
conn.close()

# Step 5️⃣: Compute Graph Metrics
degree_centrality = nx.degree_centrality(G)
closeness_centrality = nx.closeness_centrality(G)
betweenness_centrality = nx.betweenness_centrality(G)
pagerank = nx.pagerank(G)

# Print Graph Metrics
print("\nGraph Metrics:")
print("Node | Degree | Closeness | Betweenness | PageRank")
for node in G.nodes():
    print(f"{node} | {degree_centrality[node]:.4f} | {closeness_centrality[node]:.4f} | {betweenness_centrality[node]:.4f} | {pagerank[node]:.4f}")

# Step 6️⃣: Visualize the Graph
plt.figure(figsize=(14, 10))
font_path = "./font/NotoSansDevanagari-VariableFont_wdth,wght.ttf"
prop = font_manager.FontProperties(fname=font_path)

# Compute Circular Layout with Adjusted Root Words Positions
pos = nx.circular_layout(G)
angle_shift = np.linspace(-0.4, 0.4, len(main_nodes))  # Small shifts for center nodes
radius = 0.3  # Adjust distance from the exact center
for i, main_word in enumerate(main_nodes):
    pos[main_word] = [radius * np.cos(angle_shift[i]), radius * np.sin(angle_shift[i])]

# Assign different colors to each root word and their related nodes
root_colors = plt.cm.rainbow(np.linspace(0, 1, len(main_nodes)))
node_colors = []
color_map = {}
for i, root in enumerate(main_nodes):
    color_map[root] = root_colors[i]
    
for node in G.nodes():
    if node in main_nodes:
        node_colors.append(color_map[node])
    else:
        # Assign related nodes the same color as their root word
        for root in main_nodes:
            if G.has_edge(root, node):
                node_colors.append(color_map[root])
                break
        else:
            node_colors.append("lightgray")

node_sizes = [max(len(n) * 800, 3000) for n in G.nodes()]  # Adjust node size
edge_widths = [G[u][v]['weight'] for u, v in G.edges()]

# Draw Graph
nx.draw(G, pos, node_size=node_sizes, node_color=node_colors, edge_color="gray", width=edge_widths, with_labels=True, font_size=12, font_family="Noto Sans Devanagari")

plt.title("Sanskrit WordNet Graph", fontproperties=prop)
plt.show()