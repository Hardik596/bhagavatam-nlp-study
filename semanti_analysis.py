from transformers import pipeline, AutoModelForQuestionAnswering, AutoTokenizer
import nltk
from nltk.corpus import wordnet as wn

# Download WordNet
nltk.download('wordnet')

# Load Pre-trained LLM (IndicBERT as placeholder)
model_name = "ai4bharat/indic-bert"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForQuestionAnswering.from_pretrained(model_name)

# Initialize QA pipeline
qa_pipeline = pipeline("question-answering", model=model, tokenizer=tokenizer)

# Sample Shastra Passage (from Bhagavad Gita)
shastra_passage = "You have the right to perform your prescribed duties, but you are not entitled to the fruits of your actions. Never consider yourself to be the cause of the results of your activities, nor be attached to inaction."

# Semantic Analysis using WordNet
def get_synonyms(word):
    synonyms = wn.synsets(word)
    return [lemma.name() for syn in synonyms for lemma in syn.lemmas()]

# Chatbot Interaction
while True:
    user_question = input("Ask a question about the Shastras (or type 'exit' to quit): ")
    if user_question.lower() == 'exit':
        break

    # Semantic Enhancement
    key_terms = user_question.split()
    semantic_info = {term: get_synonyms(term) for term in key_terms}
    print(f"Semantic enrichment: {semantic_info}")

    # Get Answer from LLM
    result = qa_pipeline({
        'context': shastra_passage,
        'question': user_question
    })

    print(f"Answer: {result['answer']}\n")