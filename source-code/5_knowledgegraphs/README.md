# KnowledgeGraph example derived from an example in my "Ollama in Action book

## Example output

```text
$ p gemini_kuzu.py
Graph Schema:
Node properties: [{'properties': [('name', 'STRING')], 'label': 'Movie'}, {'properties': [('name', 'STRING'), ('birthDate', 'STRING')], 'label': 'Person'}]
Relationships properties: [{'properties': [], 'label': 'ActedIn'}]
Relationships: ['(:Person)-[:ActedIn]->(:Movie)']

------------------------------

> Question: Who acted in The Godfather: Part II?


> Entering new KuzuQAChain chain...
Generated Cypher:
MATCH (p:Person)-[:ActedIn]->(m:Movie {name: 'The Godfather: Part II'}) RETURN p.name
Full Context:
[{'p.name': 'Al Pacino'}, {'p.name': 'Robert De Niro'}, {'p.name': 'Diane Keaton'}]

> Finished chain.
< Answer: Al Pacino, Robert De Niro, and Diane Keaton acted in The Godfather: Part II.
------------------------------

> Question: Robert De Niro played in which movies?


> Entering new KuzuQAChain chain...
Generated Cypher:
MATCH (p:Person)-[:ActedIn]->(m:Movie) WHERE p.name = 'Robert De Niro' RETURN m.name
Full Context:
[{'m.name': 'The Godfather: Part II'}]

> Finished chain.
< Answer: Robert De Niro played in The Godfather: Part II.
------------------------------

> Question: Which actors acted in Apocalypse Now?


> Entering new KuzuQAChain chain...
Generated Cypher:
MATCH (p:Person)-[:ActedIn]->(m:Movie {name: 'Apocalypse Now'}) RETURN p.name
Full Context:
[{'p.name': 'Al Pacino'}, {'p.name': 'Marlon Brando'}]

> Finished chain.
< Answer: Al Pacino, Marlon Brando acted in Apocalypse Now.
------------------------------

> Question: What movies did Diane Keaton act in?


> Entering new KuzuQAChain chain...
Generated Cypher:
MATCH (p:Person)-[:ActedIn]->(m:Movie) WHERE p.name = 'Diane Keaton' RETURN m.name
Full Context:
[{'m.name': 'The Godfather: Part II'}, {'m.name': 'Annie Hall'}]

> Finished chain.
< Answer: Diane Keaton acted in *The Godfather: Part II* and *Annie Hall*.
------------------------------

> Question: Which actors appeared in more than one movie in the database?


> Entering new KuzuQAChain chain...
Generated Cypher:
MATCH (p:Person)-[:ActedIn]->(m:Movie)
WITH p, COUNT(m) AS movieCount
WHERE movieCount > 1
RETURN p.name
Full Context:
[{'p.name': 'Diane Keaton'}, {'p.name': 'Al Pacino'}]

> Finished chain.
< Answer: Diane Keaton and Al Pacino appeared in more than one movie in the database.
------------------------------

Example complete.
```
