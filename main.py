#---imports
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
import os
import datetime
import requests
import sqlite_base as sb
from token_bot import TOKEN, API
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.dispatcher import FSMContext
import sqlite3


#---add const
global dbs, curs
global db, cur
db = sqlite3.connect('telebot_time/base_crypto.db')
cur = db.cursor()
dbs = sqlite3.connect('telebot_time/base_weather.db')
curs = dbs.cursor()
storage = MemoryStorage()
bot = Bot(TOKEN)
dp = Dispatcher(bot, storage = storage)


#---keyboard
kb_start = ReplyKeyboardMarkup()
kb_weather = ReplyKeyboardMarkup()
kb_crypto = ReplyKeyboardMarkup()
kb_rem = ReplyKeyboardRemove()

#---buttons
b0 = KeyboardButton('/Exit')
b1 = KeyboardButton('/Crypto')
b2 = KeyboardButton('/Weather')
b3 = KeyboardButton('/Choose_my_city')
b4 = KeyboardButton('/Choose_main_crypto')
b5 = KeyboardButton('/Choose_crypto')
b6 = KeyboardButton('/Get_weather')
b7 = KeyboardButton('/Back')
b8 = KeyboardButton('/Weather_in_my_city')
b9 = KeyboardButton('/Cheak_price_my_crypto')


#---relise keyboard
kb_start.row(b1, b2).add(b0)
kb_crypto.row(b4, b5).add(b9).row(b0, b7)
kb_weather.row(b6, b3).add(b8).row(b0, b7)


#---class's
class Crypto(StatesGroup):
  ids = State()
  sell = State()
  crypto = State()

class Weather(StatesGroup):
  ids = State()
  city = State()

class Choose_crypto(StatesGroup):
  name = State()
  sell = State()

#---machine state(weather)
@dp.message_handler(commands = 'Choose_my_city', state = None)
async def start_weather(message: types.Message):
  await Weather.ids.set()
  await message.answer('Enter your city:', reply_markup = kb_rem)

@dp.message_handler(state = Weather.ids)
async def choose_my_city(message: types.Message, state = FSMContext):
  async with state.proxy() as data:
    data['ids'] = message.from_user.id
  await Weather.next()
  await message.answer('Enter city again:')

@dp.message_handler(state = Weather.city)
async def choose_my_city(message: types.Message, state = FSMContext):
  async with state.proxy() as data:
    data['city'] = message.text
  await sb.add_info_weather(state)
  await state.finish()
  await message.answer('Good, city added! \U00002714', reply_markup = kb_weather)


#---machine state(crypto)
@dp.message_handler(commands = 'Choose_main_crypto', state = None)
async def start_crypto(message: types.Message):
  await Crypto.ids.set()
  await message.answer('Enter main crypto (format iso 4217 code):')

@dp.message_handler(state = Crypto.ids)
async def get_id(message: types.Message, state: FSMContext):
  async with state.proxy() as data:
    data['ids'] = message.from_user.id
  await Crypto.next()
  await message.answer('Enter main crypto again (format iso 4217 code):')

@dp.message_handler(state = Crypto.sell)
async def what_is_the_price(message: types.Message, state: FSMContext):
  async with state.proxy() as data:
    data['sell'] = message.text
  await Crypto.next()
  await message.answer('Enter what is the price (format iso 4217 code):')

@dp.message_handler(state = Crypto.crypto)
async def choose_my_crypto(message: types.Message, state = FSMContext):
  async with state.proxy() as data:
    data['crypto'] = message.text
  await sb.add_info_crypto(state)
  await state.finish()
  await message.answer('Good, main crypto added! \U00002714', reply_markup = kb_crypto)


#---machine state(choose_crypto)
@dp.message_handler(commands = 'Choose_crypto', state = None)
async def start_choose(message: types.Message):
  await Choose_crypto.name.set()
  await message.answer('\U0001F58B Enter named crypto (format iso 4217 code) \U0001F58B', reply_markup = kb_rem)

@dp.message_handler(state = Choose_crypto.name)
async def choose_name_crypto(message: types.Message, state = FSMContext):
  async with state.proxy() as data:
    data['name'] = message.text
  await Choose_crypto.next()
  await message.answer('\U0001F58B Enter what is the price (format iso 4217 code) \U0001F58B')

@dp.message_handler(state = Choose_crypto.sell)
async def choose_sell_crypto(message: types.Message, state = FSMContext):
  async with state.proxy() as data:
    data['sell'] = message.text
  try:
    named = data['name']
    selled = data['sell']
    r = requests.get(url = f'https://yobit.net/api/3/ticker/{named}_{selled}')
    data = r.json()
    res = data.get(f'{named}_{selled}').get('avg')
    if selled == 'usd':
      re = data.get(f'{named}_{selled}').get('last')
      if re < res:
        await message.answer(f'Average price {named}: {round(res, 2)}$ \U0001F4B8\nPrice is falling \U0001F4C9', reply_markup = kb_crypto)
      elif re > res:
        await message.answer(f'Average price {named}: {round(res, 2)}$ \U0001F4B8\nPrice is growing \U0001F4C8', reply_markup = kb_crypto)
      else:
        await message.answer(f'Average price {named}: {round(res, 2)}$ \U0001F4B8\nPrice remained old \U0001F4CA', reply_markup = kb_crypto)
    else:
      re = data.get(f'{named}_{selled}').get('last')
      if re < res:
        await message.answer(f'Average price {named}: {round(res, 2)}$ \U0001FA99\nPrice is falling \U0001F4C9', reply_markup = kb_crypto)
      elif re > res:
        await message.answer(f'Average price {named}: {round(res, 2)}$ \U0001FA99\nPrice is growing \U0001F4C8', reply_markup = kb_crypto)
      else:
        await message.answer(f'Average price {named}: {round(res, 2)}$ \U0001FA99\nPrice remained old \U0001F4CA', reply_markup = kb_crypto)
    await state.finish()
  except Exception as error:
    await message.answer(f'[!]Opps.. {error}\nTry again \U0001F9D0', reply_markup = kb_crypto)


#---handlersв
@dp.message_handler(commands = 'start')
async def start(message: types.Message):
  await message.answer('Welcome \U0001F973\nWhat u choose?\nUsing keyboard \U0001F60E', reply_markup = kb_start)

@dp.message_handler(commands = 'Crypto')
async def start(message: types.Message):
  sb.create_db_crypto()
  await message.answer('\U0001F4B8 Welcome to crypto menu \U0001F4B8\nChoose point into keyboard \U0001F9FE', reply_markup = kb_crypto)

@dp.message_handler(commands = 'Weather')
async def start(message: types.Message):
  sb.create_db_weather()
  await message.answer('\U00002602 Welcome to weather menu \U00002602\nChoose point into keyboard \U0001F9FE', reply_markup = kb_weather)

@dp.message_handler(commands = 'Exit')
async def start(message: types.Message):
  await message.answer("As soon?\nIt's a pity \U0001F635\nBye \U0001F927", reply_markup = kb_rem)

@dp.message_handler(commands = 'Back')
async def start(message: types.Message):
  await message.answer('\U0001F47E Welcome again \U0001F47E\nUsing keyboard \U0001F913', reply_markup = kb_start)

@dp.message_handler(commands = 'Cheak_price_my_crypto')
async def start(message: types.Message):
  id_user = message.from_user.id
  cur.execute(f"SELECT crypto FROM main WHERE ids = '{id_user}'")
  sell_crypto = cur.fetchone()[0]
  cur.execute(f"SELECT sell FROM main WHERE ids = '{id_user}'")
  name_crypto = cur.fetchone()[0]
  r = requests.get(url = f'https://yobit.net/api/3/ticker/{name_crypto}_{sell_crypto}')
  data = r.json()
  avg = round(data.get(f'{name_crypto}_{sell_crypto}').get('avg'),2)
  high = round(data.get(f'{name_crypto}_{sell_crypto}').get('high'),2)
  low = round(data.get(f'{name_crypto}_{sell_crypto}').get('low'),2)
  last = round(data.get(f'{name_crypto}_{sell_crypto}').get('last'),2)
  buy = round(data.get(f'{name_crypto}_{sell_crypto}').get('buy'),2)
  await message.answer(f'Info for {name_crypto}:\nAverage price: {avg}$ \U0001F4B5\nHigh price: {high}$ \U00002197\nLow price: {low}$ \U00002198\nLast transaction: {last}$ \U000021A9\nBuy price: {buy}$ \U0001F4B8\nGood day \U0001F603')


@dp.message_handler(commands = 'Weather_in_my_city')
async def weather_in_my_city(message: types.Message):
  id_user = message.from_user.id
  curs.execute(f"SELECT city FROM main WHERE ids = '{id_user}'")
  cityd = curs.fetchone()[0]
  code_to_smile = {
    'Clear': 'Sun \U0001F31E',
    'Clouds': 'Clounds \U00002601',
    'Rain': 'Rain \U0001F327',
    'Brizzle': 'Brizzle \U0001F326',
    'Thundersthorm': 'Thundershtorm \U0001F329',
    'Snow': 'Snow \U0001F328',
    'Mist': 'Mist \U0001F32B'
  }
  try:
    r = requests.get(f'https://api.openweathermap.org/data/2.5/weather?q={cityd}&appid={API}&units=metric')
    data = r.json()
    type_weather = data['weather'][0]['main']
    temp_sity = data['main']['temp']
    humidity = data['main']['humidity']
    wind = data['wind']['speed']
    sunup = datetime.datetime.fromtimestamp(data['sys']['sunrise'])
    sundown = datetime.datetime.fromtimestamp(data['sys']['sunset'])
    time_now = datetime.datetime.now().strftime('%Y-%m-%d %H-%M')
    if type_weather in code_to_smile:
      wd = code_to_smile[type_weather]
    else:
      wd = 'Just look into window, i can`t know!'
    await message.answer(f'\U0001F55B {time_now} \U0001F55B\nSity: {cityd}\nTemp: {temp_sity} C° {wd}\nHumidity: {humidity}\nSunup: {sunup}\nSundown: {sundown}\nWind: {wind} m/s\n\n\U0001F47E Have a good day \U0001F47E')
  except:
    await message.answer('\U0001F6AB Error! Cheack name city! \U0001F6AB')


###---weather---
@dp.message_handler(commands = 'Get_the_weather')
async def weather(message: types.Message):
  await message.answer('Enter city and i`ll resend u inforamtion!')
  @dp.message_handler()
  async def get_weather(message: types.Message):
    code_to_smile = {
      'Clear': 'Sun \U0001F31E',
      'Clouds': 'Clounds \U00002601',
      'Rain': 'Rain \U0001F327',
      'Brizzle': 'Brizzle \U0001F326',
      'Thundersthorm': 'Thundershtorm \U0001F329',
      'Snow': 'Snow \U0001F328',
      'Mist': 'Mist \U0001F32B'
  }

    try:
      r = requests.get(f'https://api.openweathermap.org/data/2.5/weather?q={message.text}&appid={API}&units=metric')
      data = r.json()
      type_weather = data['weather'][0]['main']
      temp_sity = data['main']['temp']
      humidity = data['main']['humidity']
      wind = data['wind']['speed']
      sunup = datetime.datetime.fromtimestamp(data['sys']['sunrise'])
      sundown = datetime.datetime.fromtimestamp(data['sys']['sunset'])
      time_now = datetime.datetime.now().strftime('%Y-%m-%d %H-%M')
      if type_weather in code_to_smile:
        wd = code_to_smile[type_weather]
      else:
        wd = 'Just look into window, i can`t know!'
      await message.answer(f'\U0001F55B {time_now} \U0001F55B\nSity: {message.text}\nTemp: {temp_sity} C° {wd}\nHumidity: {humidity}\nSunup: {sunup}\nSundown: {sundown}\nWind: {wind} m/s\n\n\U0001F47E Have a good day \U0001F47E')
    except:
      await message.answer('\U0001F6AB Error! Cheack name city! \U0001F6AB')


#---start
if __name__ == '__main__':
  executor.start_polling(dp, skip_updates = True)