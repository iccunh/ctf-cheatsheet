# Steganography

{% embed url="https://0xrick.github.io/lists/stego/" %}

## Image

PNG Structure:

&#x20;[https://medium.com/@0xwan/png-structure-for-beginner-8363ce2a9f73](https://medium.com/@0xwan/png-structure-for-beginner-8363ce2a9f73)

JPG Structure:&#x20;

A JPEG file consists of a number of sections. Each section starts with `0xff`, followed by 1-byte section identifier, followed by number of data bytes in the section (in 2 bytes), followed by the data bytes. The sequence `0xffc0`, or any other `0xff--` two-byte sequence, inside the data byte sequence, has no significance and does not mark a start of a section.\
Ref: [https://stackoverflow.com/questions/13111228/getting-width-and-height-from-jpeg-image-file](https://stackoverflow.com/questions/13111228/getting-width-and-height-from-jpeg-image-file)

