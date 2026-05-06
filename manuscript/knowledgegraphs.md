# Knowledge Graphs with Kuzu and Gemini


Knowledge graphs represent information as networks of entities (nodes) connected by relationships (edges). Unlike flat tables or plain text documents, graphs capture the *structure* of knowledge — who acted in which film, which company acquired which startup, which gene regulates which protein. For solo knowledge workers, knowledge graphs offer a powerful way to organize, query, and reason over interconnected data that would be awkward to fit into spreadsheets or relational databases.

In this chapter we combine three technologies to build a natural language question-answering system over a knowledge graph:

- **Kuzu** — a high-performance, embedded graph database that requires no server setup
- **LangChain** — an orchestration framework that wires LLMs to external tools and data sources
- **Google Gemini** — the LLM that translates natural language questions into graph queries and formulates human-readable answers

![System architecture for Knowledge Graph QA with Kuzu, LangChain, and Gemini](resources/FIG_5_knowledgegraphs.jpg)

## Why Knowledge Graphs Matter for Solo Knowledge Workers

Traditional databases store data in rows and columns. When your data is inherently relational — people connected to projects, documents linked to topics, products tied to suppliers — you end up writing complex JOIN queries or maintaining brittle cross-reference spreadsheets. Knowledge graphs make these relationships first-class citizens: you simply traverse edges to find connected information.

For solo consultants, researchers, and content creators, knowledge graphs are especially useful for:

- **Research synthesis**: Connecting authors, papers, institutions, and topics into a navigable network
- **Client/project management**: Tracking relationships between contacts, companies, deliverables, and skills
- **Content knowledge bases**: Organizing articles, tags, sources, and citations as a graph you can query in natural language

## The Kuzu Embedded Graph Database

Kuzu is an embedded, ACID-compliant graph database written in C++ with Python bindings. "Embedded" means it runs in-process — there is no separate database server to install or manage. You simply create a database directory and start issuing queries. This makes Kuzu ideal for solo developers and small projects where operational overhead should be minimal.

Kuzu uses the **Cypher** query language, which is the most widely adopted language for property graphs. Cypher reads like ASCII art for graphs:

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
import kuzu
from langchain.chains import KuzuQAChain
from langchain_community.graphs import KuzuGraph
from langchain_google_genai import ChatGoogleGenerativeAI
import os

db = kuzu.Database("test_db_gemini")
conn = kuzu.Connection(db)

# Create schema
conn.execute("CREATE NODE TABLE Movie (name STRING, PRIMARY KEY(name))")
conn.execute(
    "CREATE NODE TABLE Person (name STRING, birthDate STRING, PRIMARY KEY(name))"
)
conn.execute("CREATE REL TABLE ActedIn (FROM Person TO Movie)")
```

Each node table has a primary key (the `name` field), and the relationship table `ActedIn` defines directed edges from `Person` nodes to `Movie` nodes. We then insert actors, movies, and the relationships between them:

```python
conn.execute("CREATE (:Person {name: 'Al Pacino', birthDate: '1940-04-25'})")
conn.execute("CREATE (:Person {name: 'Robert De Niro', birthDate: '1943-08-17'})")
conn.execute("CREATE (:Movie {name: 'The Godfather'})")
conn.execute("CREATE (:Movie {name: 'The Godfather: Part II'})")
conn.execute(
    "CREATE (:Movie {name: 'The Godfather Coda: The Death of Michael Corleone'})"
)

# Create relationships
conn.execute(
    "MATCH (p:Person), (m:Movie) WHERE p.name = 'Al Pacino' "
    "AND m.name = 'The Godfather' CREATE (p)-[:ActedIn]->(m)"
)
```

Additional actors (Marlon Brando, Diane Keaton) and films (Apocalypse Now, Annie Hall) are added with their respective `ActedIn` relationships.

## Connecting Gemini to the Graph via LangChain

The real power of this example emerges when we connect the knowledge graph to Gemini through LangChain's `KuzuQAChain`. This chain automates the entire question-answering pipeline:

1. The user asks a natural language question
2. Gemini generates a Cypher query based on the graph schema
3. The Cypher query executes against the Kuzu database
4. The query results are sent back to Gemini
5. Gemini formulates a natural language answer

```python
graph = KuzuGraph(db, allow_dangerous_requests=True)

llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro-latest")

chain = KuzuQAChain.from_llm(
    llm=llm,
    graph=graph,
    verbose=True,
    allow_dangerous_requests=True,
)
```

The `verbose=True` flag is especially instructive during development because it prints the generated Cypher query and the raw database results before the final answer — letting you see exactly how Gemini translates your question.

## Asking Natural Language Questions

With the chain set up, we can ask questions in plain English and receive answers grounded in the graph data:

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
    result = chain.invoke(question)
    print(f"< Answer: {result['result']}")
```

### Example Output

Here is typical output from running the script. Notice how Gemini generates correct Cypher for each question:

```text
> Question: Who acted in The Godfather: Part II?
Generated Cypher:
MATCH (p:Person)-[:ActedIn]->(m:Movie {name: 'The Godfather: Part II'}) RETURN p.name
Full Context:
[{'p.name': 'Al Pacino'}, {'p.name': 'Robert De Niro'}, {'p.name': 'Diane Keaton'}]
< Answer: Al Pacino, Robert De Niro, and Diane Keaton acted in The Godfather: Part II.

> Question: Robert De Niro played in which movies?
Generated Cypher:
MATCH (p:Person)-[:ActedIn]->(m:Movie) WHERE p.name = 'Robert De Niro' RETURN m.name
Full Context:
[{'m.name': 'The Godfather: Part II'}]
< Answer: Robert De Niro played in The Godfather: Part II.

> Question: Which actors appeared in more than one movie in the database?
Generated Cypher:
MATCH (p:Person)-[:ActedIn]->(m:Movie)
WITH p, COUNT(m) AS movieCount
WHERE movieCount > 1
RETURN p.name
Full Context:
[{'p.name': 'Diane Keaton'}, {'p.name': 'Al Pacino'}]
< Answer: Diane Keaton and Al Pacino appeared in more than one movie in the database.
```

The last question is particularly noteworthy: Gemini correctly generates a Cypher query with aggregation (`COUNT`) and filtering (`WHERE movieCount > 1`) — demonstrating that the LLM understands both the graph schema and the semantics of the question.

## Running the Example

Ensure your `GOOGLE_API_KEY` environment variable is set, then install the dependencies and run:

```bash
pip install kuzu langchain langchain-community langchain-google-genai
python movies_demo.py
```

The script creates a local `test_db_gemini/` directory for the Kuzu database. You can delete this directory to start fresh on subsequent runs.

## Wrap Up

Knowledge graphs paired with LLMs create a powerful pattern: the graph provides structured, reliable data while the LLM handles the translation between human language and formal queries. Kuzu's embedded architecture eliminates operational complexity, and LangChain's `KuzuQAChain` handles the orchestration automatically. This combination lets solo knowledge workers build domain-specific question-answering systems — over client data, research corpora, or any structured knowledge — with minimal code and no infrastructure to manage.
