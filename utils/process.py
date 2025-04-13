import subprocess
from subprocess import PIPE
from django.conf import settings


LINUX_USER_PASS = getattr(settings, 'LINUX_USER_PASS')


def process(
    cmd, 
    sudo=False,
    **kwargs
):
    process = subprocess.Popen(
        cmd, 
        stdin=PIPE, 
        stdout=PIPE, 
        stderr=PIPE, 
        **kwargs
    )

    if sudo:
        input_str = LINUX_USER_PASS+'\n'
        universal_newlines = kwargs.get('universal_newlines', False)
        if not universal_newlines:
            input_str = input_str.encode()
        
        try:
            out, err = process.communicate(input=input_str, timeout=20)
            return out, err
        except subprocess.TimeoutExpired:
            process.kill()
            return None, None
    
    out, err = process.communicate()
    return out, err