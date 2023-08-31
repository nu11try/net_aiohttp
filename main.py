from aiohttp import web
import sqlite3
import datetime

app = web.Application()


def create_advertisement(conn, title, description, owner):
    current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO advertisements (title, description, created_at, owner)
        VALUES (?, ?, ?, ?)
    ''', (title, description, current_time, owner))
    conn.commit()


async def create_advertisement_handler(request):
    data = await request.json()
    title = data.get('title')
    description = data.get('description')
    owner = data.get('owner')

    if not title or not description or not owner:
        return web.json_response({'error': 'Missing fields'}, status=400)

    conn = request.app['db']
    create_advertisement(conn, title, description, owner)

    return web.json_response({'message': 'Advertisement created successfully'}, status=201)


async def get_advertisement_handler(request):
    ad_id = int(request.match_info['id'])

    conn = request.app['db']
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM advertisements WHERE id = ?', (ad_id,))
    advertisement = cursor.fetchone()

    if advertisement is None:
        return web.json_response({'error': 'Advertisement not found'}, status=404)

    ad_dict = {
        'id': advertisement[0],
        'title': advertisement[1],
        'description': advertisement[2],
        'created_at': advertisement[3],
        'owner': advertisement[4]
    }

    return web.json_response(ad_dict)


async def delete_advertisement_handler(request):
    ad_id = int(request.match_info['id'])

    conn = request.app['db']
    cursor = conn.cursor()
    cursor.execute('DELETE FROM advertisements WHERE id = ?', (ad_id,))
    conn.commit()

    return web.json_response({'message': 'Advertisement deleted successfully'})


app.add_routes([
    web.post('/advertisements', create_advertisement_handler),
    web.get('/advertisements/{id}', get_advertisement_handler),
    web.delete('/advertisements/{id}', delete_advertisement_handler)
])


async def init_db(app):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS advertisements (
            id INTEGER PRIMARY KEY,
            title TEXT,
            description TEXT,
            created_at TEXT,
            owner TEXT
        )
    ''')
    conn.commit()
    app['db'] = conn


async def close_db(app):
    app['db'].close()


app.on_startup.append(init_db)
app.on_cleanup.append(close_db)

if __name__ == '__main__':
    web.run_app(app)
