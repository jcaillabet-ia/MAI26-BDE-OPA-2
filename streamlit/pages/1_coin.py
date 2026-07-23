import asyncio
import httpx
import pandas as pd
import streamlit as st

async def fetch_prediction():
    url = f"http://api:8000/ml/predict"
    st.write(st.query_params['id'])
    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(url, json={"coin_id": st.query_params['id']})
        return response.json()

url = f"http://api:8000/candle/{st.query_params['id']}/list"
response = httpx.get(url)
candles = response.json()

df = pd.DataFrame(candles, columns= ['timestamp', 'open', 'high', 'low', 'close', 'volume'])
df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
last_candle = df.iloc[-1]
df = df.iloc[::50]

axe_x = "timestamp"
axe_y = "close"

st.line_chart(
    df, 
    x=axe_x, 
    y=axe_y
)

st.title("Prediction:")

# url = f"http://api:8000/ml/predict"
# response = httpx.post(url, json={"coin_id": st.query_params['id']})
# st.write(response.status_code)
# candles = response.json()

with st.spinner("Prédiction en cours..."):
    # asyncio.run() permet d'exécuter la fonction async dans le flux Streamlit
    try:
        resultat = asyncio.run(fetch_prediction())
        st.success("Données récupérées avec succès !")
        st.write(resultat)
    except httpx.TimeoutException:
        st.error(
            "L'API a mis trop de temps à répondre, même avec le nouveau timeout."
        )
    except Exception as e:
        st.error(f"Une erreur est survenue : {e}")