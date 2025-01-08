from faker import Faker
import random
import uuid

def generate_spotify_data(num_artists=5, albums_per_artist=3, songs_per_album=10):
    faker = Faker()
    
    data = []
    for _ in range(num_artists):
        artist = {
            "id": str(uuid.uuid4()),
            "name": faker.name(),
            "genre": random.choice(["Pop", "Rock", "Hip-Hop", "Jazz", "Classical", "Electronic", "R&B", "Reggae"]),
            "followers": faker.random_int(min=1000, max=1000000),
            "albums": []
        }
        for _ in range(albums_per_artist):
            album = {
                "id": str(uuid.uuid4()),
                "title": faker.catch_phrase(),
                "release_date": faker.date_time_this_year(), # faker.date_between(start_date='-10y', end_date='today'),
                "songs": []
            }
            for _ in range(songs_per_album):
                song = {
                    "id": str(uuid.uuid4()),
                    "title": faker.sentence(nb_words=3).strip("."),
                    "duration": random.randint(120, 300),  # Duration in seconds
                    "scrobbles": random.randint(1, 10000)
                }
                album["songs"].append(song)
            artist["albums"].append(album)
        data.append(artist)
    return data
