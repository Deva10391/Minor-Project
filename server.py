from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import torch
import uvicorn
import shap
import pickle
import json

app = FastAPI()

def removeID(msg):
    msg_i=msg.value.decode('utf-8')
    data_dict = json.loads(msg_i)
    ID=data_dict['ID']
    del data_dict['ID']
    data_list=[value for value in data_dict.values()]
    keys=[key for key in data_dict.keys()]

    return data_list, ID, keys

def prepare(data_list):
    prev_data_frame = pd.DataFrame(data_list)
    data_frame=prev_data_frame.transpose().values[0]
    
    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(data_frame, check_additivity=False)
    shap_values = shap_values.transpose()
    
    return {'data_frame': data_frame, 'shap_values': shap_values}

name = "lr"

with open(f"model_{name}.pkl", "rb") as f:
    model = pickle.load(f)

with open(f"explainer_{name}.pkl", "rb") as f:
    explainer = pickle.load(f)

def predict(data_list):
    y_pred_test=model.predict([data_list])
    return y_pred_test

@app.websocket("/predict")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("Client connected")
    try:
        while True:
            data = await websocket.receive_text()
            data_dict = json.loads(data)
            ID = data_dict.pop("ID", None)
            # rL=removeID(data)
            data_list = list(data_dict.values()) # rL[0]
            # ID=rL[1]
            # keys=rL[2]
            y=predict(data_list)
            response = {"ID": ID, "prediction": y.tolist()}
            # if y == 1.0:
            #     print(response)
            try:
                await websocket.send_text(json.dumps(response))
            except Exception as e:
                print(f"Error processing input: {e}")
    except WebSocketDisconnect:
        print("Client disconnected.")
    except Exception as e:
        print(f"Connection closed: {e}")
        await websocket.close()

    finally:
        print("WebSocket closed.")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
