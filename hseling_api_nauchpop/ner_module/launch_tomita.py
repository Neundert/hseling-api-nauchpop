import subprocess

def launch_tomita(user_text: str) -> None:
    command = 'echo "'+user_text+'" | \
    /hseling_api_nauchpop/tomita-parser/build/bin/tomita-parser /hseling_api_nauchpop/tomita-parser/build/bin/config.proto'

    subprocess.call(command, shell=True) 
