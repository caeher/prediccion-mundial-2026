# Estructura de `data/raw`

Este documento describe la estructura de cada archivo CSV ubicado en `data/raw`, indicando su ruta relativa desde la raiz del proyecto, las columnas disponibles y dos registros de ejemplo.

## `data/raw/fifa-world-cup/WorldCupMatches.csv`

- Ruta relativa: `data/raw/fifa-world-cup/WorldCupMatches.csv`
- Columnas disponibles (20): `Year`, `Datetime`, `Stage`, `Stadium`, `City`, `Home Team Name`, `Home Team Goals`, `Away Team Goals`, `Away Team Name`, `Win conditions`, `Attendance`, `Half-time Home Goals`, `Half-time Away Goals`, `Referee`, `Assistant 1`, `Assistant 2`, `RoundID`, `MatchID`, `Home Team Initials`, `Away Team Initials`
- Ejemplos de datos:

```json
{"Year": "1930", "Datetime": "13 Jul 1930 - 15:00 ", "Stage": "Group 1", "Stadium": "Pocitos", "City": "Montevideo ", "Home Team Name": "France", "Home Team Goals": "4", "Away Team Goals": "1", "Away Team Name": "Mexico", "Win conditions": " ", "Attendance": "4444", "Half-time Home Goals": "3", "Half-time Away Goals": "0", "Referee": "LOMBARDI Domingo (URU)", "Assistant 1": "CRISTOPHE Henry (BEL)", "Assistant 2": "REGO Gilberto (BRA)", "RoundID": "201", "MatchID": "1096", "Home Team Initials": "FRA", "Away Team Initials": "MEX"}
{"Year": "1930", "Datetime": "13 Jul 1930 - 15:00 ", "Stage": "Group 4", "Stadium": "Parque Central", "City": "Montevideo ", "Home Team Name": "USA", "Home Team Goals": "3", "Away Team Goals": "0", "Away Team Name": "Belgium", "Win conditions": " ", "Attendance": "18346", "Half-time Home Goals": "2", "Half-time Away Goals": "0", "Referee": "MACIAS Jose (ARG)", "Assistant 1": "MATEUCCI Francisco (URU)", "Assistant 2": "WARNKEN Alberto (CHI)", "RoundID": "201", "MatchID": "1090", "Home Team Initials": "USA", "Away Team Initials": "BEL"}
```

## `data/raw/fifa-world-cup/WorldCupPlayers.csv`

- Ruta relativa: `data/raw/fifa-world-cup/WorldCupPlayers.csv`
- Columnas disponibles (9): `RoundID`, `MatchID`, `Team Initials`, `Coach Name`, `Line-up`, `Shirt Number`, `Player Name`, `Position`, `Event`
- Ejemplos de datos:

```json
{"RoundID": "201", "MatchID": "1096", "Team Initials": "FRA", "Coach Name": "CAUDRON Raoul (FRA)", "Line-up": "S", "Shirt Number": "0", "Player Name": "Alex THEPOT", "Position": "GK", "Event": ""}
{"RoundID": "201", "MatchID": "1096", "Team Initials": "MEX", "Coach Name": "LUQUE Juan (MEX)", "Line-up": "S", "Shirt Number": "0", "Player Name": "Oscar BONFIGLIO", "Position": "GK", "Event": ""}
```

## `data/raw/fifa-world-cup/WorldCups.csv`

- Ruta relativa: `data/raw/fifa-world-cup/WorldCups.csv`
- Columnas disponibles (10): `Year`, `Country`, `Winner`, `Runners-Up`, `Third`, `Fourth`, `GoalsScored`, `QualifiedTeams`, `MatchesPlayed`, `Attendance`
- Ejemplos de datos:

```json
{"Year": "1930", "Country": "Uruguay", "Winner": "Uruguay", "Runners-Up": "Argentina", "Third": "USA", "Fourth": "Yugoslavia", "GoalsScored": "70", "QualifiedTeams": "13", "MatchesPlayed": "18", "Attendance": "590.549"}
{"Year": "1934", "Country": "Italy", "Winner": "Italy", "Runners-Up": "Czechoslovakia", "Third": "Germany", "Fourth": "Austria", "GoalsScored": "70", "QualifiedTeams": "16", "MatchesPlayed": "17", "Attendance": "363.000"}
```

## `data/raw/international_results.csv`

- Ruta relativa: `data/raw/international_results.csv`
- Columnas disponibles (9): `date`, `home_team`, `away_team`, `home_score`, `away_score`, `tournament`, `city`, `country`, `neutral`
- Ejemplos de datos:

```json
{"date": "1872-11-30", "home_team": "Scotland", "away_team": "England", "home_score": "0.0", "away_score": "0.0", "tournament": "Friendly", "city": "Glasgow", "country": "Scotland", "neutral": "False"}
{"date": "1873-03-08", "home_team": "England", "away_team": "Scotland", "home_score": "4.0", "away_score": "2.0", "tournament": "Friendly", "city": "London", "country": "England", "neutral": "False"}
```

## `data/raw/worldcup_data/award_winners.csv`

- Ruta relativa: `data/raw/worldcup_data/award_winners.csv`
- Columnas disponibles (12): `key_id`, `tournament_id`, `tournament_name`, `award_id`, `award_name`, `shared`, `player_id`, `family_name`, `given_name`, `team_id`, `team_name`, `team_code`
- Ejemplos de datos:

```json
{"key_id": "1", "tournament_id": "WC-1930", "tournament_name": "1930 FIFA Men's World Cup", "award_id": "A-4", "award_name": "Golden Boot", "shared": "0", "player_id": "P-56486", "family_name": "Stábile", "given_name": "Guillermo", "team_id": "T-03", "team_name": "Argentina", "team_code": "ARG"}
{"key_id": "2", "tournament_id": "WC-1930", "tournament_name": "1930 FIFA Men's World Cup", "award_id": "A-5", "award_name": "Silver Boot", "shared": "0", "player_id": "P-18628", "family_name": "Cea", "given_name": "Pedro", "team_id": "T-84", "team_name": "Uruguay", "team_code": "URY"}
```

## `data/raw/worldcup_data/awards.csv`

- Ruta relativa: `data/raw/worldcup_data/awards.csv`
- Columnas disponibles (5): `key_id`, `award_id`, `award_name`, `award_description`, `year_introduced`
- Ejemplos de datos:

```json
{"key_id": "1", "award_id": "A-1", "award_name": "Golden Ball", "award_description": "best player", "year_introduced": "1978"}
{"key_id": "2", "award_id": "A-2", "award_name": "Silver Ball", "award_description": "second best player", "year_introduced": "1978"}
```

## `data/raw/worldcup_data/bookings.csv`

- Ruta relativa: `data/raw/worldcup_data/bookings.csv`
- Columnas disponibles (26): `key_id`, `booking_id`, `tournament_id`, `tournament_name`, `match_id`, `match_name`, `match_date`, `stage_name`, `group_name`, `team_id`, `team_name`, `team_code`, `home_team`, `away_team`, `player_id`, `family_name`, `given_name`, `shirt_number`, `minute_label`, `minute_regulation`, `minute_stoppage`, `match_period`, `yellow_card`, `red_card`, `second_yellow_card`, `sending_off`
- Ejemplos de datos:

```json
{"key_id": "1", "booking_id": "B-0001", "tournament_id": "WC-1970", "tournament_name": "1970 FIFA Men's World Cup", "match_id": "M-1970-01", "match_name": "Mexico vs Soviet Union", "match_date": "1970-05-31", "stage_name": "group stage", "group_name": "Group 1", "team_id": "T-72", "team_name": "Soviet Union", "team_code": "SUN", "home_team": "0", "away_team": "1", "player_id": "P-33189", "family_name": "Asatiani", "given_name": "Kakhi", "shirt_number": "11", "minute_label": "30'", "minute_regulation": "30", "minute_stoppage": "0", "match_period": "first half", "yellow_card": "1", "red_card": "0", "second_yellow_card": "0", "sending_off": "0"}
{"key_id": "2", "booking_id": "B-0002", "tournament_id": "WC-1970", "tournament_name": "1970 FIFA Men's World Cup", "match_id": "M-1970-01", "match_name": "Mexico vs Soviet Union", "match_date": "1970-05-31", "stage_name": "group stage", "group_name": "Group 1", "team_id": "T-72", "team_name": "Soviet Union", "team_code": "SUN", "home_team": "0", "away_team": "1", "player_id": "P-43733", "family_name": "Nodia", "given_name": "Givi", "shirt_number": "19", "minute_label": "31'", "minute_regulation": "31", "minute_stoppage": "0", "match_period": "first half", "yellow_card": "1", "red_card": "0", "second_yellow_card": "0", "sending_off": "0"}
```

## `data/raw/worldcup_data/confederations.csv`

- Ruta relativa: `data/raw/worldcup_data/confederations.csv`
- Columnas disponibles (5): `key_id`, `confederation_id`, `confederation_name`, `confederation_code`, `confederation_wikipedia_link`
- Ejemplos de datos:

```json
{"key_id": "1", "confederation_id": "CF-1", "confederation_name": "Asian Football Confederation", "confederation_code": "AFC", "confederation_wikipedia_link": "https://en.wikipedia.org/wiki/Asian_Football_Confederation"}
{"key_id": "2", "confederation_id": "CF-2", "confederation_name": "Confederation of African Football", "confederation_code": "CAF", "confederation_wikipedia_link": "https://en.wikipedia.org/wiki/Confederation_of_African_Football"}
```

## `data/raw/worldcup_data/goals.csv`

- Ruta relativa: `data/raw/worldcup_data/goals.csv`
- Columnas disponibles (27): `key_id`, `goal_id`, `tournament_id`, `tournament_name`, `match_id`, `match_name`, `match_date`, `stage_name`, `group_name`, `team_id`, `team_name`, `team_code`, `home_team`, `away_team`, `player_id`, `family_name`, `given_name`, `shirt_number`, `player_team_id`, `player_team_name`, `player_team_code`, `minute_label`, `minute_regulation`, `minute_stoppage`, `match_period`, `own_goal`, `penalty`
- Ejemplos de datos:

```json
{"key_id": "1", "goal_id": "G-0001", "tournament_id": "WC-1930", "tournament_name": "1930 FIFA Men's World Cup", "match_id": "M-1930-01", "match_name": "France vs Mexico", "match_date": "1930-07-13", "stage_name": "group stage", "group_name": "Group 1", "team_id": "T-30", "team_name": "France", "team_code": "FRA", "home_team": "1", "away_team": "0", "player_id": "P-05470", "family_name": "Laurent", "given_name": "Lucien", "shirt_number": "0", "player_team_id": "T-30", "player_team_name": "France", "player_team_code": "FRA", "minute_label": "19'", "minute_regulation": "19", "minute_stoppage": "0", "match_period": "first half", "own_goal": "0", "penalty": "0"}
{"key_id": "2", "goal_id": "G-0002", "tournament_id": "WC-1930", "tournament_name": "1930 FIFA Men's World Cup", "match_id": "M-1930-01", "match_name": "France vs Mexico", "match_date": "1930-07-13", "stage_name": "group stage", "group_name": "Group 1", "team_id": "T-30", "team_name": "France", "team_code": "FRA", "home_team": "1", "away_team": "0", "player_id": "P-99087", "family_name": "Langiller", "given_name": "Marcel", "shirt_number": "0", "player_team_id": "T-30", "player_team_name": "France", "player_team_code": "FRA", "minute_label": "40'", "minute_regulation": "40", "minute_stoppage": "0", "match_period": "first half", "own_goal": "0", "penalty": "0"}
```

## `data/raw/worldcup_data/group_standings.csv`

- Ruta relativa: `data/raw/worldcup_data/group_standings.csv`
- Columnas disponibles (19): `key_id`, `tournament_id`, `tournament_name`, `stage_number`, `stage_name`, `group_name`, `position`, `team_id`, `team_name`, `team_code`, `played`, `wins`, `draws`, `losses`, `goals_for`, `goals_against`, `goal_difference`, `points`, `advanced`
- Ejemplos de datos:

```json
{"key_id": "1", "tournament_id": "WC-1930", "tournament_name": "1930 FIFA Men's World Cup", "stage_number": "1", "stage_name": "group stage", "group_name": "Group 1", "position": "1", "team_id": "T-03", "team_name": "Argentina", "team_code": "ARG", "played": "3", "wins": "3", "draws": "0", "losses": "0", "goals_for": "10", "goals_against": "4", "goal_difference": "6", "points": "6", "advanced": "1"}
{"key_id": "2", "tournament_id": "WC-1930", "tournament_name": "1930 FIFA Men's World Cup", "stage_number": "1", "stage_name": "group stage", "group_name": "Group 1", "position": "2", "team_id": "T-13", "team_name": "Chile", "team_code": "CHL", "played": "3", "wins": "2", "draws": "0", "losses": "1", "goals_for": "5", "goals_against": "3", "goal_difference": "2", "points": "4", "advanced": "0"}
```

## `data/raw/worldcup_data/groups.csv`

- Ruta relativa: `data/raw/worldcup_data/groups.csv`
- Columnas disponibles (7): `key_id`, `tournament_id`, `tournament_name`, `stage_number`, `stage_name`, `group_name`, `count_teams`
- Ejemplos de datos:

```json
{"key_id": "1", "tournament_id": "WC-1930", "tournament_name": "1930 FIFA Men's World Cup", "stage_number": "1", "stage_name": "group stage", "group_name": "Group 1", "count_teams": "4"}
{"key_id": "2", "tournament_id": "WC-1930", "tournament_name": "1930 FIFA Men's World Cup", "stage_number": "1", "stage_name": "group stage", "group_name": "Group 2", "count_teams": "3"}
```

## `data/raw/worldcup_data/host_countries.csv`

- Ruta relativa: `data/raw/worldcup_data/host_countries.csv`
- Columnas disponibles (7): `key_id`, `tournament_id`, `tournament_name`, `team_id`, `team_name`, `team_code`, `performance`
- Ejemplos de datos:

```json
{"key_id": "1", "tournament_id": "WC-1930", "tournament_name": "1930 FIFA Men's World Cup", "team_id": "T-84", "team_name": "Uruguay", "team_code": "URY", "performance": "champions"}
{"key_id": "2", "tournament_id": "WC-1934", "tournament_name": "1934 FIFA Men's World Cup", "team_id": "T-41", "team_name": "Italy", "team_code": "ITA", "performance": "champions"}
```

## `data/raw/worldcup_data/manager_appearances.csv`

- Ruta relativa: `data/raw/worldcup_data/manager_appearances.csv`
- Columnas disponibles (17): `key_id`, `tournament_id`, `tournament_name`, `match_id`, `match_name`, `match_date`, `stage_name`, `group_name`, `team_id`, `team_name`, `team_code`, `home_team`, `away_team`, `manager_id`, `family_name`, `given_name`, `country_name`
- Ejemplos de datos:

```json
{"key_id": "1", "tournament_id": "WC-1930", "tournament_name": "1930 FIFA Men's World Cup", "match_id": "M-1930-01", "match_name": "France vs Mexico", "match_date": "1930-07-13", "stage_name": "group stage", "group_name": "Group 1", "team_id": "T-30", "team_name": "France", "team_code": "FRA", "home_team": "1", "away_team": "0", "manager_id": "M-075", "family_name": "Caudron", "given_name": "Raoul", "country_name": "France"}
{"key_id": "2", "tournament_id": "WC-1930", "tournament_name": "1930 FIFA Men's World Cup", "match_id": "M-1930-01", "match_name": "France vs Mexico", "match_date": "1930-07-13", "stage_name": "group stage", "group_name": "Group 1", "team_id": "T-46", "team_name": "Mexico", "team_code": "MEX", "home_team": "0", "away_team": "1", "manager_id": "M-235", "family_name": "Luque de Serrallonga", "given_name": "Juan", "country_name": "Mexico"}
```

## `data/raw/worldcup_data/manager_appointments.csv`

- Ruta relativa: `data/raw/worldcup_data/manager_appointments.csv`
- Columnas disponibles (10): `key_id`, `tournament_id`, `tournament_name`, `team_id`, `team_name`, `team_code`, `manager_id`, `family_name`, `given_name`, `country_name`
- Ejemplos de datos:

```json
{"key_id": "1", "tournament_id": "WC-1930", "tournament_name": "1930 FIFA Men's World Cup", "team_id": "T-56", "team_name": "Peru", "team_code": "PER", "manager_id": "M-061", "family_name": "Bru", "given_name": "Francisco", "country_name": "Spain"}
{"key_id": "2", "tournament_id": "WC-1930", "tournament_name": "1930 FIFA Men's World Cup", "team_id": "T-30", "team_name": "France", "team_code": "FRA", "manager_id": "M-075", "family_name": "Caudron", "given_name": "Raoul", "country_name": "France"}
```

## `data/raw/worldcup_data/managers.csv`

- Ruta relativa: `data/raw/worldcup_data/managers.csv`
- Columnas disponibles (7): `key_id`, `manager_id`, `family_name`, `given_name`, `female`, `country_name`, `manager_wikipedia_link`
- Ejemplos de datos:

```json
{"key_id": "1", "manager_id": "M-001", "family_name": "Acosta", "given_name": "Nelson", "female": "0", "country_name": "Uruguay", "manager_wikipedia_link": "https://en.wikipedia.org/wiki/Nelson_Acosta"}
{"key_id": "2", "manager_id": "M-002", "family_name": "Addo", "given_name": "Otto", "female": "0", "country_name": "Ghana", "manager_wikipedia_link": "https://en.wikipedia.org/wiki/Otto_Addo"}
```

## `data/raw/worldcup_data/matches.csv`

- Ruta relativa: `data/raw/worldcup_data/matches.csv`
- Columnas disponibles (37): `key_id`, `tournament_id`, `tournament_name`, `match_id`, `match_name`, `stage_name`, `group_name`, `group_stage`, `knockout_stage`, `replayed`, `replay`, `match_date`, `match_time`, `stadium_id`, `stadium_name`, `city_name`, `country_name`, `home_team_id`, `home_team_name`, `home_team_code`, `away_team_id`, `away_team_name`, `away_team_code`, `score`, `home_team_score`, `away_team_score`, `home_team_score_margin`, `away_team_score_margin`, `extra_time`, `penalty_shootout`, `score_penalties`, `home_team_score_penalties`, `away_team_score_penalties`, `result`, `home_team_win`, `away_team_win`, `draw`
- Ejemplos de datos:

```json
{"key_id": "1", "tournament_id": "WC-1930", "tournament_name": "1930 FIFA Men's World Cup", "match_id": "M-1930-01", "match_name": "France vs Mexico", "stage_name": "group stage", "group_name": "Group 1", "group_stage": "1", "knockout_stage": "0", "replayed": "0", "replay": "0", "match_date": "1930-07-13", "match_time": "15:00", "stadium_id": "S-240", "stadium_name": "Estadio Pocitos", "city_name": "Montevideo", "country_name": "Uruguay", "home_team_id": "T-30", "home_team_name": "France", "home_team_code": "FRA", "away_team_id": "T-46", "away_team_name": "Mexico", "away_team_code": "MEX", "score": "4–1", "home_team_score": "4", "away_team_score": "1", "home_team_score_margin": "3", "away_team_score_margin": "-3", "extra_time": "0", "penalty_shootout": "0", "score_penalties": "0-0", "home_team_score_penalties": "0", "away_team_score_penalties": "0", "result": "home team win", "home_team_win": "1", "away_team_win": "0", "draw": "0"}
{"key_id": "2", "tournament_id": "WC-1930", "tournament_name": "1930 FIFA Men's World Cup", "match_id": "M-1930-02", "match_name": "United States vs Belgium", "stage_name": "group stage", "group_name": "Group 4", "group_stage": "1", "knockout_stage": "0", "replayed": "0", "replay": "0", "match_date": "1930-07-13", "match_time": "15:00", "stadium_id": "S-239", "stadium_name": "Estadio Gran Parque Central", "city_name": "Montevideo", "country_name": "Uruguay", "home_team_id": "T-83", "home_team_name": "United States", "home_team_code": "USA", "away_team_id": "T-06", "away_team_name": "Belgium", "away_team_code": "BEL", "score": "3–0", "home_team_score": "3", "away_team_score": "0", "home_team_score_margin": "3", "away_team_score_margin": "-3", "extra_time": "0", "penalty_shootout": "0", "score_penalties": "0-0", "home_team_score_penalties": "0", "away_team_score_penalties": "0", "result": "home team win", "home_team_win": "1", "away_team_win": "0", "draw": "0"}
```

## `data/raw/worldcup_data/penalty_kicks.csv`

- Ruta relativa: `data/raw/worldcup_data/penalty_kicks.csv`
- Columnas disponibles (19): `key_id`, `penalty_kick_id`, `tournament_id`, `tournament_name`, `match_id`, `match_name`, `match_date`, `stage_name`, `group_name`, `team_id`, `team_name`, `team_code`, `home_team`, `away_team`, `player_id`, `family_name`, `given_name`, `shirt_number`, `converted`
- Ejemplos de datos:

```json
{"key_id": "1", "penalty_kick_id": "PK-001", "tournament_id": "WC-1982", "tournament_name": "1982 FIFA Men's World Cup", "match_id": "M-1982-50", "match_name": "West Germany vs France", "match_date": "1982-07-08", "stage_name": "semi-finals", "group_name": "not applicable", "team_id": "T-86", "team_name": "West Germany", "team_code": "DEU", "home_team": "1", "away_team": "0", "player_id": "P-68969", "family_name": "Kaltz", "given_name": "Manfred", "shirt_number": "20", "converted": "1"}
{"key_id": "2", "penalty_kick_id": "PK-002", "tournament_id": "WC-1982", "tournament_name": "1982 FIFA Men's World Cup", "match_id": "M-1982-50", "match_name": "West Germany vs France", "match_date": "1982-07-08", "stage_name": "semi-finals", "group_name": "not applicable", "team_id": "T-86", "team_name": "West Germany", "team_code": "DEU", "home_team": "1", "away_team": "0", "player_id": "P-48686", "family_name": "Breitner", "given_name": "Paul", "shirt_number": "3", "converted": "1"}
```

## `data/raw/worldcup_data/player_appearances.csv`

- Ruta relativa: `data/raw/worldcup_data/player_appearances.csv`
- Columnas disponibles (21): `key_id`, `tournament_id`, `tournament_name`, `match_id`, `match_name`, `match_date`, `stage_name`, `group_name`, `team_id`, `team_name`, `team_code`, `home_team`, `away_team`, `player_id`, `family_name`, `given_name`, `shirt_number`, `position_name`, `position_code`, `starter`, `substitute`
- Ejemplos de datos:

```json
{"key_id": "1", "tournament_id": "WC-1970", "tournament_name": "1970 FIFA Men's World Cup", "match_id": "M-1970-01", "match_name": "Mexico vs Soviet Union", "match_date": "1970-05-31", "stage_name": "group stage", "group_name": "Group 1", "team_id": "T-46", "team_name": "Mexico", "team_code": "MEX", "home_team": "1", "away_team": "0", "player_id": "P-66980", "family_name": "Calderón", "given_name": "Ignacio", "shirt_number": "1", "position_name": "goal keeper", "position_code": "GK", "starter": "1", "substitute": "0"}
{"key_id": "2", "tournament_id": "WC-1970", "tournament_name": "1970 FIFA Men's World Cup", "match_id": "M-1970-01", "match_name": "Mexico vs Soviet Union", "match_date": "1970-05-31", "stage_name": "group stage", "group_name": "Group 1", "team_id": "T-46", "team_name": "Mexico", "team_code": "MEX", "home_team": "1", "away_team": "0", "player_id": "P-64553", "family_name": "Peña", "given_name": "Gustavo", "shirt_number": "3", "position_name": "defender", "position_code": "DF", "starter": "1", "substitute": "0"}
```

## `data/raw/worldcup_data/players.csv`

- Ruta relativa: `data/raw/worldcup_data/players.csv`
- Columnas disponibles (13): `key_id`, `player_id`, `family_name`, `given_name`, `birth_date`, `female`, `goal_keeper`, `defender`, `midfielder`, `forward`, `count_tournaments`, `list_tournaments`, `player_wikipedia_link`
- Ejemplos de datos:

```json
{"key_id": "1", "player_id": "P-35894", "family_name": "A'Court", "given_name": "Alan", "birth_date": "1934-09-30", "female": "0", "goal_keeper": "0", "defender": "0", "midfielder": "0", "forward": "1", "count_tournaments": "1", "list_tournaments": "1958", "player_wikipedia_link": "https://en.wikipedia.org/wiki/Alan_A%27Court"}
{"key_id": "2", "player_id": "P-29915", "family_name": "Aarønes", "given_name": "Ann Kristin", "birth_date": "1973-01-19", "female": "1", "goal_keeper": "0", "defender": "0", "midfielder": "1", "forward": "1", "count_tournaments": "2", "list_tournaments": "1995, 1999", "player_wikipedia_link": "https://en.wikipedia.org/wiki/Ann_Kristin_Aar%C3%B8nes"}
```

## `data/raw/worldcup_data/qualified_teams.csv`

- Ruta relativa: `data/raw/worldcup_data/qualified_teams.csv`
- Columnas disponibles (8): `key_id`, `tournament_id`, `tournament_name`, `team_id`, `team_name`, `team_code`, `count_matches`, `performance`
- Ejemplos de datos:

```json
{"key_id": "1", "tournament_id": "WC-1930", "tournament_name": "1930 FIFA Men's World Cup", "team_id": "T-03", "team_name": "Argentina", "team_code": "ARG", "count_matches": "5", "performance": "final"}
{"key_id": "2", "tournament_id": "WC-1930", "tournament_name": "1930 FIFA Men's World Cup", "team_id": "T-06", "team_name": "Belgium", "team_code": "BEL", "count_matches": "2", "performance": "group stage"}
```

## `data/raw/worldcup_data/referee_appearances.csv`

- Ruta relativa: `data/raw/worldcup_data/referee_appearances.csv`
- Columnas disponibles (15): `key_id`, `tournament_id`, `tournament_name`, `match_id`, `match_name`, `match_date`, `stage_name`, `group_name`, `referee_id`, `family_name`, `given_name`, `country_name`, `confederation_id`, `confederation_name`, `confederation_code`
- Ejemplos de datos:

```json
{"key_id": "1", "tournament_id": "WC-1930", "tournament_name": "1930 FIFA Men's World Cup", "match_id": "M-1930-01", "match_name": "France vs Mexico", "match_date": "1930-07-13", "stage_name": "group stage", "group_name": "Group 1", "referee_id": "R-251", "family_name": "Lombardi", "given_name": "Domingo", "country_name": "Uruguay", "confederation_id": "CF-4", "confederation_name": "South American Football Confederation", "confederation_code": "CONMEBOL"}
{"key_id": "2", "tournament_id": "WC-1930", "tournament_name": "1930 FIFA Men's World Cup", "match_id": "M-1930-02", "match_name": "United States vs Belgium", "match_date": "1930-07-13", "stage_name": "group stage", "group_name": "Group 4", "referee_id": "R-260", "family_name": "Macías", "given_name": "José", "country_name": "Argentina", "confederation_id": "CF-4", "confederation_name": "South American Football Confederation", "confederation_code": "CONMEBOL"}
```

## `data/raw/worldcup_data/referee_appointments.csv`

- Ruta relativa: `data/raw/worldcup_data/referee_appointments.csv`
- Columnas disponibles (10): `key_id`, `tournament_id`, `tournament_name`, `referee_id`, `family_name`, `given_name`, `country_name`, `confederation_id`, `confederation_name`, `confederation_code`
- Ejemplos de datos:

```json
{"key_id": "1", "tournament_id": "WC-1930", "tournament_name": "1930 FIFA Men's World Cup", "referee_id": "R-039", "family_name": "Balvay", "given_name": "Thomas", "country_name": "France", "confederation_id": "CF-6", "confederation_name": "Union of European Football Associations", "confederation_code": "UEFA"}
{"key_id": "2", "tournament_id": "WC-1930", "tournament_name": "1930 FIFA Men's World Cup", "referee_id": "R-091", "family_name": "Christophe", "given_name": "Henri", "country_name": "Belgium", "confederation_id": "CF-6", "confederation_name": "Union of European Football Associations", "confederation_code": "UEFA"}
```

## `data/raw/worldcup_data/referees.csv`

- Ruta relativa: `data/raw/worldcup_data/referees.csv`
- Columnas disponibles (10): `key_id`, `referee_id`, `family_name`, `given_name`, `female`, `country_name`, `confederation_id`, `confederation_name`, `confederation_code`, `referee_wikipedia_link`
- Ejemplos de datos:

```json
{"key_id": "1", "referee_id": "R-001", "family_name": "Abdel-Fatah", "given_name": "Essam", "female": "0", "country_name": "Egypt", "confederation_id": "CF-2", "confederation_name": "Confederation of African Football", "confederation_code": "CAF", "referee_wikipedia_link": "https://en.wikipedia.org/wiki/Essam_Abd_El_Fatah"}
{"key_id": "2", "referee_id": "R-002", "family_name": "Abidoye", "given_name": "Bola Elizabeth", "female": "1", "country_name": "Nigeria", "confederation_id": "CF-2", "confederation_name": "Confederation of African Football", "confederation_code": "CAF", "referee_wikipedia_link": "not available"}
```

## `data/raw/worldcup_data/squads.csv`

- Ruta relativa: `data/raw/worldcup_data/squads.csv`
- Columnas disponibles (12): `key_id`, `tournament_id`, `tournament_name`, `team_id`, `team_name`, `team_code`, `player_id`, `family_name`, `given_name`, `shirt_number`, `position_name`, `position_code`
- Ejemplos de datos:

```json
{"key_id": "1", "tournament_id": "WC-1930", "tournament_name": "1930 FIFA Men's World Cup", "team_id": "T-03", "team_name": "Argentina", "team_code": "ARG", "player_id": "P-69244", "family_name": "Bossio", "given_name": "Ángel", "shirt_number": "0", "position_name": "goal keeper", "position_code": "GK"}
{"key_id": "2", "tournament_id": "WC-1930", "tournament_name": "1930 FIFA Men's World Cup", "team_id": "T-03", "team_name": "Argentina", "team_code": "ARG", "player_id": "P-23160", "family_name": "Botasso", "given_name": "Juan", "shirt_number": "0", "position_name": "goal keeper", "position_code": "GK"}
```

## `data/raw/worldcup_data/stadiums.csv`

- Ruta relativa: `data/raw/worldcup_data/stadiums.csv`
- Columnas disponibles (8): `key_id`, `stadium_id`, `stadium_name`, `city_name`, `country_name`, `stadium_capacity`, `stadium_wikipedia_link`, `city_wikipedia_link`
- Ejemplos de datos:

```json
{"key_id": "1", "stadium_id": "S-001", "stadium_name": "Estadio José Amalfitani", "city_name": "Buenos Aires", "country_name": "Argentina", "stadium_capacity": "49000", "stadium_wikipedia_link": "https://en.wikipedia.org/wiki/José_Amalfitani_Stadium", "city_wikipedia_link": "https://en.wikipedia.org/wiki/Buenos_Aires"}
{"key_id": "2", "stadium_id": "S-002", "stadium_name": "Estadio Monumental", "city_name": "Buenos Aires", "country_name": "Argentina", "stadium_capacity": "75000", "stadium_wikipedia_link": "https://en.wikipedia.org/wiki/Estadio_Monumental_Antonio_Vespucio_Liberti", "city_wikipedia_link": "https://en.wikipedia.org/wiki/Buenos_Aires"}
```

## `data/raw/worldcup_data/substitutions.csv`

- Ruta relativa: `data/raw/worldcup_data/substitutions.csv`
- Columnas disponibles (24): `key_id`, `substitution_id`, `tournament_id`, `tournament_name`, `match_id`, `match_name`, `match_date`, `stage_name`, `group_name`, `team_id`, `team_name`, `team_code`, `home_team`, `away_team`, `player_id`, `family_name`, `given_name`, `shirt_number`, `minute_label`, `minute_regulation`, `minute_stoppage`, `match_period`, `going_off`, `coming_on`
- Ejemplos de datos:

```json
{"key_id": "1", "substitution_id": "S-0001", "tournament_id": "WC-1970", "tournament_name": "1970 FIFA Men's World Cup", "match_id": "M-1970-01", "match_name": "Mexico vs Soviet Union", "match_date": "1970-05-31", "stage_name": "group stage", "group_name": "Group 1", "team_id": "T-72", "team_name": "Soviet Union", "team_code": "SUN", "home_team": "0", "away_team": "1", "player_id": "P-60181", "family_name": "Serebryanikov", "given_name": "Viktor", "shirt_number": "15", "minute_label": "46'", "minute_regulation": "46", "minute_stoppage": "0", "match_period": "second half", "going_off": "1", "coming_on": "0"}
{"key_id": "2", "substitution_id": "S-0002", "tournament_id": "WC-1970", "tournament_name": "1970 FIFA Men's World Cup", "match_id": "M-1970-01", "match_name": "Mexico vs Soviet Union", "match_date": "1970-05-31", "stage_name": "group stage", "group_name": "Group 1", "team_id": "T-72", "team_name": "Soviet Union", "team_code": "SUN", "home_team": "0", "away_team": "1", "player_id": "P-59828", "family_name": "Puzach", "given_name": "Anatoliy", "shirt_number": "20", "minute_label": "46'", "minute_regulation": "46", "minute_stoppage": "0", "match_period": "second half", "going_off": "0", "coming_on": "1"}
```

## `data/raw/worldcup_data/team_appearances.csv`

- Ruta relativa: `data/raw/worldcup_data/team_appearances.csv`
- Columnas disponibles (36): `key_id`, `tournament_id`, `tournament_name`, `match_id`, `match_name`, `stage_name`, `group_name`, `group_stage`, `knockout_stage`, `replayed`, `replay`, `match_date`, `match_time`, `stadium_id`, `stadium_name`, `city_name`, `country_name`, `team_id`, `team_name`, `team_code`, `opponent_id`, `opponent_name`, `opponent_code`, `home_team`, `away_team`, `goals_for`, `goals_against`, `goal_differential`, `extra_time`, `penalty_shootout`, `penalties_for`, `penalties_against`, `result`, `win`, `lose`, `draw`
- Ejemplos de datos:

```json
{"key_id": "1", "tournament_id": "WC-1930", "tournament_name": "1930 FIFA Men's World Cup", "match_id": "M-1930-01", "match_name": "France vs Mexico", "stage_name": "group stage", "group_name": "Group 1", "group_stage": "1", "knockout_stage": "0", "replayed": "0", "replay": "0", "match_date": "1930-07-13", "match_time": "15:00", "stadium_id": "S-240", "stadium_name": "Estadio Pocitos", "city_name": "Montevideo", "country_name": "Uruguay", "team_id": "T-30", "team_name": "France", "team_code": "FRA", "opponent_id": "T-46", "opponent_name": "Mexico", "opponent_code": "MEX", "home_team": "1", "away_team": "0", "goals_for": "4", "goals_against": "1", "goal_differential": "3", "extra_time": "0", "penalty_shootout": "0", "penalties_for": "0", "penalties_against": "0", "result": "win", "win": "1", "lose": "0", "draw": "0"}
{"key_id": "2", "tournament_id": "WC-1930", "tournament_name": "1930 FIFA Men's World Cup", "match_id": "M-1930-01", "match_name": "France vs Mexico", "stage_name": "group stage", "group_name": "Group 1", "group_stage": "1", "knockout_stage": "0", "replayed": "0", "replay": "0", "match_date": "1930-07-13", "match_time": "15:00", "stadium_id": "S-240", "stadium_name": "Estadio Pocitos", "city_name": "Montevideo", "country_name": "Uruguay", "team_id": "T-46", "team_name": "Mexico", "team_code": "MEX", "opponent_id": "T-30", "opponent_name": "France", "opponent_code": "FRA", "home_team": "0", "away_team": "1", "goals_for": "1", "goals_against": "4", "goal_differential": "-3", "extra_time": "0", "penalty_shootout": "0", "penalties_for": "0", "penalties_against": "0", "result": "lose", "win": "0", "lose": "1", "draw": "0"}
```

## `data/raw/worldcup_data/teams.csv`

- Ruta relativa: `data/raw/worldcup_data/teams.csv`
- Columnas disponibles (14): `key_id`, `team_id`, `team_name`, `team_code`, `mens_team`, `womens_team`, `federation_name`, `region_name`, `confederation_id`, `confederation_name`, `confederation_code`, `mens_team_wikipedia_link`, `womens_team_wikipedia_link`, `federation_wikipedia_link`
- Ejemplos de datos:

```json
{"key_id": "1", "team_id": "T-01", "team_name": "Algeria", "team_code": "DZA", "mens_team": "1", "womens_team": "0", "federation_name": "Algerian Football Federation", "region_name": "Africa", "confederation_id": "CF-2", "confederation_name": "Confederation of African Football", "confederation_code": "CAF", "mens_team_wikipedia_link": "https://en.wikipedia.org/wiki/Algeria_national_football_team", "womens_team_wikipedia_link": "not applicable", "federation_wikipedia_link": "https://en.wikipedia.org/wiki/Algerian_Football_Federation"}
{"key_id": "2", "team_id": "T-02", "team_name": "Angola", "team_code": "AGO", "mens_team": "1", "womens_team": "0", "federation_name": "Angolan Football Federation", "region_name": "Africa", "confederation_id": "CF-2", "confederation_name": "Confederation of African Football", "confederation_code": "CAF", "mens_team_wikipedia_link": "https://en.wikipedia.org/wiki/Angola_national_football_team", "womens_team_wikipedia_link": "not applicable", "federation_wikipedia_link": "https://en.wikipedia.org/wiki/Angolan_Football_Federation"}
```

## `data/raw/worldcup_data/tournament_stages.csv`

- Ruta relativa: `data/raw/worldcup_data/tournament_stages.csv`
- Columnas disponibles (16): `key_id`, `tournament_id`, `tournament_name`, `stage_number`, `stage_name`, `group_stage`, `knockout_stage`, `unbalanced_groups`, `start_date`, `end_date`, `count_matches`, `count_teams`, `count_scheduled`, `count_replays`, `count_playoffs`, `count_walkovers`
- Ejemplos de datos:

```json
{"key_id": "1", "tournament_id": "WC-1930", "tournament_name": "1930 FIFA Men's World Cup", "stage_number": "1", "stage_name": "group stage", "group_stage": "1", "knockout_stage": "0", "unbalanced_groups": "1", "start_date": "1930-07-13", "end_date": "1930-07-22", "count_matches": "15", "count_teams": "13", "count_scheduled": "15", "count_replays": "0", "count_playoffs": "0", "count_walkovers": "0"}
{"key_id": "2", "tournament_id": "WC-1930", "tournament_name": "1930 FIFA Men's World Cup", "stage_number": "2", "stage_name": "semi-finals", "group_stage": "0", "knockout_stage": "1", "unbalanced_groups": "0", "start_date": "1930-07-26", "end_date": "1930-07-27", "count_matches": "2", "count_teams": "4", "count_scheduled": "2", "count_replays": "0", "count_playoffs": "0", "count_walkovers": "0"}
```

## `data/raw/worldcup_data/tournament_standings.csv`

- Ruta relativa: `data/raw/worldcup_data/tournament_standings.csv`
- Columnas disponibles (7): `key_id`, `tournament_id`, `tournament_name`, `position`, `team_id`, `team_name`, `team_code`
- Ejemplos de datos:

```json
{"key_id": "1", "tournament_id": "WC-1930", "tournament_name": "1930 FIFA Men's World Cup", "position": "1", "team_id": "T-84", "team_name": "Uruguay", "team_code": "URY"}
{"key_id": "2", "tournament_id": "WC-1930", "tournament_name": "1930 FIFA Men's World Cup", "position": "2", "team_id": "T-03", "team_name": "Argentina", "team_code": "ARG"}
```

## `data/raw/worldcup_data/tournaments.csv`

- Ruta relativa: `data/raw/worldcup_data/tournaments.csv`
- Columnas disponibles (18): `key_id`, `tournament_id`, `tournament_name`, `year`, `start_date`, `end_date`, `host_country`, `winner`, `host_won`, `count_teams`, `group_stage`, `second_group_stage`, `final_round`, `round_of_16`, `quarter_finals`, `semi_finals`, `third_place_match`, `final`
- Ejemplos de datos:

```json
{"key_id": "1", "tournament_id": "WC-1930", "tournament_name": "1930 FIFA Men's World Cup", "year": "1930", "start_date": "1930-07-13", "end_date": "1930-07-30", "host_country": "Uruguay", "winner": "Uruguay", "host_won": "1", "count_teams": "13", "group_stage": "1", "second_group_stage": "0", "final_round": "0", "round_of_16": "0", "quarter_finals": "0", "semi_finals": "1", "third_place_match": "0", "final": "1"}
{"key_id": "2", "tournament_id": "WC-1934", "tournament_name": "1934 FIFA Men's World Cup", "year": "1934", "start_date": "1934-05-27", "end_date": "1934-06-10", "host_country": "Italy", "winner": "Italy", "host_won": "1", "count_teams": "16", "group_stage": "0", "second_group_stage": "0", "final_round": "0", "round_of_16": "1", "quarter_finals": "1", "semi_finals": "1", "third_place_match": "1", "final": "1"}
```
