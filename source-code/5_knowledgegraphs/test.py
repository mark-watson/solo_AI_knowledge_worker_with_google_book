import ladybug as lb

def main():
     # Create an empty on-disk database and connect to it
    db = lb.Database("example.lbug")
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
