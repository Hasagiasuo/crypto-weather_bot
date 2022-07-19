#---imports
import sqlite3


#---data base for weather
def create_db_weather():
  global dbs, curs
  dbs = sqlite3.connect('telebot_time/base_weather.db')
  curs = dbs.cursor()

  curs.execute("""
    CREATE TABLE IF NOT EXISTS main(
      ids INT,
      city TEXT
    )
  """)
  dbs.commit()


#---data base for crypto
def create_db_crypto():
  global db, cur
  db = sqlite3.connect('telebot_time/base_crypto.db')
  cur = db.cursor()

  cur.execute("""
    CREATE TABLE IF NOT EXISTS main(
      ids INT, 
      sell TEXT,
      crypto TEXT
    )
  """)
  db.commit()


#---add info into crypto
async def add_info_crypto(state):
  async with state.proxy() as data:
    db = sqlite3.connect('telebot_time/base_crypto.db')
    cur = db.cursor()
    cur.execute('INSERT INTO main VALUES (?, ?, ?)', tuple(data.values()))
    db.commit()


#---Update
async def add_info_crypto(state, id_user):
  async with state.proxy() as data:
    db = sqlite3.connect('telebot_time/base_crypto.db')
    cur = db.cursor()
    cur.execute(f'UPDATE main SET sell, name = "{tuple(data.values())}" WHERE ids = "{id_user}"')
    db.commit()


#---add info into weather
async def add_info_weather(state):
  async with state.proxy() as data:
    curs.execute('INSERT INTO main VALUES (?, ?)', tuple(data.values()))
    dbs.commit()

