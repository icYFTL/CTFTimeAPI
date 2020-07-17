from source.api.teams import *

app.run(port=config.get("port", 8080), debug=config.get("debug", False))