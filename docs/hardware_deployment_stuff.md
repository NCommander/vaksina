# Various hardware/deployment scenarios

Vaksina plus its API are designed to have as minium requirements as possible. The goal is to keep as code in base Python libraries as is possible, and as few dependencies as possible

Current thought process towards deployment image:

Goals:
 * Easy to deploy/install
 * Easy to embed/adapt

Hardware Deployment Scenarios:
 * Old laptop with webcam
 * RaspPi with camera module
 * Any SBC with V4L Linux module
 * ... maybe Windows Embedded ... maybe?

Ability to interface with external hardware:
 * i.e., print a ticket with a thermal scanner
 * may require access to either /dev/tty{S0/USB0}, and/or CUPS (but please no)
 * Easy to extend various cases as needs change

We may end up deploying multiple solutions ... We'll see ...

An important factor is this needs to be entirely turnkey. You download a premade IMG file, you pop it in, and it boots regardless. No configuration, or changes are needed. Furthermore, no internet access or network connectivity of any sort is needed. All information is locally stored.

## Ubuntu Core Based Solution
The use of Ubuntu Core as a base has all needed dependencies pre-packaged, and is trivial to deploy Docker containers on.

It also allows easy upscaling to other machines, support for RPi, and general familiarity. Ubuntu Core offers "Ubuntu Frame" as a key solution to host a web application to gather QR codes and similar.

Unknowns:
 - Can Ubuntu Frame access camera devices? (I couldn't tell from the documentation)

One of the major pros of Ubuntu Core is the long life of an LTS release, with Ubuntu 22.04 LTS coming soon

## Alpine Based Solution
Alpine is based around muslc, and is *in general* considerably smaller than Ubuntu. Alpine might be better for constrained hardware, *but* I'm less familiar with it in a general sense. Furthermore, if interaction with existing Glibc binaries needs to happen, alpine is difficult, as such things are not supported.

Alpine has generally excellent hardware and environment support, *but*, need to consider support life as a whole. Mostly just boils down to I have to do more research.

May want to support both these cases in reality. The biggest question is what to do for frontend

## Web-based front end vs. say PyQt
I think this is "more research required"
