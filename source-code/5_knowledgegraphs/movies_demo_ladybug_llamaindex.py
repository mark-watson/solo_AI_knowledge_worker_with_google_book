"""
Movies demo using LlamaIndex + LadyBug (official integration).

Unlike langchain-kuzu (archived), LlamaIndex has an official LadyBug integration:
  - llama-index-graph-stores-ladybug (PyPI)
  - LadybugPropertyGraphStore + PropertyGraphIndex

This demo shows two approaches:
  1. Seed the graph with manual Cypher (like the original movies_demo.py)
  2. Query via LlamaIndex's PropertyGraphIndex query engine
"""
import ladybug as lb
from llama_index.graph_stores.ladybug import LadybugPropertyGraphStore
from llama_index.core import PropertyGraphIndex
from llama_index.core.schema import TextNode
from llama_index.core.llms import MockLLM
import os
import shutil

# ---------------------------------------------------------------------------
# Database setup
# ---------------------------------------------------------------------------
DB_PATH = "test_db_ladybug_li"

if os.path.exists(DB_PATH):
    if os.path.isdir(DB_PATH):
        shutil.rmtree(DB_PATH)
    else:
        os.remove(DB_PATH)

db = lb.Database(DB_PATH)

# ---------------------------------------------------------------------------
# Approach 1: Seed the graph with manual Cypher (same as original movies_demo)
# ---------------------------------------------------------------------------
conn = lb.Connection(db)

# Schema
conn.execute("CREATE NODE TABLE Movie (name STRING PRIMARY KEY)")
conn.execute("CREATE NODE TABLE Person (name STRING, birthDate STRING PRIMARY KEY)")
conn.execute("CREATE REL TABLE ActedIn (FROM Person TO Movie)")

# People
conn.execute("CREATE (:Person {name: 'Al Pacino', birthDate: '1940-04-25'})")
conn.execute("CREATE (:Person {name: 'Robert De Niro', birthDate: '1943-08-17'})")
conn.execute("CREATE (:Person {name: 'Marlon Brando', birthDate: '1924-04-03'})")
conn.execute("CREATE (:Person {name: 'Diane Keaton', birthDate: '1946-01-05'})")

# Movies
conn.execute("CREATE (:Movie {name: 'The Godfather'})")
conn.execute("CREATE (:Movie {name: 'The Godfather: Part II'})")
conn.execute("CREATE (:Movie {name: 'The Godfather Coda: The Death of Michael Corleone'})")
conn.execute("CREATE (:Movie {name: 'Apocalypse Now'})")
conn.execute("CREATE (:Movie {name: 'Annie Hall'})")

# Relationships
relationships = [
     ("Al Pacino", "The Godfather"),
     ("Al Pacino", "The Godfather: Part II"),
     ("Al Pacino", "The Godfather Coda: The Death of Michael Corleone"),
     ("Al Pacino", "Apocalypse Now"),
     ("Robert De Niro", "The Godfather: Part II"),
     ("Marlon Brando", "Apocalypse Now"),
     ("Diane Keaton", "Annie Hall"),
     ("Diane Keaton", "The Godfather: Part II"),
]

for person_name, movie_name in relationships:
    conn.execute(
        f"MATCH (p:Person), (m:Movie) "
        f"WHERE p.name = '{person_name}' AND m.name = '{movie_name}' "
        f"CREATE (p)-[:ActedIn]->(m)"
     )

print("=== Graph seeded with manual Cypher ===")
print()

# ---------------------------------------------------------------------------
# Approach 2: Query via LlamaIndex PropertyGraphIndex
# ---------------------------------------------------------------------------

# Create a LadybugPropertyGraphStore (unstructured mode, no vector index needed)
graph_store = LadybugPropertyGraphStore(
     db=db,
     use_vector_index=False,  # Not needed for this demo
)

# Build a PropertyGraphIndex on top of the existing database
# The index will discover the schema we just created
index = PropertyGraphIndex.from_existing(
     property_graph_store=graph_store,
)

# Print the discovered schema
print("=== Discovered Schema ===")
print(index.property_graph_store.get_schema())
print()

# ---------------------------------------------------------------------------
# Query the graph using LlamaIndex query engine
# ---------------------------------------------------------------------------

# For this demo we use structured_query which executes Cypher directly.
# In production you'd use an LLM to generate Cypher from natural language.

queries = [
     "MATCH (p:Person)-[:ActedIn]->(m:Movie {name: 'The Godfather: Part II'}) RETURN p.name",
     "MATCH (p:Person {name: 'Robert De Niro'})-[:ActedIn]->(m:Movie) RETURN m.name",
     "MATCH (p:Person)-[:ActedIn]->(m:Movie {name: 'Apocalypse Now'}) RETURN p.name",
     "MATCH (p:Person {name: 'Diane Keaton'})-[:ActedIn]->(m:Movie) RETURN m.name",
     "MATCH (p:Person)-[:ActedIn]->(m:Movie) WITH p.name AS actor, COUNT(m) AS movie_count WHERE movie_count > 1 RETURN actor, movie_count ORDER BY movie_count DESC",
]

questions = [
     "Who acted in The Godfather: Part II?",
     "Robert De Niro played in which movies?",
     "Which actors acted in Apocalypse Now?",
     "What movies did Diane Keaton act in?",
     "Which actors appeared in more than one movie?",
]

print("=== Query Results ===")
for question, cypher in zip(questions, queries):
    print(f"\n> Question: {question}")
    print(f"  Cypher: {cypher}")
    try:
        result = index.structured_query(cypher)
        print(f"  Result: {result}")
    except Exception as e:
        print(f"  Error: {e}")

print()

# ---------------------------------------------------------------------------
# Approach 3: Natural language queries (requires an LLM)
# ---------------------------------------------------------------------------
# To use natural language queries, you need an LLM. Uncomment below:
#
# from llama_index.llms.gemini import Gemini
#
# llm = Gemini(model="gemini-2.5-flash-preview")
#
# query_engine = index.as_query_engine(
#     llm=llm,
#     structured_predictor=llm,  # LLM generates Cypher from natural language
# )
#
# for question in questions:
#     print(f"\n> Question: {question}")
#     response = query_engine.query(question)
#     print(f"  Answer: {response}")

# ---------------------------------------------------------------------------
# Approach 4: Auto-extract entities from text documents
# ---------------------------------------------------------------------------
# This is the main strength of LlamaIndex + LadyBug:
# Feed it text and it auto-extracts a knowledge graph!
#
# from llama_index.core import SimpleDirectoryReader
# from llama_index.embeddings.gemini import GeminiEmbedding
#
# embed_model = GeminiEmbedding(model="models/embedding-001")
# graph_store_auto = LadybugPropertyGraphStore(
#     db=lb.Database("auto_graph.ladybug"),
#     use_vector_index=True,
#     embed_model=embed_model,
#     relationship_schema=[
#         ("PERSON", "ACTED_IN", "MOVIE"),
#         ("PERSON", "DIRECTED", "MOVIE"),
#     ],
#     has_structured_schema=True,
# )
#
# documents = SimpleDirectoryReader("./movie_scripts").load_data()
# index_auto = PropertyGraphIndex.from_documents(
#     documents,
#     llm=llm,
#     embed_model=embed_model,
#     property_graph_store=graph_store_auto,
#     show_progress=True,
# )
#
# query_engine_auto = index_auto.as_query_engine(llm=llm)
# response = query_engine_auto.query("Which actors appeared in Godfather movies?")
# print(response)

print("\nExample complete.")

# Clean up
if os.path.exists(DB_PATH):
    if os.path.isdir(DB_PATH):
        shutil.rmtree(DB_PATH)
    else:
        os.remove(DB_PATH)
