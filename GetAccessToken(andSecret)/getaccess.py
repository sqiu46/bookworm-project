from rauth.service import OAuth1Service, OAuth1Session
# Get a real consumer key & secret from: https://www.goodreads.com/api/keys
CONSUMER_KEY = 'CMGnSCDuSnCKGc1srxhQUw'
CONSUMER_SECRET = 'r2YyJQRjPrVFSgfD36RmlK1Ynxi7fTfgVld9WWmc8'

goodreads = OAuth1Service(
    consumer_key=CONSUMER_KEY,
    consumer_secret=CONSUMER_SECRET,
    name='goodreads',
    request_token_url='https://www.goodreads.com/oauth/request_token',
    authorize_url='https://www.goodreads.com/oauth/authorize',
    access_token_url='https://www.goodreads.com/oauth/access_token',
    base_url='https://www.goodreads.com/'
    )

# head_auth=True is important here; this doesn't work with oauth2 for some reason
request_token, request_token_secret = goodreads.get_request_token(header_auth=True)
print(request_token)
print(request_token_secret)

authorize_url = goodreads.get_authorize_url(request_token)
print('Visit this URL in your browser: ' + authorize_url)
accepted = 'n'
while accepted.lower() == 'n':
    # you need to access the authorize_link via a browser,
    # and proceed to manually authorize the consumer
    accepted = raw_input('Have you authorized me? (y/n) ')
    
session = goodreads.get_auth_session(request_token, request_token_secret)

# book_id 631932 is "The Greedy Python"
data = {'name': 'to-read', 'book_id': 631932}

# add this to our "to-read" shelf
response = session.post('https://www.goodreads.com/shelf/add_to_shelf.xml', data)

# these values are what you need to save for subsequent access.
ACCESS_TOKEN = session.access_token
ACCESS_TOKEN_SECRET = session.access_token_secret
print(ACCESS_TOKEN)
print(ACCESS_TOKEN_SECRET)