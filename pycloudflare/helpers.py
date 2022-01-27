from .abc import Traffic,Session

session = Session()

def secure_error(error):
    session['CURRENT_ERROR'] = error
    

def TimeConverter(time):
    """Converts any time (1s,2m,3h,4d) to integers

    Args:
        time (TimeString || Str)

    Returns:
        int
    """
    pos = ["s","m","h","d"]
    time_dict = {"s":1,"m":60,"h":3600,"d":3600*24}
    unit = time[-1]
    
    if unit not in pos:
        return -1
    try:
        val = int(time[:-1])
    except:
        return -2

    return val * time_dict[unit]

def catch(traffic:Traffic):
    req = traffic.request

def render(redirect_after=3):
    return f'''
    <head>
    <meta http-equiv="refresh" content="{redirect_after};/">
    </head>
    <link rel="favicon" href="https://img.favpng.com/19/3/24/portable-network-graphics-lens-flare-vector-graphics-clip-art-psd-png-favpng-3zn23z06UdD80QwygW9d4B1k6.jpg">
    <h1>You are being redirected...</h1>
    <h3>DDoS Protection by PyCloudFlare</h3>
    '''

