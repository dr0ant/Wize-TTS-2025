import psycopg2

class PostgresClient:
    def __init__(self, host, port, database, user, password):
        self.DB_HOST = host
        self.DB_PORT = port
        self.DB_NAME = database
        self.DB_USER = user
        self.DB_PASSWORD = password

    def execute_query(self, query, params=None, fetch=True):
        """
        Executes a query on the PostgreSQL database.

        :param query: The SQL query to execute.
        :param params: Optional parameters for the query (tuple).
        :param fetch: Boolean indicating whether to fetch results. If False, only executes the query.
        :return: Query results if fetch=True, otherwise None.
        """
        try:
            with psycopg2.connect(
                host=self.DB_HOST,
                port=self.DB_PORT,
                database=self.DB_NAME,
                user=self.DB_USER,
                password=self.DB_PASSWORD
            ) as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query, params)
                    
                    if fetch:
                        return cursor.fetchall()
                    else:
                        conn.commit()
                        return None
        except psycopg2.Error as e:
            print(f"An error occurred: {e}")
            return None
