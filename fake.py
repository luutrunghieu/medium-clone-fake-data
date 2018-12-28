from faker import Faker
from pymongo import MongoClient
from random import randint, sample
from datetime import datetime, timedelta
from bson.objectid import ObjectId
import sys

env = sys.argv[1]
if env == 'production':
  storyClient = MongoClient("mongodb://35.240.184.156:27017/")
  userClient = MongoClient("mongodb://35.221.160.168:27017/")  
else:
  storyClient = MongoClient("mongodb://localhost:27018/")
  userClient = MongoClient("mongodb://localhost:27017/")

fake = Faker()
storyDb = storyClient['medium-clone']
userDb = userClient['medium-clone']

def fake_data():
  user_ids = []
  story_ids = []
  topics = ['design','marketing','languages','technology','science','culture','economic']
  features = [True, False]
  userDb.users.delete_many({})
  storyDb.stories.delete_many({})

  # insert user
  for x in range(20):
    fullname = fake.first_name() + " " + fake.last_name()
    avatar = fake.image_url(width=100, height=100)
    bio = fake.job()
    written_stories = []
    followers = []
    following = []
    google_id = fake.sha256(raw_output=False)
    access_token = fake.sha256(raw_output=False)
    insertedUser = userDb.users.insert_one(
        {"fullname": fullname, "avatar": avatar, "bio": bio, "written_stories":written_stories, "followers": followers, "following": following, "google_provider":{"id": google_id, "token":access_token}}
    )
    user_ids.append(str(insertedUser.inserted_id))

  # insert stories
  for x in range(400):
    title = fake.sentence(nb_words=10)
    topic = sample(topics,2)
    featured_image = fake.image_url(width=100, height=100)
    author_id = user_ids[randint(0,19)]
    read_time = randint(1,15)
    featured = features[randint(0,1)]
    popular = features[randint(0,1)]
    reacted_user = sample(user_ids, randint(1,20))
    year = randint(2016,2017)
    month = randint(1,12)
    if(month == 2):
      day = randint(1,28)
    else:
      day = randint(1,30)
    created_at = datetime(year,month,day)
    updated_at = created_at
    content = fake.text(max_nb_chars=1000, ext_word_list=None)
    number_of_comments = randint(0,5)
    comments = []
    for y in range(number_of_comments):
      comment = {}
      comment['content'] = fake.sentence(nb_words=10)
      comment['author_id'] = sample(user_ids, 1)[0]
      comment['created_at'] = created_at + timedelta(days=1)
      comments.append(comment)
    insertedStory = storyDb.stories.insert_one(
        {"title": title, "content": content, "topics": topic, "featured_image": featured_image, "author_id": author_id,"read_time":read_time, "featured":featured, "popular":popular, "reacted_user":reacted_user, "created_at":created_at,"updated_at":updated_at, "comments":comments}
    )
    author = userDb.users.find_one({"_id":ObjectId(author_id)})
    author["written_stories"].append(insertedStory.inserted_id)
    userDb.users.update({"_id":ObjectId(author_id)},author)
  
  #update follwers, following
  for user_id in user_ids:
    following_ids = sample(user_ids, randint(1,20))
    follower = userDb.users.find_one({"_id":ObjectId(user_id)})
    follower['following'] = following_ids
    userDb.users.update({"_id":ObjectId(user_id)},follower)
    for following_id in following_ids:
      followee = userDb.users.find_one({"_id":ObjectId(following_id)})
      followee['followers'].append(user_id)
      userDb.users.update({"_id":ObjectId(following_id)},followee)
if __name__ == "__main__":
  fake_data()

