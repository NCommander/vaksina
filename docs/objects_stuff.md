# Vaksina Top Level Object

Defines the public API for the Vaksina library

## CardTypeManager

The manager acts as a top level facility for processing various cards, and dispatches
as needed. i.e., it will handle creating all SHC key manage stuff, and more, ready for
processing

## CardObjects

A card object represents a given digital card, and is handled by other classes to
determine if the holder is currently up to date with their vaccination records

CardObjects are a generic superclass for each type of card, i.e. SHC, Green Pass, etc.

A card MUST have the following information

* Name
* Date of Birth
* Immunization Record (if possible)

CardObjects get passed to Validation modules to determine if holder is *actually* vaccinated

## Person

A Person is the end result created from parsing a given card

... probably should have a unique identifer if storage backed

A Person object is created from parsing card objects in a card manager

A Person contains the following information

* Given Name
* Date of Birth
* Records of Procedures
  * Could include PCR tests/rapid antigen
  * Must include vaccination complete with status

Can be processed by a validator module to determine status
