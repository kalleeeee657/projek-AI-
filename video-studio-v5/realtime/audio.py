import math,wave,random,array,pathlib
p=pathlib.Path('public');p.mkdir(exist_ok=True)
r=random.Random(42);sr=44100;buf=array.array('h');lo=0
for i in range(sr*6):
 t=i/sr;lo=.97*lo+.03*r.uniform(-1,1)
 v=.16*lo*(.7+.3*math.sin(t*2))+.027*math.sin(t*math.tau*110)+.018*math.sin(t*math.tau*164.81)
 for k in [1.3,2.7,4.1,5.5]:
  dt=t-k
  if 0<=dt<.65:v+=.13*math.sin(dt*math.tau*42)*math.exp(-8*dt)
 v*=max(0,min(1,t/.25,(6-t)/.35))
 buf.append(int(max(-1,min(1,v))*32767))
with wave.open(str(p/'ambience.wav'),'wb') as w:
 w.setnchannels(1);w.setsampwidth(2);w.setframerate(sr);w.writeframes(buf.tobytes())
