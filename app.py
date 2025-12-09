from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
import sqlite3
import random
from pathlib import Path
import shutil
import os

app = FastAPI()
dbpath = None
if os.environ["DEPLOY_ENV"] == "DEV":
	dbpath = "anime.db"
elif os.environ["DEPLOY_ENV"] == "PROD":
	dbpath = "/db/anime.db"

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

dbfile = Path(dbpath)
if not dbfile.is_file():
	prototype = Path("anime.db")
	os.makedirs(os.path.dirname(dbfile), exist_ok=True)
	shutil.copyfile(prototype, dbfile)

@app.get("/allanime")
async def get_all_anime():
	return {"message": get_anime_with_completion()}

@app.get("/anime/{anime_id}")
async def get_anime(anime_id):
	con = sqlite3.connect(dbfile)
	cur = con.cursor()
	anime_res = cur.execute("SELECT * FROM Anime WHERE AnimeId = ?", (anime_id,))
	anime_cols = tuple([col[0] for col in cur.description])
	anime_data = {"columns": anime_cols, "rows": anime_res.fetchall()}
	tags_res = cur.execute("""SELECT T.*
		FROM Anime A
			JOIN AnimeTag AT ON A.AnimeId = AT.AnimeId
			JOIN Tag T ON T.TagId = AT.TagId
		WHERE A.AnimeId = ?""", (anime_id,))
	tags_cols = tuple([col[0] for col in cur.description])
	tags_data = {"columns": tags_cols, "rows": tags_res.fetchall()}
	extras_res = cur.execute("""SELECT AE.*
		FROM Anime A JOIN AnimeExtra AE ON A.AnimeId = AE.AnimeId
		WHERE A.AnimeId = ?""", (anime_id,))
	extras_cols = tuple([col[0] for col in cur.description])
	extras_data = {"columns": extras_cols, "rows": extras_res.fetchall()}
	return {"message": {"anime": anime_data, "tags": tags_data, "extras": extras_data}}

@app.get("/randomanime")
async def get_random_anime():
	data = get_anime_with_completion()
	completion_index = data["columns"].index("Completion")
	filtered_data = [anime for anime in data["rows"] if anime[completion_index] == 0]
	index = random.randint(0, len(filtered_data))
	return {"message": filtered_data[index][0]}

@app.get("/tags/{anime_id}")
async def get_anime_tags(anime_id):
	con = sqlite3.connect(dbfile)
	cur = con.cursor()
	res = cur.execute("""SELECT T.*
		FROM Anime A
			JOIN AnimeTag AT ON A.AnimeId = AT.AnimeId
			JOIN Tag T ON T.TagId = AT.TagId
		WHERE A.AnimeId = ?""", (anime_id,))
	cols = tuple([col[0] for col in cur.description])
	data = {"columns": cols, "rows": res.fetchall()}
	return {"message": data}

@app.get("/extras/{anime_id}")
async def get_anime_extras(anime_id):
	con = sqlite3.connect(dbfile)
	cur = con.cursor()
	res = cur.execute("""SELECT AE.*
		FROM Anime A JOIN AnimeExtra AE ON A.AnimeId = AE.AnimeId
		WHERE A.AnimeId = ?""", (anime_id,))
	cols = tuple([col[0] for col in cur.description])
	data = {"columns": cols, "rows": res.fetchall()}
	return {"message": data}
	
@app.get("/sources")
async def get_sources():
	con = sqlite3.connect(dbfile)
	cur = con.cursor()
	res = cur.execute("SELECT * FROM Source")
	cols = tuple([col[0] for col in cur.description])
	data = {"columns": cols, "rows": res.fetchall()}
	return {"message": data}

@app.get("/tags")
async def get_tags():
	con = sqlite3.connect(dbfile)
	cur = con.cursor()
	res = cur.execute("SELECT * FROM Tag")
	cols = tuple([col[0] for col in cur.description])
	data = {"columns": cols, "rows": res.fetchall()}
	return {"message": data}
	
@app.get("/series")
async def get_series():
	con = sqlite3.connect(dbfile)
	cur = con.cursor()
	res = cur.execute("SELECT * FROM Series")
	cols = tuple([col[0] for col in cur.description])
	data = {"columns": cols, "rows": res.fetchall()}
	return {"message": data}

@app.get("/watchpartners")
async def get_watchpartners():
	con = sqlite3.connect(dbfile)
	cur = con.cursor()
	res = cur.execute("SELECT * FROM WatchPartner")
	cols = tuple([col[0] for col in cur.description])
	data = {"columns": cols, "rows": res.fetchall()}
	return {"message": data}
	
@app.get("/series/{series_id}")
async def get_single_series(series_id):
	con = sqlite3.connect(dbfile)
	cur = con.cursor()
	res = cur.execute("""
		SELECT S.SeriesId, S.Name, S.Notes, STRING_AGG(A.Title, '|') AS AnimeInSeries
		FROM Series S
			LEFT OUTER JOIN (SELECT * FROM Anime ORDER BY ReleaseDate) A ON A.SeriesId = S.SeriesId
		WHERE S.SeriesId = ?
		GROUP BY S.SeriesId, S.Name, S.Notes""", (series_id,))
	cols = tuple([col[0] for col in cur.description])
	data = {"columns": cols, "rows": res.fetchall()}
	return {"message": data}
	
@app.get("/watchthrough/{anime_id}/{partner_id}")
async def get_single_watchthrough(anime_id, partner_id):
	con = sqlite3.connect(dbfile)
	cur = con.cursor()
	select_query = """
		SELECT W.WatchthroughId, A.AnimeId, WP.Name AS WatchPartner, A.Title AS AnimeTitle, 
		W.Episode, W.Season, W.IsActive, W.ForceComplete, AE.Description AS AnimeExtra,
		AE.AnimeExtraId, CASE WHEN WAE.WatchthroughId IS NOT NULL THEN 1 ELSE 0 END As ExtraWatched
		FROM Watchthrough W
			JOIN WatchPartner WP ON W.WatchPartnerId = WP.WatchPartnerId
			JOIN Anime A ON W.AnimeId = A.AnimeId
			LEFT OUTER JOIN AnimeExtra AE ON W.AnimeId = AE.AnimeId
			LEFT OUTER JOIN WatchthroughAnimeExtra WAE ON W.WatchthroughId = WAE.WatchthroughId AND AE.AnimeExtraId = WAE.AnimeExtraId
		WHERE W.AnimeId = ? AND W.WatchPartnerId = ?"""
	res = cur.execute(select_query, (anime_id, partner_id))
	cols = tuple([col[0] for col in cur.description])
	rows = res.fetchall()
	if len(rows) == 0:
		cur.execute("INSERT INTO Watchthrough (WatchPartnerId, AnimeId, Episode, Season, IsActive, ForceComplete) VALUES (?, ?, 0, 0, 1, 0)", (partner_id, anime_id))
		con.commit()
		res = cur.execute(select_query, (anime_id, partner_id))
		rows = res.fetchall()
	data = {"columns": cols, "rows": rows}
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
	seriesId: int | None = None
	tags: list[int]
	extras: list[list]

@app.post("/saveanime")
async def save_anime(anime: Anime):
	con = sqlite3.connect(dbfile)
	cur = con.cursor()
	if anime.animeId is None:
		cur.execute("INSERT INTO Anime (Title, Notes, Review, YuriRatingId, ReleaseDate, LastSeason, LastEpisode, SourceId, Priority, SeriesId) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
			(anime.title, anime.notes, anime.review, anime.yuriRating, anime.releaseDate,
			anime.lastSeason, anime.lastEpisode, anime.source, anime.priority, anime.seriesId))
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
		cur.execute("UPDATE Anime SET Title=?, Notes=?, Review=?, YuriRatingId=?, ReleaseDate=?, LastSeason=?, LastEpisode=?, SourceId=?, Priority=?, SeriesId=? WHERE AnimeId=?",
			(anime.title, anime.notes, anime.review, anime.yuriRating, anime.releaseDate,
			anime.lastSeason, anime.lastEpisode, anime.source, anime.priority, anime.seriesId, anime.animeId))
		cur.execute("DELETE FROM AnimeTag WHERE AnimeId=?", (anime.animeId,))
		for tag_id in anime.tags:
			cur.execute("INSERT INTO AnimeTag (AnimeId, TagId) VALUES (?, ?)", (anime.animeId, tag_id))
		res = cur.execute("SELECT AnimeExtraId FROM AnimeExtra WHERE AnimeId = ?", (anime.animeId,))
		current_extra_ids = [extra[0] for extra in res.fetchall()]
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
		
class Series(BaseModel):
	seriesId: int | None = None
	name: str
	notes: str | None = None
	
@app.post("/saveseries")
async def save_series(series: Series):
	con = sqlite3.connect(dbfile)
	cur = con.cursor()
	if series.seriesId is None:
		cur.execute("INSERT INTO Series (Name, Notes) VALUES (?, ?)", (series.name, series.notes))
		con.commit()
		res = cur.execute("SELECT last_insert_rowid()")
		new_series_id = res.fetchone()[0]
		return {"message": new_series_id}
	else:
		cur.execute("UPDATE Series SET Name=?, Notes=? WHERE SeriesId = ?", (series.name, series.notes, series.seriesId))
		con.commit()
		return {"message": series.seriesId}

class WatchthroughCreate(BaseModel):
	animeId: int
	watchPartnerId: int

@app.post("/createwatchthrough")
async def create_watchthrough(watchthrough: WatchthroughCreate):
	con = sqlite3.connect(dbfile)
	cur = con.cursor()
	cur.execute("INSERT INTO Watchthrough (AnimeId, WatchPartnerId, IsActive, ForceComplete, Episode, Season) VALUES (?, ?, 1, 0, 0, 0)", (watchthrough.animeId, watchthrough.watchPartnerId))
	con.commit()
	res = cur.execute("SELECT last_insert_rowid()")
	new_watchthrough_id = res.fetchone()[0]
	return {"message": new_watchthrough_id}
		
class WatchthroughUpdate(BaseModel):
	watchthroughId: int
	isActive: bool
	episode: int
	season: int
	forceComplete: int
	completedExtras: list[int]
		
@app.post("/updatewatchthrough")
async def update_watchthrough(watchthrough: WatchthroughUpdate):
	con = sqlite3.connect(dbfile)
	cur = con.cursor()
	cur.execute("UPDATE Watchthrough SET IsActive = ?, Episode = ?, Season = ?, ForceComplete = ? WHERE watchthroughId = ?", (watchthrough.isActive, watchthrough.episode, watchthrough.season, watchthrough.forceComplete, watchthrough.watchthroughId))
	cur.execute("DELETE FROM WatchthroughAnimeExtra WHERE WatchthroughId = ?", (watchthrough.watchthroughId,))
	for completed_extra_id in watchthrough.completedExtras:
		cur.execute("INSERT INTO WatchthroughAnimeExtra (WatchthroughId, AnimeExtraId) VALUES (?, ?)", (watchthrough.watchthroughId, completed_extra_id))
	con.commit()
	return {"message": watchthrough.watchthroughId}
	
@app.get("/backup")
async def get_db_backup():
	return FileResponse(dbpath, media_type="application/octet-stream", filename="anime.db")

def get_anime_with_completion():
	con = sqlite3.connect(dbfile)
	cur = con.cursor()
	res = cur.execute("""
		SELECT DISTINCT A.AnimeId, A.Title, A.Review, A.Notes, A.YuriRatingId, A.ReleaseDate, 'S' || A.LastSeason || 'E' || A.LastEpisode AS LastEpisode,
			S.Name AS Source, S.SourceId, A.Priority, WP.WatchPartners, WPA.WatchPartnersActive, T.TagIds,
			CASE
				WHEN C1.WatchthroughId IS NOT NULL THEN 4
				WHEN C2.Season = A.LastSeason AND C2.Episode = A.LastEpisode THEN 3
				WHEN C2.Season > 1 OR A.LastSeason = 1 AND C2.Season = 1 AND C2.Episode = A.LastEpisode THEN 2
				WHEN C2.Season > 0 OR C2.Episode > 0 THEN 1
				ELSE 0
			END AS Completion
		FROM Anime A
			JOIN Source S ON A.SourceId = S.SourceId
			LEFT OUTER JOIN (SELECT DISTINCT W.*
						FROM Watchthrough W
							JOIN Anime A ON A.AnimeId = W.AnimeId
							LEFT OUTER JOIN Watchthrough W2 ON W.AnimeId = W2.AnimeId AND (W.ForceComplete * 1000000 + W.Season * 1000 + W.Episode) < (W.ForceComplete * 1000000 + W2.Season * 1000 + W2.Episode)
							LEFT OUTER JOIN AnimeExtra AE ON AE.AnimeId = W.AnimeId
							LEFT OUTER JOIN WatchthroughAnimeExtra WAE ON WAE.WatchthroughId = W.WatchthroughId AND AE.AnimeExtraId = WAE.AnimeExtraId
						WHERE (W2.WatchthroughId IS NULL AND (W.Episode >= A.LastEpisode AND W.Season >= A.LastSeason)) OR (W.ForceComplete = 1 AND W.WatchPartnerId = 1)
						GROUP BY W.WatchthroughId, W.WatchPartnerId, W.AnimeId, W.Episode, W.Season, W.IsActive, W.ForceComplete
						HAVING count(*) = sum(CASE WHEN WAE.WatchthroughId IS NOT NULL THEN 1 ELSE 0 END) OR (W.ForceComplete = 1 AND W.WatchPartnerId = 1)) C1 ON C1.AnimeId = A.AnimeId
			LEFT OUTER JOIN (SELECT DISTINCT W.*
						FROM Watchthrough W
							LEFT OUTER JOIN Watchthrough W2 ON W.AnimeId = W2.AnimeId AND (W.Season * 1000 + W.Episode) < (W2.Season * 1000 + W2.Episode)
							LEFT OUTER JOIN AnimeExtra AE ON AE.AnimeId = W.AnimeId
							LEFT OUTER JOIN WatchthroughAnimeExtra WAE ON WAE.WatchthroughId = W.WatchthroughId AND AE.AnimeExtraId = WAE.AnimeExtraId
						WHERE W2.WatchthroughId IS NULL) C2 ON C2.AnimeId = A.AnimeId
			LEFT OUTER JOIN (SELECT A.AnimeId, group_concat(W.WatchPartnerId) AS WatchPartners
						FROM Anime A
							JOIN Watchthrough W ON W.AnimeId = A.AnimeId
						GROUP BY A.AnimeId) WP ON A.AnimeId = WP.AnimeId
			LEFT OUTER JOIN (SELECT A.AnimeId, group_concat(W.WatchPartnerId) AS WatchPartnersActive
						FROM Anime A
							JOIN Watchthrough W ON W.AnimeId = A.AnimeId
						WHERE W.IsActive = 1
						GROUP BY A.AnimeId) WPA ON A.AnimeId = WPA.AnimeId
			LEFT OUTER JOIN (SELECT AT.AnimeId, group_concat(AT.TagId) AS TagIds
						FROM AnimeTag AT
						GROUP BY AT.AnimeId) T ON T.AnimeId = A.AnimeId
		ORDER BY CASE WHEN LOWER(Title) LIKE 'the %' THEN SUBSTR(LOWER(Title), 5) ELSE LOWER(Title) END""")
	cols = tuple([col[0] for col in cur.description])
	data = {"columns": cols, "rows": res.fetchall()}
	return data