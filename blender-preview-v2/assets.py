import json,pathlib,urllib.request
root=pathlib.Path(__file__).resolve().parent
folder=root/'assets';folder.mkdir(exist_ok=True)
def fetch(url):
    return urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'MandalikaDinosaurPreview/2.0 (single CC0 HDRI asset)'}),timeout=120)
with fetch('https://api.polyhaven.com/files/kloppenheim_06_puresky') as res:data=json.load(res)
url=data['hdri']['2k']['hdr']['url']
with fetch(url) as res:(folder/'sky.hdr').write_bytes(res.read())
assert (folder/'sky.hdr').stat().st_size>100000
print('Downloaded licensed CC0 HDRI')
