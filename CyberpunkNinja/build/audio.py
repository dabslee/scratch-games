"""
Procedural music and sound effects for Cyberpunk Ninja.

Everything is synthesized with numpy: synthwave pads, bass and arps,
Karplus-Strong shamisen, taiko drums and a pile of combat foley.
Music is encoded to MP3 with ffmpeg; effects stay as 16-bit WAV.
"""
import io
import os
import subprocess
import tempfile
import wave

import numpy as np
from scipy import signal

SR = 22050
RNG = np.random.default_rng(7)


# ====================================================================== core
def T(dur):
    return np.arange(int(dur * SR)) / SR


def silence(dur):
    return np.zeros(int(dur * SR))


def mtof(m):
    return 440.0 * 2 ** ((m - 69) / 12.0)


NOTE = {'C': 0, 'C#': 1, 'Db': 1, 'D': 2, 'D#': 3, 'Eb': 3, 'E': 4, 'F': 5, 'F#': 6, 'Gb': 6,
        'G': 7, 'G#': 8, 'Ab': 8, 'A': 9, 'A#': 10, 'Bb': 10, 'B': 11}


def n2m(name):
    """'A4' -> 69"""
    p, o = (name[:-1], int(name[-1]))
    return 12 * (o + 1) + NOTE[p]


def phase_of(freq, n):
    f = np.broadcast_to(np.asarray(freq, dtype=float), (n,))
    return 2 * np.pi * np.cumsum(f) / SR


def sine(freq, dur):
    n = int(dur * SR)
    return np.sin(phase_of(freq, n))


def saw(freq, dur):
    n = int(dur * SR)
    ph = phase_of(freq, n) / (2 * np.pi)
    return 2 * (ph - np.floor(ph + 0.5))


def square(freq, dur, duty=0.5):
    n = int(dur * SR)
    ph = phase_of(freq, n) / (2 * np.pi)
    return np.where((ph % 1.0) < duty, 1.0, -1.0)


def tri(freq, dur):
    return 2 * np.abs(saw(freq, dur)) - 1


def noise(dur):
    return RNG.uniform(-1, 1, int(dur * SR))


def expenv(dur, decay, attack=0.002):
    t = T(dur)
    e = np.exp(-t / max(decay, 1e-4))
    if attack > 0:
        a = np.minimum(1, t / attack)
        e = e * a
    return e


def adsr(dur, a=0.01, d=0.1, s=0.7, r=0.2):
    n = int(dur * SR)
    t = np.arange(n) / SR
    e = np.ones(n) * s
    e[t < a] = t[t < a] / max(a, 1e-4)
    m = (t >= a) & (t < a + d)
    e[m] = 1 - (1 - s) * (t[m] - a) / max(d, 1e-4)
    rel = t > dur - r
    e[rel] *= np.maximum(0, (dur - t[rel]) / max(r, 1e-4))
    return e


def _filt(x, kind, fc, order=2, q=None):
    fc = np.clip(fc, 20, SR / 2 - 100)
    if kind == 'bp':
        lo, hi = fc
        b, a = signal.butter(order, [lo / (SR / 2), hi / (SR / 2)], 'band')
    else:
        b, a = signal.butter(order, fc / (SR / 2), kind)
    return signal.lfilter(b, a, x)


def lp(x, fc, order=2):
    return _filt(x, 'low', fc, order)


def hp(x, fc, order=2):
    return _filt(x, 'high', fc, order)


def bp(x, lo, hi, order=2):
    return _filt(x, 'bp', (lo, hi), order)


def sweep_lp(x, f0, f1, steps=24):
    """Time-varying low-pass by crossfading filtered segments (cheap filter envelope)."""
    out = np.zeros_like(x)
    n = len(x)
    edges = np.linspace(0, n, steps + 1).astype(int)
    zi = None
    for i in range(steps):
        fc = f0 * (f1 / f0) ** (i / max(1, steps - 1))
        b, a = signal.butter(2, np.clip(fc, 30, SR / 2 - 200) / (SR / 2), 'low')
        if zi is None:
            zi = signal.lfilter_zi(b, a) * 0
        seg, zi = signal.lfilter(b, a, x[edges[i]:edges[i + 1]], zi=zi)
        out[edges[i]:edges[i + 1]] = seg
    return out


def dist(x, k=3.0):
    return np.tanh(k * x) / np.tanh(k)


def reverb(x, decay=1.2, mix=0.25, bright=4000):
    n = int(decay * SR)
    ir = RNG.normal(0, 1, n) * np.exp(-np.arange(n) / SR / (decay / 5))
    ir = lp(ir, bright)
    ir[:int(0.012 * SR)] *= np.linspace(0, 1, int(0.012 * SR))
    ir /= np.sqrt(np.sum(ir ** 2)) + 1e-9
    wet = signal.fftconvolve(x, ir)[:len(x) + n]
    out = np.zeros(len(x) + n)
    out[:len(x)] += x * (1 - mix)
    out[:len(wet)] += wet * mix * 1.6
    return out


def delay(x, secs, fb=0.35, mix=0.3, n_taps=5):
    d = int(secs * SR)
    out = np.zeros(len(x) + d * n_taps)
    out[:len(x)] += x
    g = mix
    for k in range(1, n_taps + 1):
        out[k * d:k * d + len(x)] += x * g
        g *= fb
    return out


def mix_into(buf, x, at, gain=1.0):
    i = int(at * SR)
    if i >= len(buf):
        return
    j = min(len(buf), i + len(x))
    buf[i:j] += x[:j - i] * gain


def normalize(x, peak=0.9):
    m = np.max(np.abs(x)) + 1e-9
    return x * (peak / m)


def fade(x, fin=0.002, fout=0.01):
    x = x.copy()
    a = int(fin * SR)
    b = int(fout * SR)
    if a > 0:
        x[:a] *= np.linspace(0, 1, a)
    if b > 0:
        x[-b:] *= np.linspace(1, 0, b)
    return x


def loopify(x, length):
    """Fold a rendered tail past `length` seconds back onto the start (seamless loop)."""
    n = int(length * SR)
    out = x[:n].copy()
    tail = x[n:]
    k = min(len(tail), n)
    out[:k] += tail[:k]
    return out


# ====================================================================== instruments
def kick(gain=1.0):
    d = 0.42
    f = 48 + 110 * np.exp(-T(d) / 0.035)
    x = sine(f, d) * expenv(d, 0.16, 0.001)
    click = lp(noise(0.01), 3000) * np.linspace(1, 0, int(0.01 * SR))
    x[:len(click)] += click * 0.5
    return dist(x * 1.2, 1.5) * gain


def snare(gain=1.0, gated=True):
    d = 0.32
    body = sine(185 * (1 + 0.3 * np.exp(-T(d) / 0.02)), d) * expenv(d, 0.06)
    nz = bp(noise(d), 1200, 7000) * expenv(d, 0.11 if not gated else 0.2)
    x = body * 0.6 + nz * 0.9
    if gated:
        x = reverb(x, 0.5, 0.45, 6000)[:int(d * SR)]
        g = np.ones(len(x))
        cut = int(0.18 * SR)
        g[cut:] = np.linspace(1, 0, len(x) - cut) ** 2
        x = x * g
    return x * gain


def clap(gain=1.0):
    d = 0.3
    x = np.zeros(int(d * SR))
    for k, off in enumerate([0, 0.011, 0.022, 0.034]):
        b = bp(noise(0.12), 900, 5000) * expenv(0.12, 0.03 if k < 3 else 0.09)
        mix_into(x, b, off)
    return x * gain


def hat(open_=False, gain=1.0):
    d = 0.22 if open_ else 0.06
    x = hp(noise(d), 7000, 3) * expenv(d, 0.09 if open_ else 0.018)
    return x * gain


def taiko(gain=1.0, pitch=1.0):
    d = 1.1
    f = (52 + 70 * np.exp(-T(d) / 0.05)) * pitch
    body = sine(f, d) * expenv(d, 0.32, 0.002)
    skin = lp(noise(d), 380) * expenv(d, 0.08)
    x = body + skin * 0.9
    x = dist(x * 1.3, 1.3)
    x = reverb(x, 1.4, 0.22, 2500)[:int(1.4 * SR)]
    return x * gain


def ka(gain=1.0):
    d = 0.08
    x = bp(noise(d), 1500, 4500) * expenv(d, 0.012) + sine(1150, d) * expenv(d, 0.01) * 0.4
    return x * gain


def ks_pluck(freq, dur, decay=0.996, bright=0.6):
    """Karplus-Strong string, vectorised block by block."""
    n = int(dur * SR)
    N = max(2, int(round(SR / freq)))
    exc = RNG.uniform(-1, 1, N)
    exc = bright * exc + (1 - bright) * np.convolve(exc, [0.5, 0.5], 'same')
    y = np.zeros(n + N + 1)
    y[:N] = exc
    pos = N
    while pos < n + N:
        end = min(pos + N, n + N)
        seg = np.arange(pos, end)
        y[seg] = decay * 0.5 * (y[seg - N] + y[seg - N - 1])
        pos = end
    return y[N:N + n]


def shamisen(m, dur, gain=1.0):
    f = mtof(m)
    x = ks_pluck(f, dur + 0.05, decay=0.9935, bright=0.85)
    # sawari: a buzzy, slightly bent attack
    buzz = dist(x * 2.2, 2.0) * np.exp(-T(dur + 0.05) / 0.12)
    x = x * 0.75 + buzz * 0.35
    x = hp(x, 160)
    pick = hp(noise(0.012), 2500) * np.linspace(1, 0, int(0.012 * SR))
    x[:len(pick)] += pick * 0.5
    x = x[:int(dur * SR)]
    return fade(x, 0.001, 0.03) * gain


def koto(m, dur, gain=1.0):
    f = mtof(m)
    x = ks_pluck(f, dur, decay=0.998, bright=0.5)
    return fade(lp(x, 4000), 0.001, 0.05) * gain


def supersaw(m, dur, voices=5, detune=0.012):
    f = mtof(m)
    x = np.zeros(int(dur * SR))
    for v in range(voices):
        dv = (v - (voices - 1) / 2) * detune / max(1, voices - 1) * 2
        ph = RNG.uniform(0, 1)
        s = saw(f * (1 + dv), dur + 1 / f)
        k = int(ph * SR / f)
        x += s[k:k + len(x)]
    return x / voices


def pad(ms, dur, cutoff=1400, gain=1.0, a=0.35, r=0.6):
    x = np.zeros(int(dur * SR))
    for m in ms:
        x += supersaw(m, dur, 4, 0.01)
    x = lp(x / len(ms), cutoff, 2)
    return x * adsr(dur, a, 0.3, 0.8, r) * gain


def bass(m, dur, gain=1.0, cutoff=900, pluck=True):
    f = mtof(m)
    x = saw(f, dur) * 0.7 + square(f / 2, dur) * 0.35
    if pluck:
        x = sweep_lp(x, cutoff * 2.5, cutoff * 0.5, 8)
    else:
        x = lp(x, cutoff)
    return fade(x * adsr(dur, 0.004, 0.08, 0.7, 0.03), 0.002, 0.01) * gain


def arp_note(m, dur, gain=1.0):
    f = mtof(m)
    x = square(f, dur, 0.3) * 0.6 + saw(f * 1.005, dur) * 0.4
    x = lp(x, 2600) * expenv(dur, dur * 0.35)
    return fade(x, 0.002, 0.01) * gain


def lead(m, dur, gain=1.0, vib=True):
    f = mtof(m)
    t = T(dur)
    fv = f * (1 + (0.006 * np.sin(2 * np.pi * 5.5 * t) * np.minimum(1, t / 0.25) if vib else 0))
    x = saw(fv, dur) * 0.5 + square(fv * 1.003, dur, 0.45) * 0.5
    x = lp(x, 3200)
    return fade(x * adsr(dur, 0.01, 0.1, 0.75, 0.08), 0.002, 0.02) * gain


# ====================================================================== sequencing
class Song:
    def __init__(self, bpm, bars, beats=4):
        self.bpm = bpm
        self.beat = 60.0 / bpm
        self.bars = bars
        self.length = bars * beats * self.beat
        self.buf = np.zeros(int((self.length + 3) * SR))

    def at(self, bar, beat=0.0):
        return (bar * 4 + beat) * self.beat

    def add(self, x, bar, beat=0.0, gain=1.0):
        mix_into(self.buf, x, self.at(bar, beat), gain)

    def render(self, tail_reverb=None):
        x = self.buf
        if tail_reverb:
            x = reverb(x, *tail_reverb)
        x = loopify(x, self.length)
        return x


def chord(root_name, kind='m', octave_shift=0):
    r = n2m(root_name) + 12 * octave_shift
    shapes = {'m': [0, 3, 7], 'M': [0, 4, 7], 'm7': [0, 3, 7, 10], 'M7': [0, 4, 7, 11],
              'sus4': [0, 5, 7], 'add9': [0, 3, 7, 14], '7': [0, 4, 7, 10], 'm9': [0, 3, 7, 10, 14]}
    return [r + i for i in shapes[kind]]


# ---------------------------------------------------------------------- title
def song_title():
    s = Song(88, 8)
    prog = [('A3', 'add9'), ('F3', 'M7'), ('D3', 'm7'), ('E3', 'sus4'),
            ('A3', 'add9'), ('F3', 'M7'), ('G3', 'M'), ('E3', '7')]
    bl = s.beat * 4
    for i, (r, k) in enumerate(prog):
        s.add(pad(chord(r, k), bl + 0.6, 1600, 0.55, 0.5, 0.6), i)
        s.add(bass(n2m(r) - 12, bl * 0.95, 0.5, 500, pluck=False), i)
        notes = chord(r, k, 1)
        for j in range(8):
            s.add(arp_note(notes[j % len(notes)] + (12 if j % 4 == 3 else 0), s.beat * 0.45, 0.10), i, j * 0.5)
        s.add(taiko(0.35), i, 0)
        if i % 2 == 1:
            s.add(taiko(0.22, 1.15), i, 3)
    mel = [('A4', 0, 1.5), ('C5', 1.5, 0.5), ('B4', 2, 1), ('A4', 3, 1),
           ('E5', 4, 1.5), ('F5', 5.5, 0.5), ('E5', 6, 1), ('C5', 7, 1),
           ('D5', 8, 1.5), ('C5', 9.5, 0.5), ('A4', 10, 2),
           ('B4', 12, 1), ('E5', 13, 1), ('E4', 14, 2),
           ('A4', 16, 1.5), ('C5', 17.5, 0.5), ('E5', 18, 1), ('F5', 19, 1),
           ('E5', 20, 1.5), ('C5', 21.5, 0.5), ('A4', 22, 2),
           ('B4', 24, 1), ('C5', 25, 1), ('D5', 26, 2),
           ('B4', 28, 1), ('G#4', 29, 1), ('E4', 30, 2)]
    for nm, b, d in mel:
        s.add(shamisen(n2m(nm), d * s.beat + 0.5, 0.42), 0, b)
    return s.render((1.8, 0.28, 3500)), s.length


# ---------------------------------------------------------------------- sump
def song_sump():
    s = Song(84, 8)
    prog = [('A2', 'm'), ('A2', 'm'), ('F2', 'M7'), ('E2', 'sus4'),
            ('A2', 'm'), ('C3', 'M'), ('F2', 'M7'), ('E2', '7')]
    bl = s.beat * 4
    for i, (r, k) in enumerate(prog):
        s.add(pad([m + 12 for m in chord(r, k)], bl + 0.8, 900, 0.5, 0.8, 0.8), i)
        for j in range(8):
            s.add(bass(n2m(r) - 12 + (12 if j % 4 == 2 else 0), s.beat * 0.45, 0.42, 420), i, j * 0.5)
        for j in range(4):
            s.add(hat(False, 0.12 if j % 2 else 0.2), i, j + 0.5)
        if i % 2 == 0:
            s.add(taiko(0.5), i, 0)
        else:
            s.add(taiko(0.3, 1.2), i, 2.5)
            s.add(ka(0.18), i, 3.5)
    motif = [('A3', 0), ('C4', 0.75), ('E4', 1.5), ('B3', 2.5), ('A3', 3)]
    for bar in (0, 2, 4, 6):
        for nm, b in motif:
            m = n2m(nm) + (0 if bar < 4 else 0)
            s.add(shamisen(m + (5 if bar == 2 else 0) - (1 if bar == 6 and nm == 'C4' else 0), 0.9, 0.34), bar + 1, b)
    s.add(shamisen(n2m('E5'), 1.6, 0.25), 3, 2)
    s.add(shamisen(n2m('F5'), 1.6, 0.25), 7, 2)
    return s.render((2.2, 0.3, 2500)), s.length


# ---------------------------------------------------------------------- alley
def song_alley():
    s = Song(116, 16)
    prog = [('A2', 'm'), ('F2', 'M'), ('C3', 'M'), ('G2', 'M'),
            ('A2', 'm'), ('F2', 'M'), ('G2', 'M'), ('E2', 'M')]
    bl = s.beat * 4
    k, sn, h, ho = kick(0.95), snare(0.55), hat(False, 0.22), hat(True, 0.16)
    for i in range(16):
        r, kd = prog[i % 8]
        root = n2m(r)
        s.add(pad([m + 12 for m in chord(r, kd)], bl + 0.4, 1500, 0.32, 0.25, 0.5), i)
        for j in range(8):
            oct_ = 12 if j % 2 else 0
            s.add(bass(root + oct_, s.beat * 0.42, 0.55, 800), i, j * 0.5)
        for j in range(4):
            if j % 2 == 0:
                s.add(k, i, j)
            else:
                s.add(sn, i, j)
            s.add(h, i, j + 0.5)
        s.add(k, i, 2.5, 0.6)
        if i % 4 == 3:
            s.add(ho, i, 3.5)
        notes = chord(r, kd, 2)
        for j in range(16):
            s.add(arp_note(notes[(j * 2) % len(notes)] + (12 if j % 8 == 7 else 0), s.beat * 0.22, 0.07), i, j * 0.25)
        if i % 4 == 0:
            s.add(taiko(0.35), i, 0)
    riff = [('A4', 0, 0.5), ('C5', 0.5, 0.5), ('E5', 1, 1), ('D5', 2, 0.5), ('C5', 2.5, 0.5), ('B4', 3, 1),
            ('A4', 4, 0.5), ('C5', 4.5, 0.5), ('F5', 5, 1), ('E5', 6, 1), ('C5', 7, 1),
            ('E5', 8, 0.5), ('G5', 8.5, 0.5), ('E5', 9, 1), ('D5', 10, 0.5), ('C5', 10.5, 0.5), ('D5', 11, 1),
            ('E5', 12, 1.5), ('D5', 13.5, 0.5), ('C5', 14, 0.5), ('B4', 14.5, 0.5), ('G#4', 15, 1)]
    for rep in (0, 1):
        for nm, b, d in riff:
            s.add(shamisen(n2m(nm), d * s.beat + 0.3, 0.36), 8 + rep * 4, b)
    lead_line = [('A5', 0, 2), ('G5', 2, 1), ('E5', 3, 1), ('F5', 4, 3), ('E5', 7, 1),
                 ('D5', 8, 2), ('E5', 10, 1), ('G5', 11, 1), ('E5', 12, 4)]
    for nm, b, d in lead_line:
        s.add(lead(n2m(nm), d * s.beat * 0.95, 0.13), 12, b)
    return s.render((1.2, 0.18, 4000)), s.length


# ---------------------------------------------------------------------- boss
def song_boss(drums=False):
    s = Song(140, 8)
    prog = [('A2', 'm'), ('A#2', 'M'), ('F2', 'M'), ('E2', 'M'),
            ('A2', 'm'), ('A#2', 'M'), ('G2', 'M'), ('E2', '7')]
    if drums:
        for i in range(8):
            for j in range(8):
                acc = j in (0, 3, 6)
                s.add(taiko(0.75 if acc else 0.4, 1.0 if acc else 1.25), i, j * 0.5)
            s.add(ka(0.35), i, 1.75)
            s.add(ka(0.35), i, 3.75)
            if i % 2 == 1:
                for j in range(4):
                    s.add(taiko(0.5, 1.4), i, 3 + j * 0.25)
        return s.render((0.8, 0.12, 2500)), s.length
    bl = s.beat * 4
    k, sn, h = kick(1.0), snare(0.6), hat(False, 0.25)
    for i, (r, kd) in enumerate(prog):
        root = n2m(r)
        for j in range(16):
            s.add(bass(root + (12 if j % 4 == 2 else 0) + (7 if j % 8 == 7 else 0), s.beat * 0.22, 0.6, 1100), i, j * 0.25)
        for j in range(4):
            s.add(k, i, j)
            if j % 2:
                s.add(sn, i, j)
            s.add(h, i, j + 0.5)
        s.add(pad([m + 12 for m in chord(r, kd)], bl, 2200, 0.3, 0.05, 0.2), i)
        stab = pad([m + 24 for m in chord(r, kd)], s.beat * 0.4, 3000, 0.35, 0.005, 0.1)
        s.add(stab, i, 0)
        s.add(stab, i, 1.5)
    riff = ['A4', 'A4', 'C5', 'A4', 'D5', 'A4', 'E5', 'D5', 'A#4', 'A#4', 'D5', 'A#4', 'F5', 'E5', 'D5', 'A#4']
    for bar in range(8):
        base = 0 if bar % 2 == 0 else 8
        for j in range(8):
            nm = riff[base + j]
            off = -2 if bar in (2, 6) else (-5 if bar in (3, 7) else 0)
            s.add(shamisen(n2m(nm) + off, s.beat * 0.5 + 0.2, 0.3), bar, j * 0.5)
    return s.render((0.9, 0.14, 4000)), s.length



# ---------------------------------------------------------------------- vaults
def song_vaults():
    """Chapter 2: swung casino synthwave with a walking bass and shamisen hook."""
    s = Song(124, 16)
    prog = [('D3', 'm9'), ('G2', '7'), ('C3', 'M7'), ('A2', '7'),
            ('D3', 'm9'), ('A#2', 'M7'), ('E2', 'm7'), ('A2', '7')]
    bl = s.beat * 4
    sw = 0.62
    k, rim, h = kick(0.8), ka(0.35), hat(False, 0.2)
    for i in range(16):
        r, kd = prog[i % 8]
        root = n2m(r)
        s.add(pad([m + 12 for m in chord(r, kd)], bl + 0.3, 1800, 0.3, 0.05, 0.4), i)
        walk = [0, 7, 10, 12] if i % 2 == 0 else [12, 10, 7, 5]
        for j, iv in enumerate(walk):
            s.add(bass(root + iv - 12, s.beat * 0.85, 0.55, 700, pluck=False), i, j)
        for j in range(4):
            s.add(h, i, j)
            s.add(h, i, j + sw, 0.6)
            if j % 2 == 0:
                s.add(k, i, j)
            else:
                s.add(rim, i, j)
        if i % 4 == 3:
            s.add(chime([root + 24, root + 31, root + 36], 0.05, 0.5, 0.18), i, 3)
    hook = [('D5', 0, 0.62), ('F5', 0.62, 0.38), ('A5', 1, 1), ('G5', 2, 0.62), ('F5', 2.62, 0.38), ('E5', 3, 1),
            ('D5', 4, 0.62), ('E5', 4.62, 0.38), ('F5', 5, 0.62), ('A5', 5.62, 0.38), ('C6', 6, 1), ('A5', 7, 1)]
    for rep in (4, 8, 12):
        for nm, b, d in hook:
            s.add(shamisen(n2m(nm), d * s.beat + 0.25, 0.32), rep, b)
    return s.render((1.3, 0.2, 4200)), s.length


# ---------------------------------------------------------------------- luck
def song_luck(drums=False):
    """Lady Luck: frantic minor-key boss theme; the drum layer joins at phase 2."""
    s = Song(150, 8)
    prog = [('E2', 'm'), ('C3', 'M'), ('A2', 'm'), ('B2', '7'),
            ('E2', 'm'), ('C3', 'M'), ('D3', 'M'), ('B2', '7')]
    if drums:
        cl = clap(0.6)
        for i in range(8):
            for j in range(8):
                acc = j in (0, 3, 5)
                s.add(taiko(0.7 if acc else 0.35, 1.0 if acc else 1.3), i, j * 0.5)
            s.add(cl, i, 1)
            s.add(cl, i, 3)
            s.add(ka(0.3), i, 2.75)
        return s.render((0.7, 0.12, 2500)), s.length
    k, sn, h = kick(1.0), snare(0.55), hat(False, 0.24)
    bl = s.beat * 4
    for i, (r, kd) in enumerate(prog):
        root = n2m(r)
        for j in range(16):
            s.add(bass(root + (12 if j % 4 == 3 else 0), s.beat * 0.22, 0.6, 1200), i, j * 0.25)
        for j in range(4):
            s.add(k, i, j)
            if j % 2:
                s.add(sn, i, j)
            s.add(h, i, j + 0.5)
            s.add(h, i, j + 0.75, 0.5)
        s.add(pad([m + 12 for m in chord(r, kd)], bl, 2400, 0.28, 0.05, 0.2), i)
        stab = pad([m + 24 for m in chord(r, kd)], s.beat * 0.3, 3200, 0.35, 0.005, 0.08)
        s.add(stab, i, 0.5)
        s.add(stab, i, 2.5)
    riff = ['E5', 'G5', 'B5', 'E6', 'D6', 'B5', 'G5', 'F#5']
    for bar in range(8):
        off = {2: -4, 3: -1, 6: 2, 7: -1}.get(bar, 0)
        for j, nm in enumerate(riff):
            s.add(shamisen(n2m(nm) + off, s.beat * 0.5 + 0.15, 0.28), bar, j * 0.5)
    return s.render((0.9, 0.14, 4000)), s.length


# ---------------------------------------------------------------------- gardens
def song_gardens():
    """Chapter 3: quiet koto over cooling-fan pads, water drops and soft taiko."""
    s = Song(80, 12)
    prog = [('D3', 'm9'), ('A#2', 'M7'), ('G2', 'm7'), ('A2', 'sus4'),
            ('D3', 'm9'), ('F2', 'M7'), ('G2', 'm7'), ('A2', 'm')]
    bl = s.beat * 4
    h = hat(False, 0.08)
    for i in range(12):
        r, kd = prog[i % 8]
        s.add(pad([m + 12 for m in chord(r, kd)], bl + 0.9, 1100, 0.42, 0.9, 0.9), i)
        s.add(bass(n2m(r) - 12, bl * 0.9, 0.38, 380, pluck=False), i)
        for j in range(4):
            s.add(h, i, j + 0.5, 0.7 if j % 2 else 1.0)
        if i % 2 == 0:
            s.add(taiko(0.32, 0.9), i, 0)
        else:
            s.add(ka(0.12), i, 2.5)
        for _ in range(2):
            drop = sine(RNG.uniform(1800, 2600) * np.exp(-T(0.12) / 0.05) + 600, 0.12) * expenv(0.12, 0.03)
            s.add(drop, i, RNG.choice([0.75, 1.75, 2.25, 3.25]), 0.12)
    # Japanese "in" scale motif on koto, answered an octave up.
    phrase = [('D5', 0, 1), ('D#5', 1, 0.5), ('G5', 1.5, 1.5), ('A5', 3, 1),
              ('A#5', 4, 1), ('A5', 5, 0.5), ('G5', 5.5, 1.5), ('D5', 7, 1)]
    for rep, shift in ((0, 0), (2, 0), (4, -2), (6, 0), (8, 12), (10, 0)):
        for nm, b, d in phrase:
            m = n2m(nm) + shift
            if rep == 4 and nm == 'D#5':
                m = n2m('D5')
            s.add(koto(m, d * s.beat + 0.8, 0.34), rep, b)
    return s.render((2.4, 0.32, 3200)), s.length


# ---------------------------------------------------------------------- mukuro
def song_mukuro(drums=False):
    """Mukuro I: a cold, driving duel theme; taiko join at phase 2."""
    s = Song(138, 8)
    prog = [('C#3', 'm'), ('C#3', 'm'), ('A2', 'M'), ('B2', 'M'),
            ('C#3', 'm'), ('E3', 'M'), ('D3', 'M'), ('G#2', '7')]
    if drums:
        for i in range(8):
            for j in range(8):
                acc = j in (0, 3, 6)
                s.add(taiko(0.75 if acc else 0.3, 1.0 if acc else 1.25), i, j * 0.5)
            s.add(ka(0.35), i, 1.75)
            s.add(ka(0.35), i, 3.75)
        return s.render((0.8, 0.12, 2400)), s.length
    k, sn, h = kick(1.0), snare(0.5), hat(False, 0.2)
    bl = s.beat * 4
    for i, (r, kd) in enumerate(prog):
        root = n2m(r)
        for j in range(8):
            s.add(bass(root - 12 + (7 if j == 6 else 0), s.beat * 0.4, 0.62, 900), i, j * 0.5)
        for j in range(4):
            s.add(k, i, j)
            if j % 2:
                s.add(sn, i, j)
            s.add(h, i, j + 0.5)
        s.add(pad([m + 12 for m in chord(r, kd)], bl, 1600, 0.32, 0.2, 0.3), i)
    riff = [('C#5', 0, 0.5), ('E5', 0.5, 0.5), ('G#5', 1, 1), ('F#5', 2, 0.5), ('E5', 2.5, 0.5),
            ('D#5', 3, 0.5), ('E5', 3.5, 0.5)]
    for bar in range(8):
        off = {2: -4, 3: -2, 6: -3, 7: -5}.get(bar, 0)
        for nm, b, d in riff:
            s.add(shamisen(n2m(nm) + off, d * s.beat + 0.2, 0.3), bar, b)
    for bar in (3, 7):
        s.add(metal(1700, 1.2, 0.12), bar, 3)
    return s.render((1.0, 0.16, 3600)), s.length


# ---------------------------------------------------------------------- monorail
def song_monorail():
    """Chapter 4: driving synthwave over a train-wheel clatter."""
    s = Song(132, 16)
    prog = [('E3', 'm'), ('C3', 'M7'), ('G2', 'M'), ('D3', 'M'),
            ('E3', 'm'), ('C3', 'M7'), ('A2', 'm7'), ('B2', '7')]
    k, sn, h = kick(0.9), snare(0.5), hat(False, 0.18)
    clack = hp(noise(0.04), 1800) * expenv(0.04, 0.01)
    bl = s.beat * 4
    for i in range(16):
        r, kd = prog[i % 8]
        root = n2m(r)
        s.add(pad([m + 12 for m in chord(r, kd)], bl + 0.2, 2000, 0.26, 0.1, 0.3), i)
        for j in range(8):
            s.add(bass(root - 12 + (12 if j in (3, 7) else 0), s.beat * 0.42, 0.55, 1000), i, j * 0.5)
        for j in range(4):
            s.add(k, i, j)
            if j % 2:
                s.add(sn, i, j)
            s.add(h, i, j + 0.5)
        # da-dum da-dum: rail joints
        for b in (0, 0.25, 2, 2.25):
            s.add(clack, i, b, 0.45)
        notes = chord(r, kd, 1)
        for j in range(8):
            s.add(arp_note(notes[(j * 2) % len(notes)] + 12, s.beat * 0.4, 0.08), i, j * 0.5 + 0.25)
    hook = [('B4', 0, 0.5), ('E5', 0.5, 0.5), ('G5', 1, 1), ('F#5', 2, 0.5), ('E5', 2.5, 0.5), ('D5', 3, 1),
            ('E5', 4, 1.5), ('B4', 5.5, 0.5), ('D5', 6, 1), ('E5', 7, 1)]
    for rep in (4, 6, 12, 14):
        for nm, b, d in hook:
            s.add(shamisen(n2m(nm), d * s.beat + 0.2, 0.3), rep, b)
    return s.render((1.0, 0.16, 4200)), s.length


# ---------------------------------------------------------------------- raijin
def song_raijin(drums=False):
    """Raijin: thunder-god taiko and a growling synth bass; extra drums at phase 2."""
    s = Song(144, 8)
    prog = [('D3', 'm'), ('D3', 'm'), ('A#2', 'M'), ('C3', 'M'),
            ('D3', 'm'), ('F3', 'M'), ('G2', 'm'), ('A2', '7')]
    if drums:
        for i in range(8):
            for j in range(16):
                acc = j in (0, 3, 6, 10, 12)
                if acc or j % 2 == 0:
                    s.add(taiko(0.8 if acc else 0.3, 0.9 if acc else 1.3), i, j * 0.25)
            s.add(ka(0.4), i, 1.5)
            s.add(ka(0.4), i, 3.5)
        return s.render((0.9, 0.12, 2200)), s.length
    k, sn = kick(1.0), snare(0.6)
    bl = s.beat * 4
    for i, (r, kd) in enumerate(prog):
        root = n2m(r)
        for j in range(8):
            g = dist(bass(root - 12, s.beat * 0.45, 0.5, 700), 2.5)
            s.add(g, i, j * 0.5)
        for j in range(4):
            s.add(k, i, j)
            if j % 2:
                s.add(sn, i, j)
        s.add(taiko(0.8), i, 0)
        s.add(taiko(0.5, 1.2), i, 2.5)
        s.add(pad([m + 12 for m in chord(r, kd)], bl, 1400, 0.3, 0.05, 0.2), i)
    riff = [('D5', 0, 0.75), ('F5', 0.75, 0.25), ('A5', 1, 0.5), ('G#5', 1.5, 0.5), ('A5', 2, 1), ('C6', 3, 0.5),
            ('A5', 3.5, 0.5)]
    for bar in range(8):
        off = {2: -4, 3: -2, 5: 3, 6: -7, 7: -5}.get(bar, 0)
        for nm, b, d in riff:
            s.add(shamisen(n2m(nm) + off, d * s.beat + 0.2, 0.3), bar, b)
    for bar in (3, 7):
        s.add(lp(noise(1.2), 400) * expenv(1.2, 0.6) * 0.6, bar, 2)
    return s.render((1.0, 0.18, 3200)), s.length


def wind_loop():
    d = 6.0
    x = lp(noise(d + 1), 900) * 0.5 + bp(noise(d + 1), 1500, 3500) * 0.18
    x = x * (0.75 + 0.25 * np.sin(2 * np.pi * T(d + 1) / (d / 2)))
    return loopify(x, d), d


def rain_loop():
    d = 8.0
    x = lp(noise(d + 1), 3500) * 0.35 + hp(lp(noise(d + 1), 9000), 2500) * 0.25
    drops = np.zeros(len(x))
    for _ in range(260):
        at = RNG.uniform(0, d)
        dr = bp(noise(0.03), RNG.uniform(1500, 5000), 8000) * expenv(0.03, 0.006)
        mix_into(drops, dr, at, RNG.uniform(0.1, 0.5))
    x = x + drops
    x = x * (0.85 + 0.15 * np.sin(2 * np.pi * T(d + 1) / (d / 2)))
    return loopify(x, d), d


# ====================================================================== SFX
def whoosh(d=0.18, lo=600, hi=4000, gain=1.0, rise=True):
    t = T(d)
    x = noise(d)
    x = sweep_lp(x, lo if rise else hi, hi if rise else lo, 10)
    e = np.sin(np.pi * np.minimum(1, t / d)) ** 2
    return x * e * gain


def blade(pitch=1.0, d=0.22, gain=1.0):
    w = whoosh(d, 1500 * pitch, 7000, 0.7)
    ring = sine(2600 * pitch, d) * expenv(d, 0.05) * 0.18 + sine(3900 * pitch, d) * expenv(d, 0.03) * 0.1
    return (w + ring) * gain


def impact(d=0.3, f=90, gain=1.0, crunch=0.5):
    body = sine(f * (1 + 1.5 * np.exp(-T(d) / 0.02)), d) * expenv(d, d / 3)
    nz = lp(noise(d), 2500) * expenv(d, 0.05) * crunch
    return dist((body + nz) * 1.4, 2) * gain


def metal(f=1800, d=0.5, gain=1.0):
    x = np.zeros(int(d * SR))
    for k, (m, g) in enumerate([(1, 1), (2.76, 0.6), (5.4, 0.4), (8.93, 0.25)]):
        x += sine(f * m, d) * expenv(d, d / (2 + k)) * g
    x += hp(noise(d), 4000) * expenv(d, 0.01) * 0.8
    return x * gain


def blip(f, d=0.06, shape='square', gain=1.0):
    x = (square(f, d) if shape == 'square' else sine(f, d)) * expenv(d, d / 2.5, 0.001)
    return lp(x, 5000) * gain


def glitch(d=0.3, gain=1.0):
    x = np.zeros(int(d * SR))
    pos = 0
    while pos < len(x):
        seg = int(RNG.uniform(0.008, 0.04) * SR)
        f = RNG.choice([220, 440, 660, 880, 1320, 1760, 110])
        kind = RNG.integers(0, 3)
        if kind == 0:
            s = square(f, seg / SR + 0.001)[:seg]
        elif kind == 1:
            s = noise(seg / SR + 0.001)[:seg]
        else:
            s = np.zeros(seg)
        x[pos:pos + seg] = s[:len(x) - pos][:seg] * RNG.uniform(0.3, 1)
        pos += seg
    return lp(x, 6000) * gain


def explosion(d=0.9, gain=1.0):
    x = lp(noise(d), 1200) * expenv(d, 0.25) + impact(d, 60, 0.8, 1.0)
    x = reverb(x, 0.8, 0.25, 2000)[:int(d * SR)]
    return dist(x * 1.5, 1.5) * gain


def chime(notes, step=0.07, d=0.5, gain=1.0):
    total = step * len(notes) + d
    x = np.zeros(int(total * SR))
    for i, m in enumerate(notes):
        f = mtof(m)
        tone = (sine(f, d) + 0.3 * sine(f * 2, d) + 0.15 * sine(f * 3, d)) * expenv(d, d / 3, 0.003)
        mix_into(x, tone, i * step)
    return reverb(x, 0.7, 0.25)[:len(x) + int(0.3 * SR)] * gain


def zap(d=0.35, gain=1.0):
    t = T(d)
    f = 120 + 80 * np.sin(2 * np.pi * 37 * t)
    x = square(f, d, 0.3) * 0.6 + hp(noise(d), 3000) * 0.6
    x *= (np.sin(2 * np.pi * 60 * t) > 0) * 0.8 + 0.2
    return lp(x, 6000) * expenv(d, 0.15) * gain


def sweep_tone(f0, f1, d, shape='sine', gain=1.0):
    f = f0 * (f1 / f0) ** (T(d) / d)
    x = sine(f, d) if shape == 'sine' else square(f, d)
    return x * gain


def add(*xs):
    """Sum arrays of different lengths (zero padded)."""
    n = max(len(x) for x in xs)
    out = np.zeros(n)
    for x in xs:
        out[:len(x)] += x
    return out


def cat(*xs):
    return np.concatenate([np.asarray(x, dtype=float) for x in xs])


def build_sfx():
    S = {}
    S['step'] = lp(noise(0.05), 900) * expenv(0.05, 0.012) * 0.5
    S['jump'] = add(whoosh(0.16, 500, 2500, 0.55), sweep_tone(300, 520, 0.08, 'sine', 0.1))
    S['land'] = impact(0.18, 70, 0.7, 0.8)
    S['dash'] = add(whoosh(0.28, 400, 6000, 0.9), glitch(0.12, 0.25))
    S['nodash'] = blip(140, 0.08, 'square', 0.3)
    S['slash1'] = blade(1.0, 0.2)
    S['slash2'] = blade(1.15, 0.2)
    S['slash3'] = blade(0.9, 0.18) * 0.9
    S['finisher'] = add(blade(0.8, 0.3) * 1.1, metal(2400, 0.3, 0.25))
    S['launcher'] = whoosh(0.25, 800, 7000, 0.9)
    S['plunge'] = whoosh(0.3, 6000, 600, 0.8, rise=False)
    S['heavy'] = np.concatenate([sweep_tone(200, 900, 0.12, 'square', 0.12), blade(0.7, 0.3) * 1.2])
    S['sever_draw'] = np.concatenate([silence(0.03), blade(0.6, 0.35)])
    S['throw'] = whoosh(0.15, 1500, 6000, 0.7)
    S['clink'] = metal(3000, 0.15, 0.4)
    S['hit'] = impact(0.16, 160, 0.8, 1.2) + hp(noise(0.16), 2000) * expenv(0.16, 0.02) * 0.5
    S['hit_heavy'] = impact(0.4, 70, 1.0, 1.0)
    S['severance'] = np.concatenate([metal(1200, 0.2, 0.5) + blade(0.5, 0.2), impact(0.6, 50, 1.0, 1.0)])
    S['deflect'] = metal(2100, 0.7, 0.9) + impact(0.7, 300, 0.3, 0.5)
    S['block'] = metal(900, 0.25, 0.7) + impact(0.25, 180, 0.4, 0.8)
    S['clang'] = metal(1300, 0.6, 0.9)
    S['swish'] = whoosh(0.12, 1200, 5000, 0.35)
    S['hurt'] = glitch(0.22, 0.6) + impact(0.22, 120, 0.6, 0.6)
    S['overheat'] = hp(noise(1.2), 2500) * adsr(1.2, 0.05, 0.3, 0.5, 0.6) * 0.5 + sweep_tone(900, 300, 1.2, 'square', 0.06)
    S['uncork'] = sine(700 * np.exp(-T(0.08) / 0.03) + 300, 0.08) * expenv(0.08, 0.02) * 0.6
    S['heal'] = add(chime([n2m(x) for x in ('C5', 'E5', 'G5', 'C6')], 0.06, 0.4, 0.5),
                    lp(noise(0.3), 700) * adsr(0.3, 0.02, 0.1, 0.5, 0.1) * 0.25)
    S['empty'] = blip(180, 0.12, 'square', 0.3)
    S['reboot'] = np.concatenate([glitch(0.6, 0.5), sweep_tone(80, 600, 0.6, 'square', 0.15) * expenv(0.6, 0.5)])
    S['respawn'] = sweep_tone(200, 1200, 0.5, 'sine', 0.4) * adsr(0.5, 0.05, 0.1, 0.8, 0.2) + glitch(0.5, 0.2)
    S['flatline'] = np.concatenate([glitch(0.3, 0.6), sine(988, 1.6) * adsr(1.6, 0.01, 0.1, 0.9, 0.4) * 0.35])
    S['zap'] = zap(0.35, 0.8)
    S['drone_charge'] = sweep_tone(400, 1600, 0.35, 'square', 0.18) * adsr(0.35, 0.01, 0.1, 0.8, 0.05)
    S['drone_dive'] = whoosh(0.35, 3000, 600, 0.5, rise=False) + sweep_tone(1400, 500, 0.35, 'square', 0.08)
    S['explode'] = explosion(0.8, 1.0)
    S['metal_hit'] = metal(1500, 0.25, 0.6)
    S['turret_charge'] = sweep_tone(300, 1200, 0.3, 'square', 0.15) * adsr(0.3, 0.01, 0.05, 0.9, 0.05)
    S['turret_fire'] = add(impact(0.2, 220, 0.6, 1.0), blip(1500, 0.08, 'square', 0.25))
    S['windup'] = whoosh(0.4, 300, 1500, 0.4)
    S['swing'] = whoosh(0.22, 400, 3500, 0.75)
    S['breach'] = np.concatenate([blip(1760, 0.09, 'square', 0.45), silence(0.03), blip(1760, 0.09, 'square', 0.45),
                                  silence(0.03), blip(1320, 0.2, 'square', 0.5)])
    S['thug_hurt'] = sweep_tone(220, 140, 0.15, 'square', 0.12) * expenv(0.15, 0.06) + lp(noise(0.15), 800) * expenv(0.15, 0.04) * 0.3
    S['thug_die'] = sweep_tone(200, 70, 0.5, 'square', 0.15) * expenv(0.5, 0.2) + impact(0.5, 60, 0.5)
    S['stagger'] = np.concatenate([metal(700, 0.15, 0.4), sweep_tone(600, 200, 0.4, 'square', 0.15) * expenv(0.4, 0.2)])
    S['oni_grunt'] = lp(saw(70 + 10 * np.sin(2 * np.pi * 9 * T(0.4)), 0.4), 600) * adsr(0.4, 0.03, 0.1, 0.7, 0.15) * 0.7
    S['oni_roar'] = dist(lp(saw(55 + 15 * np.sin(2 * np.pi * 7 * T(1.6)), 1.6) + noise(1.6) * 0.4, 900) * adsr(1.6, 0.1, 0.3, 0.8, 0.6), 2) * 0.8
    S['oni_swing'] = whoosh(0.45, 200, 2000, 0.9)
    S['oni_slam'] = explosion(1.1, 1.0) + impact(1.1, 40, 1.0, 1.0)
    S['oni_hurt'] = lp(saw(90 * np.exp(-T(0.4) / 0.4), 0.4), 800) * expenv(0.4, 0.2) * 0.8
    S['oni_die'] = np.concatenate([S['oni_roar'][:int(0.9 * SR)], explosion(1.0, 0.9)])
    S['door_open'] = np.concatenate([blip(660, 0.06, 'square', 0.25), lp(noise(0.5), 600) * adsr(0.5, 0.05, 0.1, 0.6, 0.2) * 0.4])
    S['door_close'] = impact(0.4, 80, 0.9, 1.0) + metal(400, 0.4, 0.2)
    S['laser_hum'] = lp(saw(110, 0.25), 1200) * adsr(0.25, 0.05, 0.05, 0.6, 0.1) * 0.15
    S['crate_hit'] = impact(0.15, 200, 0.5, 1.5)
    S['crate_break'] = impact(0.4, 120, 0.7, 2.0) + lp(noise(0.4), 3000) * expenv(0.4, 0.1) * 0.4
    S['block_break'] = impact(0.45, 90, 0.8, 2.0) + lp(noise(0.45), 1800) * expenv(0.45, 0.15) * 0.5
    S['pickup'] = chime([n2m('E5'), n2m('A5')], 0.08, 0.3, 0.5)
    S['shard_appear'] = chime([n2m(x) for x in ('A5', 'E6')], 0.12, 0.6, 0.35)
    S['shard'] = chime([n2m(x) for x in ('A4', 'C5', 'E5', 'B5', 'E6')], 0.09, 0.9, 0.55)
    S['sync'] = add(chime([n2m(x) for x in ('A4', 'E5', 'A5', 'C6', 'E6')], 0.07, 0.8, 0.5),
                    sweep_tone(200, 800, 0.4, 'sine', 0.2) * adsr(0.4, 0.05, 0.1, 0.6, 0.2))
    S['victory'] = victory_sting()
    S['banner'] = impact(0.5, 55, 0.5, 0.6) + metal(1600, 0.5, 0.15)
    S['card'] = np.concatenate([whoosh(0.3, 400, 3000, 0.6), taiko(0.6)[:int(0.9 * SR)]])
    S['blip'] = blip(1320, 0.04, 'square', 0.18)
    S['kuro'] = glitch(0.09, 0.35) + blip(330, 0.09, 'square', 0.12)
    S['cam_beep'] = np.concatenate([blip(1800, 0.06, 'sine', 0.4), silence(0.04), blip(2400, 0.08, 'sine', 0.4)])
    S['menu_move'] = blip(880, 0.035, 'square', 0.18)
    S['menu_select'] = np.concatenate([blip(1320, 0.05, 'square', 0.22), blip(1760, 0.07, 'square', 0.22)])
    S['menu_back'] = np.concatenate([blip(990, 0.05, 'square', 0.2), blip(660, 0.07, 'square', 0.2)])
    S['pause'] = np.concatenate([blip(660, 0.05, 'sine', 0.3), blip(440, 0.08, 'sine', 0.3)])
    S['lift'] = lp(saw(55, 0.5) + saw(55.7, 0.5), 400) * adsr(0.5, 0.05, 0.1, 0.8, 0.15) * 0.35
    S['card_throw'] = add(whoosh(0.14, 2500, 8000, 0.7), metal(4200, 0.08, 0.15))
    S['reels'] = reel_spin()
    S['reel_stop'] = add(impact(0.12, 300, 0.6, 1.2), blip(1760, 0.06, 'square', 0.15))
    S['jackpot'] = add(chime([n2m(x) for x in ('C6', 'E6', 'G6', 'C7', 'G6', 'C7')], 0.06, 0.4, 0.5),
                       cat(silence(0.4), np.tile(cat(blip(1320, 0.08, 'square', 0.3), silence(0.04)), 6)))
    S['thunder'] = thunder()
    S['muk_guard'] = add(metal(1900, 0.45, 0.8), impact(0.3, 260, 0.3, 0.4))
    S['muk_slash'] = add(blade(1.3, 0.2, 1.0), metal(3200, 0.12, 0.12))
    S['muk_warp'] = cat(glitch(0.35, 0.6), sweep_tone(900, 120, 0.5, 'square', 0.12) * expenv(0.5, 0.25))
    S['vent'] = lp(noise(0.6), 2200) * adsr(0.6, 0.08, 0.1, 0.6, 0.3) * 0.5
    S['post'] = add(whoosh(0.45, 300, 5000, 0.9), sweep_tone(900, 500, 0.45, 'square', 0.05))
    S['horn'] = lp(add(saw(196, 1.4), saw(247, 1.4), saw(294, 1.4)), 1800) * adsr(1.4, 0.08, 0.1, 0.8, 0.3) * 0.5
    S['cannon'] = add(impact(0.5, 60, 1.0, 1.4), lp(noise(0.5), 1200) * expenv(0.5, 0.15) * 0.6)
    S['zap_warn'] = cat(*[cat(hp(noise(0.03), 3000) * 0.6, silence(0.05)) for _ in range(8)])
    S['arm'] = add(whoosh(0.6, 200, 2500, 1.0), metal(500, 0.6, 0.3))
    S['rj_hurt'] = add(metal(700, 0.5, 0.8), impact(0.4, 100, 0.6, 1.2))
    S['rj_die'] = cat(explosion(0.9, 1.0), explosion(1.2, 0.9))
    out = {}
    for k, v in S.items():
        v = np.asarray(v, dtype=float)
        out[k] = fade(normalize(v, 0.85), 0.001, 0.01)
    return out


def victory_sting():
    d = 2.8
    x = np.zeros(int((d + 1) * SR))
    for i, nm in enumerate(['A4', 'C5', 'E5']):
        mix_into(x, shamisen(n2m(nm), 0.4, 0.6), i * 0.11)
    mix_into(x, taiko(1.0), 0.0)
    mix_into(x, taiko(0.8, 1.2), 0.33)
    chordx = pad(chord('A3', 'add9') + [n2m('E5')], 2.2, 2400, 1.0, 0.02, 1.2)
    mix_into(x, chordx, 0.45, 0.8)
    mix_into(x, shamisen(n2m('A5'), 1.6, 0.7), 0.45)
    return reverb(x, 1.6, 0.3)[:int(d * SR)]


def reel_spin():
    d = 1.8
    x = np.zeros(int(d * SR))
    t = 0.0
    step = 0.035
    while t < d - 0.05:
        mix_into(x, hp(noise(0.012), 2500) * np.linspace(1, 0, int(0.012 * SR)), t, 0.5)
        mix_into(x, sine(900, 0.01) * 0.2, t)
        t += step
    return x + lp(saw(80, d), 300) * adsr(d, 0.1, 0.2, 0.5, 0.3) * 0.2


def thunder():
    d = 3.0
    x = lp(noise(d), 300) * expenv(d, 0.9, 0.08) * 1.2
    crack = hp(noise(0.3), 1500) * expenv(0.3, 0.06)
    x[:len(crack)] += crack * 0.5
    x = x * (0.6 + 0.4 * np.abs(lp(noise(d), 6)) * 6)
    return reverb(x, 1.8, 0.3, 1500)[:int(d * SR)] * 0.8


# ====================================================================== encoding
def wav_bytes(x):
    pcm = (np.clip(x, -1, 1) * 32767).astype('<i2')
    buf = io.BytesIO()
    w = wave.open(buf, 'wb')
    w.setnchannels(1)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes(pcm.tobytes())
    w.close()
    return buf.getvalue()


def mp3_bytes(x, kbps=96):
    with tempfile.TemporaryDirectory() as d:
        src = os.path.join(d, 'in.wav')
        dst = os.path.join(d, 'out.mp3')
        open(src, 'wb').write(wav_bytes(x))
        subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', src, '-ac', '1', '-ar', str(SR),
                        '-b:a', '%dk' % kbps, dst], check=True)
        return open(dst, 'rb').read()


SFX_NAMES = []
MUSIC = {}
CACHE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.audio_cache')


def build_all():
    os.makedirs(CACHE, exist_ok=True)
    out = {}
    sfx = build_sfx()
    for k, v in sfx.items():
        out[k] = (wav_bytes(v), SR, len(v), 'wav')
        SFX_NAMES.append(k)
    songs = {'title': song_title, 'sump': song_sump, 'alley': song_alley, 'boss': song_boss,
             'vaults': song_vaults, 'luck': song_luck, 'gardens': song_gardens, 'mukuro': song_mukuro,
             'monorail': song_monorail, 'raijin': song_raijin}
    for name, fn in songs.items():
        x, length = fn()
        x = normalize(x, 0.8)
        out[name] = (mp3_bytes(x), SR, len(x), 'mp3')
        MUSIC[name] = round(length, 4)
    for name, fn in (('boss_drums', song_boss), ('luck_drums', song_luck), ('mukuro_drums', song_mukuro), ('raijin_drums', song_raijin)):
        x, length = fn(drums=True)
        x = normalize(x, 0.8)
        out[name] = (mp3_bytes(x), SR, len(x), 'mp3')
    x, length = rain_loop()
    x = normalize(x, 0.5)
    out['rain_loop'] = (mp3_bytes(x, 64), SR, len(x), 'mp3')
    x, length = wind_loop()
    x = normalize(x, 0.5)
    out['wind_loop'] = (mp3_bytes(x, 64), SR, len(x), 'mp3')
    return out


def export_previews(folder):
    """Write every sound to `folder` for listening outside Scratch."""
    os.makedirs(folder, exist_ok=True)
    for k, (data, rate, n, fmt) in build_all().items():
        open(os.path.join(folder, '%s.%s' % (k, fmt)), 'wb').write(data)


if __name__ == '__main__':
    import sys
    export_previews(sys.argv[1] if len(sys.argv) > 1 else 'audio_preview')
