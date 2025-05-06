import websockets
import asyncio
import psycopg2
import json
import uuid
import time

def dict_serializer(data):
  return json.dumps(data).encode('utf-8')

async def sendToWS(message, websocket):
        await websocket.send(json.dumps(message))
        try:
            prediction = await websocket.recv()
            # print(f"Response: {prediction}")
        except Exception as e:
            print(e)
        # await asyncio.sleep(1)

async def manage(row, websocket):
    data={}

    data['ID'] = row[0]
    data['Time']= row[1]
    for i in range (2,30):
        data[f"V{i-1}"]= float(row[i])
    data['Amount']= row[30]

    await sendToWS(data, websocket)        

async def send_function(rows):
    upto=max(10000, len(rows))
    # print("Now >")
    s = time.time()
    url = "ws://localhost:8000/predict"
    async with websockets.connect(url) as websocket:
        for row in rows[:upto]:
            await manage(row, websocket)
        await websocket.close()
    
    # print('Sent All :)')
    print(time.time() - s)
    cursor.close()
    conn.close()

server = "localhost"
database = "db_02"
username = "postgres"
password = "ABcd@12#$"
source = "creditcard_train"

try:
  conn = psycopg2.connect(dbname=database, user=username, password=password, host=server, port="5432", sslmode='disable')
except psycopg2.Error as e:
  print("Error connecting to PostgreSQL database:", e)
else:
  print("Connection established successfully!")

cursor = conn.cursor()

query =f"SELECT * FROM {source}"
cursor.execute(query)
rows = cursor.fetchall()

if __name__ == "__main__":
    asyncio.run(send_function(rows))


# kafka > websocket : DONE
# SHAP in admin
# GAN ... multiple fields of application
