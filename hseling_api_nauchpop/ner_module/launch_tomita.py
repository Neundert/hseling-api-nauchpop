import subprocess


def launch_tomita(user_text: str) -> int:
    command_2 = 'cd /app/hseling_api_nauchpop/ner_module/tomita-parser/build/bin &&' \
                ' echo "'+user_text+'" | ./tomita-parser config.proto'
    code = subprocess.call(command_2, shell=True)
    return code
