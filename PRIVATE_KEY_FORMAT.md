# Private Key Format for GitHub Secrets

## ⚠️ CRITICAL: Private Key Format

The **most common issue** is how the private key is formatted in GitHub Secrets.

## Your Private Key (from JSON)

```
-----BEGIN PRIVATE KEY-----
MIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQCz+sQdDZszp4Rl
njHCVcP7aybaZFQAzMP3Zruh+4TiavtcF07QMfhIvpQfEwt2UcbRZTmSZFOs+ej5
fL4ooKo85DmppniirpUVQ4zpeeDLWLdpruG5OhVGpu4Yf+85+EL/Buz9lWeJF/fu
IguB0PEqpesp2ZcZCpwTewO06hbPNd/WByPara0E9L8JMT959Dz2XbPH00gwcngG
MzLfSUV0az904dOS59V7BCV3Bq8DcJwI4x7UWiJT6kTi5r9msVX955gRKom3WMYJ
z7yVVzb34U91512PZFeQI+CqwdT7LFRKmyp+yn7rofw7Jwahdn+HOxAeTsV14fKl
PnrEwZ3XAgMBAAECggEACx3iHylH/NjMBLrQuAA0KsNjkvm/do0vTYi67jZq7tFM
1VNbOuDbRSMAYyr5+kTy0tw9wh0QTg7hpQdfd4L1AO3X4fK2YNYHv1h8y68Lg4Pn
UE/NAXPk/IgzDLBaRmpfOQFkggVIb99bIQpZS5tsSgYVkHAwNQvCuDFQ+Uu8PPAs
Y1Ga2tMy+KVm6d5YJMVesOS9gC4Rbdk8Zx9R4+aNRBu2tMUKVBb/RdlhIdpJIooj
WP6GTUxG5tWbhaxPtHLxA4QYLryVkGtY5A5ZW9Z9EqYvfukLZ3BHSvKwj6wTXE0r
16zTyEey/ue24XjkNQFr/QCr8joHiTrCa61BryO5gQKBgQDjkflE6sPrL2nFEGQB
0Jdo5RU7oEf2DbN+Na+u0/sVcnl2MERrcOhxMkq3N4q2OyyOomYWJAfPiYNoQ8B6
NSI0H6Dh26Uhpwbgop/vKYS8AHHJPf2Z6cXFjPAEcPZfGcYcUI8zyrlgDhKU/OcD
TSXPhfnyjZjQ0kDkywU480ykfQKBgQDKdsYk+yqnyeIGKQnTODEZfVW5nTMv/aUH
9TYLbe7/xrBX6M4IcNa0a5eZDCtXFfjNdIk4gp/4id0ZobCN/8+LtHeNjkNdH3Cs
xtr4SW2+LuG6g0Mq020Rzvduy7cIEe9Q93mIFoC5QxSaRFXqKnkZVnYtkltIatHl
+6KoPmU/4wKBgQCUid5Tbo1NAJigSU+No7KAhC60yazO3SiQs8glbDYSTLMdQuoV
2w/New8rwfQneD5gJ35M612xyEdekgKbgfz+WrqvUafabGRf0aZk/Auojv22ZmEW
ynENvi2YKIeXkYIvTyH5o1QWb3kPiHfdPsj0SLXZ7TSW8PXsoNuazav0HQKBgG7N
4BU/LJIVh9CtRwZE+4IiuPbTlL8QBvC6/6/zo1hySfJio9e0wZyOQbJuGY4YpUj0
HWFDA//Gm626cuDT/qdLxh4/nJhra4PzdMVrklcCW2FzEyBuA4Q6i+okLXCKODpM
pkOXZS1/C9h9y7NTOWFnk1fPgIu6glNmixeexlTXAoGAVdT498Rhy9f5Z3v2gjzt
r8jn8706znt+8Dz5VAFP7HJTRSWXNimR+JlYhq+VfBArS0aOESRFP4pZ+IJJzSm0
hC6GNPAqa6aImlzbjuiY9QarSRK2yLHCqxYWxV0/JyAtMBPcXH+HL5q4YeBD0lLd
rdne+A+pECBrbbArScRnZC0=
-----END PRIVATE KEY-----
```

## How to Add to GitHub Secrets

### Method 1: Single Line with \n (RECOMMENDED)

Copy this EXACTLY (as one line with `\n` characters):

```
-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQCz+sQdDZszp4Rl\nnjHCVcP7aybaZFQAzMP3Zruh+4TiavtcF07QMfhIvpQfEwt2UcbRZTmSZFOs+ej5\nfL4ooKo85DmppniirpUVQ4zpeeDLWLdpruG5OhVGpu4Yf+85+EL/Buz9lWeJF/fu\nIguB0PEqpesp2ZcZCpwTewO06hbPNd/WByPara0E9L8JMT959Dz2XbPH00gwcngG\nMzLfSUV0az904dOS59V7BCV3Bq8DcJwI4x7UWiJT6kTi5r9msVX955gRKom3WMYJ\nz7yVVzb34U91512PZFeQI+CqwdT7LFRKmyp+yn7rofw7Jwahdn+HOxAeTsV14fKl\nPnrEwZ3XAgMBAAECggEACx3iHylH/NjMBLrQuAA0KsNjkvm/do0vTYi67jZq7tFM\n1VNbOuDbRSMAYyr5+kTy0tw9wh0QTg7hpQdfd4L1AO3X4fK2YNYHv1h8y68Lg4Pn\nUE/NAXPk/IgzDLBaRmpfOQFkggVIb99bIQpZS5tsSgYVkHAwNQvCuDFQ+Uu8PPAs\nY1Ga2tMy+KVm6d5YJMVesOS9gC4Rbdk8Zx9R4+aNRBu2tMUKVBb/RdlhIdpJIooj\nWP6GTUxG5tWbhaxPtHLxA4QYLryVkGtY5A5ZW9Z9EqYvfukLZ3BHSvKwj6wTXE0r\n16zTyEey/ue24XjkNQFr/QCr8joHiTrCa61BryO5gQKBgQDjkflE6sPrL2nFEGQB\n0Jdo5RU7oEf2DbN+Na+u0/sVcnl2MERrcOhxMkq3N4q2OyyOomYWJAfPiYNoQ8B6\nNSI0H6Dh26Uhpwbgop/vKYS8AHHJPf2Z6cXFjPAEcPZfGcYcUI8zyrlgDhKU/OcD\nTSXPhfnyjZjQ0kDkywU480ykfQKBgQDKdsYk+yqnyeIGKQnTODEZfVW5nTMv/aUH\n9TYLbe7/xrBX6M4IcNa0a5eZDCtXFfjNdIk4gp/4id0ZobCN/8+LtHeNjkNdH3Cs\nxtr4SW2+LuG6g0Mq020Rzvduy7cIEe9Q93mIFoC5QxSaRFXqKnkZVnYtkltIatHl\n+6KoPmU/4wKBgQCUid5Tbo1NAJigSU+No7KAhC60yazO3SiQs8glbDYSTLMdQuoV\n2w/New8rwfQneD5gJ35M612xyEdekgKbgfz+WrqvUafabGRf0aZk/Auojv22ZmEW\nynENvi2YKIeXkYIvTyH5o1QWb3kPiHfdPsj0SLXZ7TSW8PXsoNuazav0HQKBgG7N\n4BU/LJIVh9CtRwZE+4IiuPbTlL8QBvC6/6/zo1hySfJio9e0wZyOQbJuGY4YpUj0\nHWFDA//Gm626cuDT/qdLxh4/nJhra4PzdMVrklcCW2FzEyBuA4Q6i+okLXCKODpM\npkOXZS1/C9h9y7NTOWFnk1fPgIu6glNmixeexlTXAoGAVdT498Rhy9f5Z3v2gjzt\nr8jn8706znt+8Dz5VAFP7HJTRSWXNimR+JlYhq+VfBArS0aOESRFP4pZ+IJJzSm0\nhC6GNPAqa6aImlzbjuiY9QarSRK2yLHCqxYWxV0/JyAtMBPcXH+HL5q4YeBD0lLd\nrdne+A+pECBrbbArScRnZC0=\n-----END PRIVATE KEY-----\n
```

**Steps:**
1. Copy the ENTIRE line above (it's all one line)
2. Go to GitHub Secrets
3. Paste it into `GOOGLE_PRIVATE_KEY` value field
4. Click "Add secret"

### Method 2: Multi-line (Alternative)

If Method 1 doesn't work, try with actual line breaks:

1. Copy the private key from JSON file (with actual line breaks)
2. Paste into GitHub Secrets
3. Make sure it starts with `-----BEGIN` and ends with `-----END`

## Verification

After adding, test with the "Test Google Sheets Connection" workflow:
1. Go to Actions
2. Click "Test Google Sheets Connection"
3. Click "Run workflow"
4. Should complete successfully!

## Common Mistakes

❌ **Don't**: Remove the `\n` characters
❌ **Don't**: Add extra spaces
❌ **Don't**: Remove `-----BEGIN` or `-----END` lines
❌ **Don't**: Break it into multiple lines (unless using Method 2)

✅ **Do**: Copy the entire key exactly as shown
✅ **Do**: Keep all `\n` characters (they represent newlines)
✅ **Do**: Include `-----BEGIN` and `-----END` lines

