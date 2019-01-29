from rauth import OAuth1Service, OAuth1Session

from xml.etree import ElementTree

import time

import json

import sys

from goodreads import client





#Parse XML using ElementTree https://docs.python.org/2/library/xml.etree.elementtree.html

def get_auth_user_id(authSession):

	response = authSession.get('https://www.goodreads.com/api/auth_user')

	tree = ElementTree.fromstring(response.content)

	id = tree[1].attrib['id']

	return id



def API_get(authSession, formatUrl):

	response = authSession.get(formatUrl)

	data = ElementTree.fromstring(response.content)

	for elem in data.iter():

		print(elem.tag, elem.attrib)



def get_user_friends(friend_dict, authSession, user, n_pages):

	user = int(user)

	url = "https://www.goodreads.com/friend/user"

	#1 Second delay between API calls

	time.sleep(1);

	response = authSession.get(url, params={'format': 'xml', 'id': user, 'page': n_pages})

	lines = (line.decode('utf-8') for line in 

									response.content.splitlines())

	id_flag = 1

	author_flag = 0; #I hate XML, filter out open/close author flags

	for line in lines:

		#Open author tag

		if (not author_flag): 

			if ('authors' in line):

				author_flag = 1

			else:

			#print line.strip()

				if '<id>' in line.strip() and id_flag and ('work' not in line.strip()):

					#replace the close brackets so I can split along single delimiter

					temp = line.strip().replace('>','<').split('<');

					id = temp[2] if (temp[1] == 'id') else temp[4];

					id_flag = 0;

				elif '<name>' in line.strip() and not id_flag:

					name = line.strip().replace('>','<').split('<')[2]

					friend_dict[name] = int(id);

					id_flag = 1

		#Found matching, close off author tag

		elif (author_flag) and ("/authors" in line):

			author_flag = 0



def get_user_bookshelf(client, userID):

	user = client.user(userID)

	book_dict = {}

	#10 books per page

	for page in range(10):

		time.sleep(1);

		try: 

			reviews = user.reviews(page)

			for review in reviews:

				#print(review.book.keys())

				

				book_dict[review.book['title']] = {

								'user_rating': int(review.rating),

								'isbn' : review.book['isbn'],

								'isbn13': review.book['isbn13'],

								'avg_rating': review.book['average_rating'],

								'description': review.book['description']

									}

		except:

			break



			#print("{0} gave {1} by {2} a score of : {3}".format(user.name, review.book['title'], (review.book['authors'])['author']['name'], review.rating))

	return (book_dict)



def build_user_dict(START, GLOBAL_COUNT, FULL_DICT, authSession, client, root_user_array):

	try:

		

		# Get the list of all friends of the root_user_array

		global_friends_array = []



		for suser in root_user_array:

			try:

				#print("before client")

				user = client.user(suser)

				

				#print("before bookshelf: " + str(user.name))



				# Getting user dict

				user_dict = {}

				user_dict['name'] = user.name

				user_dict['books'] = get_user_bookshelf(client, user)

				#print("-- No. of books grabbed: {}".format(len(user_dict['book_ratings'])))



				#print("after bookshelf: " + str(user.name))



				#print("before get friends: " + str(user.name))

				# Getting friend dict

				friend_dict = {}

				#3 pages of max(30) should be fine for our purposes

				for n_pages in range(3):

					get_user_friends(friend_dict, authSession, user.gid, n_pages)

				#print("-- No. of friends grabbed: {}".format(len(friend_dict)))

				user_dict['friends'] = friend_dict



				#print("after get friends: " + str(user.name))





				#print("before profile url: " + str(user.name))



				# Adding data point into the FULL_DICT

				GLOBAL_COUNT += len(user_dict['friends'])

				user_dict['profile_image'] = user.image_url



				#print("before profile url: " + str(user.name))



				FULL_DICT[user.gid] = user_dict



				# Setting the global_friends_array

				for friend, friendid in friend_dict.items():



					if friendid not in FULL_DICT:

						#print(friend + " : " + str(friendid))

						global_friends_array.append(friendid)





				# print("Logged friends and books of {}".format(root_user.name))

				# print("Current data dump size: {}".format(len(FULL_DICT)))

				

				elapsed = time.perf_counter()-START

				print("Logged: {} >>datapoints: {} >> elapsed: {:.2f}".format(user.name, len(FULL_DICT), elapsed))



			except KeyboardInterrupt:

				print("Interrupted, writing data")

				try:

					with open('dat.json', 'r') as r_file:

						data = json.load(r_file)

					data.update(FULL_DICT)

					with open('dat.json', 'w+') as w_file:

						json.dump(data, w_file)

					print("File contains ({}) users".format(len(data)))

				#first write, file doesn't exist

				except FileNotFoundError:

					with open('dat.json', 'w+') as w_file:

						json.dump(FULL_DICT, w_file)		



			except:

				#print("Unable to read values... skipping {}".format(root_user.name))

				#print(suser)

				#print(user.name)

				pass





		#print(global_friends_array)

		build_user_dict(START, GLOBAL_COUNT, FULL_DICT, authSession, client, global_friends_array)

	





	except KeyboardInterrupt:

		print("Interrupted, writing data")

		try:

			with open('dat.json', 'r') as r_file:

				data = json.load(r_file)

			data.update(FULL_DICT)

			with open('dat.json', 'w+') as w_file:

				json.dump(data, w_file)

			print("File contains ({}) users".format(len(data)))

		#first write, file doesn't exist

		except FileNotFoundError:

			with open('dat.json', 'w+') as w_file:

				json.dump(FULL_DICT, w_file)		



	except:

		#print("Unable to read values... skipping {}".format(root_user.name))

		pass



def main():



	#This is my developer key and secret. Hopefully it doesn't get blacklisted for so many API requests lol



	CONSUMER_KEY = "CMGnSCDuSnCKGc1srxhQUw"

	CONSUMER_SECRET = "r2YyJQRjPrVFSgfD36RmlK1Ynxi7fTfgVld9WWmc8"

	ACCESS_TOKEN = 'AnRyRnliP7WsNoCA3NaZw'

	ACCESS_TOKEN_SECRET = 'R1rEGz1Hq11YrFI4sG4WdjS6trOabu7M4G42Qrml9g'

	ouath = OAuth1Session(

		consumer_key=CONSUMER_KEY,

		consumer_secret=CONSUMER_SECRET,

		access_token = ACCESS_TOKEN,

		access_token_secret = ACCESS_TOKEN_SECRET,

	)



	gc = client.GoodreadsClient('CMGnSCDuSnCKGc1srxhQUw', 'r2YyJQRjPrVFSgfD36RmlK1Ynxi7fTfgVld9WWmc8')

	gc.authenticate('AnRyRnliP7WsNoCA3NaZw', 'R1rEGz1Hq11YrFI4sG4WdjS6trOabu7M4G42Qrml9g')



	authId = gc.auth_user()

	#ROOT_USER = gc.user(sys.argv[1])

	ROOT_USER = gc.user(authId)



	GLOBAL_COUNT = 0

	big_dict = {}

	START = time.perf_counter()

	build_user_dict(START, GLOBAL_COUNT, big_dict, ouath, gc, [ROOT_USER.gid])

	print("Finished building, writing json object")

	try:

		with open('dat.json', 'r') as r_file:

			data = json.load(r_file)

		data.update(big_dict)

		with open('dat.json', 'w+') as w_file:

			json.dump(data, w_file)

		print("File contains ({}) users".format(len(data)))

	#first write, file doesn't exist

	except FileNotFoundError:

		with open('dat.json', 'w+') as w_file:

			json.dump(big_dict, w_file)

			print("Saved {} users".format(len(big_dict)))





if __name__ == "__main__":

	main()

