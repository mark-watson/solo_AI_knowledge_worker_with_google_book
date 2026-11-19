"""
Movies demo using LadyBug (a fork of Kuzu) with Gemini.

There is no LangChain integration package for LadyBug, so this example builds
a small Text2Cypher chain by hand:
  1. Gemini writes a Cypher query from a natural language question.
  2. We check that the query only reads data, then run it against LadyBug.
  3. Gemini answers the question using the query results.
"""

import os
import re
import shutil
import sys

import ladybug as lb
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI

DB_PATH = "test_db_ladybug"

# Google ships new models several times a year. See the model naming note in
# python_auth_setup.md when this model ID stops working.
MODEL_ID = "gemini-4-hydrogen"

PEOPLE = [
    ("Al Pacino", "1940-04-25"),
    ("Robert De Niro", "1943-08-17"),
    ("Marlon Brando", "1924-04-03"),
    ("Diane Keaton", "1946-01-05"),
]

MOVIES = [
    "The Godfather",
    "The Godfather: Part II",
    "The Godfather Coda: The Death of Michael Corleone",
    "Apocalypse Now",
    "Annie Hall",
]

ACTED_IN = [
    ("Marlon Brando", "The Godfather"),
    ("Al Pacino", "The Godfather"),
    ("Diane Keaton", "The Godfather"),
    ("Al Pacino", "The Godfather: Part II"),
    ("Robert De Niro", "The Godfather: Part II"),
    ("Diane Keaton", "The Godfather: Part II"),
    ("Al Pacino", "The Godfather Coda: The Death of Michael Corleone"),
    ("Diane Keaton", "The Godfather Coda: The Death of Michael Corleone"),
    ("Marlon Brando", "Apocalypse Now"),
    ("Diane Keaton", "Annie Hall"),
]


def remove_db():
    if os.path.isdir(DB_PATH):
        shutil.rmtree(DB_PATH)
    elif os.path.exists(DB_PATH):
        os.remove(DB_PATH)


def build_graph(conn):
    conn.execute("CREATE NODE TABLE Person (name STRING PRIMARY KEY, birthDate STRING)")
    conn.execute("CREATE NODE TABLE Movie (name STRING PRIMARY KEY)")
    conn.execute("CREATE REL TABLE ActedIn (FROM Person TO Movie)")

    # $name and friends are query parameters. LadyBug fills them in safely,
    # so a title that contains a quote cannot break or change the query.
    for name, birth_date in PEOPLE:
        conn.execute(
            "CREATE (:Person {name: $name, birthDate: $birthDate})",
            {"name": name, "birthDate": birth_date},
        )
    for title in MOVIES:
        conn.execute("CREATE (:Movie {name: $name})", {"name": title})
    for person, title in ACTED_IN:
        conn.execute(
            "MATCH (p:Person {name: $person}), (m:Movie {name: $title}) "
            "CREATE (p)-[:ActedIn]->(m)",
            {"person": person, "title": title},
        )


def get_schema(conn):
    """Return a schema description for the LLM prompt."""
    lines = ["Node tables:"]
    rels = []
    tables = conn.execute("CALL SHOW_TABLES() RETURN name, type;")
    for table_name, table_type in tables:
        if table_type == "NODE":
            info = conn.execute(f"CALL TABLE_INFO('{table_name}') RETURN name, type;")
            props = ", ".join(f"{prop}: {ptype}" for prop, ptype in info)
            lines.append(f"  (:{table_name} {{{props}}})")
        elif table_type == "REL":
            ends = conn.execute(f"CALL SHOW_CONNECTION('{table_name}') RETURN *;")
            for src, dst, *_ in ends:
                rels.append(f"  (:{src})-[:{table_name}]->(:{dst})")
    return "\n".join(lines + ["Relationship tables:"] + rels)


READ_START = re.compile(r"\s*(MATCH|OPTIONAL\s+MATCH|WITH|UNWIND|RETURN)\b", re.IGNORECASE)
WRITE_CLAUSES = re.compile(
    r"\b(CREATE|MERGE|DELETE|DETACH|SET|REMOVE|DROP|ALTER|COPY|INSTALL|LOAD|ATTACH)\b",
    re.IGNORECASE,
)


def clean_cypher(text):
    """Strip a Markdown code fence if the model added one."""
    match = re.search(r"```(?:cypher)?\s*(.*?)```", text, re.DOTALL | re.IGNORECASE)
    return (match.group(1) if match else text).strip()


def ask_graph(conn, schema, cypher_chain, qa_chain, question):
    cypher = clean_cypher(cypher_chain.invoke({"schema": schema, "question": question}).text)
    print(f"  Generated Cypher: {cypher}")

    # Never run model-written text unless it is a read-only query.
    if not READ_START.match(cypher) or WRITE_CLAUSES.search(cypher):
        return "Refusing to run: the model did not return a read-only Cypher query."

    try:
        result = conn.execute(cypher)
        columns = result.get_column_names()
        rows = [dict(zip(columns, row)) for row in result]
    except Exception as e:
        return f"Error executing Cypher query: {e}"

    return qa_chain.invoke({"question": question, "context": rows}).text


def main():
    remove_db()
    db = lb.Database(DB_PATH)
    conn = lb.Connection(db)
    build_graph(conn)

    schema = get_schema(conn)
    print(schema)
    print("-" * 30)

    try:
        llm = ChatGoogleGenerativeAI(model=MODEL_ID, thinking_level="low")
    except Exception as e:
        sys.exit(f"Error initializing Gemini. Is GOOGLE_API_KEY set?\nDetails: {e}")

    cypher_prompt = ChatPromptTemplate.from_messages([
        ("system", """You write Cypher queries for the LadyBug graph database.
Given the graph schema and a question, return ONLY one read-only Cypher query.
Do not add Markdown code fences, explanations, or any other text.

Schema:
{schema}

Return useful properties such as names, not internal node IDs."""),
        ("human", "Question: {question}"),
    ])

    qa_prompt = ChatPromptTemplate.from_messages([
        ("system", """Answer the question using only the query results below.
If the results are empty, say that the database has no answer."""),
        ("human", "Question: {question}\n\nQuery results: {context}"),
    ])

    cypher_chain = cypher_prompt | llm
    qa_chain = qa_prompt | llm

    questions = [
        "Who acted in The Godfather: Part II?",
        "Robert De Niro played in which movies?",
        "Which actors acted in Apocalypse Now?",
        "What movies did Diane Keaton act in?",
        "Which actors appeared in more than one movie in the database?",
        "Delete every movie from the database.",
    ]

    for question in questions:
        print(f"\n> Question: {question}")
        print(f"< Answer: {ask_graph(conn, schema, cypher_chain, qa_chain, question)}")
        print("-" * 30)

    conn.close()
    db.close()
    remove_db()


if __name__ == "__main__":
    main()
