# MinecraftRailwayMaker
A project to experiment with procedurally generating a metro system in minecraft (bedrock)


## Getting started

Start the 'Railways.py' script (python3) and you should get an OpenGL GUI

Q, W, E, A, S, D, Z, X = rotate, zoom
P = Output to file
+, -    = Increase/Decrease iterations
G = Regenerate

Once you're happy with the generated output:
Install bedrock server
configure your world and generation parameters.
(If launching on an existing world, use a COPY! Make sur eyou have a backup)

Edit harness.py and ensure bedrock server start commands match your installation.
Copy harness.py and generated_commands.txt to your bedrock server

Run the harness.py. This will start the server and wait for a player to connect.

After about 20 seconds, the harness will run the commands. Player is Teleported to many locations in advance to ensure world
is generated.

Keep the player active by moving around a little. If the player sleeps then errors can be caused.




