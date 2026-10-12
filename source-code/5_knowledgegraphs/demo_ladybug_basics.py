"""LadyBug smoke test: create a small database, insert rows, and query it.

This checks that the embedded LadyBug database works on your machine before
you run the full movies_demo_ladybug.py example.
"""

import os
import shutil

import ladybug as lb

DB_PATH = "example.lbug"


def main():
    if os.path.exists(DB_PATH):
        shutil.rmtree(DB_PATH) if os.path.isdir(DB_PATH) else os.remove(DB_PATH)

    # Create an empty on-disk database and connect to it
    db = lb.Database(DB_PATH)
    conn = lb.Connection(db)

    # Create schema
    conn.execute("CREATE NODE TABLE User(name STRING PRIMARY KEY, age INT64)")

    # Insert some data
    conn.execute("CREATE (u:User {name: 'Alice', age: 30})")
    conn.execute("CREATE (u:User {name: 'Bob', age: 25})")
    conn.execute("CREATE (u:User {name: 'Charlie', age: 35})")

    # Query the data
    results = conn.execute("MATCH (u:User) RETURN u.name, u.age ORDER BY u.age")
    for row in results:
        print(row)

    # Optional: output as a DataFrame
    # results = conn.execute("MATCH (u:User) RETURN u.*")
    # print(results.get_as_df())


if __name__ == "__main__":
    main()
