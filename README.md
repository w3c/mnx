# MNX

Welcome to the [Music Notation Community Group](https://www.w3.org/community/music-notation/)'s next-generation music markup proposal.

Quick links:

- Read [MNX-Common by example](https://w3c.github.io/mnx/by-example/) to get a flavor of MNX-Common.
- Read the [current MNX-Common draft specification](https://w3c.github.io/mnx/specification/common/).
- Look at the [MNX-Generic examples](https://joeberkovitz.github.io/gmnx-viewer/).

## An introduction to MNX-Common

MNX-Common is a new, open standard for representing music notation as machine-readable data. It’s still being created, but this document gives context on our goals and plans.

Conceptually, MNX-Common is a way to represent this image:

<img src="https://github.com/w3c/mnx/blob/master/middle-c.png" alt="Image of music notation with middle C" width="300">

...as something like this:

```
staves=1
keysignature=C major
clef=treble
notes=whole note at C4
```

The former, an image, is intended for humans. A computer can’t understand it without using advanced, error-prone [computer vision techniques](https://en.wikipedia.org/wiki/Optical_music_recognition).

The latter — which encodes the _meaning_ (aka _semantics_) of the music, as opposed to a specific collection of pixels — is much easier for a computer to understand. Treating music in this way means it can be shared among different programs, automatically manipulated and much more.

MNX-Common is a standard that describes how to encode music, so that computers can have a shared understanding on how to interpret it. As HTML describes a web page such that any web browser can read it, MNX-Common describes a piece of music such that any notation software can read or write it.

### Motivation

People have been using computers to encode music for decades; a wide variety of encoding formats has been developed over the years. Why do we need yet another format?

Each music encoding format has its own biases and priorities. The [ABC format](https://abcnotation.com/), for example, aims for simplicity and was originally developed for folk music. [MusicXML](https://www.musicxml.com/) is optimized for notation interchange. [MIDI](https://en.wikipedia.org/wiki/MIDI) focuses on low-level instrument sequencing, as opposed to higher-level musical concepts. [MEI](https://music-encoding.org/), a general-purpose framework for encoding arbitrary musical documents, pays particular attention to the needs of scholars. Proprietary formats, such as [Finale](https://www.finalemusic.com/)’s `.musx` or [Sibelius](https://www.avid.com/sibelius)’ `.sib`, are optimized for specific notation programs and not meant to be read by others.

Our goal with MNX-Common is to create a format that does all of the following:

* **It’s open**, meaning: it’s clearly documented, free to use and developed in a vendor-independent, inclusive way.
* **It supports all of Common Western Musical Notation (CWMN)**, meaning: it has a clear answer for how to encode any musical concept found in CWMN. (CWMN is, by nature, an [imprecise concept](https://w3c.github.io/mnx/overview/#mnx-score-types).)
* **It prioritizes interchange**, meaning: it can be generated unambiguously, it can be parsed unambiguously, it favors one-and-only-one way to express concepts, and multiple programs reading the same MNX-Common file will interpret it the same way.
* **It’s semantically rich**, meaning: it’s biased toward encoding concepts rather than presentation when prudent.
* **It can be used as a native format**, meaning: it’s robust enough for programs to use directly instead of needing to invent their own format.

The existing format that comes closest to these goals is MusicXML. In fact, MNX-Common’s creation is being led by the [W3C Music Notation Community Group](https://www.w3.org/community/music-notation/), which also oversees the MusicXML standard. So what’s the difference?

We see MNX-Common as the next generation of MusicXML, enabling new uses that MusicXML didn’t set out to support.

With hundreds of applications supporting it, MusicXML has succeeded in becoming the de facto notation interchange standard. These days, you can be reasonably sure that, if you compose music in a commonly used notation application, you’ll be able to export it and open it in another application with decent fidelity — thanks to MusicXML. This has been a major cultural step forward, considering major notation programs hadn’t always looked kindly on making music exportable into competitors’ products.

As the dream of universal interchange has become a reality, users and developers have come to demand even more. Users want richer interchange (i.e., preserving the details of music more crisply), the advent of “reflowing” web-based renderers has shifted expectations around music engraving, and some developers even use MusicXML as a native format (something it wasn’t designed to do).

MNX-Common is an effort to take everything we’ve learned from 15 years of MusicXML development — along with its diverse community of developers, musicians and publishers — and build a better future together.

Finally, we should note there are many music notation systems throughout the world’s cultures, along with historical notation systems. MNX-Common deals specifically with Common Western Musical Notation, as it’s a high priority for the current MusicXML community and it’s where our collective expertise is the strongest — but our long-term plan is to support other systems. We’re also designing a format tentatively called MNX-Generic, which allows for mappings between graphics and audio, and we envision adding other formats to the MNX family.

### The plan / current status

The first step in our design was assembling an exhaustive list of roles and use cases for music notation in general. We published this document, [MNX Use Cases](https://w3c.github.io/mnx/use-cases/), in 2017. Not every use case there is meant to be covered by MNX-Common, but this is a solid reference that helps us consider the spectrum of what people do with digital music notation. It also gives us a common language around “roles” such as Composer, Performer or Developer.

Beyond that, we’ve jumped into writing [an early draft specification for MNX-Common](https://w3c.github.io/mnx/overview/). The [MNX GitHub issue tracker](https://github.com/w3c/mnx/issues) collects open issues we need to work through in designing the format.

Our plan of action is to start with large questions — such as whether notes are stored by their sounding pitch or written pitch — and progressively nail down the format.
