from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sqlite3

app = FastAPI()

origins = [
	"*"
]

app.add_middleware(
	CORSMiddleware,
	allow_origins=origins,
	allow_credentials=True,
	allow_methods=["*"],
	allow_headers=["*"],
)

@app.get("/allanime")
async def get_all_anime():
	con = sqlite3.connect("anime.db")
	cur = con.cursor()
	res = cur.execute("SELECT AnimeId, Title, Notes, YuriRatingId, ReleaseDate, LastSeason, LastEpisode, SourceId, Priority FROM Anime")
	cols = tuple([col[0] for col in cur.description])
	data = {"columns": cols, "rows": res.fetchall()}
	return {"message": data}

@app.get("/anime/{anime_id}")
async def get_anime(anime_id):
	con = sqlite3.connect("anime.db")
	cur = con.cursor()
	anime_res = cur.execute("SELECT * FROM Anime WHERE AnimeId = ?", (anime_id))
	anime_cols = tuple([col[0] for col in cur.description])
	anime_data = {"columns": anime_cols, "rows": anime_res.fetchall()}
	tags_res = cur.execute("""SELECT T.*
		FROM Anime A
			JOIN AnimeTag AT ON A.AnimeId = AT.AnimeId
			JOIN Tag T ON T.TagId = AT.TagId
		WHERE A.AnimeId = ?""", (anime_id))
	tags_cols = tuple([col[0] for col in cur.description])
	tags_data = {"columns": tags_cols, "rows": tags_res.fetchall()}
	extras_res = cur.execute("""SELECT AE.*
		FROM Anime A JOIN AnimeExtra AE ON A.AnimeId = AE.AnimeId
		WHERE A.AnimeId = ?""", (anime_id))
	extras_cols = tuple([col[0] for col in cur.description])
	extras_data = {"columns": extras_cols, "rows": extras_res.fetchall()}
	return {"message": {"anime": anime_data, "tags": tags_data, "extras": extras_data}}

@app.get("/tags/{anime_id}")
async def get_anime_tags(anime_id):
	con = sqlite3.connect("anime.db")
	cur = con.cursor()
	res = cur.execute("""SELECT T.*
		FROM Anime A
			JOIN AnimeTag AT ON A.AnimeId = AT.AnimeId
			JOIN Tag T ON T.TagId = AT.TagId
		WHERE A.AnimeId = ?""", (anime_id))
	cols = tuple([col[0] for col in cur.description])
	data = {"columns": cols, "rows": res.fetchall()}
	return {"message": data}

@app.get("/extras/{anime_id}")
async def get_anime_extras(anime_id):
	con = sqlite3.connect("anime.db")
	cur = con.cursor()
	res = cur.execute("""SELECT AE.*
		FROM Anime A JOIN AnimeExtra AE ON A.AnimeId = AE.AnimeId
		WHERE A.AnimeId = ?""", (anime_id))
	cols = tuple([col[0] for col in cur.description])
	data = {"columns": cols, "rows": res.fetchall()}
	return {"message": data}
	
@app.get("/sources")
async def get_sources():
	con = sqlite3.connect("anime.db")
	cur = con.cursor()
	res = cur.execute("SELECT * FROM Source")
	cols = tuple([col[0] for col in cur.description])
	data = {"columns": cols, "rows": res.fetchall()}
	return {"message": data}

@app.get("/tags")
async def get_sources():
	con = sqlite3.connect("anime.db")
	cur = con.cursor()
	res = cur.execute("SELECT * FROM Tag")
	cols = tuple([col[0] for col in cur.description])
	data = {"columns": cols, "rows": res.fetchall()}
	return {"message": data}
	
class Anime(BaseModel):
	animeId: int | None = None
	title: str
	notes: str | None = None
	review: str | None = None
	yuriRating: int | None = None
	releaseDate: str
	lastSeason: int
	lastEpisode: int
	source: int
	priority: int
	tags: list[int]
	extras: list[list]

@app.post("/saveanime")
async def save_anime(anime: Anime):
	con = sqlite3.connect("anime.db")
	cur = con.cursor()
	if anime.animeId is None:
		cur.execute("INSERT INTO Anime (Title, Notes, Review, YuriRatingId, ReleaseDate, LastSeason, LastEpisode, SourceId, Priority) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
			(anime.title, anime.notes, anime.review, anime.yuriRating, anime.releaseDate,
			anime.lastSeason, anime.lastEpisode, anime.source, anime.priority))
		con.commit()
		res = cur.execute("SELECT last_insert_rowid()")
		new_anime_id = res.fetchone()[0]
		for tag_id in anime.tags:
			cur.execute("INSERT INTO AnimeTag (AnimeId, TagId) VALUES (?, ?)", (new_anime_id, tag_id))
		for extra in anime.extras:
			cur.execute("INSERT INTO AnimeExtra (AnimeId, Description) VALUES (?, ?)", (new_anime_id, extra[2]))
		con.commit()
		return {"message": new_anime_id}
	else:
		cur.execute("UPDATE Anime SET Title=?, Notes=?, Review=?, YuriRatingId=?, ReleaseDate=?, LastSeason=?, LastEpisode=?, SourceId=?, Priority=? WHERE AnimeId=?",
			(anime.title, anime.notes, anime.review, anime.yuriRating, anime.releaseDate,
			anime.lastSeason, anime.lastEpisode, anime.source, anime.priority, anime.animeId))
		cur.execute("DELETE FROM AnimeTag WHERE AnimeId=?", (anime.animeId,))
		for tag_id in anime.tags:
			cur.execute("INSERT INTO AnimeTag (AnimeId, TagId) VALUES (?, ?)", (anime.animeId, tag_id))
		res = cur.execute("SELECT AnimeExtraId FROM AnimeExtra WHERE AnimeId = ?", (anime.animeId,))
		current_extra_ids = [extra[0] for extra in res.fetchall()]
		print(current_extra_ids)
		new_extra_ids = [extra[0] for extra in anime.extras]
		for extra_id in current_extra_ids:
			if extra_id not in new_extra_ids:
				cur.execute("DELETE FROM AnimeExtra WHERE AnimeExtraId = ?", (extra_id,))
		for extra in anime.extras:
			if extra[0] is None:
				cur.execute("INSERT INTO AnimeExtra (AnimeId, Description) VALUES (?, ?)", (extra[1], extra[2]))
			else:
				cur.execute("UPDATE AnimeExtra SET Description = ? WHERE AnimeId = ? AND AnimeExtraId = ?", (extra[2], extra[1], extra[0]))
		con.commit()
		return {"message": anime.animeId}