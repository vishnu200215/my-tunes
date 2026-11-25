"""Procedural sound design for the Abbottabad reel.
Every effect is synthesized here (noise, sines, filters, a convolution reverb)
and placed on the cue times read from cues.js. Writes sfx.wav (48 kHz stereo).
"""
import re, sys, wave
import numpy as np

SR = 48000
cues = {k: float(v) for k, v in re.findall(r'(\w+):\s*([\d.]+)', open('cues.js').read())}
C = lambda k: cues[k]
DUR = C('duration')
N = int(DUR * SR)
rng = np.random.default_rng(7)
out = np.zeros((N, 2))

# ---------- dsp helpers ----------
def t_(d): return np.arange(int(d * SR)) / SR
def noise(d): return rng.standard_normal(int(d * SR))
def band(x, lo, hi, soft=0.15):
    """Smooth FFT band-pass (lo/hi in Hz; None = open)."""
    X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1 / SR); g = np.ones_like(f)
    if lo: g *= 1 / (1 + np.exp(-(np.log(f + 1) - np.log(lo)) / soft))
    if hi: g *= 1 / (1 + np.exp((np.log(f + 1) - np.log(hi)) / soft))
    return np.fft.irfft(X * g, len(x))
def env_ad(n, a, d, curve=4.0):
    t = np.arange(n) / SR
    return np.where(t < a, (t / max(a, 1e-4)) ** 1.5, np.exp(-(t - a) / d * curve / 4))
def fade(x, fi=0.005, fo=0.02):
    n = len(x); a = int(fi * SR); b = int(fo * SR)
    if a: x[:a] *= np.linspace(0, 1, a)
    if b: x[-b:] *= np.linspace(1, 0, b)
    return x
def norm(x, peak=1.0): return x / (np.max(np.abs(x)) + 1e-9) * peak
_ir = None
def reverb(x, wet=0.25, size=1.6):
    global _ir
    if _ir is None:
        L = int(size * SR); t = np.arange(L) / SR
        _ir = band(rng.standard_normal(L), 180, 6500) * np.exp(-t * 3.2)
        _ir[:int(0.012 * SR)] = 0; _ir /= np.sqrt(np.sum(_ir ** 2))
    y = np.fft.irfft(np.fft.rfft(x, len(x) + len(_ir)) * np.fft.rfft(_ir, len(x) + len(_ir)))
    y = y[:len(x) + len(_ir)]
    dry = np.concatenate([x, np.zeros(len(_ir))])
    return dry * (1 - wet) + y * wet * 0.6
def place(sig, at, gain_db=0.0, pan=0.0, lead=0.0):
    """Add mono sig at time `at` (s); `lead` starts it slightly early so the hit lands on the frame."""
    g = 10 ** (gain_db / 20); i = int((at - lead) * SR)
    if i < 0: sig = sig[-i:]; i = 0
    n = min(len(sig), N - i)
    if n <= 0: return
    l, r = np.cos((pan + 1) * np.pi / 4), np.sin((pan + 1) * np.pi / 4)
    out[i:i + n, 0] += sig[:n] * g * l * 1.414; out[i:i + n, 1] += sig[:n] * g * r * 1.414

# ---------- sound recipes ----------
def thump(freq=70, d=0.35):
    t = t_(d); f = freq * (1 + 1.2 * np.exp(-t * 30))
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 11)
def paper_slap(d=0.28, bright=3200):
    n = noise(d); x = band(n, 250, bright) * env_ad(len(n), 0.002, 0.05)
    return norm(x + 0.5 * thump(95, d) * 0.6)
def plastic_clack():
    n = noise(0.18); click = band(n, 1500, 7000) * env_ad(len(n), 0.0008, 0.018)
    body = band(noise(0.18), 300, 1500) * env_ad(int(0.18 * SR), 0.001, 0.04)
    return norm(click + 0.7 * body + 0.6 * thump(130, 0.18))
def disc_clatter():
    t = t_(0.5); ring = sum(np.sin(2 * np.pi * f * t + p) * np.exp(-t * k) for f, p, k in [(2350, 0, 14), (3710, 1, 18), (5120, 2, 24), (1180, .5, 10)])
    hit = band(noise(0.5), 2000, 9000) * env_ad(len(t), 0.0005, 0.012)
    return norm(0.35 * ring + hit + 0.4 * thump(160, 0.5) * np.exp(-t * 20))
def whoosh(d=0.9, lo=300, hi=2600, peak=0.6):
    n = noise(d); t = t_(d); p = t / d
    e = np.exp(-((p - peak) ** 2) / 0.05)
    # moving band: split into chunks with sweeping centre
    x = np.zeros_like(n); seg = 2048
    for s in range(0, len(n), seg // 2):
        c = lo * (hi / lo) ** min(1, s / len(n)); w = np.hanning(min(seg, len(n) - s))
        x[s:s + len(w)] += band(n[s:s + len(w)] * w, c * 0.5, c * 2.2) * 0.5
    return norm(x * e)
def pin_slam():
    t = t_(0.6); tick = band(noise(0.6), 2500, 9000) * env_ad(len(t), 0.0004, 0.006)
    return norm(tick * 1.2 + thump(62, 0.6) + 0.3 * band(noise(0.6), 200, 900) * np.exp(-t * 35))
def marker(d=0.7, density=7.0):
    """Felt-tip on paper: band noise with stroke-rate amplitude wobble."""
    n = noise(d); t = t_(d)
    am = 0.55 + 0.45 * np.abs(np.sin(2 * np.pi * density * t + 3 * np.sin(2 * np.pi * 1.3 * t)))
    x = band(n, 1800, 6500) * am + 0.25 * band(n, 400, 1200) * am
    return fade(norm(x), 0.03, 0.08)
def highlighter(d=0.38): return fade(norm(band(noise(d), 1500, 5000) * np.sin(np.pi * t_(d) / d) ** 0.6), 0.01, 0.05)
def string_run(d):
    t = t_(d); f = 420 + 380 * t / d
    tone = np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.08
    hiss = band(noise(d), 2500, 8000) * (0.35 + 0.25 * np.sin(2 * np.pi * 9 * t))
    return fade(norm(hiss + tone) * np.sin(np.pi * t / d) ** 0.5, 0.05, 0.2)
def boom(d=3.0):
    t = t_(d); f = 48 * (1 + 0.8 * np.exp(-t * 6))
    sub = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 1.6)
    body = band(noise(d), 60, 500) * np.exp(-t * 4)
    return norm(sub + 0.35 * body)
def riser(d):
    t = t_(d); f = 90 * 2 ** (1.2 * t / d)
    tone = sum(np.sin(2 * np.pi * np.cumsum(f * h) / SR) / h for h in (1, 2, 3))
    air = band(noise(d), 800, 6000) * (t / d) ** 2
    return fade(norm(0.6 * tone + 0.6 * air) * (t / d) ** 1.6, 0.2, 0.06)
def ink_bleed(d=0.9):
    t = t_(d); x = band(noise(d), 300, 2500) * np.exp(-((t / d - 0.35) ** 2) / 0.06)
    return fade(norm(x), 0.05, 0.2)

# ---------- ambience bed ----------
t = np.arange(N) / SR
room = band(rng.standard_normal(N), 40, 900) * 0.6 + band(rng.standard_normal(N), 900, 5000) * 0.08
hum = 0.25 * np.sin(2 * np.pi * 50 * t) + 0.12 * np.sin(2 * np.pi * 100 * t)
drone = (np.sin(2 * np.pi * 55 * t) + 0.5 * np.sin(2 * np.pi * 82.4 * t + np.sin(2 * np.pi * 0.11 * t)) + 0.3 * np.sin(2 * np.pi * 110.3 * t)) \
        * (0.55 + 0.45 * np.sin(2 * np.pi * 0.05 * t - 1.2))
swell = np.clip((t - C('l6')) / (C('ended') - C('l6')), 0, 1) ** 2 * np.clip((DUR - t) / 1.2, 0, 1)
bed = norm(room) * 10 ** (-38 / 20) + norm(hum) * 10 ** (-48 / 20) + norm(drone) * 10 ** (-34 / 20) * (1 + 1.5 * swell)
bed *= np.clip(t / 1.0, 0, 1) * np.clip((DUR - t) / 0.8, 0, 1)
out += bed[:, None]

# ---------- cue map (one sound per visual beat) ----------
place(ink_bleed(1.0), C('y2011'), -24, -0.3)                                  # "2011" inks in
lands = [C('videos') - 1.15, C('videos') - 0.85, C('videos') - 0.55, C('videos') - 0.28, C('videos')]
for i, at in enumerate(lands):                                                   # cases, then discs
    s = plastic_clack() if i < 2 else disc_clatter()
    place(reverb(s, 0.18), at, -15 - (0 if i == 4 else 2), -0.25 + 0.12 * i, lead=0.01)
place(whoosh(0.55, 400, 2200, 0.8), C('compound') - 0.5, -24, 0.2)              # print falls
place(reverb(paper_slap()), C('compound'), -14, 0.15, lead=0.01)              # print lands
place(reverb(pin_slam(), 0.3), C('abbottabad'), -11, 0.25, lead=0.01)         # pin slams
place(marker(0.7, 6), C('abbottabad') + 0.05, -25, 0.25)                      # circle on label
place(whoosh(1.5, 250, 3000, 0.55), C('l2') - 0.25, -21, 0.0)                 # travel to document
place(reverb(paper_slap(0.35, 2600), 0.25), C('published'), -12, 0.3, lead=0.01)
place(reverb(thump(55, 0.8), 0.3), C('published'), -15, 0.0, lead=0.01)        # weight of the landing
for k in ('cars', 'chicken', 'antz'):                                             # highlighter sweeps
    place(highlighter(), C(k), -24, 0.1)
place(whoosh(1.6, 300, 1600, 0.5), C('scroll') - 0.05, -23, 0.0)              # scroll down the list
place(riser(1.5), C('title') - 1.5, -29, 0.0)                                  # tension into the title
place(reverb(thump(48, 1.2), 0.35), C('title'), -18, 0.0)                     # soft hit on the title
place(marker(0.9, 7), C('title') + 0.02, -22, 0.1)                            # red circle drawn
place(reverb(pin_slam(), 0.3), C('l6') + 0.15, -14, 0.2, lead=0.01)           # pin into the title
run = C('place') - 0.1 - (C('l6') + 0.45)
place(string_run(run), C('l6') + 0.45, -30, -0.1)                             # string runs out
place(whoosh(run, 200, 1400, 0.45), C('l6') + 0.5, -25, -0.2)                 # camera follows it
place(reverb(boom(3.0), 0.4), C('ended'), -10, 0.0, lead=0.02)                # "ended"
place(reverb(pin_slam(), 0.35), C('ended'), -18, 0.1, lead=0.01)
place(whoosh(1.4, 200, 900, 0.4), C('ended') + 0.35, -28, 0.0)               # final pull back

out = np.tanh(out * 1.2) / 1.2
pcm = (np.clip(out, -1, 1) * 32767).astype('<i2')
with wave.open('sfx.wav', 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
print('wrote sfx.wav', DUR, 's')
