import mysql.connector
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib import font_manager
import requests
import numpy as np
import stanza

# ✅ Database Connection
db_config = {
    "host": "localhost",
    "user": "root",
    "password": "root",
    "database": "sanskrit_wordnet"
}
conn = mysql.connector.connect(**db_config)
cursor = conn.cursor(dictionary=True)

# ✅ Input Sanskrit Sentence
sanskrit_sentence = "सर्वे जीवा कृष्णस्य भागाः सन्ति"

# 🔹 Step 1: Tokenization using Stanza
stanza.download("sa")
nlp = stanza.Pipeline("sa", processors="tokenize,pos,lemma")

doc = nlp(sanskrit_sentence)
tokens = [word.text for sent in doc.sentences for word in sent.words if word.text not in ["।", ".", ",", ";", ":", "!", "?"]]

print("🔹 Tokens:", tokens)

# 🔹 Step 2: Use Sanskrit Heritage Reader for Lemmatization
import requests
from bs4 import BeautifulSoup

def get_lemma(word):
    url = f"https://sanskrit.inria.fr/cgi-bin/sktlemmatizer?t=SL&q={word}&output=slp1&script=devanagari"
    response = requests.get(url)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        lemma_elements = soup.find_all("td", class_="lemma")
        
        if lemma_elements:
            return lemma_elements[0].text.strip()  # Get first lemma found
    return word  # If no lemma is found, return the original word



# Apply Lemmatization
lemmas = [get_lemma(token) for token in tokens]
print("🔹 Lemmatized Sanskrit Words:", lemmas)

# 🔹 Step 3: Query Sanskrit WordNet and Construct Graph
G = nx.Graph()
main_nodes = set()

for word in lemmas:
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
        gloss_words = row["gloss"].decode("utf-8").split(", ")
        
        # Synonyms
        for synonym in synset_words:
            if synonym != word:
                relation_weights[synonym] = relation_weights.get(synonym, 0) + 1
        
        # Hypernyms & Hyponyms (Extract from Gloss)
        for gloss_word in gloss_words:
            if gloss_word in lemmas and gloss_word != word:
                relation_weights[gloss_word] = relation_weights.get(gloss_word, 0) + 2
        
        # Holonyms & Meronyms (Find contextual clues in Gloss)
        for gloss_word in gloss_words:
            gloss_text = row["gloss"].decode("utf-8")  # ✅ Convert bytes to string
            if "part of" in gloss_text or "portion of" in gloss_text:
                relation_weights[gloss_word] = relation_weights.get(gloss_word, 0) + 3  # Meronym
            elif "whole of" in gloss_text or "contains" in gloss_text:
                relation_weights[gloss_word] = relation_weights.get(gloss_word, 0) + 3  # Holonym
    
    # Select top 20 highest weighted relations
    top_20_relations = sorted(relation_weights.items(), key=lambda x: x[1], reverse=True)[:20]
    
    for related_word, weight in top_20_relations:
        G.add_node(related_word, category="Related")
        G.add_edge(word, related_word, weight=weight)

cursor.close()
conn.close()
print(relation_weights)
# 🔹 Step 4: Compute Graph Metrics
degree_centrality = nx.degree_centrality(G)
closeness_centrality = nx.closeness_centrality(G)
betweenness_centrality = nx.betweenness_centrality(G)
pagerank = nx.pagerank(G)

# Print Graph Metrics
print("\n📊 Graph Metrics:")
print("Node | Degree | Closeness | Betweenness | PageRank")
for node in G.nodes():
    print(f"{node} | {degree_centrality[node]:.4f} | {closeness_centrality[node]:.4f} | {betweenness_centrality[node]:.4f} | {pagerank[node]:.4f}")

# 🔹 Step 5: Visualize the Graph
plt.figure(figsize=(14, 10))
font_path = "./font/NotoSansDevanagari-VariableFont_wdth,wght.ttf"
prop = font_manager.FontProperties(fname=font_path)

# Compute Circular Layout with Adjusted Root Words Positions
pos = nx.circular_layout(G)
angle_shift = np.linspace(-0.4, 0.4, len(main_nodes))
radius = 0.3
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
        for root in main_nodes:
            if G.has_edge(root, node):
                node_colors.append(color_map[root])
                break
        else:
            node_colors.append("lightgray")

node_sizes = [max(len(n) * 800, 3000) for n in G.nodes()]
edge_widths = [G[u][v]['weight'] for u, v in G.edges()]

# Draw Graph
nx.draw(G, pos, node_size=node_sizes, node_color=node_colors, edge_color="gray", width=edge_widths, with_labels=True, font_size=12, font_family="Noto Sans Devanagari")

plt.title("Sanskrit WordNet Graph", fontproperties=prop)
plt.show()