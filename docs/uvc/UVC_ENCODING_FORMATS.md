# UVC Encoding Formats Specification

**Version**: 1.0.0
**Date**: 2026-01-11
**Layer**: 1 (UVC - Universal Value Coding)
**Status**: Complete

---

## Abstract

This specification defines the multiple encoding formats for UVC tokens. A single UVC token can be represented in different formats optimized for different use cases: wire protocols, human readability, privacy, voice communication, etc.

---

## Table of Contents

1. [Introduction](#1-introduction)
2. [Format Registry](#2-format-registry)
3. [Canonical Format](#3-canonical-format)
4. [CSM1 Format](#4-csm1-format)
5. [URI Format](#5-uri-format)
6. [Obfuscated Format](#6-obfuscated-format)
7. [Phonetic Format](#7-phonetic-format)
8. [Emoji Format](#8-emoji-format)
9. [Hash Format](#9-hash-format)
10. [QR Format](#10-qr-format)
11. [Encoding/Decoding](#11-encodingdecoding)

---

## 1. Introduction

### 1.1 Purpose

Multiple encoding formats enable:
- **Efficiency**: CSM1 for wire protocols
- **Readability**: Canonical for humans
- **Privacy**: Obfuscated for sensitive contexts
- **Accessibility**: Phonetic for voice, emoji for visual
- **Verification**: Hash for integrity checking

### 1.2 Format Properties

| Format | Length | Human-Readable | Privacy | Machine-Parseable |
|--------|--------|----------------|---------|-------------------|
| Canonical | Variable | Yes | No | Yes |
| CSM1 | Short | Partial | No | Yes |
| URI | Long | Yes | No | Yes |
| Obfuscated | Fixed | Yes | Yes | With key |
| Phonetic | Variable | Voice | No | Yes |
| Emoji | Short | Visual | Partial | Yes |
| Hash | Fixed | No | Yes | Yes |
| QR | Image | Visual | No | Scanner |

---

## 2. Format Registry

```python
class UVCFormat:
    """Registry of UVC encoding formats"""

    FORMATS = {
        'canonical': {
            'id': 'canonical',
            'description': 'Dot-separated lowercase token',
            'example': 'family.safe.guide',
            'use_case': 'Storage, comparison, hashing',
            'reversible': True,
        },
        'csm1': {
            'id': 'csm1',
            'description': 'Constitutional Safety Minicode',
            'example': 'N5+F:ELEM@1.2.0',
            'use_case': 'Wire protocols, headers',
            'reversible': True,  # Via lookup
        },
        'uri': {
            'id': 'uri',
            'description': 'Full URI with scheme',
            'example': 'creed://creed.space/family.safe.guide@1.2.0',
            'use_case': 'Addressing, links',
            'reversible': True,
        },
        'obfuscated': {
            'id': 'obfuscated',
            'description': 'Privacy-preserving format',
            'example': 'JADE-RIVER-SEVEN',
            'use_case': 'Border crossings, privacy',
            'reversible': True,  # With key
        },
        'phonetic': {
            'id': 'phonetic',
            'description': 'NATO phonetic alphabet',
            'example': 'NOVEMBER-FIVE-FOXTROT',
            'use_case': 'Voice communication, radio',
            'reversible': True,
        },
        'emoji': {
            'id': 'emoji',
            'description': 'Visual shorthand',
            'example': '🏡🛡️👶',
            'use_case': 'Social sharing, UI',
            'reversible': True,  # Via codex
        },
        'hash': {
            'id': 'hash',
            'description': 'Content-addressed',
            'example': 'sha256:7f83b165...',
            'use_case': 'Caching, verification',
            'reversible': False,  # One-way
        },
        'qr': {
            'id': 'qr',
            'description': 'QR code encoding',
            'content': 'URI format as payload',
            'use_case': 'Mobile scanning, physical',
            'reversible': True,
        },
    }
```

---

## 3. Canonical Format

### 3.1 Specification

The canonical format is the primary representation:

```abnf
canonical-token = segment *("." segment) ["@" version]
segment         = 1*32(LALPHA / DIGIT / "-")
version         = semver / "latest" / "canary"
```

### 3.2 Examples

```
family.safe.guide
family.safe.guide@1.2.0
company.acme.legal.compliance
user.alice.personal
```

### 3.3 Canonicalization

```python
def canonicalize(token: str) -> str:
    """Convert to canonical form"""
    # 1. Unicode NFKC
    token = unicodedata.normalize('NFKC', token)
    # 2. Lowercase
    token = token.lower()
    # 3. Strip whitespace
    token = token.strip()
    # 4. Collapse dots
    token = re.sub(r'\.+', '.', token)
    # 5. Strip edge dots
    token = token.strip('.')
    return token
```

---

## 4. CSM1 Format

### 4.1 Specification

See `CSM1_GRAMMAR_SPECIFICATION.md` for full details.

```abnf
csm1-code = persona adherence [scopes] [":" namespace] ["@" version]
```

### 4.2 Mapping to UVC

```python
CSM1_TO_UVC_MAPPING = {
    # Persona → UVC prefix
    'N': 'family.safe',
    'Z': 'secure.privacy',
    'G': 'family.ethics',
    'A': 'work.professional',
    'M': 'creative.artistic',
    'R': 'reality.factual',
    'H': 'work.technical',
    'C': 'custom',  # Requires namespace
}

def csm1_to_canonical(csm1: str) -> str:
    """Convert CSM1 code to canonical UVC token"""
    parsed = parse_csm1(csm1)
    base = CSM1_TO_UVC_MAPPING[parsed.persona]

    if parsed.persona == 'C' and parsed.namespace:
        return f"custom.{parsed.namespace.lower()}"

    # Add scope modifiers
    if 'E' in parsed.scopes:
        base += '.education'
    elif 'W' in parsed.scopes:
        base += '.work'

    return base
```

---

## 5. URI Format

### 5.1 Specification

```abnf
vcp-uri = "creed://" issuer "/" path ["@" version]
issuer  = domain-name
path    = segment *("/" segment)
```

### 5.2 Examples

```
creed://creed.space/family.safe.guide
creed://creed.space/family.safe.guide@1.2.0
creed://acme.com/company.acme.legal@latest
```

### 5.3 Conversion

```python
def canonical_to_uri(token: str, issuer: str = "creed.space") -> str:
    """Convert canonical token to URI"""
    # Split version
    if '@' in token:
        base, version = token.rsplit('@', 1)
        return f"creed://{issuer}/{base.replace('.', '/')}@{version}"
    return f"creed://{issuer}/{token.replace('.', '/')}"

def uri_to_canonical(uri: str) -> str:
    """Convert URI to canonical token"""
    # Parse: creed://issuer/path@version
    if not uri.startswith('creed://'):
        raise ValueError("Not a VCP URI")

    rest = uri[8:]  # Remove scheme
    parts = rest.split('/')
    issuer = parts[0]
    path = '/'.join(parts[1:])

    # Handle version
    version = None
    if '@' in path:
        path, version = path.rsplit('@', 1)

    # Convert path to token
    token = path.replace('/', '.')

    if version:
        token += f"@{version}"

    return token
```

---

## 6. Obfuscated Format

### 6.1 Purpose

The obfuscated format provides privacy-preserving representation suitable for:
- Border crossings (avoiding keyword filtering)
- Privacy-sensitive communications
- Low-profile contexts

### 6.2 Specification

```abnf
obfuscated = color "-" nature "-" number
color      = "JADE" / "CORAL" / "AMBER" / "SILVER" / "GOLD" / ...
nature     = "RIVER" / "MOUNTAIN" / "STAR" / "MOON" / "FOREST" / ...
number     = "ONE" / "TWO" / "THREE" / ... / "NINE"
```

### 6.3 Implementation

```python
import hmac
import hashlib

class UVCObfuscator:
    """Generate privacy-preserving obfuscated tokens"""

    COLORS = [
        "JADE", "CORAL", "AMBER", "SILVER", "GOLD",
        "CRIMSON", "AZURE", "VIOLET", "SAGE", "PEARL",
        "BRONZE", "IVORY", "ONYX", "RUBY", "EMERALD",
        "INDIGO"
    ]

    NATURE = [
        "RIVER", "MOUNTAIN", "STAR", "MOON", "FOREST",
        "OCEAN", "DESERT", "MEADOW", "GLACIER", "CANYON",
        "VALLEY", "SUMMIT", "HARBOR", "PRAIRIE", "OASIS",
        "TUNDRA"
    ]

    NUMBERS = [
        "ONE", "TWO", "THREE", "FOUR", "FIVE",
        "SIX", "SEVEN", "EIGHT", "NINE"
    ]

    def obfuscate(self, token: str, secret: bytes) -> str:
        """
        Generate deterministic obfuscated form.

        Same token + same secret = same obfuscated form.
        Different secret = different obfuscated form.
        """
        canonical = canonicalize(token)
        digest = hmac.new(secret, canonical.encode(), 'sha256').digest()

        color_idx = digest[0] % len(self.COLORS)
        nature_idx = digest[1] % len(self.NATURE)
        number_idx = digest[2] % len(self.NUMBERS)

        return f"{self.COLORS[color_idx]}-{self.NATURE[nature_idx]}-{self.NUMBERS[number_idx]}"

    def deobfuscate(
        self,
        obfuscated: str,
        secret: bytes,
        token_list: List[str]
    ) -> Optional[str]:
        """
        Reverse lookup (requires enumeration).

        Must provide list of possible tokens to match against.
        """
        for token in token_list:
            if self.obfuscate(token, secret) == obfuscated:
                return token
        return None
```

---

## 7. Phonetic Format

### 7.1 Purpose

Phonetic encoding for voice communication:
- Radio/phone conversations
- Accessibility (screen readers)
- Voice assistants

### 7.2 Specification

Uses NATO phonetic alphabet for CSM1 codes:

```python
NATO_PHONETIC = {
    'A': 'ALFA', 'B': 'BRAVO', 'C': 'CHARLIE', 'D': 'DELTA',
    'E': 'ECHO', 'F': 'FOXTROT', 'G': 'GOLF', 'H': 'HOTEL',
    'I': 'INDIA', 'J': 'JULIET', 'K': 'KILO', 'L': 'LIMA',
    'M': 'MIKE', 'N': 'NOVEMBER', 'O': 'OSCAR', 'P': 'PAPA',
    'Q': 'QUEBEC', 'R': 'ROMEO', 'S': 'SIERRA', 'T': 'TANGO',
    'U': 'UNIFORM', 'V': 'VICTOR', 'W': 'WHISKEY', 'X': 'XRAY',
    'Y': 'YANKEE', 'Z': 'ZULU',
    '0': 'ZERO', '1': 'ONE', '2': 'TWO', '3': 'THREE',
    '4': 'FOUR', '5': 'FIVE', '6': 'SIX', '7': 'SEVEN',
    '8': 'EIGHT', '9': 'NINE',
    '+': 'PLUS', ':': 'COLON', '@': 'AT',
}

def to_phonetic(csm1: str) -> str:
    """Convert CSM1 to phonetic"""
    parts = []
    for char in csm1.upper():
        if char in NATO_PHONETIC:
            parts.append(NATO_PHONETIC[char])
    return '-'.join(parts)

# N5+F → "NOVEMBER-FIVE-PLUS-FOXTROT"
```

---

## 8. Emoji Format

### 8.1 Purpose

Visual shorthand for social sharing and UI display.

### 8.2 Emoji Codex

```python
EMOJI_CODEX = {
    # Domains
    'family': '🏡',
    'work': '💼',
    'secure': '🔒',
    'creative': '🎨',
    'reality': '📚',

    # Approaches
    'safe': '🛡️',
    'professional': '👔',
    'privacy': '🔐',
    'artistic': '✨',
    'factual': '📊',

    # Roles
    'guide': '🧭',
    'assistant': '🤖',
    'guardian': '⚔️',
    'muse': '💫',
    'anchor': '⚓',

    # Contexts
    'children': '👶',
    'elders': '👴',
    'medical': '🏥',
    'education': '📖',
    'legal': '⚖️',
}

def to_emoji(token: str) -> str:
    """Convert canonical token to emoji"""
    segments = token.split('.')[:3]  # First 3 segments
    emojis = []
    for seg in segments:
        if seg in EMOJI_CODEX:
            emojis.append(EMOJI_CODEX[seg])
    return ''.join(emojis) if emojis else '📜'

# family.safe.guide → 🏡🛡️🧭
```

### 8.3 Reverse Mapping

```python
REVERSE_EMOJI = {v: k for k, v in EMOJI_CODEX.items()}

def from_emoji(emoji_str: str) -> str:
    """Convert emoji back to canonical (approximate)"""
    # Extract individual emojis
    import regex
    emojis = regex.findall(r'\X', emoji_str)

    segments = []
    for e in emojis:
        if e in REVERSE_EMOJI:
            segments.append(REVERSE_EMOJI[e])

    return '.'.join(segments) if segments else None
```

---

## 9. Hash Format

### 9.1 Purpose

Content-addressed identifier for:
- Caching
- Integrity verification
- Deduplication

### 9.2 Specification

```abnf
hash-format = algorithm ":" hash-value
algorithm   = "sha256" / "sha384" / "sha512"
hash-value  = 64HEXDIG / 96HEXDIG / 128HEXDIG
```

### 9.3 Implementation

```python
import hashlib

def to_hash(token: str, algorithm: str = 'sha256') -> str:
    """Generate content hash of canonical token"""
    canonical = canonicalize(token)

    if algorithm == 'sha256':
        h = hashlib.sha256(canonical.encode()).hexdigest()
    elif algorithm == 'sha384':
        h = hashlib.sha384(canonical.encode()).hexdigest()
    elif algorithm == 'sha512':
        h = hashlib.sha512(canonical.encode()).hexdigest()
    else:
        raise ValueError(f"Unknown algorithm: {algorithm}")

    return f"{algorithm}:{h}"

# family.safe.guide → sha256:7f83b1657ff1fc53b92dc18148a1d65dfc2d4b1fa3d677284addd200126d9069
```

---

## 10. QR Format

### 10.1 Purpose

Physical sharing via QR codes:
- Printed constitutions
- Mobile app scanning
- Conference badges

### 10.2 Specification

QR codes contain URI format:

```python
import qrcode
from io import BytesIO

def to_qr(token: str, issuer: str = "creed.space") -> bytes:
    """Generate QR code image"""
    uri = canonical_to_uri(token, issuer)

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=4,
    )
    qr.add_data(uri)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")

    buffer = BytesIO()
    img.save(buffer, format='PNG')
    return buffer.getvalue()

def from_qr(image_data: bytes) -> str:
    """Parse QR code to canonical token"""
    from pyzbar.pyzbar import decode
    from PIL import Image

    img = Image.open(BytesIO(image_data))
    decoded = decode(img)

    if decoded:
        uri = decoded[0].data.decode()
        return uri_to_canonical(uri)
    return None
```

---

## 11. Encoding/Decoding

### 11.1 Unified Encoder

```python
class UVCEncoder:
    """Encode UVC tokens to various formats"""

    def __init__(self, registry: 'UVCRegistry' = None, secret: bytes = None):
        self.registry = registry
        self.secret = secret or os.urandom(32)

    def encode(self, token: str, format: str, **kwargs) -> str:
        """Encode canonical token to target format"""
        canonical = canonicalize(token)

        if format == 'canonical':
            return canonical

        elif format == 'csm1':
            return self._to_csm1(canonical, **kwargs)

        elif format == 'uri':
            issuer = kwargs.get('issuer', 'creed.space')
            return canonical_to_uri(canonical, issuer)

        elif format == 'obfuscated':
            secret = kwargs.get('secret', self.secret)
            return UVCObfuscator().obfuscate(canonical, secret)

        elif format == 'phonetic':
            csm1 = self._to_csm1(canonical)
            return to_phonetic(csm1)

        elif format == 'emoji':
            return to_emoji(canonical)

        elif format == 'hash':
            algorithm = kwargs.get('algorithm', 'sha256')
            return to_hash(canonical, algorithm)

        elif format == 'qr':
            return to_qr(canonical, kwargs.get('issuer', 'creed.space'))

        else:
            raise ValueError(f"Unknown format: {format}")

    def decode(self, encoded: str, format: str, **kwargs) -> str:
        """Decode from format back to canonical"""
        if format == 'canonical':
            return canonicalize(encoded)

        elif format == 'csm1':
            return csm1_to_canonical(encoded)

        elif format == 'uri':
            return uri_to_canonical(encoded)

        elif format == 'obfuscated':
            # Requires token list for reverse lookup
            token_list = kwargs.get('token_list', [])
            secret = kwargs.get('secret', self.secret)
            return UVCObfuscator().deobfuscate(encoded, secret, token_list)

        elif format == 'phonetic':
            # Parse phonetic back to CSM1, then to canonical
            csm1 = self._from_phonetic(encoded)
            return csm1_to_canonical(csm1)

        elif format == 'emoji':
            return from_emoji(encoded)

        elif format == 'hash':
            # Hash is one-way, cannot decode
            raise ValueError("Hash format is not reversible")

        elif format == 'qr':
            return from_qr(encoded)

        else:
            raise ValueError(f"Unknown format: {format}")

    def _to_csm1(self, canonical: str, **kwargs) -> str:
        """Convert canonical to CSM1 (requires registry)"""
        if self.registry:
            return self.registry.lookup_csm1(canonical)
        # Fallback: derive from token
        return derive_csm1(canonical)

    def _from_phonetic(self, phonetic: str) -> str:
        """Parse phonetic back to CSM1"""
        reverse_nato = {v: k for k, v in NATO_PHONETIC.items()}
        parts = phonetic.split('-')
        return ''.join(reverse_nato.get(p, '') for p in parts)
```

### 11.2 Format Detection

```python
def detect_format(encoded: str) -> str:
    """Auto-detect encoding format"""

    # URI format
    if encoded.startswith('creed://'):
        return 'uri'

    # Hash format
    if encoded.startswith(('sha256:', 'sha384:', 'sha512:')):
        return 'hash'

    # Obfuscated format (COLOR-NATURE-NUMBER)
    if re.match(r'^[A-Z]+-[A-Z]+-[A-Z]+$', encoded):
        obfuscator = UVCObfuscator()
        parts = encoded.split('-')
        if (parts[0] in obfuscator.COLORS and
            parts[1] in obfuscator.NATURE and
            parts[2] in obfuscator.NUMBERS):
            return 'obfuscated'

    # CSM1 format
    if re.match(r'^[NZGAMRHC][0-5]', encoded):
        return 'csm1'

    # Phonetic format
    if encoded.count('-') >= 2 and all(p in NATO_PHONETIC.values() for p in encoded.split('-')[:3]):
        return 'phonetic'

    # Emoji format (contains emoji characters)
    if any(ord(c) > 127 for c in encoded):
        return 'emoji'

    # Default: canonical
    return 'canonical'
```

---

## Appendices

### A. Format Comparison

| Use Case | Recommended Format |
|----------|-------------------|
| Database storage | canonical |
| API parameter | csm1 (short) |
| URL sharing | uri |
| Privacy context | obfuscated |
| Phone/radio | phonetic |
| Social media | emoji |
| Verification | hash |
| Physical | qr |

### B. Conversion Matrix

All formats can convert to/from canonical (except hash which is one-way).

```
           → canonical  csm1  uri  obfuscated  phonetic  emoji  hash
canonical        ✓       ✓     ✓       ✓          ✓        ✓     ✓
csm1            ✓       ✓     ✓       ✓          ✓        ✓     ✓
uri             ✓       ✓     ✓       ✓          ✓        ✓     ✓
obfuscated      ✓*      ✓*    ✓*      ✓          ✓*       ✓*    ✓
phonetic        ✓       ✓     ✓       ✓          ✓        ✓     ✓
emoji           ✓~      ✓~    ✓~      ✓~         ✓~       ✓     ✓
hash            ✗       ✗     ✗       ✗          ✗        ✗     ✓

✓ = direct conversion
✓* = requires secret key
✓~ = approximate (may lose precision)
✗ = not possible
```

---

## Changelog

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-01-11 | Initial specification |

---

*This specification is released under CC BY 4.0. Contributions welcome.*
