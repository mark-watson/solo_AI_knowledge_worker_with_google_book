# Knowledge Graphs with LadyBug and Gemini


Knowledge graphs represent information as networks of entities (nodes) connected by relationships (edges). Unlike flat tables or plain text documents, graphs capture the *structure* of knowledge — who acted in which film, which company acquired which startup, which gene regulates which protein. For solo knowledge workers, knowledge graphs offer a powerful way to organize, query, and reason over interconnected data that would be awkward to fit into spreadsheets or relational databases.

In this chapter we combine three technologies to build a natural language question-answering system over a knowledge graph:

- **LadyBug** — a high-performance, embedded graph database (a fork of Kuzu) that requires no server setup
- **LangChain** — an orchestration framework that we use to wire Gemini to our graph data
- **Google Gemini** — the LLM that translates natural language questions into graph queries and formulates human-readable answers

![System architecture for Knowledge Graph QA with LadyBug and Gemini](resources/FIG_5_knowledgegraphs.jpg)

## Why Knowledge Graphs Matter for Solo Knowledge Workers

Traditional databases store data in rows and columns. When your data is inherently relational — people connected to projects, documents linked to topics, products tied to suppliers — you end up writing complex JOIN queries or maintaining brittle cross-reference spreadsheets. Knowledge graphs make these relationships first-class citizens: you simply traverse edges to find connected information.

For solo consultants, researchers, and content creators, knowledge graphs are especially useful for:

- **Research synthesis**: Connecting authors, papers, institutions, and topics into a navigable network
- **Client/project management**: Tracking relationships between contacts, companies, deliverables, and skills
- **Content knowledge bases**: Organizing articles, tags, sources, and citations as a graph you can query in natural language

## The LadyBug Embedded Graph Database

LadyBug is an embedded, ACID-compliant graph database (forked from Kuzu) written in C++ with Python bindings. "Embedded" means it runs in-process — there is no separate database server to install or manage. You simply create a database directory and start issuing queries. This makes LadyBug ideal for solo developers and small projects where operational overhead should be minimal.

LadyBug uses the **Cypher** query language, which is the most widely adopted language for property graphs. Cypher reads like ASCII art for graphs:

```cypher
MATCH (p:Person)-[:ActedIn]->(m:Movie)
WHERE p.name = 'Al Pacino'
RETURN m.name
```

This query says: "find all Movie nodes connected to a Person node named 'Al Pacino' via an ActedIn edge, and return the movie names."

## Building a Movie Knowledge Graph

Our example builds a small movie knowledge graph with two node types (`Person` and `Movie`) and one relationship type (`ActedIn`). We populate it with classic film data:

- **Actors**: Al Pacino, Robert De Niro, Marlon Brando, Diane Keaton
- **Films**: The Godfather, The Godfather: Part II, The Godfather Coda, Apocalypse Now, Annie Hall

### Schema and Data Setup

The first part of the script creates the graph schema and inserts data using Cypher statements:

```python
import ladybug as lb
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
import os
import shutil

DB_PATH = "test_db_ladybug"
db = lb.Database(DB_PATH)
conn = lb.Connection(db)

# Create schema
conn.execute("CREATE NODE TABLE Movie (name STRING PRIMARY KEY)")
conn.execute("CREATE NODE TABLE Person (name STRING, birthDate STRING PRIMARY KEY)")
conn.execute("CREATE REL TABLE ActedIn (FROM Person TO Movie)")
```

Each node table has a primary key, and the relationship table `ActedIn` defines directed edges from `Person` nodes to `Movie` nodes. We then insert actors, movies, and the relationships between them:

```python
conn.execute("CREATE (:Person {name: 'Al Pacino', birthDate: '1940-04-25'})")
conn.execute("CREATE (:Movie {name: 'The Godfather'})")

# Create relationships
conn.execute(
    f"MATCH (p:Person), (m:Movie) "
    f"WHERE p.name = 'Al Pacino' AND m.name = 'The Godfather' "
    f"CREATE (p)-[:ActedIn]->(m)"
)
```

Additional actors (Marlon Brando, Diane Keaton) and films (Apocalypse Now, Annie Hall) are added with their respective `ActedIn` relationships.

## Implementing a Text2Cypher Chain Manually

Since specialized LangChain integrations for LadyBug are evolving, we implement a robust "Text2Cypher" chain manually using LangChain Expression Language (LCEL). This involves two main steps: first, generating a Cypher query from the natural language question, and second, using the database results to generate a final answer.

We start by defining a helper to extract the schema from the database so Gemini knows what labels and properties are available:

```python
def get_schema(conn: lb.Connection) -> str:
    """Return a human-readable schema description for the LLM."""
    tables = conn.execute("CALL SHOW_TABLES() RETURN *;")
    schema_lines = ["Graph Schema:", "=============", "Node labels and properties:"]
    while tables.has_next():
        row = tables.get_next()
        table_name, table_type = row[1], row[2]
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
            if conn_info.has_next():
                r = conn_info.get_next()
                schema_lines.append(f"  (: {r[0]} )-[:{table_name}]->(: {r[1]} )")
    return "\n".join(schema_lines)

SCHEMA = get_schema(conn)
```

Next, we set up the prompts and the LCEL chains:

```python
llm = ChatGoogleGenerativeAI(model="gemini-3.1-flash-lite")

cypher_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a Cypher query expert... [Schema and rules here]"),
    ("human", "Question: {question}\n\nCypher:"),
])

qa_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant. Answer based on query results."),
    ("human", "Question: {question}\n\nQuery Results: {context}\n\nAnswer:"),
])

cypher_chain = cypher_prompt | llm
qa_chain = qa_prompt | llm
```

The `ask_graph` function orchestration involves invoking the `cypher_chain`, cleaning the output, executing it against the database, and finally passing the results to the `qa_chain`.

## Asking Natural Language Questions

With the setup complete, we can ask questions in plain English and receive answers grounded in the graph data:

```python
questions = [
    "Who acted in The Godfather: Part II?",
    "Robert De Niro played in which movies?",
    "Which actors acted in Apocalypse Now?",
    "What movies did Diane Keaton act in?",
    "Which actors appeared in more than one movie in the database?"
]

for question in questions:
    print(f"\n> Question: {question}")
    answer = ask_graph(question)
    print(f"< Answer: {answer}")
```

### Example Output

Here is typical output from running the script. Notice how Gemini generates correct Cypher for each question:

```text
> Question: Who acted in The Godfather: Part II?
  Generated Cypher: MATCH (p:Person)-[:ActedIn]->(m:Movie {name: "The Godfather: Part II"})
RETURN p.name
< Answer: The actors in The Godfather: Part II include Al Pacino, Robert De Niro, and Diane Keaton.

> Question: Robert De Niro played in which movies?
  Generated Cypher: MATCH (p:Person {name: "Robert De Niro"})-[:ActedIn]->(m:Movie)
RETURN m.name
< Answer: Robert De Niro played in The Godfather: Part II.

> Question: Which actors appeared in more than one movie in the database?
  Generated Cypher: MATCH (p:Person)-[:ActedIn]->(m:Movie)
WITH p, count(m) AS movieCount
WHERE movieCount > 1
RETURN p.name, movieCount
< Answer: The actors who appeared in more than one movie are Diane Keaton and Al Pacino.
```

The last question demonstrates that Gemini understands both the graph schema and the semantics of the question, correctly using aggregation and filtering.

## Running the Example

Ensure your `GOOGLE_API_KEY` environment variable is set, then install the dependencies and run:

```bash
uv sync
uv run movies_demo_ladybug.py
```

The script creates a local `test_db_ladybug/` directory for the database. You can delete this directory to start fresh on subsequent runs.

## Wrap Up

Knowledge graphs paired with LLMs create a powerful pattern: the graph provides structured, reliable data while the LLM handles the translation between human language and formal queries. LadyBug's embedded architecture eliminates operational complexity, and manual Text2Cypher implementation via LangChain provides maximum control. This combination lets solo knowledge workers build domain-specific question-answering systems — over client data, research corpora, or any structured knowledge — with minimal code and no infrastructure to manage.
