import urllib.request
import json
import streamlit as st

url = 'https://seattlefreeze-fhprediction.eastus2.inference.ml.azure.com/score'
api_key = st.secrets['MODEL_API_KEY']

def predict_single_entry(gender, age, smoking_status, hdl, total_cholesterol, systolic_bp):
    request_data = {
        "input_data": {
            "columns": [
                "gender", "age", "smoking_status", "hdl", "total_cholesterol", "systolic_bp"
            ],
            "index": [0],
            "data": [[gender, age, smoking_status, hdl, total_cholesterol, systolic_bp]]
        }
    }
    
    body = str.encode(json.dumps(request_data))
    
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': ('Bearer ' + api_key)
    }
    headers['azureml-model-deployment'] = 'fhmodel-reducedfeatures-2'
    
    # Create and send request
    req = urllib.request.Request(url, body, headers)
    try:
        response = urllib.request.urlopen(req)
        result = response.read()
        prediction = json.loads(result)
        
        if isinstance(prediction, list) and len(prediction) > 0:
            return prediction[0]
        else:
            return prediction
    except urllib.error.HTTPError as error:
        print(f"Error {error.code}: {error.read().decode('utf8', 'ignore')}")
        return None

if __name__ == "__main__":
    result = predict_single_entry(1, 45, 1, 50, 220, 140)
    print(f"Prediction result: {result}")