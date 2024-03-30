# Whiteboard Application
Using PySide6 to make a Whiteboard with (potentially) over-the-network capabilities.

## Progress So Far
- Can draw
- Can erase
- Can change size of the pen using the dial
- Can change colour
- Can clear the screen
- Undo & Redo
- Open new whiteboard
- Save and load whiteboards

## TODO
- Be able to draw shapes (ellipse, rectangle and straight line) using the mouse
- Have pages within a single whiteboard
- Give access to users (Google Drive-esque)
<br>
- Have users working on the same whiteboard from different PCs <br>
  In this, have a main server as a UDP server, then connect to main server using QUDPSocket from the clients.
  Have redis store temporary info for sessions i.e. host and clients etc

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
