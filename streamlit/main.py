import httpx
import streamlit as st

url = "http://api:8000/coin/"
response = httpx.get(url)
coins = response.json()

def toggle_coin():
    clic = st.session_state.btn_toggle
    if clic:
        index_ligne = clic["row"]
        coin = coins[index_ligne]    
        if coin['enabled']:
            httpx.patch(url + coin['id'] + '/disable')
        else:
            httpx.patch(url + coin['id'] + '/enable')


st.title("Crypto-bot dashboard")
table_data = []
for coin in coins:
    table_data.append({
        'id': coin['id'],
        'symbol': coin['symbol'],
        "Action": "Désactiver" if coin['enabled'] else "Activer",
        "Score": coin['score']
    })

st.dataframe(table_data, 
    column_config={
    "Action": st.column_config.ButtonColumn(
        "Action",
        type="primary",
        on_click=toggle_coin,
        key="btn_toggle" ,
        )
    }, 
    hide_index=True, 
    use_container_width=True
)