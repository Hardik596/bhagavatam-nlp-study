import mysql.connector
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import font_manager
from deep_translator import GoogleTranslator
from textblob import TextBlob

# 🛠️ Step 1: Connect to MySQL Database
db_config = {
    "host": "localhost",
    "user": "root",
    "password": "root",
    "database": "sanskrit_wordnet"
}

conn = mysql.connector.connect(**db_config)
cursor = conn.cursor(dictionary=True)

# 🚀 INPUT: Sanskrit Sentence
sanskrit_sentence = "देवी गुरु स्पष्ट"
words_in_sentence = sanskrit_sentence.split()

# 🎯 Step 2: Query WordNet & Construct Graph
G = nx.Graph()

for word in words_in_sentence:
    cursor.execute(f"SELECT synset FROM synset_table WHERE synset LIKE '%{word}%';")
    results = cursor.fetchall()
    
    if not results:
        print(f"⚠️ No WordNet data found for: {word}")
        continue

    related_words = set()

    for row in results:
        synset = row["synset"].decode("utf-8") if isinstance(row["synset"], bytes) else row["synset"]
        synset_words = synset.split(", ")
        
        for related_word in synset_words:
            if related_word != word and len(related_words) < 50:
                related_words.add(related_word)
                G.add_edge(word, related_word)  # Create relation in graph

# 🎯 Step 3: Compute Graph Metrics
page_rank = nx.pagerank(G)
closeness = nx.closeness_centrality(G)
betweenness = nx.betweenness_centrality(G)
degree_centrality = nx.degree_centrality(G)

# 🔍 Step 4: Compute Node Importance
node_scores = {}
for node in G.nodes():
    node_scores[node] = (
        page_rank.get(node, 0) +
        closeness.get(node, 0) +
        betweenness.get(node, 0) +
        degree_centrality.get(node, 0)
    )

# 🏆 Step 5: Select Top 50 Related Nodes for Each Word
top_nodes = set(words_in_sentence)  # Keep input words
for word in words_in_sentence:
    related_nodes = {n for n in G.neighbors(word)}
    top_related = sorted(related_nodes, key=node_scores.get, reverse=True)[:50]
    top_nodes.update(top_related)  # Add only the top 50

G_filtered = G.subgraph(top_nodes)

# 🎯 Step 6: Sentiment Analysis
translator = GoogleTranslator(source="auto", target="en")
translated_sentence = translator.translate(sanskrit_sentence)
sentiment_score = TextBlob(translated_sentence).sentiment.polarity  # -1 to 1 scale

if sentiment_score > 0:
    sentiment_label = "😊 Positive"
elif sentiment_score < 0:
    sentiment_label = "😞 Negative"
else:
    sentiment_label = "😐 Neutral"

print(f"🔤 Translated Sentence: {translated_sentence}")
print(f"📊 Sentiment Score: {sentiment_score} ({sentiment_label})")

# 🎨 Step 7: Circular Graph Visualization
plt.figure(figsize=(12, 12))
font_path = "./font/NotoSansDevanagari-VariableFont_wdth,wght.ttf"
prop = font_manager.FontProperties(fname=font_path)

# 🏛 Step 1: Positioning Nodes in a Circle
n_center = len(words_in_sentence)  # Number of center words
n_outer = len(G_filtered.nodes()) - n_center  # Number of related words

angle_step = 2 * np.pi / n_outer  # Angle for outer circle
radius = 2  # Radius for outer circle

pos = {}
# Center words at origin
for i, word in enumerate(words_in_sentence):
    pos[word] = (0, 0)  # Center position

# Related words in a circular pattern
for i, node in enumerate(G_filtered.nodes()):
    if node not in words_in_sentence:  # Avoid overwriting center words
        angle = i * angle_step
        pos[node] = (radius * np.cos(angle), radius * np.sin(angle))

# 🏛 Step 2: Adjust Node Sizes & Colors
node_size = [3000 if n in words_in_sentence else 2500 for n in G_filtered.nodes()]
node_color = ["red" if n in words_in_sentence else np.random.rand(3,) for n in G_filtered.nodes()]

# 🏛 Step 3: Draw Graph
nx.draw_networkx_nodes(G_filtered, pos, node_size=node_size, node_color=node_color, alpha=0.8, edgecolors="black")
nx.draw_networkx_edges(G_filtered, pos, alpha=0.5, edge_color="gray", width=1.5)
nx.draw_networkx_labels(G_filtered, pos, font_size=10, font_family="Noto Sans Devanagari",
                        bbox=dict(facecolor="white", edgecolor="none", alpha=0.7))

# 🎯 Final Touches
plt.title(f"📌 Sanskrit WordNet Graph - Sentiment: {sentiment_label}", fontname="Noto Sans Devanagari")
plt.axis("off")  # Hide axes
plt.show()
