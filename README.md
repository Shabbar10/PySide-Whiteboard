# Whiteboard Application
Using PySide6 to make a Whiteboard with over-the-network capabilities.

## Progress So Far
- Can draw
- Can erase
- Can change size of the pen using the dial
- Can change colour
- Can clear the screen
- Undo & Redo
- Open new whiteboard
- Save and load whiteboards
- Be able to draw shapes (ellipse, rectangle and straight line) using the mouse
- Have users working on the same whiteboard from different PCs
  <br>In this, have a main server as a TCP server, then connect to main server using QTcpSocket from the clients.
  <br>Have redis store temporary info for sessions i.e. host and clients etc

## TODO
- Have pages within a single whiteboard
- Give access to users (Google Drive-esque) <br>
- See about multithreading and proper message framing

# Contributions
1. Shabbar Adamjee
  - Main UI
  - Core functions (freehand drawing, erasing)
  - Message framing for network communication

2. Hussain Ceyloni
  - Straight line, ellipse, and rectangle functionality
  - Save/Save As, Load, Open functions
  - Open new board function

3. Atharva Ghanekar
  - Established main server and client communication
  - Message framing for network communication

4. Abubakar Siddiq
  - Undo & redo
  - Login screen and function
  - Database (redis) handling

## To Get Started
Optional: Have a virtual environment: <br> `python -m venv <name of environemt>` <br><br>
### Activate environment: <br>
#### On Windows:
`<name of environment>\Scripts\activate`

#### On Mac/Linux:
`source <name of environment>/bin/activate`

Next, install pyside6
```python
pip install pyside6
```

Run main.py (from PyCharm for now)
