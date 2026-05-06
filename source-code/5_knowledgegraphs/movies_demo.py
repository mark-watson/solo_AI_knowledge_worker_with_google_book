import kuzu
from langchain_community.chains.graph_qa.kuzu import KuzuQAChain
from langchain_community.graphs import KuzuGraph
# Import the Gemini LLM
from langchain_google_genai import ChatGoogleGenerativeAI
import os
import shutil

# --- Optional: Set your Google API Key ---
# If you haven't set it as an environment variable, you can do it here
# os.environ["GOOGLE_API_KEY"] = "YOUR_GOOGLE_API_KEY"
# Alternatively, pass it directly to ChatGoogleGenerativeAI:
# llm = ChatGoogleGenerativeAI(model="gemini-pro", google_api_key="YOUR_GOOGLE_API_KEY")

db_path = "test_db_gemini"
if os.path.exists(db_path):
    if os.path.isdir(db_path):
        shutil.rmtree(db_path)
    else:
        os.remove(db_path)

db = kuzu.Database(db_path) # Use a new DB path to avoid conflicts
conn = kuzu.Connection(db)

# --- Schema and Data Creation (same as your original code) ---
# Create two tables and a relation: Movie, Person, ActedIn
conn.execute("CREATE NODE TABLE Movie (name STRING, PRIMARY KEY(name))")
conn.execute(
    "CREATE NODE TABLE Person (name STRING, birthDate STRING, PRIMARY KEY(name))"
)
conn.execute("CREATE REL TABLE ActedIn (FROM Person TO Movie)")
conn.execute("CREATE (:Person {name: 'Al Pacino', birthDate: '1940-04-25'})")
conn.execute("CREATE (:Person {name: 'Robert De Niro', birthDate: '1943-08-17'})")
conn.execute("CREATE (:Movie {name: 'The Godfather'})")
conn.execute("CREATE (:Movie {name: 'The Godfather: Part II'})")
conn.execute(
    "CREATE (:Movie {name: 'The Godfather Coda: The Death of Michael Corleone'})"
)
conn.execute(
    "MATCH (p:Person), (m:Movie) WHERE p.name = 'Al Pacino' AND m.name = 'The Godfather' CREATE (p)-[:ActedIn]->(m)"
)
conn.execute(
    "MATCH (p:Person), (m:Movie) WHERE p.name = 'Al Pacino' AND m.name = 'The Godfather: Part II' CREATE (p)-[:ActedIn]->(m)"
)
conn.execute(
    "MATCH (p:Person), (m:Movie) WHERE p.name = 'Al Pacino' AND m.name = 'The Godfather Coda: The Death of Michael Corleone' CREATE (p)-[:ActedIn]->(m)"
)
conn.execute(
    "MATCH (p:Person), (m:Movie) WHERE p.name = 'Robert De Niro' AND m.name = 'The Godfather: Part II' CREATE (p)-[:ActedIn]->(m)"
)

conn.execute("CREATE (:Person {name: 'Marlon Brando', birthDate: '1924-04-03'})")
conn.execute("CREATE (:Person {name: 'Diane Keaton', birthDate: '1946-01-05'})")
conn.execute("CREATE (:Movie {name: 'Apocalypse Now'})")
conn.execute("CREATE (:Movie {name: 'Annie Hall'})")

conn.execute(
    "MATCH (p:Person), (m:Movie) WHERE p.name = 'Marlon Brando' AND m.name = 'Apocalypse Now' CREATE (p)-[:ActedIn]->(m)"
)
conn.execute(
    "MATCH (p:Person), (m:Movie) WHERE p.name = 'Diane Keaton' AND m.name = 'Annie Hall' CREATE (p)-[:ActedIn]->(m)"
)
conn.execute(
    "MATCH (p:Person), (m:Movie) WHERE p.name = 'Diane Keaton' AND m.name = 'The Godfather: Part II' CREATE (p)-[:ActedIn]->(m)"
)
conn.execute(
    "MATCH (p:Person), (m:Movie) WHERE p.name = 'Al Pacino' AND m.name = 'Apocalypse Now' CREATE (p)-[:ActedIn]->(m)"
)
# --- End of Schema and Data Creation ---

graph = KuzuGraph(db, allow_dangerous_requests=True)

# --- Instantiate Gemini LLM ---
# Ensure you have your GOOGLE_API_KEY environment variable set
# or pass it directly to the constructor.
try:
    llm = ChatGoogleGenerativeAI(model="gemini-3-flash-preview")
    # You can also specify temperature, top_p, etc.
    # llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro-latest", temperature=0.7)
except Exception as e:
    print(f"Error initializing Gemini LLM. Ensure GOOGLE_API_KEY is set and langchain_google_genai is installed.")
    print(f"Details: {e}")
    exit()

# --- Create a KuzuQAChain with Gemini ---
chain = KuzuQAChain.from_llm(
    llm=llm,
    graph=graph,
    verbose=True, # Set to False for less output
    allow_dangerous_requests=True, # Be cautious with this in production
)

print("Graph Schema:")
print(graph.get_schema)
print("-" * 30)

# --- Ask questions ---
questions = [
    "Who acted in The Godfather: Part II?",
    "Robert De Niro played in which movies?",
    "Which actors acted in Apocalypse Now?",
    "What movies did Diane Keaton act in?",
    "Which actors appeared in more than one movie in the database?"
]

for question in questions:
    print(f"\n> Question: {question}")
    try:
        result = chain.invoke(question)
        print(f"< Answer: {result['result']}") # KuzuQAChain typically returns a dict with 'result'
    except Exception as e:
        print(f"Error invoking chain for question '{question}': {e}")
    print("-" * 30)

print("\nExample complete.")

# Clean up the database directory
if os.path.exists(db_path):
    if os.path.isdir(db_path):
        shutil.rmtree(db_path)
    else:
        os.remove(db_path)
