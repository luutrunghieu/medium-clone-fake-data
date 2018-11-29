from faker import Faker
from pymongo import MongoClient
from random import randint, sample
import datetime
from bson.objectid import ObjectId

client = MongoClient("mongodb://localhost:27017/")
db = client['medium-clone']
fake = Faker()


def fake_data():
  user_ids = []
  story_ids = []
  topics = ['design','marketing','languages','tech','science','culture','economic']
  features = [True, False]
  db.users.delete_many({})
  db.stories.delete_many({})

  # insert user
  for x in range(20):
    fullname = fake.first_name() + " " + fake.last_name()
    avatar = fake.image_url(width=100, height=100)
    bio = fake.job()
    written_stories = []
    followers = []
    following = []
    insertedUser = db.users.insert_one(
        {"fullname": fullname, "avatar": avatar, "bio": bio, "written_stories":written_stories, "followers": followers, "following": following}
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
    created_at = datetime.datetime(year,month,day)
    updated_at = created_at
    content = fake.text(max_nb_chars=1000, ext_word_list=None)
    insertedStory = db.stories.insert_one(
        {"title": title, "content": content, "topic": topic, "featured_image": featured_image, "author_id": author_id,"read_time":read_time, "featured":featured, "popular":popular, "reacted_user":reacted_user, "created_at":created_at,"updated_at":updated_at}
    )
    author = db.users.find_one({"_id":ObjectId(author_id)})
    author["written_stories"].append(insertedStory.inserted_id)
    db.users.update({"_id":ObjectId(author_id)},author)
  
  #update follwers, following
  for user_id in user_ids:
    following_ids = sample(user_ids, randint(1,20))
    follower = db.users.find_one({"_id":ObjectId(user_id)})
    follower['following'] = following_ids
    db.users.update({"_id":ObjectId(user_id)},follower)
    for following_id in following_ids:
      followee = db.users.find_one({"_id":ObjectId(following_id)})
      followee['followers'].append(user_id)
      db.users.update({"_id":ObjectId(following_id)},followee)
if __name__ == "__main__":
  fake_data()

