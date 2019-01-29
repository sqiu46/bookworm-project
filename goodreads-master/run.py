##https://github.com/sefakilic/goodreads/tree/master/goodreads


from goodreads import client
import time

gc = client.GoodreadsClient('88aqmuwFlnxichZaM5HQ', 'EuGsjtx6Xu66BOEFUzdQqZtNk1XgJKG6l2FOW3Bag')
gc.authenticate('jjh8PVDwzADWWVijUHKTPA', '0AoZhfh5s95KlkZQ0oTKWadzmuqlQniElhyGf6XGCU')

authId = gc.auth_user()
print(authId)

me = gc.user(authId)
# shelves = me.shelves()
# reviewsArr = (me.reviews())

# for review in reviewsArr:
# 	time.sleep(1.1)
# 	book = review.book
# 	print(book['title_without_series'])


def get_user_bookshelf(userID):
	user = gc.user(userID)
	reviews = user.reviews()
	for review in reviews:
		print("{0} gave {1} by {2} a score of : {3}".format(user.name, review.book['title'], (review.book['authors'])['author']['name'], review.rating))

get_user_bookshelf(authId)