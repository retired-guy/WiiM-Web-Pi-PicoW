import urequests as requests

def getWiimData(WiimIp):
    url = f"http://{WiimIp}:49152/upnp/control/rendertransport1"

    data = """
    <?xml version="1.0" encoding="utf-8"?>
    <s:Envelope s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/" xmlns:s="http://schemas.xmlsoap.org/soap/envelope/">
        <s:Body>
            <u:GetMediaInfo xmlns:u="urn:schemas-upnp-org:service:AVTransport:1">
                <InstanceID>0</InstanceID>
            </u:GetMediaInfo>
        </s:Body>
    </s:Envelope>
    """

    headers = {'Content-Type' : 'text/xml; charset=utf-8',
              'SOAPAction' : '"urn:schemas-upnp-org:service:AVTransport:1#GetMediaInfo"'}

    resp = requests.post(url, headers=headers, data=data)

    meta = resp.content.decode("UTF-8").split("CurrentURIMetaData>")[1][0:-2]

    meta = meta.replace("&gt;",">")
    meta = meta.replace("&lt;","<")
    meta = meta.replace("&quot;","\'")
    meta = meta.replace("&amp;","&")
    meta = meta.replace("&apos;","\'")

    meta = meta.split("<item id=")[1][9:]
    meta = meta.split("</item>")[0]
    items = meta.split("\n")

    dict = {}
    for item in items:
        try:
          name = item.split(">")[0].replace("<","")
          value = item.split(">")[1].split("</")[0]
          dict[name] = value
        except:
            continue

    return dict

