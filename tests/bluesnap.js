/*
 * Copyright 2009-2010 Emily Stark, Mike Hamburg, Dan Boneh, Stanford University.
 * All rights reserved.
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions are
 * met:
 *
 * 1. Redistributions of source code must retain the above copyright
 *    notice, this list of conditions and the following disclaimer.
 *
 * 2. Redistributions in binary form must reproduce the above
 *    copyright notice, this list of conditions and the following
 *    disclaimer in the documentation and/or other materials provided
 *    with the distribution.
 *
 * THIS SOFTWARE IS PROVIDED BY THE AUTHORS "AS IS" AND ANY EXPRESS OR
 * IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
 * WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
 * DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
 * LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
 * CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
 * SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR
 * BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
 * WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE
 * OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN
 * IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 *
 * The views and conclusions contained in the software and documentation
 * are those of the authors and should not be interpreted as representing
 * official policies, either expressed or implied, of the authors.
 */
var window = new Object()
var navigator = new Object()
navigator.appName = "Netscape"
navigator.appVersion = "5.0 (Macintosh; Intel Mac OS X 10_9_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.104 Safari/537.36"

var BlueSnap = new Object()
BlueSnap.publicKey = "10001$a3adc4b2c417a9c1be31cfe010a4c200289581d2f3e95f54587412d29cef00f84b04764a8014a3dad88e1a8ef2778335f0d3be7fc27328664efd9205a0e86c8ee9c43df75008854ac295209235ef4ee6208e75b44bb103c752eea0b4d2b924cf9c5ad3d61bcbf2861314501134c1c21b6f1020dfb8655c4d861f808582e161a068e01ae3eb8bc64054a4cbf88c40174ec4b158fe68c9ac31a0b97ee20eea624d407adbaca7b0676ab23885182ecdbd488328274af11b31a555167b6dd8bc5faf2e64cf9faa54aa9fa780cebebcf4b70c2eb6d508681629c7a68af54b290c05177d85d84d0c89d7ab36e3e0402dcba44cf5458c594e6f9cb174760cc6a28a4b8b";
BlueSnap.version = "0.0.1",


! function() {
    "use strict";

    function a() {
        this.i = 0, this.j = 0, this.S = new Array
    }

    function b(a) {
        var b, c, d;
        for (b = 0; 256 > b; ++b) this.S[b] = b;
        for (c = 0, b = 0; 256 > b; ++b) c = 255 & c + this.S[b] + a[b % a.length], d = this.S[b], this.S[b] = this.S[c], this.S[c] = d;
        this.i = 0, this.j = 0
    }

    function c() {
        var a;
        return this.i = 255 & this.i + 1, this.j = 255 & this.j + this.S[this.i], a = this.S[this.i], this.S[this.i] = this.S[this.j], this.S[this.j] = a, this.S[255 & a + this.S[this.i]]
    }

    function d() {
        return new a
    }

    function e(a) {
        hb[ib++] ^= 255 & a, hb[ib++] ^= 255 & a >> 8, hb[ib++] ^= 255 & a >> 16, hb[ib++] ^= 255 & a >> 24, ib >= jb && (ib -= jb)
    }

    function f() {
        e((new Date).getTime())
    }

    function g() {
        if (null == gb) {
            for (f(), gb = d(), gb.init(hb), ib = 0; ib < hb.length; ++ib) hb[ib] = 0;
            ib = 0
        }
        return gb.next()
    }

    function h(a) {
        var b;
        for (b = 0; b < a.length; ++b) a[b] = g()
    }

    function i() {}

    function j(a, b, c) {
        null != a && ("number" == typeof a ? this.fromNumber(a, b, c) : null == b && "string" != typeof a ? this.fromString(a, 256) : this.fromString(a, b))
    }

    function k() {
        return new j(null)
    }

    function l(a, b, c, d, e, f) {
        for (; --f >= 0;) {
            var g = b * this[a++] + c[d] + e;
            e = Math.floor(g / 67108864), c[d++] = 67108863 & g
        }
        return e
    }

    function m(a, b, c, d, e, f) {
        for (var g = 32767 & b, h = b >> 15; --f >= 0;) {
            var i = 32767 & this[a],
                j = this[a++] >> 15,
                k = h * i + j * g;
            i = g * i + ((32767 & k) << 15) + c[d] + (1073741823 & e), e = (i >>> 30) + (k >>> 15) + h * j + (e >>> 30), c[d++] = 1073741823 & i
        }
        return e
    }

    function n(a, b, c, d, e, f) {
        for (var g = 16383 & b, h = b >> 14; --f >= 0;) {
            var i = 16383 & this[a];
            var j = this[a++] >> 14;
            var k = h * i + j * g;
            i = g * i + ((16383 & k) << 14) + c[d] + e, e = (i >> 28) + (k >> 14) + h * j, c[d++] = 268435455 & i
        }
        return e
    }

    function o(a) {
        return tb.charAt(a)
    }

    function p(a, b) {
        var c = ub[a.charCodeAt(b)];
        return null == c ? -1 : c
    }

    function q(a) {
        for (var b = this.t - 1; b >= 0; --b) a[b] = this[b];
        a.t = this.t, a.s = this.s
    }

    function r(a) {
        this.t = 1, this.s = 0 > a ? -1 : 0, a > 0 ? this[0] = a : -1 > a ? this[0] = a + this.DV : this.t = 0
    }

    function s(a) {
        var b = k();
        return b.fromInt(a), b
    }

    function t(a, b) {
        var c;
        if (16 == b) c = 4;
        else if (8 == b) c = 3;
        else if (256 == b) c = 8;
        else if (2 == b) c = 1;
        else if (32 == b) c = 5;
        else {
            if (4 != b) return this.fromRadix(a, b), void 0;
            c = 2
        }
        this.t = 0, this.s = 0;
        for (var d = a.length, e = !1, f = 0; --d >= 0;) {
            var g = 8 == c ? 255 & a[d] : p(a, d);
            0 > g ? "-" == a.charAt(d) && (e = !0) : (e = !1, 0 == f ? this[this.t++] = g : f + c > this.DB ? (this[this.t - 1] |= (g & (1 << this.DB - f) - 1) << f, this[this.t++] = g >> this.DB - f) : this[this.t - 1] |= g << f, f += c, f >= this.DB && (f -= this.DB))
        }
        8 == c && 0 != (128 & a[0]) && (this.s = -1, f > 0 && (this[this.t - 1] |= (1 << this.DB - f) - 1 << f)), this.clamp(), e && j.ZERO.subTo(this, this)
    }

    function u() {
        for (var a = this.s & this.DM; this.t > 0 && this[this.t - 1] == a;) --this.t
    }

    function v(a) {
        if (this.s < 0) return "-" + this.negate().toString(a);
        var b;
        if (16 == a) b = 4;
        else if (8 == a) b = 3;
        else if (2 == a) b = 1;
        else if (32 == a) b = 5;
        else {
            if (4 != a) return this.toRadix(a);
            b = 2
        }
        var c, d = (1 << b) - 1,
            e = !1,
            f = "",
            g = this.t,
            h = this.DB - g * this.DB % b;
        if (g-- > 0)
            for (h < this.DB && (c = this[g] >> h) > 0 && (e = !0, f = o(c)); g >= 0;) b > h ? (c = (this[g] & (1 << h) - 1) << b - h, c |= this[--g] >> (h += this.DB - b)) : (c = this[g] >> (h -= b) & d, 0 >= h && (h += this.DB, --g)), c > 0 && (e = !0), e && (f += o(c));
        return e ? f : "0"
    }

    function w() {
        var a = k();
        return j.ZERO.subTo(this, a), a
    }

    function x() {
        return this.s < 0 ? this.negate() : this
    }

    function y(a) {
        var b = this.s - a.s;
        if (0 != b) return b;
        var c = this.t;
        if (b = c - a.t, 0 != b) return this.s < 0 ? -b : b;
        for (; --c >= 0;)
            if (0 != (b = this[c] - a[c])) return b;
        return 0
    }

    function z(a) {
        var b, c = 1;
        return 0 != (b = a >>> 16) && (a = b, c += 16), 0 != (b = a >> 8) && (a = b, c += 8), 0 != (b = a >> 4) && (a = b, c += 4), 0 != (b = a >> 2) && (a = b, c += 2), 0 != (b = a >> 1) && (a = b, c += 1), c
    }

    function A() {
        return this.t <= 0 ? 0 : this.DB * (this.t - 1) + z(this[this.t - 1] ^ this.s & this.DM)
    }

    function B(a, b) {
        var c;
        for (c = this.t - 1; c >= 0; --c) b[c + a] = this[c];
        for (c = a - 1; c >= 0; --c) b[c] = 0;
        b.t = this.t + a, b.s = this.s
    }

    function C(a, b) {
        for (var c = a; c < this.t; ++c) b[c - a] = this[c];
        b.t = Math.max(this.t - a, 0), b.s = this.s
    }

    function D(a, b) {
        var c, d = a % this.DB,
            e = this.DB - d,
            f = (1 << e) - 1,
            g = Math.floor(a / this.DB),
            h = this.s << d & this.DM;
        for (c = this.t - 1; c >= 0; --c) b[c + g + 1] = this[c] >> e | h, h = (this[c] & f) << d;
        for (c = g - 1; c >= 0; --c) b[c] = 0;
        b[g] = h, b.t = this.t + g + 1, b.s = this.s, b.clamp()
    }

    function E(a, b) {
        b.s = this.s;
        var c = Math.floor(a / this.DB);
        if (c >= this.t) return b.t = 0, void 0;
        var d = a % this.DB,
            e = this.DB - d,
            f = (1 << d) - 1;
        b[0] = this[c] >> d;
        for (var g = c + 1; g < this.t; ++g) b[g - c - 1] |= (this[g] & f) << e, b[g - c] = this[g] >> d;
        d > 0 && (b[this.t - c - 1] |= (this.s & f) << e), b.t = this.t - c, b.clamp()
    }

    function F(a, b) {
        for (var c = 0, d = 0, e = Math.min(a.t, this.t); e > c;) d += this[c] - a[c], b[c++] = d & this.DM, d >>= this.DB;
        if (a.t < this.t) {
            for (d -= a.s; c < this.t;) d += this[c], b[c++] = d & this.DM, d >>= this.DB;
            d += this.s
        } else {
            for (d += this.s; c < a.t;) d -= a[c], b[c++] = d & this.DM, d >>= this.DB;
            d -= a.s
        }
        b.s = 0 > d ? -1 : 0, -1 > d ? b[c++] = this.DV + d : d > 0 && (b[c++] = d), b.t = c, b.clamp()
    }

    function G(a, b) {
        var c = this.abs(),
            d = a.abs(),
            e = c.t;
        for (b.t = e + d.t; --e >= 0;) b[e] = 0;
        for (e = 0; e < d.t; ++e) b[e + c.t] = c.am(0, d[e], b, e, 0, c.t);
        b.s = 0, b.clamp(), this.s != a.s && j.ZERO.subTo(b, b)
    }

    function H(a) {
        for (var b = this.abs(), c = a.t = 2 * b.t; --c >= 0;) a[c] = 0;
        for (c = 0; c < b.t - 1; ++c) {
            var d = b.am(c, b[c], a, 2 * c, 0, 1);
            (a[c + b.t] += b.am(c + 1, 2 * b[c], a, 2 * c + 1, d, b.t - c - 1)) >= b.DV && (a[c + b.t] -= b.DV, a[c + b.t + 1] = 1)
        }
        a.t > 0 && (a[a.t - 1] += b.am(c, b[c], a, 2 * c, 0, 1)), a.s = 0, a.clamp()
    }

    function I(a, b, c) {
        var d = a.abs();
        if (!(d.t <= 0)) {
            var e = this.abs();
            if (e.t < d.t) return null != b && b.fromInt(0), null != c && this.copyTo(c), void 0;
            null == c && (c = k());
            var f = k(),
                g = this.s,
                h = a.s,
                i = this.DB - z(d[d.t - 1]);
            i > 0 ? (d.lShiftTo(i, f), e.lShiftTo(i, c)) : (d.copyTo(f), e.copyTo(c));
            var l = f.t,
                m = f[l - 1];
            if (0 != m) {
                var n = m * (1 << this.F1) + (l > 1 ? f[l - 2] >> this.F2 : 0),
                    o = this.FV / n,
                    p = (1 << this.F1) / n,
                    q = 1 << this.F2,
                    r = c.t,
                    s = r - l,
                    t = null == b ? k() : b;
                for (f.dlShiftTo(s, t), c.compareTo(t) >= 0 && (c[c.t++] = 1, c.subTo(t, c)), j.ONE.dlShiftTo(l, t), t.subTo(f, f); f.t < l;) f[f.t++] = 0;
                for (; --s >= 0;) {
                    var u = c[--r] == m ? this.DM : Math.floor(c[r] * o + (c[r - 1] + q) * p);
                    if ((c[r] += f.am(0, u, c, s, 0, l)) < u)
                        for (f.dlShiftTo(s, t), c.subTo(t, c); c[r] < --u;) c.subTo(t, c)
                }
                null != b && (c.drShiftTo(l, b), g != h && j.ZERO.subTo(b, b)), c.t = l, c.clamp(), i > 0 && c.rShiftTo(i, c), 0 > g && j.ZERO.subTo(c, c)
            }
        }
    }

    function J(a) {
        var b = k();
        return this.abs().divRemTo(a, null, b), this.s < 0 && b.compareTo(j.ZERO) > 0 && a.subTo(b, b), b
    }

    function K(a) {
        this.m = a
    }

    function L(a) {
        return a.s < 0 || a.compareTo(this.m) >= 0 ? a.mod(this.m) : a
    }

    function M(a) {
        return a
    }

    function N(a) {
        a.divRemTo(this.m, null, a)
    }

    function O(a, b, c) {
        a.multiplyTo(b, c), this.reduce(c)
    }

    function P(a, b) {
        a.squareTo(b), this.reduce(b)
    }

    function Q() {
        if (this.t < 1) return 0;
        var a = this[0];
        if (0 == (1 & a)) return 0;
        var b = 3 & a;
        return b = 15 & b * (2 - (15 & a) * b), b = 255 & b * (2 - (255 & a) * b), b = 65535 & b * (2 - (65535 & (65535 & a) * b)), b = b * (2 - a * b % this.DV) % this.DV, b > 0 ? this.DV - b : -b
    }

    function R(a) {
        this.m = a, this.mp = a.invDigit(), this.mpl = 32767 & this.mp, this.mph = this.mp >> 15, this.um = (1 << a.DB - 15) - 1, this.mt2 = 2 * a.t
    }

    function S(a) {
        var b = k();
        return a.abs().dlShiftTo(this.m.t, b), b.divRemTo(this.m, null, b), a.s < 0 && b.compareTo(j.ZERO) > 0 && this.m.subTo(b, b), b
    }

    function T(a) {
        var b = k();
        return a.copyTo(b), this.reduce(b), b
    }

    function U(a) {
        for (; a.t <= this.mt2;) a[a.t++] = 0;
        for (var b = 0; b < this.m.t; ++b) {
            var c = 32767 & a[b],
                d = c * this.mpl + ((c * this.mph + (a[b] >> 15) * this.mpl & this.um) << 15) & a.DM;
            for (c = b + this.m.t, a[c] += this.m.am(0, d, a, b, 0, this.m.t); a[c] >= a.DV;) a[c] -= a.DV, a[++c] ++
        }
        a.clamp(), a.drShiftTo(this.m.t, a), a.compareTo(this.m) >= 0 && a.subTo(this.m, a)
    }

    function V(a, b) {
        a.squareTo(b), this.reduce(b)
    }

    function W(a, b, c) {
        a.multiplyTo(b, c), this.reduce(c)
    }

    function X() {
        return 0 == (this.t > 0 ? 1 & this[0] : this.s)
    }

    function Y(a, b) {
        if (a > 4294967295 || 1 > a) return j.ONE;
        var c = k(),
            d = k(),
            e = b.convert(this),
            f = z(a) - 1;
        for (e.copyTo(c); --f >= 0;)
            if (b.sqrTo(c, d), (a & 1 << f) > 0) b.mulTo(d, e, c);
            else {
                var g = c;
                c = d, d = g
            }
        return b.revert(c)
    }

    function Z(a, b) {
        var c;
        return c = 256 > a || b.isEven() ? new K(b) : new R(b), this.exp(a, c)
    }

    function $(a) {
        var b, c, d = "";
        for (b = 0; b + 3 <= a.length; b += 3) c = parseInt(a.substring(b, b + 3), 16), d += vb.charAt(c >> 6) + vb.charAt(63 & c);
        for (b + 1 == a.length ? (c = parseInt(a.substring(b, b + 1), 16), d += vb.charAt(c << 2)) : b + 2 == a.length && (c = parseInt(a.substring(b, b + 2), 16), d += vb.charAt(c >> 2) + vb.charAt((3 & c) << 4));
            (3 & d.length) > 0;) d += wb;
        return d
    }

    function _(a, b) {
        return new j(a, b)
    }

    function ab(a, b) {
        if (b < a.length + 11) return alert("Message too long for RSA"), null;
        for (var c = new Array, d = a.length - 1; d >= 0 && b > 0;) {
            var e = a.charCodeAt(d--);
            128 > e ? c[--b] = e : e > 127 && 2048 > e ? (c[--b] = 128 | 63 & e, c[--b] = 192 | e >> 6) : (c[--b] = 128 | 63 & e, c[--b] = 128 | 63 & e >> 6, c[--b] = 224 | e >> 12)
        }
        c[--b] = 0;
        for (var f = new i, g = new Array; b > 2;) {
            for (g[0] = 0; 0 == g[0];) f.nextBytes(g);
            c[--b] = g[0]
        }
        return c[--b] = 2, c[--b] = 0, new j(c)
    }

    function bb() {
        this.n = null, this.e = 0, this.d = null, this.p = null, this.q = null, this.dmp1 = null, this.dmq1 = null, this.coeff = null
    }

    function cb(a, b) {
        null != a && null != b && a.length > 0 && b.length > 0 ? (this.n = _(a, 16), this.e = parseInt(b, 16)) : alert("Invalid RSA public key")
    }

    function db(a) {
        return a.modPowInt(this.e, this.n)
    }

    function eb(a) {
        var b = ab(a, this.n.bitLength() + 7 >> 3);
        if (null == b) return null;
        var c = this.doPublic(b);
        if (null == c) return null;
        var d = c.toString(16);
        return 0 == (1 & d.length) ? d : "0" + d
    }
    var fb = {
        cipher: {},
        hash: {},
        keyexchange: {},
        mode: {},
        misc: {},
        codec: {},
        exception: {
            corrupt: function(a) {
                this.toString = function() {
                    return "CORRUPT: " + this.message
                }, this.message = a
            },
            invalid: function(a) {
                this.toString = function() {
                    return "INVALID: " + this.message
                }, this.message = a
            },
            bug: function(a) {
                this.toString = function() {
                    return "BUG: " + this.message
                }, this.message = a
            },
            notReady: function(a) {
                this.toString = function() {
                    return "NOT READY: " + this.message
                }, this.message = a
            }
        }
    };
    "undefined" != typeof module && module.exports && (module.exports = fb), fb.cipher.aes = function(a) {
            this._tables[0][0][0] || this._precompute();
            var b, c, d, e, f, g = this._tables[0][4],
                h = this._tables[1],
                i = a.length,
                j = 1;
            if (4 !== i && 6 !== i && 8 !== i) throw new fb.exception.invalid("invalid aes key size");
            for (this._key = [e = a.slice(0), f = []], b = i; 4 * i + 28 > b; b++) d = e[b - 1], (0 === b % i || 8 === i && 4 === b % i) && (d = g[d >>> 24] << 24 ^ g[255 & d >> 16] << 16 ^ g[255 & d >> 8] << 8 ^ g[255 & d], 0 === b % i && (d = d << 8 ^ d >>> 24 ^ j << 24, j = j << 1 ^ 283 * (j >> 7))), e[b] = e[b - i] ^ d;
            for (c = 0; b; c++, b--) d = e[3 & c ? b : b - 4], f[c] = 4 >= b || 4 > c ? d : h[0][g[d >>> 24]] ^ h[1][g[255 & d >> 16]] ^ h[2][g[255 & d >> 8]] ^ h[3][g[255 & d]]
        }, fb.cipher.aes.prototype = {
            encrypt: function(a) {
                return this._crypt(a, 0)
            },
            decrypt: function(a) {
                return this._crypt(a, 1)
            },
            _tables: [
                [
                    [],
                    [],
                    [],
                    [],
                    []
                ],
                [
                    [],
                    [],
                    [],
                    [],
                    []
                ]
            ],
            _precompute: function() {
                var a, b, c, d, e, f, g, h, i, j = this._tables[0],
                    k = this._tables[1],
                    l = j[4],
                    m = k[4],
                    n = [],
                    o = [];
                for (a = 0; 256 > a; a++) o[(n[a] = a << 1 ^ 283 * (a >> 7)) ^ a] = a;
                for (b = c = 0; !l[b]; b ^= d || 1, c = o[c] || 1)
                    for (g = c ^ c << 1 ^ c << 2 ^ c << 3 ^ c << 4, g = 99 ^ (g >> 8 ^ 255 & g), l[b] = g, m[g] = b, f = n[e = n[d = n[b]]], i = 16843009 * f ^ 65537 * e ^ 257 * d ^ 16843008 * b, h = 257 * n[g] ^ 16843008 * g, a = 0; 4 > a; a++) j[a][b] = h = h << 24 ^ h >>> 8, k[a][g] = i = i << 24 ^ i >>> 8;
                for (a = 0; 5 > a; a++) j[a] = j[a].slice(0), k[a] = k[a].slice(0)
            },
            _crypt: function(a, b) {
                if (4 !== a.length) throw new fb.exception.invalid("invalid aes block size");
                var c, d, e, f, g = this._key[b],
                    h = a[0] ^ g[0],
                    i = a[b ? 3 : 1] ^ g[1],
                    j = a[2] ^ g[2],
                    k = a[b ? 1 : 3] ^ g[3],
                    l = g.length / 4 - 2,
                    m = 4,
                    n = [0, 0, 0, 0],
                    o = this._tables[b],
                    p = o[0],
                    q = o[1],
                    r = o[2],
                    s = o[3],
                    t = o[4];
                for (f = 0; l > f; f++) c = p[h >>> 24] ^ q[255 & i >> 16] ^ r[255 & j >> 8] ^ s[255 & k] ^ g[m], d = p[i >>> 24] ^ q[255 & j >> 16] ^ r[255 & k >> 8] ^ s[255 & h] ^ g[m + 1], e = p[j >>> 24] ^ q[255 & k >> 16] ^ r[255 & h >> 8] ^ s[255 & i] ^ g[m + 2], k = p[k >>> 24] ^ q[255 & h >> 16] ^ r[255 & i >> 8] ^ s[255 & j] ^ g[m + 3], m += 4, h = c, i = d, j = e;
                for (f = 0; 4 > f; f++) n[b ? 3 & -f : f] = t[h >>> 24] << 24 ^ t[255 & i >> 16] << 16 ^ t[255 & j >> 8] << 8 ^ t[255 & k] ^ g[m++], c = h, h = i, i = j, j = k, k = c;
                return n
            }
        }, fb.bitArray = {
            bitSlice: function(a, b, c) {
                return a = fb.bitArray._shiftRight(a.slice(b / 32), 32 - (31 & b)).slice(1), void 0 === c ? a : fb.bitArray.clamp(a, c - b)
            },
            extract: function(a, b, c) {
                var d, e = Math.floor(31 & -b - c);
                return d = -32 & (b + c - 1 ^ b) ? a[0 | b / 32] << 32 - e ^ a[0 | b / 32 + 1] >>> e : a[0 | b / 32] >>> e, d & (1 << c) - 1
            },
            concat: function(a, b) {
                if (0 === a.length || 0 === b.length) return a.concat(b);
                var c = a[a.length - 1],
                    d = fb.bitArray.getPartial(c);
                return 32 === d ? a.concat(b) : fb.bitArray._shiftRight(b, d, 0 | c, a.slice(0, a.length - 1))
            },
            bitLength: function(a) {
                var b, c = a.length;
                return 0 === c ? 0 : (b = a[c - 1], 32 * (c - 1) + fb.bitArray.getPartial(b))
            },
            clamp: function(a, b) {
                if (32 * a.length < b) return a;
                a = a.slice(0, Math.ceil(b / 32));
                var c = a.length;
                return b = 31 & b, c > 0 && b && (a[c - 1] = fb.bitArray.partial(b, a[c - 1] & 2147483648 >> b - 1, 1)), a
            },
            partial: function(a, b, c) {
                return 32 === a ? b : (c ? 0 | b : b << 32 - a) + 1099511627776 * a
            },
            getPartial: function(a) {
                return Math.round(a / 1099511627776) || 32
            },
            equal: function(a, b) {
                if (fb.bitArray.bitLength(a) !== fb.bitArray.bitLength(b)) return !1;
                var c, d = 0;
                for (c = 0; c < a.length; c++) d |= a[c] ^ b[c];
                return 0 === d
            },
            _shiftRight: function(a, b, c, d) {
                var e, f, g = 0;
                for (void 0 === d && (d = []); b >= 32; b -= 32) d.push(c), c = 0;
                if (0 === b) return d.concat(a);
                for (e = 0; e < a.length; e++) d.push(c | a[e] >>> b), c = a[e] << 32 - b;
                return g = a.length ? a[a.length - 1] : 0, f = fb.bitArray.getPartial(g), d.push(fb.bitArray.partial(31 & b + f, b + f > 32 ? c : d.pop(), 1)), d
            },
            _xor4: function(a, b) {
                return [a[0] ^ b[0], a[1] ^ b[1], a[2] ^ b[2], a[3] ^ b[3]]
            }
        }, fb.codec.hex = {
            fromBits: function(a) {
                var b, c = "";
                for (b = 0; b < a.length; b++) c += ((0 | a[b]) + 0xf00000000000).toString(16).substr(4);
                return c.substr(0, fb.bitArray.bitLength(a) / 4)
            },
            toBits: function(a) {
                var b, c, d = [];
                for (a = a.replace(/\s|0x/g, ""), c = a.length, a += "00000000", b = 0; b < a.length; b += 8) d.push(0 ^ parseInt(a.substr(b, 8), 16));
                return fb.bitArray.clamp(d, 4 * c)
            }
        }, fb.codec.utf8String = {
            fromBits: function(a) {
                var b, c, d = "",
                    e = fb.bitArray.bitLength(a);
                for (b = 0; e / 8 > b; b++) 0 === (3 & b) && (c = a[b / 4]), d += String.fromCharCode(c >>> 24), c <<= 8;
                return decodeURIComponent(escape(d))
            },
            toBits: function(a) {
                a = unescape(encodeURIComponent(a));
                var b, c = [],
                    d = 0;
                for (b = 0; b < a.length; b++) d = d << 8 | a.charCodeAt(b), 3 === (3 & b) && (c.push(d), d = 0);
                return 3 & b && c.push(fb.bitArray.partial(8 * (3 & b), d)), c
            }
        }, fb.codec.base64 = {
            _chars: "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/",
            fromBits: function(a, b, c) {
                var d, e = "",
                    f = 0,
                    g = fb.codec.base64._chars,
                    h = 0,
                    i = fb.bitArray.bitLength(a);
                for (c && (g = g.substr(0, 62) + "-_"), d = 0; 6 * e.length < i;) e += g.charAt((h ^ a[d] >>> f) >>> 26), 6 > f ? (h = a[d] << 6 - f, f += 26, d++) : (h <<= 6, f -= 6);
                for (; 3 & e.length && !b;) e += "=";
                return e
            },
            toBits: function(a, b) {
                a = a.replace(/\s|=/g, "");
                var c, d, e = [],
                    f = 0,
                    g = fb.codec.base64._chars,
                    h = 0;
                for (b && (g = g.substr(0, 62) + "-_"), c = 0; c < a.length; c++) {
                    if (d = g.indexOf(a.charAt(c)), 0 > d) throw new fb.exception.invalid("this isn't base64!");
                    f > 26 ? (f -= 26, e.push(h ^ d >>> f), h = d << 32 - f) : (f += 6, h ^= d << 32 - f)
                }
                return 56 & f && e.push(fb.bitArray.partial(56 & f, h, 1)), e
            }
        }, fb.codec.base64url = {
            fromBits: function(a) {
                return fb.codec.base64.fromBits(a, 1, 1)
            },
            toBits: function(a) {
                return fb.codec.base64.toBits(a, 1)
            }
        }, void 0 === fb.beware && (fb.beware = {}), fb.beware["CBC mode is dangerous because it doesn't protect message integrity."] = function() {
            fb.mode.cbc = {
                name: "cbc",
                encrypt: function(a, b, c, d) {
                    if (d && d.length) throw new fb.exception.invalid("cbc can't authenticate data");
                    if (128 !== fb.bitArray.bitLength(c)) throw new fb.exception.invalid("cbc iv must be 128 bits");
                    var e, f = fb.bitArray,
                        g = f._xor4,
                        h = f.bitLength(b),
                        i = 0,
                        j = [];
                    if (7 & h) throw new fb.exception.invalid("pkcs#5 padding only works for multiples of a byte");
                    for (e = 0; h >= i + 128; e += 4, i += 128) c = a.encrypt(g(c, b.slice(e, e + 4))), j.splice(e, 0, c[0], c[1], c[2], c[3]);
                    return h = 16843009 * (16 - (15 & h >> 3)), c = a.encrypt(g(c, f.concat(b, [h, h, h, h]).slice(e, e + 4))), j.splice(e, 0, c[0], c[1], c[2], c[3]), j
                },
                decrypt: function(a, b, c, d) {
                    if (d && d.length) throw new fb.exception.invalid("cbc can't authenticate data");
                    if (128 !== fb.bitArray.bitLength(c)) throw new fb.exception.invalid("cbc iv must be 128 bits");
                    if (127 & fb.bitArray.bitLength(b) || !b.length) throw new fb.exception.corrupt("cbc ciphertext must be a positive multiple of the block size");
                    var e, f, g, h = fb.bitArray,
                        i = h._xor4,
                        j = [];
                    for (d = d || [], e = 0; e < b.length; e += 4) f = b.slice(e, e + 4), g = i(c, a.decrypt(f)), j.splice(e, 0, g[0], g[1], g[2], g[3]), c = f;
                    if (f = 255 & j[e - 1], 0 == f || f > 16) throw new fb.exception.corrupt("pkcs#5 padding corrupt");
                    if (g = 16843009 * f, !h.equal(h.bitSlice([g, g, g, g], 0, 8 * f), h.bitSlice(j, 32 * j.length - 8 * f, 32 * j.length))) throw new fb.exception.corrupt("pkcs#5 padding corrupt");
                    return h.bitSlice(j, 0, 32 * j.length - 8 * f)
                }
            }
        }, fb.misc.hmac = function(a, b) {
            this._hash = b = b || fb.hash.sha256;
            var c, d = [
                    [],
                    []
                ],
                e = b.prototype.blockSize / 32;
            for (this._baseHash = [new b, new b], a.length > e && (a = b.hash(a)), c = 0; e > c; c++) d[0][c] = 909522486 ^ a[c], d[1][c] = 1549556828 ^ a[c];
            this._baseHash[0].update(d[0]), this._baseHash[1].update(d[1])
        }, fb.misc.hmac.prototype.encrypt = fb.misc.hmac.prototype.mac = function(a, b) {
            var c = new this._hash(this._baseHash[0]).update(a, b).finalize();
            return new this._hash(this._baseHash[1]).update(c).finalize()
        }, fb.hash.sha256 = function(a) {
            this._key[0] || this._precompute(), a ? (this._h = a._h.slice(0), this._buffer = a._buffer.slice(0), this._length = a._length) : this.reset()
        }, fb.hash.sha256.hash = function(a) {
            return (new fb.hash.sha256).update(a).finalize()
        }, fb.hash.sha256.prototype = {
            blockSize: 512,
            reset: function() {
                return this._h = this._init.slice(0), this._buffer = [], this._length = 0, this
            },
            update: function(a) {
                "string" == typeof a && (a = fb.codec.utf8String.toBits(a));
                var b, c = this._buffer = fb.bitArray.concat(this._buffer, a),
                    d = this._length,
                    e = this._length = d + fb.bitArray.bitLength(a);
                for (b = -512 & 512 + d; e >= b; b += 512) this._block(c.splice(0, 16));
                return this
            },
            finalize: function() {
                var a, b = this._buffer,
                    c = this._h;
                for (b = fb.bitArray.concat(b, [fb.bitArray.partial(1, 1)]), a = b.length + 2; 15 & a; a++) b.push(0);
                for (b.push(Math.floor(this._length / 4294967296)), b.push(0 | this._length); b.length;) this._block(b.splice(0, 16));
                return this.reset(), c
            },
            _init: [],
            _key: [],
            _precompute: function() {
                function a(a) {
                    return 0 | 4294967296 * (a - Math.floor(a))
                }
                var b, c = 0,
                    d = 2;
                a: for (; 64 > c; d++) {
                    for (b = 2; d >= b * b; b++)
                        if (0 === d % b) continue a;
                    8 > c && (this._init[c] = a(Math.pow(d, .5))), this._key[c] = a(Math.pow(d, 1 / 3)), c++
                }
            },
            _block: function(a) {
                var b, c, d, e, f = a.slice(0),
                    g = this._h,
                    h = this._key,
                    i = g[0],
                    j = g[1],
                    k = g[2],
                    l = g[3],
                    m = g[4],
                    n = g[5],
                    o = g[6],
                    p = g[7];
                for (b = 0; 64 > b; b++) 16 > b ? c = f[b] : (d = f[15 & b + 1], e = f[15 & b + 14], c = f[15 & b] = 0 | (d >>> 7 ^ d >>> 18 ^ d >>> 3 ^ d << 25 ^ d << 14) + (e >>> 17 ^ e >>> 19 ^ e >>> 10 ^ e << 15 ^ e << 13) + f[15 & b] + f[15 & b + 9]), c = c + p + (m >>> 6 ^ m >>> 11 ^ m >>> 25 ^ m << 26 ^ m << 21 ^ m << 7) + (o ^ m & (n ^ o)) + h[b], p = o, o = n, n = m, m = 0 | l + c, l = k, k = j, j = i, i = 0 | c + (j & k ^ l & (j ^ k)) + (j >>> 2 ^ j >>> 13 ^ j >>> 22 ^ j << 30 ^ j << 19 ^ j << 10);
                g[0] = 0 | g[0] + i, g[1] = 0 | g[1] + j, g[2] = 0 | g[2] + k, g[3] = 0 | g[3] + l, g[4] = 0 | g[4] + m, g[5] = 0 | g[5] + n, g[6] = 0 | g[6] + o, g[7] = 0 | g[7] + p
            }
        }, fb.random = {
            randomWords: function(a, b) {
                var c, d, e = [],
                    f = this.isReady(b);
                if (f === this._NOT_READY) throw new fb.exception.notReady("generator isn't seeded");
                for (f & this._REQUIRES_RESEED && this._reseedFromPools(!(f & this._READY)), c = 0; a > c; c += 4) 0 === (c + 1) % this._MAX_WORDS_PER_BURST && this._gate(), d = this._gen4words(), e.push(d[0], d[1], d[2], d[3]);
                return this._gate(), e.slice(0, a)
            },
            setDefaultParanoia: function(a) {
                this._defaultParanoia = a
            },
            addEntropy: function(a, b, c) {
                c = c || "user";
                var d, e, f, g = (new Date).valueOf(),
                    h = this._robins[c],
                    i = this.isReady(),
                    j = 0;
                switch (d = this._collectorIds[c], void 0 === d && (d = this._collectorIds[c] = this._collectorIdNext++), void 0 === h && (h = this._robins[c] = 0), this._robins[c] = (this._robins[c] + 1) % this._pools.length, typeof a) {
                    case "number":
                        void 0 === b && (b = 1), this._pools[h].update([d, this._eventId++, 1, b, g, 1, 0 | a]);
                        break;
                    case "object":
                        var k = Object.prototype.toString.call(a);
                        if ("[object Uint32Array]" === k) {
                            for (f = [], e = 0; e < a.length; e++) f.push(a[e]);
                            a = f
                        } else
                            for ("[object Array]" !== k && (j = 1), e = 0; e < a.length && !j; e++) "number" != typeof a[e] && (j = 1);
                        if (!j) {
                            if (void 0 === b)
                                for (b = 0, e = 0; e < a.length; e++)
                                    for (f = a[e]; f > 0;) b++, f >>>= 1;
                            this._pools[h].update([d, this._eventId++, 2, b, g, a.length].concat(a))
                        }
                        break;
                    case "string":
                        void 0 === b && (b = a.length), this._pools[h].update([d, this._eventId++, 3, b, g, a.length]), this._pools[h].update(a);
                        break;
                    default:
                        j = 1
                }
                if (j) throw new fb.exception.bug("random: addEntropy only supports number, array of numbers or string");
                this._poolEntropy[h] += b, this._poolStrength += b, i === this._NOT_READY && (this.isReady() !== this._NOT_READY && this._fireEvent("seeded", Math.max(this._strength, this._poolStrength)), this._fireEvent("progress", this.getProgress()))
            },
            isReady: function(a) {
                var b = this._PARANOIA_LEVELS[void 0 !== a ? a : this._defaultParanoia];
                return this._strength && this._strength >= b ? this._poolEntropy[0] > this._BITS_PER_RESEED && (new Date).valueOf() > this._nextReseed ? this._REQUIRES_RESEED | this._READY : this._READY : this._poolStrength >= b ? this._REQUIRES_RESEED | this._NOT_READY : this._NOT_READY
            },
            getProgress: function(a) {
                var b = this._PARANOIA_LEVELS[a ? a : this._defaultParanoia];
                return this._strength >= b ? 1 : this._poolStrength > b ? 1 : this._poolStrength / b
            },
            startCollectors: function() {
                if (!this._collectorsStarted) {
                    this._loadTimeCollector()
                    this._collectorsStarted = !0
                }
            },
            stopCollectors: function() {
                this._collectorsStarted = 0
            },
            addEventListener: function(a, b) {
                this._callbacks[a][this._callbackI++] = b
            },
            removeEventListener: function(a, b) {
                var c, d, e = this._callbacks[a],
                    f = [];
                for (d in e) e.hasOwnProperty(d) && e[d] === b && f.push(d);
                for (c = 0; c < f.length; c++) d = f[c], delete e[d]
            },
            _pools: [new fb.hash.sha256],
            _poolEntropy: [0],
            _reseedCount: 0,
            _robins: {},
            _eventId: 0,
            _collectorIds: {},
            _collectorIdNext: 0,
            _strength: 0,
            _poolStrength: 0,
            _nextReseed: 0,
            _key: [0, 0, 0, 0, 0, 0, 0, 0],
            _counter: [0, 0, 0, 0],
            _cipher: void 0,
            _defaultParanoia: 6,
            _collectorsStarted: !1,
            _callbacks: {
                progress: {},
                seeded: {}
            },
            _callbackI: 0,
            _NOT_READY: 0,
            _READY: 1,
            _REQUIRES_RESEED: 2,
            _MAX_WORDS_PER_BURST: 65536,
            _PARANOIA_LEVELS: [0, 48, 64, 96, 128, 192, 256, 384, 512, 768, 1024],
            _MILLISECONDS_PER_RESEED: 3e4,
            _BITS_PER_RESEED: 80,
            _gen4words: function() {
                for (var a = 0; 4 > a && (this._counter[a] = 0 | this._counter[a] + 1, !this._counter[a]); a++);
                return this._cipher.encrypt(this._counter)
            },
            _gate: function() {
                this._key = this._gen4words().concat(this._gen4words()), this._cipher = new fb.cipher.aes(this._key)
            },
            _reseed: function(a) {
                this._key = fb.hash.sha256.hash(this._key.concat(a)), this._cipher = new fb.cipher.aes(this._key);
                for (var b = 0; 4 > b && (this._counter[b] = 0 | this._counter[b] + 1, !this._counter[b]); b++);
            },
            _reseedFromPools: function(a) {
                var b, c = [],
                    d = 0;
                for (this._nextReseed = c[0] = (new Date).valueOf() + this._MILLISECONDS_PER_RESEED, b = 0; 16 > b; b++) c.push(0 | 4294967296 * Math.random());
                for (b = 0; b < this._pools.length && (c = c.concat(this._pools[b].finalize()), d += this._poolEntropy[b], this._poolEntropy[b] = 0, a || !(this._reseedCount & 1 << b)); b++);
                this._reseedCount >= 1 << this._pools.length && (this._pools.push(new fb.hash.sha256), this._poolEntropy.push(0)), this._poolStrength -= d, d > this._strength && (this._strength = d), this._reseedCount++, this._reseed(c)
            },
            _mouseCollector: function(a) {
                var b = a.x || a.clientX || a.offsetX || 0,
                    c = a.y || a.clientY || a.offsetY || 0;
                fb.random.addEntropy([b, c], 2, "mouse")
            },
            _loadTimeCollector: function() {
                fb.random.addEntropy((new Date).valueOf(), 2, "loadtime")
            },
            _fireEvent: function(a, b) {
                var c, d = fb.random._callbacks[a],
                    e = [];
                for (c in d) d.hasOwnProperty(c) && e.push(d[c]);
                for (c = 0; c < e.length; c++) e[c](b)
            }
        },
        function() {
            try {
                var a = new Uint32Array(32);
                crypto.getRandomValues(a), fb.random.addEntropy(a, 1024, "crypto.getRandomValues")
            } catch (b) {}
        }(),
        function() {
            for (var a in fb.beware) fb.beware.hasOwnProperty(a) && fb.beware[a]()
        }(), a.prototype.init = b, a.prototype.next = c;
    var gb, hb, ib, jb = 256;
    if (null == hb) {
        hb = new Array, ib = 0;
        var kb;
        if (window.crypto && window.crypto.getRandomValues) {
            var lb = new Uint8Array(32);
            for (window.crypto.getRandomValues(lb), kb = 0; 32 > kb; ++kb) hb[ib++] = lb[kb]
        }
        if ("Netscape" == navigator.appName && navigator.appVersion < "5" && window.crypto) {
            var mb = window.crypto.random(32);
            for (kb = 0; kb < mb.length; ++kb) hb[ib++] = 255 & mb.charCodeAt(kb)
        }
        for (; jb > ib;) kb = Math.floor(65536 * Math.random()), hb[ib++] = kb >>> 8, hb[ib++] = 255 & kb;
        ib = 0, f()
    }
    i.prototype.nextBytes = h;
    var nb, ob = 0xdeadbeefcafe,
        pb = 15715070 == (16777215 & ob);
    pb && "Microsoft Internet Explorer" == navigator.appName ? (j.prototype.am = m, nb = 30) : pb && "Netscape" != navigator.appName ? (j.prototype.am = l, nb = 26) : (j.prototype.am = n, nb = 28), j.prototype.DB = nb, j.prototype.DM = (1 << nb) - 1, j.prototype.DV = 1 << nb;
    var qb = 52;
    j.prototype.FV = Math.pow(2, qb), j.prototype.F1 = qb - nb, j.prototype.F2 = 2 * nb - qb;
    var rb, sb, tb = "0123456789abcdefghijklmnopqrstuvwxyz",
        ub = new Array;
    for (rb = "0".charCodeAt(0), sb = 0; 9 >= sb; ++sb) ub[rb++] = sb;
    for (rb = "a".charCodeAt(0), sb = 10; 36 > sb; ++sb) ub[rb++] = sb;
    for (rb = "A".charCodeAt(0), sb = 10; 36 > sb; ++sb) ub[rb++] = sb;
    K.prototype.convert = L, K.prototype.revert = M, K.prototype.reduce = N, K.prototype.mulTo = O, K.prototype.sqrTo = P, R.prototype.convert = S, R.prototype.revert = T, R.prototype.reduce = U, R.prototype.mulTo = W, R.prototype.sqrTo = V, j.prototype.copyTo = q, j.prototype.fromInt = r, j.prototype.fromString = t, j.prototype.clamp = u, j.prototype.dlShiftTo = B, j.prototype.drShiftTo = C, j.prototype.lShiftTo = D, j.prototype.rShiftTo = E, j.prototype.subTo = F, j.prototype.multiplyTo = G, j.prototype.squareTo = H, j.prototype.divRemTo = I, j.prototype.invDigit = Q, j.prototype.isEven = X, j.prototype.exp = Y, j.prototype.toString = v, j.prototype.negate = w, j.prototype.abs = x, j.prototype.compareTo = y, j.prototype.bitLength = A, j.prototype.mod = J, j.prototype.modPowInt = Z, j.ZERO = s(0), j.ONE = s(1);
    var vb = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/",
        wb = "=";
    bb.prototype.doPublic = db, bb.prototype.setPublic = cb, bb.prototype.encrypt = eb;
    var xb;
    xb = function() {
        function a() {}
        var b, c, d;
        return b = function(a) {
            var b, c, d, e;
            return d = a.split("$"), b = d[0], c = d[1], e = new bb, e.setPublic(c, b), e
        }, c = function() {
            return {
                key: fb.random.randomWords(8, 0),
                encrypt: function(a) {
                    return this.encryptWithIv(a, fb.random.randomWords(4, 0))
                },
                encryptWithIv: function(a, b) {
                    var c, d, e, f;
                    return c = new fb.cipher.aes(this.key), f = fb.codec.utf8String.toBits(a), e = fb.mode.cbc.encrypt(c, f, b), d = fb.bitArray.concat(b, e), fb.codec.base64.fromBits(d)
                }
            }
        }, d = function() {
            return {
                key: fb.random.randomWords(8, 0),
                sign: function(a) {
                    var b, c;
                    return b = new fb.misc.hmac(this.key, fb.hash.sha256), c = b.encrypt(a), fb.codec.base64.fromBits(c)
                }
            }
        }, a.prototype.encrypt = function(a) {
            var e, f, g, h, i, j, k, l, m;
            return a ? (l = b(BlueSnap.publicKey), e = c(), f = e.encrypt(a), j = d(), m = j.sign(fb.codec.base64.toBits(f)), g = fb.bitArray.concat(e.key, j.key), h = fb.codec.base64.fromBits(g), i = l.encrypt_b64(h), k = "$bsjs_" + BlueSnap.version.replace(/\./g, "_"), [k, i, f, m].join("$")) : ""
        }, a
    }();
    var yb;
    yb = function() {
        function a(a) {
            this.encrypter = a
        }
        var b, c, d;
        return c = function(a) {
            var b, d, e, f, g;
            for (e = [], d = a.children, f = 0, g = d.length; g > f; f++) b = d[f], 1 === b.nodeType && b.attributes["data-bluesnap"] ? e.push(b) : b.children.length > 0 && (e = e.concat(c(b)));
            return e
        }, b = function(a, b) {
            var c, d, e;
            d = document.createElement(a);
            for (c in b) b.hasOwnProperty(c) && (e = b[c], d.setAttribute(c, e));
            return d
        }, d = [], a.prototype.extractForm = function(a) {
            return window.jQuery && a instanceof jQuery ? a[0] : a.nodeType && 1 === a.nodeType ? a : document.getElementById(a)
        }, a.prototype.encryptForm = function(a) {
            var e, f, g, h, i, j, k, l;
            for (a = this.extractForm(a), i = c(a); d.length > 0;) {
                try {
                    a.removeChild(d[0])
                } catch (m) {}
                d.splice(0, 1)
            }
            for (l = [], j = 0, k = i.length; k > j; j++) e = i[j], g = e.getAttribute("data-bluesnap"), f = this.encrypter.encrypt(e.value), e.removeAttribute("name"), h = b("input", {
                value: f,
                type: "hidden",
                name: g
            }), d.push(h), l.push(a.appendChild(h));
            return l
        }, a
    }(), bb.prototype.encrypt_b64 = function(a) {
        var b;
        return b = this.encrypt(a), b ? $(b) : null
    }, window.BlueSnap = {
        version: "0.0.1",
        setTargetFormId: function() {
            var a, b;
            a = new xb
            window.bluesnap = a
            return a, b = new yb(a),
                function(a, c) {
                    var d;
                    return a = b.extractForm(a), d = function(d) {
                        return b.encryptForm(a), c ? c(d) : d
                    }, window.jQuery ? window.jQuery(a).submit(d) : a.addEventListener ? a.addEventListener("submit", d, !1) : a.attachEvent ? a.attachEvent("onsubmit", d) : void 0
                }
        }()
    }, fb.random.startCollectors()
}();
