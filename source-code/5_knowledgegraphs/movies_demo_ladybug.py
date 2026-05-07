"""
Movies demo using LadyBug (fork of Kuzu) with Gemini LLM.

Since langchain-kuzu is archived and there's no langchain-ladybug package,
this implements a simple Text2Cypher chain manually:
  1. Gemini generates a Cypher query from a natural language question
  2. We execute it against LadyBug
  3. Gemini answers the question using the query results
"""
import ladybug as lb
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
import os
import shutil

# --- Optional: Set your Google API Key ---
# os.environ["GOOGLE_API_KEY"] = "YOUR_GOOGLE_API_KEY"

DB_PATH = "test_db_ladybug"

# ---------------------------------------------------------------------------
# Database setup
# ---------------------------------------------------------------------------
if os.path.exists(DB_PATH):
    if os.path.isdir(DB_PATH):
        shutil.rmtree(DB_PATH)
    else:
        os.remove(DB_PATH)

db = lb.Database(DB_PATH)
conn = lb.Connection(db)

# --- Schema and Data Creation ---
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

# ---------------------------------------------------------------------------
# Build schema string for the LLM prompt
# ---------------------------------------------------------------------------
def get_schema(conn: lb.Connection) -> str:
    """Return a human-readable schema description for the LLM."""
    tables = conn.execute("CALL SHOW_TABLES() RETURN *;")
    schema_lines = [
        "Graph Schema:",
        "=============",
        "Node labels and properties:",
    ]
    while tables.has_next():
        row = tables.get_next()
        # row format: [table_id, table_name, table_type, ...]
        table_name = row[1]
        table_type = row[2]
        if table_type == "NODE":
            info = conn.execute(f"CALL TABLE_INFO('{table_name}') RETURN *;")
            props = []
            while info.has_next():
                r = info.get_next()
                props.append(f"  - {r[1]}: {r[2]}")
            prop_summary = ", ".join(p.strip() for p in props)
            schema_lines.append(f"   :{table_name} {{{prop_summary}}}")
        elif table_type == "REL":
            conn_info = conn.execute(f"CALL SHOW_CONNECTION('{table_name}') RETURN *;")
            rows = []
            while conn_info.has_next():
                rows.append(conn_info.get_next())
            if rows:
                r = rows[0]
                schema_lines.append(f"  (: {r[0]} )-[:{table_name}]->(: {r[1]} )")
    return "\n".join(schema_lines)


SCHEMA = get_schema(conn)
print(SCHEMA)
print("-" * 30)

# ---------------------------------------------------------------------------
# LLM setup
# ---------------------------------------------------------------------------
try:
    llm = ChatGoogleGenerativeAI(model="gemini-3.1-flash-lite")
except Exception as e:
    print(f"Error initializing Gemini LLM. Ensure GOOGLE_API_KEY is set.")
    print(f"Details: {e}")
    exit()

# Cypher generation prompt
cypher_prompt = ChatPromptTemplate.from_messages([
    ("system", """You are a Cypher query expert for the LadyBug graph database.
Given the following graph schema and a natural language question, generate ONLY a valid Cypher query.
Do NOT include markdown code fences, explanations, or any text outside the query.

Schema:
{schema}

Important rules:
- Use MATCH, WHERE, RETURN clauses
- Node labels are: Person, Movie
- Relationship type is: ActedIn (FROM Person TO Movie)
- Property names are: name, birthDate
- Always return useful properties, not just node IDs"""),
    ("human", "Question: {question}\n\nCypher:"),
])

# QA prompt
qa_prompt = ChatPromptTemplate.from_messages([
    ("system", """You are a helpful assistant. Answer the question based on the query results below.
If the results are empty, say so clearly."""),
    ("human", "Question: {question}\n\nQuery Results: {context}\n\nAnswer:"),
])

cypher_chain = cypher_prompt | llm
qa_chain = qa_prompt | llm


def extract_text(content) -> str:
    """Helper to extract text from LangChain message content."""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        text_parts = []
        for part in content:
            if isinstance(part, str):
                text_parts.append(part)
            elif isinstance(part, dict) and "text" in part:
                text_parts.append(part["text"])
        return "".join(text_parts)
    return str(content)


def ask_graph(question: str) -> str:
    """Ask a natural language question against the graph database."""
    # Step 1: Generate Cypher
    cypher_response = cypher_chain.invoke({"schema": SCHEMA, "question": question})
    cypher = extract_text(cypher_response.content).strip()
    # Strip markdown fences if present
    if cypher.startswith("```"):
        cypher = cypher.split("\n", 1)[-1].rstrip("```")
    print(f"  Generated Cypher: {cypher}")

    # Step 2: Execute Cypher
    try:
        result = conn.execute(cypher)
        column_names = result.get_column_names()
        rows = []
        while result.has_next():
            row = result.get_next()
            rows.append(dict(zip(column_names, row, strict=False)))
    except Exception as e:
        return f"Error executing Cypher query: {e}\nQuery was: {cypher}"

    # Step 3: Generate natural language answer
    answer_response = qa_chain.invoke({"question": question, "context": rows})
    return extract_text(answer_response.content)


# ---------------------------------------------------------------------------
# Run questions
# ---------------------------------------------------------------------------
questions = [
    "Who acted in The Godfather: Part II?",
    "Robert De Niro played in which movies?",
    "Which actors acted in Apocalypse Now?",
    "What movies did Diane Keaton act in?",
    "Which actors appeared in more than one movie in the database?",
]

for question in questions:
    print(f"\n> Question: {question}")
    try:
        answer = ask_graph(question)
        print(f"< Answer: {answer}")
    except Exception as e:
        print(f"Error: {e}")
    print("-" * 30)

print("\nExample complete.")

# Clean up
if os.path.exists(DB_PATH):
    if os.path.isdir(DB_PATH):
        shutil.rmtree(DB_PATH)
    else:
        os.remove(DB_PATH)
