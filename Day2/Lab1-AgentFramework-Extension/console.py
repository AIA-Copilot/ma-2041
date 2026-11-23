import asyncio
from pathlib import Path
from dotenv import load_dotenv
from expense_agent import process_expenses_data

if __name__ == "__main__":
    load_dotenv()
    data = Path(__file__).with_name("data.txt").read_text()
    print(asyncio.run(process_expenses_data(input("What should I do with the expenses? "), data)))
