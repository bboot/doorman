# doorman
Doorman for Multi-unit Buildings

This is a modern doorbell system for multi-unit dwellings.  It is suitable for
apartments, condos, dorms, and offices.


Motivation:

There are modern doorbells in the market for the home, such as the Nest Hello.
However there is nothing on the market for multi-unit dwellings.

There is a time lag for this sort of thing to be developed for multi-unit
dwellings.  If the current offerings are any indication, it is a time lag of
20 years.  Current solutions use decades-old technology, such as analog audio
and video, 10 digit button pads, analog fixed wiring, with the need for
amplifiers and repeaters for longer distances, and physical wiring to every
unit.  Additionally, such a system requires installation by a highly skilled
electrician, and the professional will typically be dealing with a proprietary
vendor-specific vertical system of questionable quality with nothing more than
phone support.


What this solution provides:

1. A single doorbell button no matter how many units there are
2. Voice (bot) interface - asks for who or what unit to page
3. Live digital streaming video and audio feed to see who is at the door
4. Remote door unlock at the tenant's discretion
5. Wifi - no wiring required except for 12v DC power
6. Each building unit is equipped with a wireless panel
7. Scalable - no fixed limit on the number of tenants or units
8. Single-use verbal passwords for keyless entry


Implementation:

This design uses a Raspberry-Pi, Python, Google Cloud Speech API, Google AIY,
Twilio, and WebRTC.  The in-dwelling panels are Android tablets.  Adding and
removing of tenants, units, vacation messaging, and other site-specific data
resides in a simple YAML file.


Future Enhancements:

Enhancements will focus on removing the experience of dealing with a door at
all.  The technology should not even be visible.
1. App for tenants so they can use their phone to respond to visitors
2. Wooden doors can be knocked on to invoke the doorman, no button
3. Face recognition for keyless unlock by tenants and known delivery personnel
4. Visitor-facing panel for tenant-lookup, maps, announcements, etc.
5. Tenant/unit management app
6. AirBnb integration
7. Battery and solar powered
8. Real estate "smart" lock-boxes
