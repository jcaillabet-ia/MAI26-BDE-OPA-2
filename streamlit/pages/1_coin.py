import asyncio
import httpx
import pandas as pd
import streamlit as st


coin_id = st.query_params.get("id")

if not coin_id:
    st.title("Détail crypto")
    st.warning("Aucune crypto sélectionnée. Retourne sur la page principale et clique sur « Consulter ».")
    st.stop()

async def fetch_prediction():
    url = f"http://api:8000/ml/predict"
    st.write(coin_id)
    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(url, json={"coin_id": coin_id})
        return response.json()

url = f"http://api:8000/candle/{coin_id}/list"
response = httpx.get(url)
candles = response.json()

if not candles:
    st.warning("Aucune candle disponible pour cette crypto. Lance l’ingestion avant de consulter le graphique.")
    st.stop()

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
        prediction = int(resultat)

        if prediction == 1:
            label = "ACHAT"
            background = "#166534"
            border = "#22c55e"
            text_color = "#dcfce7"
        else:
            label = "VENTE"
            background = "#991b1b"
            border = "#ef4444"
            text_color = "#fee2e2"

        st.markdown(
            f"""
            <div style="
                display: inline-block;
                padding: 14px 40px;
                margin-top: 12px;
                border-radius: 10px;
                border: 2px solid {border};
                background-color: {background};
                color: {text_color};
                font-size: 24px;
                font-weight: 700;
                text-align: center;
                min-width: 180px;
            ">
                {label}
            </div>
            """,
            unsafe_allow_html=True,
        )        
    except httpx.TimeoutException:
        st.error(
            "L'API a mis trop de temps à répondre, même avec le nouveau timeout."
        )
    except Exception as e:
        st.error(f"Une erreur est survenue : {e}")