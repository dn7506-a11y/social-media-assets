# Retention-designed original 8 s loop, 120 BPM, synced to the Friday Reel timeline.
# 0.0 hook hit | 0-2 filtered groove + riser | 2.0/2.5/3.0 rising impacts on each merge
# 3.0 drop (full mix) on the "Themes, not rows" reveal | 4.5 chime on the tagline | 7.2-8 filter-down into loop
import numpy as np, wave, sys
sr=44100; dur=8.0; n=int(sr*dur); t=np.arange(n)/sr
rng=np.random.default_rng(11)
def note(m): return 440.0*2**((m-69)/12)
def env(L,a=0.005,dec=6.0): tt=np.arange(L)/sr; return np.minimum(tt/a,1)*np.exp(-tt*dec)
def place(buf,sig,start,gain=1.0):
    i=int(round((start%dur)*sr)); L=len(sig); j=min(n,i+L); buf[i:j]+=gain*sig[:j-i]
    if i+L>n: buf[:i+L-n]+=gain*sig[n-i:]
def lowpass(x,cut):  # time-varying one-pole low-pass, cut in Hz per sample
    y=np.zeros_like(x); a=1-np.exp(-2*np.pi*cut/sr); s=0.0
    for k in range(len(x)): s+=a[k]*(x[k]-s); y[k]=s
    return y
music=np.zeros(n); drums=np.zeros(n); fx=np.zeros(n)
# harmony: Am | F | C | G, 2 s each (loop returns to Am)
prog=[[57,60,64],[53,57,60],[48,52,55],[55,59,62]]
for c,ch in enumerate(prog):
    L=int(2.1*sr); tt=np.arange(L)/sr; e=np.minimum(tt/0.05,1)*np.minimum((2.1-tt)/0.3,1)
    pad=sum(np.sin(2*np.pi*note(m)*tt)+0.6*np.sin(2*np.pi*note(m)*1.006*tt)+0.3*np.sign(np.sin(2*np.pi*note(m)*tt))*0.4 for m in ch)
    place(music,pad*e,c*2.0,0.035 if c==0 else 0.05)
    for k in range(4):  # bass, quarter notes from the drop on, half notes before
        if c==0 and k%2: continue
        L=int(0.45*sr); tt=np.arange(L)/sr; b=np.sin(2*np.pi*note(ch[0]-12)*tt)+0.3*np.sin(2*np.pi*note(ch[0])*tt)
        place(music,b*env(L,0.004,4.5),c*2.0+k*0.5,0.20 if c>=1 else 0.14)
# hook motif: short plucked figure, plays at 0.0 and again from the drop
motif=[(0,76),(0.25,79),(0.5,81),(0.75,79),(1.0,76),(1.25,72),(1.5,74),(1.75,76)]
def pluck(m,L=0.35):
    LL=int(L*sr); tt=np.arange(LL)/sr; f=note(m)
    return (np.sin(2*np.pi*f*tt)+0.45*np.sin(2*np.pi*2*f*tt)+0.15*np.sin(2*np.pi*3*f*tt))*env(LL,0.002,10)
for bar in (0.0,4.0,6.0):
    for dt,m in motif: place(music,pluck(m),bar+dt,0.11)
for dt,m in motif[:4]: place(music,pluck(m),3.0+dt,0.11)
# drums: kick every beat; snare/clap on 2 and 4 from the drop; hats on 8ths, 16ths after drop
def kick():
    L=int(0.35*sr); tt=np.arange(L)/sr; f=48+110*np.exp(-tt*35); return np.sin(2*np.pi*np.cumsum(f)/sr)*np.exp(-tt*10)
def clap():
    L=int(0.25*sr); tt=np.arange(L)/sr; x=rng.standard_normal(L); return np.diff(x,prepend=0)*np.exp(-tt*22)
def hat(L=0.04):
    LL=int(L*sr); tt=np.arange(LL)/sr; x=np.diff(rng.standard_normal(LL),prepend=0); return x*np.exp(-tt*110)
for b in range(16):
    place(drums,kick(),b*0.5,0.42 if b>=6 else 0.26)
    if b>=6 and b%2==1 and b<15: place(drums,clap(),b*0.5,0.16)
    place(drums,hat(),b*0.5+0.25,0.035 if b<6 else 0.05)
    if b>=6 and b<14:
        place(drums,hat(),b*0.5+0.125,0.025); place(drums,hat(),b*0.5+0.375,0.025)
# fx: hook hit at 0, noise riser 1.0-3.0, three rising impacts on merges, drop boom, chime, reverse swell into loop
def impact(m):
    L=int(0.6*sr); tt=np.arange(L)/sr; f=note(m)
    return (np.sin(2*np.pi*f*tt)+0.5*np.sin(2*np.pi*f*1.5*tt)+0.3*np.sin(2*np.pi*2*f*tt))*env(L,0.002,5)
L=int(0.8*sr); tt=np.arange(L)/sr; place(fx,np.sin(2*np.pi*np.cumsum(40+90*np.exp(-tt*12))/sr)*np.exp(-tt*4),0.0,0.35)   # opening hit
for i,m in enumerate([69,72,76]): place(fx,impact(m),2.0+i*0.5,0.16)
L=int(2.0*sr); tt=np.arange(L)/sr; r=rng.standard_normal(L)*(tt/2.0)**2
r=lowpass(r,300+6000*(tt/2.0)**2); place(fx,r,1.0,0.32)                                                                 # riser
L=int(1.2*sr); tt=np.arange(L)/sr; place(fx,np.sin(2*np.pi*np.cumsum(35+70*np.exp(-tt*8))/sr)*np.exp(-tt*3),3.0,0.6)    # drop boom
for m,dt in ((88,0),(93,0.08)): place(fx,pluck(m,0.9),4.5+dt,0.10)                                                     # tagline chime
# filter automation on the music bus: closed before the drop, open after, close at the loop point
cut=np.where(t<3.0,500+2500*(t/3.0)**2,9000.0); cut=np.where(t>7.3,9000-8000*np.clip((t-7.3)/0.7,0,1),cut)
mix=lowpass(music,cut)+drums*np.where(t<3.0,0.8,1.0)+fx
mix[:int(0.004*sr)]*=np.linspace(0,1,int(0.004*sr))
mix=np.tanh(mix*1.6); mix=mix/np.max(np.abs(mix))*0.72
pcm=(np.stack([mix,mix],1)*32767).astype('<i2')
w=wave.open(sys.argv[1],'wb'); w.setnchannels(2); w.setsampwidth(2); w.setframerate(sr); w.writeframes(pcm.tobytes()); w.close()
# loudness per 0.25 s window, to check the shape without listening
win=int(0.25*sr); rms=[20*np.log10(np.sqrt(np.mean(mix[i:i+win]**2))+1e-9) for i in range(0,n,win)]
np.save(sys.argv[1]+".rms.npy",np.array(rms)); print("peak",round(float(np.max(np.abs(mix))),2))
import numpy as _n
def sec(a,b): 
    x=mix[int(a*sr):int(b*sr)]; return 20*_n.log10(_n.sqrt(_n.mean(x**2)))
print("intro 0-2s %.1f dB | build 2-3s %.1f | drop 3-3.5s %.1f | groove 3.5-7.2s %.1f | outro 7.2-8s %.1f"%(sec(0,2),sec(2,3),sec(3,3.5),sec(3.5,7.2),sec(7.2,8)))
