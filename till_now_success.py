import mysql.connector
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib import font_manager

# Connect to MySQL Database
db_config = {
    "host": "localhost",
    "user": "root",
    "password": "root",
    "database": "sanskrit_wordnet"
}

conn = mysql.connector.connect(**db_config)
cursor = conn.cursor(dictionary=True)

# 🚀 INPUT: Sanskrit Sentence
sanskrit_sentence = "Whenever there is a loss of religion, O Bharatha"
words_in_sentence = sanskrit_sentence.split()

# Step 1️⃣: Query WordNet for Each Word and Construct Graph
G = nx.DiGraph()

for word in words_in_sentence:
    cursor.execute(f"SELECT synset, gloss, category FROM synset_table WHERE synset LIKE '%{word}%';")
    results = cursor.fetchall()
    
    if not results:
        print(f"⚠️ No WordNet data found for: {word}")
        continue

    related_words = {}  # Dictionary to store words with weights
    
    for row in results:
        synset = row["synset"].decode("utf-8") if isinstance(row["synset"], bytes) else row["synset"]
        gloss = row["gloss"].decode("utf-8") if isinstance(row["gloss"], bytes) else row["gloss"]
        
        synset_words = synset.split(", ")
        
        for synonym in synset_words:
            if synonym != word:
                related_words[synonym] = related_words.get(synonym, 0) + 1  # Increase weight
        
        # Check hypernyms in gloss
        gloss_words = gloss.split()
        for hypernym in words_in_sentence:
            if hypernym != word and hypernym in gloss_words:
                related_words[hypernym] = related_words.get(hypernym, 0) + 2  # Hypernyms get higher weight

    # Select top 5 related words by weight
    top_5_words = sorted(related_words, key=related_words.get, reverse=True)[:5]
    
    # Add nodes & edges
    G.add_node(word, category=row["category"])
    
    for related_word in top_5_words:
        G.add_node(related_word, category=row["category"])
        G.add_edge(word, related_word, relation="related", weight=related_words[related_word])

cursor.close()
conn.close()

# Step 2️⃣: Visualize the Graph
plt.figure(figsize=(12, 8))
font_path = "./font/NotoSansDevanagari-VariableFont_wdth,wght.ttf"
prop = font_manager.FontProperties(fname=font_path)

# Step 1: Compute layout
pos = nx.spring_layout(G, k=0.5, iterations=100)

# Step 2: Compute node sizes based on PageRank importance
node_importance = nx.pagerank(G)
node_size = [5000 * node_importance[n] for n in G.nodes()]

# Step 3: Compute edge widths based on node importance
edge_widths = [(node_importance[u] + node_importance[v]) * 2 for u, v in G.edges()]

# Step 4: Draw nodes
plt.figure(figsize=(12, 8))
nx.draw(G, pos, node_size=node_size, node_color="lightblue", edge_color="gray", width=edge_widths)

# Step 5: Add labels
nx.draw_networkx_labels(G, pos, font_size=12, font_family="Noto Sans Devanagari",
                        bbox=dict(facecolor="white", edgecolor="none", alpha=0.7))

# Step 6: Add edge labels (relations)
edge_labels = nx.get_edge_attributes(G, 'relation')
nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_color='red')

plt.title("Sanskrit WordNet Graph", fontname="Noto Sans Devanagari")
plt.show()

