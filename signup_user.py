import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import asyncio
import asyncpg


from tornado.options import define, options
define("port", default=8000, help="run on the given port", type=int)

# conn = asyncpg.connect(user='postgres', password='Ritesh', database='user_db', host='localhost', port=5432)
PORT = 8000


_pool = None


async def connect():
    global _pool
    _pool = await asyncpg.create_pool(
        host="localhost",
        user="postgres",
        password="Ritesh",
        database="user_db",
        port=5432,
        min_size=0,
        max_size=3
    )


class SignUp(tornado.web.RequestHandler):
    def get(self):
        greeting = self.get_argument('greeting', 'Hello')
        print("======================")
        self.render("signup.html", title="User Signup", items=greeting)
    
    async def post(self):
        fname = self.get_argument('fname')
        lname = self.get_argument('lname')
        email = self.get_argument('email')
        phone = self.get_argument('phone')
        address = self.get_argument('address')
        password = self.get_argument('password')
        print(fname, lname, email, phone, address, password)
        await connect()
        async with _pool.acquire() as connection:
            try:
                query = """INSERT INTO users(fname, lname, email, phone, address, password) VALUES ($1, $2, $3, $4, $5, $6);"""
                values = [
                     (fname, lname, email, phone, address, password)
                    ]
                print(values)
                result = await connection.executemany(query, values)
                print(".")
                self.render("signup.html", title="User Signup")
            except asyncpg.exceptions.ConnectionDoesNotExistError:
                print("asyncpg.exceptions.ConnectionDoesNotExistError")


class UserView(tornado.web.RequestHandler):
    async def get(self):
        await connect()
        async with _pool.acquire() as connection:
            try:
                data1 = await connection.fetch('SELECT * FROM users')
                # print(data1)
                self.render("view.html", title="View User", data= data1)
            except asyncpg.exceptions.ConnectionDoesNotExistError:
                print("asyncpg.exceptions.ConnectionDoesNotExistError")


class DeleteUser(tornado.web.RequestHandler):
    async def get(self, id):
        print(id)
        
        await connect()
        async with _pool.acquire() as connection:
            try:
                query = f"""DELETE FROM users WHERE id = ($1);"""
                values = [
                    (int(id),)
                    ]
                data1 = await connection.executemany(query, values)
                self.redirect("/")
            except asyncpg.exceptions.ConnectionDoesNotExistError:
                print("asyncpg.exceptions.ConnectionDoesNotExistError")
    


class EditUser(tornado.web.RequestHandler):
    async def get(self, id):
        await connect()
        async with _pool.acquire() as connection:
            try:
                data1 = await connection.fetch(f'SELECT * FROM users where id = {id}')
                print(data1)
                self.render("edit_file.html", title="View User", data= data1)
            except asyncpg.exceptions.ConnectionDoesNotExistError:
                print("asyncpg.exceptions.ConnectionDoesNotExistError")
    
    async def post(self,id):
        print(id)
        user_id = int(self.get_argument('user_id'))
        fname = self.get_argument('fname')
        lname = self.get_argument('lname')
        email = self.get_argument('email')
        phone = self.get_argument('phone')
        address = self.get_argument('address')
        print(user_id, fname, lname, email, phone, address)
        await connect()
        async with _pool.acquire() as connection:
            try:
                query = """UPDATE users
                            SET fname = $2, lname = $3, email= $4, phone=$5, address=$6
                            WHERE id = $1;"""
                values = [
                     (user_id, fname, lname, email, phone, address)
                    ]
                print(values)
                result = await connection.executemany(query, values)
                print(".")
                self.redirect("/")
            except asyncpg.exceptions.ConnectionDoesNotExistError:
                print("asyncpg.exceptions.ConnectionDoesNotExistError")        

    


if __name__ == "__main__":
    # main()
    tornado.options.parse_command_line()
    app = tornado.web.Application([
        (r"/", UserView), 
        (r"/signup", SignUp), 
        (r"/delete/([^/]+)?", DeleteUser),
        (r"/edit/([^/]+)?", EditUser)
        ])
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(PORT)
    tornado.ioloop.IOLoop.instance().start()