---
title: "Vaksina COVID QR Validation Checker"
author:
  - Michael Casadevall (Original author)
  - Pedro Vicente Seoane Prado (Markdown checker and translator to spanish)
  - Sander Speetjens (Typo checker)
  - Guiorgy (Typo checker)
  - PancakeSparkle (Typo checker)
date: 2022-01-01
category: COVID-19
tags: [COVID-19, QR, COVID, CARD, PASSPORT, SMARTH HEALTH CARD]
---

# Vaksina COVID QR Validation Checker

**NOTE**: Under best-case scenarios, when combined with the national ID of some sort, a COVID QR checker can provide assurances that a given person is properly vaccinated. However, especially in certain areas with non-centralized issuing, it is possible to have cases where an individual will not have a valid digital record because it was split into multiple locations or registries. As such this application can only be used to streamline the best scenario, and not as a replacement for manual checking.

Vaksina is a general-purpose library intended to validate multiple COVID QR codes from multiple countries and issuers. It is intended to streamline and help make validation of codes from multiple sources easier for public venues and other events.

This was primarily written because at the time I started this project, there is still no comprehensive COVID checking platform in existence. While some exist for Canada's SMART Health Cards and the EU's Digital COVID Pass, no framework can handle them as a single source of truth.

Vaksina is the intended proof of concept to handle this and is intended to work with a REST-based API deployed on a venue, but maybe adopted for use in mobile applications and similar as a future goal, but the intent is implementation with a kiosk-like system that is used in combination with a national ID card since none of the COVID-19 QR codes are usable as an ID in and of themselves.

## Version 0.1 Goals

### Zero-Knowledge/Zero-Record Model

It is intended that no data submitted to Vaksina is stored beyond the time it takes to parse the record. The only external data loaded and kept are PKI information from a set of "known good" trusted sources, that is covered by the next bullet point.

### Creation of Public Trust Store

The creation of a "known good" set of sign keys will be provided ala Mozilla store.

### Creation of validation of SMART Health Card standard

There is no one specific standard for COVID-19 QR validation. Canada and Japan have standardized on SMART, as have several states, pharmacies, hospitals and more within the United States. While Vaksina is intended as a general COVID-19 credential verification library, the initial MVP will only handle SMART Health Cards. Support for additional standards such as the EU's Digital COVID Pass, the UK's NHS Pass, and others like the New York State Excelsior Pass will be added with time.

### Implementation of VaccinePolicy Framework, to determine the status

Given the ongoing needs of various venues, and other changes, it is planned that a given VaccinePolicy can be coded for and changed. Vaksina is intended to have a "generic" frontend with current best practices but is meant to be easily customized without having to fork the library.

### Basic Front End for testing purposes

For purposes of testing and validation, a simple REST frontend + javascript page for testing on a local install is intended as part of the MVP.

### Full code coverage and unit tests

Because we don't want to have untested code paths.

## Usecases That I Want To Handle

### Reference implementation

To the extent possible, I was this to be a comprehensive reference for all known major vaccine cards. While these exist in multiple places, they're usually either tied to a browser-based framework or a given mobile platform. As such, it is difficult to repurpose for other needs or to be used for educational purposes relating to how information is stored on COVID Cards.

For people that want independent verification of what their cards contain, this is intended also to provide insight into an otherwise murky world, with hopefully well readable and understandable code that they run on their system.

### Handle non-Android/iOS uses

In general, the only applications that appear to exist are iOS/Android-based as of right now. There are some nodejs implementations, but they don't work on universal cards. As such, it makes it very hard to use a QR code scanner as part of a larger application, such as a streamlined check-in registration. The original envisioned use case was streamlined registration for a conference, vs. dealing with either taking QR codes on faith, or manual validation of each and every card.

It should be noted, however, that COVID 19 vaccine cards are not valid without an external ID.

### Allow interface/embedding in other applications easier

For instance, COVID-19 Checker BadgeLife(tm) would be an amazing thing to see.

### Understanding the connection between objects

While seemingly simple on the surface, the relationship between a person, their immunizations, and a given card is *non-obvious*. As originally implemented, vaksina was coded to handle SMART Health Cards as a rule. In a general sense, this also means it needs to handle FHIR Patient/Immunization data, as that is how the internal data is represented.

A given COVID card can, at least by specification, have multiple people contained within, with differing immunization records, PCR results (not modelled as of yet), *and/or* meeting the criteria for a given set of rules. As such, data needs to modeled in such a way that a card can be decoded to a set of patients, and validation status is handled independent per patient on a per card basis.

This is not entirely intuitive, but it specifically handles various types of test results and more, which should be kept in mine when dealing with the interfaces.

Because Vaksina is intended store-no-data solution, identifiers given to objects are reused, and are only valid in the context of that object in and
of itself. This is an intentional design decision to re-enforced that this
information is not to be stored by a validator application.

#### Useful links

* <https://github.com/the-commons-project/vci-directory> - list of PKI providers
* <https://github.com/Path-Check/who-verifier-app> - Android no data kept FOSS app
