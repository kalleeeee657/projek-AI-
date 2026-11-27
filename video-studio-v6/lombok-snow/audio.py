import math,random,array,wave
sr=44100;r=random.Random(42);buf=array.array('h');low=0
for i in range(sr*12):
 t=i/sr;low=.985*low+.015*r.uniform(-1,1)
 v=.12*low*(.7+.3*math.sin(t*.8))+.018*math.sin(t*math.tau*110)+.013*math.sin(t*math.tau*164.81)
 v*=min(1,t/.4,(12-t)/.6);buf.append(int(max(-1,min(1,v))*32767))
with wave.open('ambience.wav','wb') as w:w.setnchannels(1);w.setsampwidth(2);w.setframerate(sr);w.writeframes(buf.tobytes())
