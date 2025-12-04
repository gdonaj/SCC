from website import create_app
from configparser import ConfigParser
import sys

app = create_app()

if __name__ == '__main__':

    configFile=sys.argv[1]
    cfgParse = ConfigParser()
    cfgParse.read(configFile)
    
    port = cfgParse.getint("main","port")
    ssl  = cfgParse.getboolean("main","ssl")
    
    if (ssl):
        cert = cfgParse.get("main","cert")
        key  = cfgParse.get("main","key")
        app.run(debug=True, port=port, ssl_context=(cert, key), host="0.0.0.0")
    else:
        app.run(debug=True, port=port, host="0.0.0.0")
