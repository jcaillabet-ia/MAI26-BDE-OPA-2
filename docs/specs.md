# Intro

Nous prévoyons la mise en place d'un CryptoBot permettant d'effectuer des opérations de trading de façon automatiques :
- Une interface permettra de choisir quelles cryptomonnaies on souhaite gérer
- Un workflow permettra de récuperer automatiquement l'hystorique des prix des cryptomonnaies choisies, à la fois du passé, et en tant réel grace aux websockets.
- Un appel API permettra de dire si il est préférable d'acheter ou vender à un moment donné

# 1: Recolte des données

Deux APIs seront utilisées :
- CoingGecko pour récupérer la liste des cryptos existantes, ainsi que le ticket à appeler pour chacune
- ccxt sera utilisée pour récupérer l'évolution des cryptos monnaies (à la fois les prix passés et le flux temps réel)

# 2: Stackage de la donnée

Deux base de données seront utilisées :
- PostgreSQL pour le paramétrage
- Cassandra pour les prix des crypto-monnaies

# 3: Consommation de la donnée

Les modèles de prédiction seront entrainés à partir d'un minimum de 50000 points.

# 4: Mise en production

# 5: Automatisation des flux et Monitoring
