import asyncio
import psycopg
from psycopg_pool import AsyncConnectionPool
import sys

# Windows-spezifische Event-Loop-Policy setzen für Kompatibilität
if sys.platform.startswith("win"):
    from asyncio import WindowsSelectorEventLoopPolicy
    asyncio.set_event_loop_policy(WindowsSelectorEventLoopPolicy())

# Verbindungsstring – bitte anpassen!
conninfo = "dbname=test user=postgres password=secret host=localhost"

class DatabasePool:
    """Einfache Klasse zur Verwaltung eines asynchronen Verbindungspools."""
    def __init__(self, conninfo, min_size=5):
        self.conninfo = conninfo
        self.min_size = min_size
        self.pool = None

    async def initialize(self):
        """Initialisiert den Verbindungspool."""
        self.pool = AsyncConnectionPool(self.conninfo, min_size=self.min_size)
        await self.pool.wait()
        print("Verbindungspool initialisiert")

    async def close(self):
        """Schließt den Verbindungspool."""
        if self.pool:
            await self.pool.close()
            print("Verbindungspool geschlossen")

    def get_pool(self):
        """Gibt den Verbindungspool zurück."""
        return self.pool

async def perform_query(pool, query_id, sql, description):
    print(f"Starte Abfrage {query_id}: {description} ...")
    
    # Verbindung aus dem Pool holen und benutzen
    async with pool.connection() as conn:
        async with conn.cursor() as cur:
            await cur.execute(sql)
            result = await cur.fetchone()
    
    print(f"Abfrage {query_id} ({description}) beendet: Ergebnis = {result[0]}")

async def main():
    # Verbindungspool über Klasse anlegen
    db_pool = DatabasePool(conninfo, min_size=5)
    
    try:
        await db_pool.initialize()
        print("Starte 3 parallele Abfragen auf my_table...\n")

        tasks = [
            perform_query(db_pool.get_pool(), 1, "SELECT COUNT(*) FROM my_table", "Gesamtanzahl der Datensätze"),
            perform_query(db_pool.get_pool(), 2, "SELECT AVG(alter) FROM my_table", "Durchschnittsalter"),
            perform_query(db_pool.get_pool(), 3, "SELECT COUNT(*) FROM my_table WHERE stadt = 'Bochum'", "Anzahl in Bochum"),
        ]
        await asyncio.gather(*tasks)
        
        print("\nAlle 3 Abfragen wurden abgeschlossen")

    finally:
        # Pool am Schluss sauber schließen
        await db_pool.close()

if __name__ == "__main__":
    asyncio.run(main())