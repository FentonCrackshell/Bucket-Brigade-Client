Replace `this is my password` below with a password of your choosing

install tor

tor --hash-password "this is my password"

(https://www.torproject.org/docs/faq.html.en#torrc)
open torrc file, and edit/add HashedControlPassword with the new hash:
`HashedControlPassword 16:872860B76453A77D60CA2BB8C1A7042072093276A3D701AD684053EC4C`
enabled control port on 9051:
`ControlPort 9051`

git pull this repo

install bucket brigade client
`python setup.py install`

run bucket_brigade once to generate config file
`bucekt_brigade`

open bucket brigade config (~/.bucket_brigade/config.json), and add the unhashed password:
"this is my password"

