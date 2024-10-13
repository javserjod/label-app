import streamlit.web.bootstrap
import os

# This import path depends on your Streamlit version
if __name__ == '__main__':
    os.chdir(os.path.dirname(__file__))
    
    flag_options = {   #this avoids using config.toml inside .streamlit folder
        "server.port": 8501,
        "global.developmentMode": False,
    }
    
    streamlit.web.bootstrap.load_config_options(flag_options=flag_options)
    flag_options["_is_running_with_streamlit"] = True
    streamlit.web.bootstrap.run(
        "./application/main.py",
        False, #"streamlit run",   AVOID: Bad message format Tried to use SessionInfo before it was initialized
        [],
        flag_options,
    )
    # We will CREATE this function inside our Streamlit framework