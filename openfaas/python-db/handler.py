import psycopg2

def handle(event, context):
    try: 
        conn = psycopg2.connect("dbname='postgresdb' user='admin' port=5432 host='postgre-svc.default.svc.cluster.local' password='psltest'")
        cur = conn.cursor()
    except Exception as e:
        print("DB error {}".format(e))
        return {
            "statusCode": 500,
            "body": e
        }

    if event.method == "GET": 
        cur.execute(f"""SELECT * FROM experiment.researcher;""")
        rows = cur.fetchall()
        return {
            "statusCode": 200,
            "body": f"{str(rows)}\n"
        }
    elif event.method == "POST": 
        researcher = event.query["researcher"]
        query = f"INSERT INTO experiment.researcher (email) VALUES (%s);"
        cur.execute(query, (researcher,))
        conn.commit()
        return {
            "statusCode": 200,
            "body": f"Created researcher {researcher}\n" 
        }
