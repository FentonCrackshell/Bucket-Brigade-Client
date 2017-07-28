## List of top secret things instructions!
*Replace `this is my password` below with a password of your choosing*

## Install tor

## Create tor controller hash
tor --hash-password "this is my password"

## Add hash to torrc, and enable control port
*https://www.torproject.org/docs/faq.html.en#torrc*
open torrc file, and edit/add HashedControlPassword with the new hash:
`HashedControlPassword hash_goes_here`
enabled control port on 9051:
`ControlPort 9051`

## git pull this repo

## install client
`python setup.py install`

## run bucket_brigade once to generate config file
`bucekt_brigade`

## open bucket brigade config (~/.bucket_brigade/config.json), and add the unhashed password:
`this is my password`

## find someone running the server API, and add that info


*if you need help with this project, call Gizmoduck*
