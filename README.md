# README

## Installatie
1. **Maak een virtual environment aan (optioneel)**  
       python -m venv venv  
       venv\Scripts\activate  

2. **Installeer de vereiste libraries**  
   Zorg dat je in dezelfde map staat als waar `requirements.txt` zich bevindt:  
       pip install -r requirements.txt  

## Uitvoeren
Start het spel door:
    python main.py
(Indien nodig: python3 main.py)

Zodra het spel draait, opent er een Pygame-venster met Blackjack.

## Schakelen tussen AI en handmatig spelen
- Open het bestand **main.py**. Zoek naar de regel waar staat:
      player_is_ai = True
  - **True** betekent: de speler is AI-bestuurd.
  - **False** betekent: je speelt handmatig.

Pas dit aan naar wens en sla het bestand op. Start vervolgens het spel opnieuw.

## AI-strategie aanpassen
- In **constants.py** staat de variabele:
      AI_STRATEGY = STRAT_BASIC_HARD
- Kies één van de volgende strategieën (allemaal gedefinieerd in `constants.py`):
  - STRAT_DEALER_MIMIC
  - STRAT_NEVER_BUST
  - STRAT_BASIC_HARD
  - STRAT_CAUTIOUS
  - STRAT_AGGRESSIVE

Voorbeeld:
      AI_STRATEGY = STRAT_AGGRESSIVE
Daarna het spel opnieuw starten om de aanpassing te gebruiken.

### Korte toelichting strategieën
- **STRAT_DEALER_MIMIC**: AI kopieert de dealer, stopt bij 17.
- **STRAT_NEVER_BUST**: AI is extreem voorzichtig en stopt al bij 12.
- **STRAT_BASIC_HARD**: Eenvoudige basisstrategie voor harde handen.
- **STRAT_CAUTIOUS**: AI houdt rekening met de dealerkaart en kan eerder of later passen.
- **STRAT_AGGRESSIVE**: AI gaat snel door en stopt pas bij 17 of meer.

## Overig
- Als je saldo (Balance) op is, dan stopt het spel en kun je op `Q` drukken om af te sluiten.
- Je kunt de balans, inzet en andere configuraties (bijvoorbeeld `STARTING_BALANCE` of `DEFAULT_BET`) aanpassen in `constants.py`.

**Veel speelplezier!**
