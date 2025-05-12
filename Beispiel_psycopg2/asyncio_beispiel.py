import asyncio

async def meine_aufgabe(n, sleep_time): 
    for i in range(3):
        print(f"Aufgabe {n}: Schritt {i+1}")
        await asyncio.sleep(sleep_time)
    print(f"Aufgabe {n} beendet!")

async def main():
    print("Programmstart")
    # Aufgaben mit unterschiedlicher Dauer:
    task1 = asyncio.create_task(meine_aufgabe(1, 1))
    task2 = asyncio.create_task(meine_aufgabe(2, 1.5))
    # Beide Aufgaben gleichzeitig abwarten:
    await asyncio.gather(task1, task2)
    print("Programmende")

asyncio.run(main())