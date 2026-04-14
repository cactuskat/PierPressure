# PierPressure
Multiplayer Battleship-inspired game
Karina Castillo
### Problem Statement:
A multiplayer, turn-based battleship game meant for friends and family to enjoy and bond over any distance with real time relay. This grid game platform that supports 1–N players, configurable board sizes, and persistent state management via a relational database. The system enables structured gameplay sessions that persist.
### Target Users:
Non-technical, casual players looking to enjoy a simple, turn-based game using their desktop
### Current Feature List:
1.	
### Non-Goals (Out of Scope):
•	Social Features or in-game chat
•	AI opponents or predictive gameplay
•	Advanced matchmaking or ranking systems
### Architecture Diagram
### Database <-> Server <-> Client
Client: Browser: Sends JSON requests and receives JSON responses, does not persist between refreshes, lives in UI
Server: Flask: validates requests and responses between client and database, does not persist between refreshes, lives in logic
Database: PostgreSQL: data kept, persist across all refreshes
### AI Tools Used: Claude
### Major Roles
Karina: Works as the designer and architect
Clauda: Works as the code-supplier
