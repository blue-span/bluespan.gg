bluespan.gg/giveaway stream chat blockchain™
============================================

The ``bluespan.gg/giveaway stream chat blockchain™`` hashes the contents of
stream chat to calculate giveaway winners in a cryptographically unpredictable
yet reproducible way.

How does it work?
-----------------

.. note:: The exact implementation details of winner selection are subject to
   change arbitrarily and without notice at any time.

Winner calculation isn't actually based on a blockchain [#blockchain-hype]_, but
instead a boring cryptographic hash function, `SHA-2`_.

.. [#blockchain-hype] "blockchain" is used ironically as a meaningless buzzword,
   which is consistent with typical usage in news/media/venture-capital startup
   propaganda

.. _`SHA-2`: https://en.wikipedia.org/wiki/SHA-2

Cryptographic hashing
~~~~~~~~~~~~~~~~~~~~~

The giveaway-bot watches YouTube stream chat using the YouTube `Live Streaming
API`_. This provides a list of chat messages, where each message has this
`structure`_:

.. code:: text

   {
     "snippet": {
       "authorChannelId": "UCpOkbe8JBvSHIEQn5D0V3tQ",
       "publishedAt": "2019-11-24T04:43:44.226Z",
       "textMessageDetails": {
         "messageText": "hei hei guys"
       }
     }
   }

These fields from each message are appended to the hash as:

.. code:: text

   hash.append(message_1["publishedAt"])
   hash.append(message_1["authorChannelId"])
   hash.append(message_1["messageText"])

   hash.append(message_2["publishedAt"])
   hash.append(message_2["authorChannelId"])
   hash.append(message_2["messageText"])

And so on, for every message that appears in stream chat.

This means that the raw hash values shown on stream depend on:

- the order that each chat message was sent, relative to all other chat messages
- the content and author of each message
- the exact date, time, and millisecond each message was sent

.. note::

   You can think of each incoming chat message roughly like a dice roll, except
   the die has 2\ :sup:`128` `faces`_, and the values on each face change each
   time you roll depending on both the previous roll, and all of the rolls
   before it.

.. _`faces`: https://www.wolframalpha.com/input/?i=2+%5E+128
.. _`Live Streaming API`: https://developers.google.com/youtube/v3/live/docs/liveChatMessages/list
.. _`structure`: https://developers.google.com/youtube/v3/live/docs/liveChatMessages#resource

Current seed
~~~~~~~~~~~~

After each message is recieved, an intermediate "digest" of the hash state is
computed, and converted to a 128-bit number which is used as the "seed" for
further computations. For example, if the current digest is:

.. code:: text

   e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855

The numeric `representation`_ of that value as used by the giveaway bot is:

.. code:: text

   302652579918965577886386472538583578916

We refer to this value internally as the "current seed", which represents a
unique and cryptographically unpredictable "winner state".

Winner succession
~~~~~~~~~~~~~~~~~

For each seed, we calculate a unique "succession" of winners for each
prize. This is based on:

- your unique/random registration ID (generated when you registered)
- the unique/random "giveaway prize ID (generated for each available prize, each giveaway period)

First, both IDs are converted to a numeric representation. For example, if your
registration ID is ``10a65d03-b4c5-420c-8fe6-98598896a86f``, and the giveaway
prize ID you selected is ``37194de1-cba9-4149-ac1c-b55a4b6b8b19``, in numeric
form, these are:

.. code:: text

   > UUID('10a65d03-b4c5-420c-8fe6-98598896a86f').int
   22131455768798834563163550531492161647

   > UUID('37194de1-cba9-4149-ac1c-b55a4b6b8b19').int
   73238926824539864358604865272067885849

These are combined using the `bitwise XOR`_ function (uncoincidentally, a
commonly used cryptographic primitive), yielding:

.. code:: text

   > 22131455768798834563163550531492161647 xor 73238926824539864358604865272067885849
   52831962999145433449111306850279433078

Internally, this value is referred to as the "registration vector". A
registration vector is calculated for all registration/prize pairs.

.. note::

   The "registration vector" step is of critical importance. If the succession
   were computed entirely based on seed distance from registration IDs alone,
   this would mean the same registration would be selected for all prize types
   (if that registration selected all prizes). In contrast, this method yields a
   unique succession ordering per prize type.

We then calculate the "distance" between current seed and the registration
vector as the magnitude of the difference between the seed and the registration
vector (also known as: "3rd grade math"):

.. code:: text

   > abs(302652579918965577886386472538583578916 - 52831962999145433449111306850279433078)
   249820616919820144437275165688304145838

The "winner" is selected by ordering all registrations by this value in
ascending order. In other words, the closer the above value is to zero for a
given seed, the more likely that registration is selected as the winner.

How is this actually better than (insert alternative here)?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This method of ordering provides the "minimal disruption" property, which is
desirable in that you can remove any single registration without causing a
complete reordering of the succession.

By contrast, if functions such as Python's ``random.choice``,
``random.shuffle``, or modulus math were used to implement this, the removal of
a single registrant would cause a total and complete reordering of the winner
succession for a given seed.

One cool property of this, if you and one other person know:

- the final seed value
- your respective registration ID
- the giveaway prize ID

You are then able to independently calculate your position in the winner
succession, relative to the other person, without having the complete list of
all other registrations.

In future giveaways, though it is not the top priority, the goal is to enable
anyone to independently reproduce each winner selection.

.. _`representation`: https://github.com/blue-span/giveaway-bot/blob/209fe15a5f88c30f0df3966f08bf74e0c6b6f6fa/giveaway_bot/selection.py#L46
.. _`ID`: https://en.wikipedia.org/wiki/Universally_unique_identifier
.. _`bitwise XOR`: https://en.wikipedia.org/wiki/Bitwise_operation#XOR
