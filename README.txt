Features
--------
* Adds Flickr Support to PloneTruegallery (collective.plonetruegallery)


General usage
--------------------

The "flickr" tab is now available in the PTG gallery settings.
The "batch size" (in general PTG settings) is also supported. Zero means no limit.

Flickr settings:
* User (name or ID)
* Photoset (name or ID)
* Collection ID
* Flickr API key
* Flickr API secret

Default values can be set here: Site Setup > Plone True Gallery Settings > flickr tab.

As far as the photosets/collections are owned by the user or available for
every album's API key, you can use different API keys for different albums.


Collection support
--------------------
* If a photoset ID is provided, the collection is ignored.
* The gallery will display photos from all albums in the collection.
* Depending on batch size, the N latest photos (by upload date) appear.
* Collection ID and API key must be owned by the user.


Author
--------------------
* Nathan van Gheem


Coding Contributions
--------------------
* Espen Moe-Nilssen
* Sylvain Bouchard
