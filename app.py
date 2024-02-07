from flask import Flask, render_template, request,jsonify, url_for, flash, redirect, session # flask: like library, python programme, connects frontend & backend
import sqlite3 #library that connects python & database
import bcrypt
from datetime import timedelta, datetime
from helper import haiku_is_standard, is_acroustic, is_sonnet, isSimilar_theme
from profanity import profanity
from textblob import TextBlob

app = Flask(__name__)
app.secret_key = "randommessage"
session = {} # if user logins, session = {"username" : "test2"}; if user x login, session = {}
app.permanent_session_lifetime = timedelta(seconds=3600)


@app.route('/', methods=['GET']) # / => main homepage; decorator
def index(): #index func calls render_template, showing login.html on website
	isLogin = False
	if "username" in session:
		isLogin = True
	return render_template('index.html', isLogin = isLogin) # html var = python var
@app.route('/bwrite', methods=['GET']) # / => main homepage; decorator
def bwrite(): #index func calls render_template, showing login.html on website
	isLogin = False
	if "username" in session:
		isLogin = True
	else:
		return redirect(url_for('login'))
	return render_template('bwrite.html', isLogin = isLogin) # html var = python var
@app.route('/mypage', methods=['GET']) # / => main homepage; decorator
def mypage(): #index func calls render_template, showing login.html on website
	isLogin = False

	if request.method == "POST":
		pass
	else:
		isLogin = True
		conn = sqlite3.connect('static/database.db')
		cursor = conn.cursor()

		# Modify your query to join Poem with Likes
		query = """
			SELECT P.username, P.content, P.date, P.title, P.type,P.id,
				   COALESCE(L.liked, 0) AS liked
			FROM Poem P
			LEFT JOIN Likes L ON P.id = L.poem_id AND L.username = ?
		"""
		cursor.execute(query, (session.get("username"),))
		rows = cursor.fetchall()

		usernames = []  # ["scott", "alice"]
		contents = []  # ["poem...", "poem2..."]
		dates = []  # ["2023-12-12", "2022-10-10"]
		titles = []
		types = []
		likes = []
		ids = []

		for row in rows:
			usernames.append(row[0])
			contents.append(row[1])
			dates.append(row[2])
			titles.append(row[3])
			types.append(row[4].title())
			likes.append(row[6])

			ids.append(row[5])
		print(likes)
		print(ids)
		if "username" not in session:
			isLogin = False
			return redirect(url_for('login'))
		else:
			isLogin = True

		return render_template('mypage.html',ids=ids, usernames=usernames, contents=contents,
							   dates=dates, titles=titles, types=types, liked_status=likes,
							   num_poems=len(usernames), isLogin=isLogin, username = session["username"])
def username_exists(username):
	conn = sqlite3.connect('static/database.db')
	cursor = conn.cursor()
	cursor.execute("Select * from Users where username=?",(username,))
	# * => select (bringing all columns)
	result = cursor.fetchone() #result=none if x exist
	conn.close()
	return result is not None #return False if result is None, True otherwise.

@app.route('/signup', methods=['GET','POST'])
def signup():
	if request.method == "POST":
		username = request.form.get("username") #username: python, "username": html
		password = request.form.get("password")
		repassword = request.form.get("repassword")
		first_name = request.form.get("firstname")
		last_name = request.form.get("lastname")
		email = request.form.get("email")

		password = password.encode('utf-8') # changing to bit (binary #: 0, 1); encoding into computer lang
		salt = bcrypt.gensalt() # making salt (adding certain val so that hacker can't access pw after hacking)
		hashed_password = bcrypt.hashpw(password, salt) # using above 2 lines to encrypt

		if username_exists(username):
			flash("Username already exists.") #sending to frontend
		else: #if there is no username which user is trying to register w/
			#connecting to database
			conn = sqlite3.connect("static/database.db")
			cursor = conn.cursor() #명령 to database, needed to execute; conn: db, cursor: 명령
			#				Insert data into table Users (column names); (?) -> python variables
			cursor.execute("Insert INTO USERS (username, password, first_name, last_name, email) VALUES (?,?,?,?,?)",(username,hashed_password,first_name,last_name,email)) #USERS: table name
			conn.commit() #write changes; saving
			conn.close() #disconnecting with the database bc x need db anymore
			return render_template('login.html') # returning to homepage (login page)
		return render_template('signup.html')

	else: #GET
		if "username" in session: #session = {}
			return redirect(url_for('index'))
		return render_template('signup.html') #render_template imported, finds signup.html file (app.py를 기준으로 template folder안에있는걸 찾는거)

def check_password(username, password):
	conn = sqlite3.connect('static/database.db')
	cursor = conn.cursor()
	cursor.execute("Select password from Users where username=?",(username,))
	real_password = cursor.fetchone() #[0] bc returns list
	conn.close()

	if real_password is None:
		return False
	else:
		real_password = real_password[0]

	if password == real_password:
		return True
	else:
		return False

@app.route('/login', methods=['GET','POST'])
def login():
	if request.method == "POST": #submitting
		username = request.form.get("username")
		password = request.form.get("password")
		input_password = password.encode('utf-8')
		conn = sqlite3.connect('static/database.db')
		cursor = conn.cursor()
		cursor.execute("Select password from Users where username=?", (username,)) # cursor -> ()
		hashed_password = cursor.fetchone() # (1234,)
		if hashed_password is None: # when input username is x in DB
			flash("Invalid username or password!")
			return render_template('login.html')

		hashed_password = hashed_password[0]
		conn.close()

		if bcrypt.checkpw(input_password, hashed_password): # 1010 == 1010
			session["username"] = username # session = {"username": test1}
			login_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

			conn = sqlite3.connect('static/database.db')
			cursor = conn.cursor()
			cursor.execute("INSERT INTO Login_logs (username, date) VALUES (?, ?)", (username, login_date))
			conn.commit()
			conn.close()
			return redirect(url_for('index')) #index = homepage
		else:
			flash("Invalid username or password!")
			return render_template('login.html')
	else: #if method == GET #accessing login page
		if "username" in session:
			return redirect(url_for('index'))
		return render_template('login.html')

@app.route('/logout', methods=['GET']) # if user presses /logout
def logout():
	session.clear()
	return redirect(url_for('login')) # sends user to /login


@app.route('/tube', methods=['GET']) # if user presses /logout
def tube():
	isLogin = False
	if "username" in session:
		isLogin = True
	return render_template('tube.html', isLogin = isLogin) # html var = python var




def contains_profanity(text):
	return profanity.contains_profanity(text)
@app.route('/poem_writing_haiku', methods=['GET', 'POST'])
def poem_writing_haiku():
	isLogin = False
	lines = []
	title = ""

	if request.method == "POST":
		isLogin = True
		lines = request.form.getlist("line") #[line1,line2,line3]
		title = request.form.get('title')
		if not isSimilar_theme(title,lines):
			isMatch = True
			flash("Wrong!")
			return render_template('poem_writing_haiku.html', isLogin=isLogin, lines=lines, title=title, isMatch=isMatch)

		for line in lines:
			if contains_profanity(line):
				isBad = True
				flash("Wrong!")
				return render_template('poem_writing_haiku.html', isLogin=isLogin, lines=lines, title=title,isBad=isBad)


		result = haiku_is_standard(lines)
		if result:
			username = session["username"]
			content = "\n".join(lines)  # "line1\nline2\nline3\n"
			today_date = datetime.today()
			conn = sqlite3.connect("static/database.db")
			title = request.form.get('title')
			cursor = conn.cursor()
			type = "haiku"

			cursor.execute('SELECT MAX(id) FROM Poem')

			largest_id = cursor.fetchone()[0]
			cursor.execute("Insert INTO Poem (username, content, date,title,type,id,numLikes) VALUES (?,?,?,?,?,?,?)",
						   (username, content, today_date, title, type, largest_id + 1,0))
			conn.commit()
			conn.close()

			return redirect(url_for('board'))
		else:
			isSyll = True
			flash("Wrong!")
			return render_template('poem_writing_haiku.html', isLogin=isLogin, lines=lines, title=title,isSyll=isSyll)


	else:
		if "username" not in session:
			return redirect(url_for('login'))
		else:
			isLogin = True

	return render_template('poem_writing_haiku.html', isLogin=isLogin, lines=lines, title=title)

@app.route('/poem_writing_free', methods=['GET','POST'])
def poem_writing_free():
	isLogin = False
	if request.method == "POST":
		isLogin=True
		lines = request.form.getlist("line") #["line1", "line2","line3"]
		title = request.form.get("theme")
		if not isSimilar_theme(title,lines):
			isMatch = True
			flash("Wrong!")
			return render_template('poem_writing_free.html', isLogin=isLogin, lines=lines, title=title, isMatch=isMatch)

		for line in lines:
			if contains_profanity(line):
				isBad = True
				flash("Wrong!")
				return render_template('poem_writing_free.html', isLogin=isLogin, lines=lines, title=title,isBad=isBad)

		username = session["username"]
		content = "\n".join(lines) # "line1\nline2\nline3\n"
		today_date = datetime.today()
		conn = sqlite3.connect("static/database.db")
		cursor = conn.cursor()
		type = "free"
		cursor.execute('SELECT MAX(id) FROM Poem')

		largest_id = cursor.fetchone()[0]
		sentiment = get_sentiment(' '.join(lines))
		cursor.execute("Insert INTO Poem (username, content, date,title,type,id,numLikes,sentiment) VALUES (?,?,?,?,?,?,?,?)",
					   (username, content, today_date, title, type, largest_id + 1,0,sentiment))
		conn.commit()
		conn.close()
		return redirect(url_for('index'))
	else:
		if "username" not in session:
			return redirect(url_for('login'))
		else:
			isLogin=True
		return render_template('poem_writing_free.html',isLogin=isLogin)

@app.route('/like_poem', methods=['POST'])
def like_poem():
	data = request.json
	username = session.get("username")
	poem_id = data.get('poem_id')
	liked_status = data.get('liked')

	if username:
		conn = sqlite3.connect("static/database.db")
		cursor = conn.cursor()

		try:
			cursor.execute("SELECT * FROM Likes WHERE username = ? AND poem_id = ?", (username, poem_id))
			existing_like_entry = cursor.fetchone()

			if existing_like_entry:
				cursor.execute("UPDATE Likes SET liked = ? WHERE username = ? AND poem_id = ?",
							   (int(liked_status), username, poem_id))
			else:
				cursor.execute("INSERT INTO Likes (username, poem_id, liked) VALUES (?, ?, ?)",
							   (username, poem_id, int(liked_status)))

			if liked_status == 1:
				cursor.execute("UPDATE Poem SET numLikes = numLikes + 1 WHERE id = ?", (poem_id,))
			else:
				cursor.execute("UPDATE Poem SET numLikes = numLikes - 1 WHERE id = ?", (poem_id,))

			conn.commit()

			cursor.execute("SELECT numLikes FROM Poem WHERE id = ?", (poem_id,))
			updated_like_count = cursor.fetchone()[0]

			return jsonify({'success': True, 'like_count': updated_like_count})

		except sqlite3.Error as e:
			conn.rollback()
			return jsonify({'success': False, 'error': str(e)})

		finally:
			conn.close()
	else:
		return jsonify({'success': False, 'error': 'User not logged in'})


# @app.route('/poem_writing_sonnet', methods=['GET','POST'])
# def poem_writing_sonnet():
# 	if "username" not in session:
# 		return redirect(url_for('login'))
# 	return render_template("poem_writing_sonnet.html")
def get_sentiment(text):
	blob = TextBlob(text)

	polarity = blob.sentiment.polarity

	if polarity > 0:
		return 1  # Positive sentiment
	elif polarity == 0:
		return 0  # Neutral sentiment
	else:
		return -1  # Negative sentiment
def execute_query(query, params=None, fetchone=False):
	conn = sqlite3.connect('static/database.db')
	cursor = conn.cursor()

	if params:
		cursor.execute(query, params)
	else:
		cursor.execute(query)

	if fetchone:
		result = cursor.fetchone()
	else:
		result = cursor.fetchall()

	conn.commit()
	conn.close()

	return result
@app.route('/add_comment', methods=['POST'])
def add_comment():
	data = request.get_json()
	poem_id = data.get('poem_id')
	comment_text = data.get('text')
	username = session['username']
	query = "INSERT INTO Comment (username, comment, poem_id, date) VALUES (?, ?, ?, ?)"
	params = (username, comment_text, poem_id, datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'))
	execute_query(query, params)


	return jsonify({'comment': {'username': username, 'text': comment_text, 'date': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}})


@app.route('/get_comments/<poem_id>')
def get_comments(poem_id):
    # Retrieve comments for the specified poem_id from the Comment table
    query = "SELECT username, comment, date FROM Comment WHERE poem_id = ?"
    params = (poem_id,)
    comments = execute_query(query, params, fetchone=False)

    formatted_comments = []
    for comment in comments:
        # Format the comment based on the username
        username, text, date = comment  # Unpack the tuple
        if username == 'admin':
            formatted_comment = {'username': f'<span class="bi bi-shield-fill"></span> <strong>{username}</strong>', 'text': text, 'date': date}
        else:
            formatted_comment = {'username': username, 'text': text, 'date': date}

        formatted_comments.append(formatted_comment)

    return jsonify({'comments': formatted_comments})

@app.route('/poem_writing_acrostic', methods=['GET', 'POST'])
def poem_writing_acrostic():
	isLogin = False
	lines = []
	title = ""

	if request.method == "POST":
		isLogin = True
		lines = request.form.getlist("line")
		title = request.form.get('theme')
		for i in lines:
			if len(lines) == len(title) and len(i) == 0:
				isLine = True
				print(lines)
				flash("Wrong!")
				return render_template('poem_writing_sonnet.html', isLogin=isLogin, lines=lines, title=title,
									   isLine=isLine)
		if not isSimilar_theme(title,lines):
			isMatch = True
			flash("Wrong!")
			return render_template('poem_writing_acrostic.html', isLogin=isLogin, lines=lines, title=title, isMatch=isMatch)

		for line in lines:
			if contains_profanity(line):
				isBad = True
				flash("Wrong!")
				return render_template('poem_writing_acrostic.html', isLogin=isLogin, lines=lines, title=title,isBad=isBad)

		result = is_acroustic(title,lines)
		if result:
			username = session["username"]
			content = "\n".join(lines)  # "line1\nline2\nline3\n"
			today_date = datetime.today()
			conn = sqlite3.connect("static/database.db")
			title = request.form.get('theme')
			cursor = conn.cursor()
			type = "acrostic"

			cursor.execute('SELECT MAX(id) FROM Poem')
			sentiment = get_sentiment(' '.join(lines))
			largest_id = cursor.fetchone()[0]

			cursor.execute("Insert INTO Poem (username, content, date,title,type,id,numLikes,sentiment) VALUES (?,?,?,?,?,?,?,?)",
						   (username, content, today_date, title, type, largest_id + 1,0,sentiment))
			conn.commit()
			conn.close()

			return redirect(url_for('board'))
		else:
			isWrong = True
			flash("Wrong!")
			print("TESSSS")
			print(isWrong)
			return render_template('poem_writing_acrostic.html', isLogin=isLogin, lines=lines, title=title, isWrong = isWrong)
	else:
		if "username" not in session:
			return redirect(url_for('login'))
		else:
			isLogin = True

	return render_template('poem_writing_acrostic.html', isLogin=isLogin, lines=lines, title=title)


@app.route('/poem_writing_sonnet', methods=['GET', 'POST'])
def poem_writing_sonnet():
	isLogin = False
	lines = []
	title = ""

	if request.method == "POST":
		isLogin = True
		lines = request.form.getlist("line")
		print(lines)
		for i in lines:
			if len(i) == 0:
				isLine = True
				flash("Wrong!")
				return render_template('poem_writing_sonnet.html', isLogin=isLogin, lines=lines, title=title,
									   isLine=isLine)

		title = request.form.get('theme')

		if not isSimilar_theme(title,lines):
			isMatch = True
			flash("Wrong!")
			return render_template('poem_writing_sonnet.html', isLogin=isLogin, lines=lines, title=title, isMatch=isMatch)

		for line in lines:
			if contains_profanity(line):
				isBad = True
				flash("Wrong!")
				return render_template('poem_writing_sonnet.html', isLogin=isLogin, lines=lines, title=title,isBad=isBad)

		result = is_sonnet(lines)
		if result:
			username = session["username"]
			content = "\n".join(lines)  # "line1\nline2\nline3\n"
			today_date = datetime.today()
			conn = sqlite3.connect("static/database.db")
			title = request.form.get('title')
			cursor = conn.cursor()
			type = "sonnet"

			cursor.execute('SELECT MAX(id) FROM Poem')

			largest_id = cursor.fetchone()[0]
			sentiment = get_sentiment(' '.join(lines))
			cursor.execute("Insert INTO Poem (username, content, date,title,type,id,numLikes,sentiment) VALUES (?,?,?,?,?,?,?,?)",
						   (username, content, today_date, title, type, largest_id + 1,0,sentiment))
			conn.commit()
			conn.close()

			return redirect(url_for('board'))
		else:
			flash("Wrong!")
			isWrong = True
			return render_template('poem_writing_sonnet.html', isLogin=isLogin, lines=lines, title=title, isWrong=isWrong)


	else:
		if "username" not in session:
			return redirect(url_for('login'))
		else:
			isLogin = True

	return render_template('poem_writing_sonnet.html', isLogin=isLogin, lines=lines, title=title)
# @app.route('/poem_writing_acrostic', methods=['GET', 'POST'])
# def poem_writing_acrostic():
# 	if request.method == "POST":
# 		lines = request.form.getlist("lines") #["line1", "line2","line3"]
# 		theme = request.form.get('theme')
# 		result = is_acroustic(theme,lines)
# 		if result:
# 			username = session["username"]
# 			content = "\n".join(lines) # "line1\nline2\nline3\n"
# 			today_date = datetime.today()
# 			conn = sqlite3.connect("static/database.db")
# 			cursor = conn.cursor()
# 			type = "acrostic"
# 			cursor.execute("Insert INTO Poem (username, content, date, type) VALUES (?,?,?,?)",(username,content,today_date, type))
# 			conn.commit()
# 			conn.close()
#
# 			return redirect(url_for('index'))
# 		else:
# 			flash("Wrong!")
# 			return render_template('poem_writing_acrostic.html')
#
# 	else:
# 		if "username" not in session:
# 			return redirect(url_for('login'))
# 		return render_template('poem_writing_acrostic.html')
@app.route("/board", methods=['GET', 'POST'])
def board():
	isLogin = False

	if request.method == "POST":
		pass
	else:
		isLogin = True
		conn = sqlite3.connect('static/database.db')
		cursor = conn.cursor()

		# Modify your query to join Poem with Likes
		query = """
			SELECT P.username, P.content, P.date, P.title, P.type,P.id, P.numLikes,
				   COALESCE(L.liked, 0) AS liked
			FROM Poem P
			LEFT JOIN Likes L ON P.id = L.poem_id AND L.username = ?
		"""
		cursor.execute(query, (session.get("username"),))

		rows = cursor.fetchall()
		num_poems = len(rows)
		usernames = []  # ["scott", "alice"]
		contents = []  # ["poem...", "poem2..."]
		dates = []  # ["2023-12-12", "2022-10-10"]
		titles = []
		types = []
		likes = []
		ids = []
		num_likes = []

		for row in rows:
			usernames.append(row[0])
			contents.append(row[1])
			dates.append(row[2])
			titles.append(row[3])
			types.append(row[4].title())
			likes.append(row[7])
			num_likes.append(row[6])

			ids.append(row[5])
		print(likes)
		print(ids)

		print("AAAAA",num_poems)
		if "username" not in session:
			isLogin = False
			return redirect(url_for('login'))
		else:
			isLogin = True

		return render_template('board.html',ids=ids, usernames=usernames, contents=contents,
							   dates=dates, titles=titles, types=types, liked_status=likes,
							   num_poems=num_poems, num_likes = num_likes,isLogin=isLogin)

@app.route("/statistics", methods=['GET', 'POST'])
def statistics():
	if request.method == "POST":
		pass
	else:
		isLogin = False
		conn = sqlite3.connect("static/database.db")
		cursor = conn.cursor()

		cursor.execute("SELECT type, COUNT(type) From Poem GROUP BY type")
		types = cursor.fetchall()
		poem_dic = {} # {"acrostic" : 1, "haiku" :2, "sonnet": 1}
		for type in types:
			poem_type, count = type
			poem_dic[poem_type] = count

		if "username" in session:
			username = session["username"]
			isLogin = True
		else:
			username = ""

		cursor.execute("SELECT type, COUNT(type) From Poem GROUP BY type")
		types = cursor.fetchall()
		conn.close()
		user_dic = {} # {"acrostic" : 1, "haiku" :2, "sonnet": 1}
		for type in types:
			poem_type, count = type
			user_dic[poem_type] = count
		print(user_dic)

		conn = sqlite3.connect('static/database.db')
		cursor = conn.cursor()
		cursor.execute("SELECT strftime('%m', date) as month, COUNT(*) FROM Login_logs GROUP BY month ORDER BY month;")
		login_data = cursor.fetchall()
		conn.close()

		labels = [str(data[0]) for data in login_data]
		values = [data[1] for data in login_data]
		connection = sqlite3.connect('static/database.db')
		cursor = connection.cursor()

		cursor.execute('SELECT sentiment FROM Poem')
		sentiments = cursor.fetchall()
		sentiment_counts = {'positive': 0, 'neutral': 0, 'negative': 0}
		for sentiment in sentiments:
			if sentiment[0] == 1:
				sentiment_counts['positive'] += 1
			elif sentiment[0] == 0:
				sentiment_counts['neutral'] += 1
			elif sentiment[0] == -1:
				sentiment_counts['negative'] += 1
		connection.close()
		return render_template('statistics.html', poem_dic = poem_dic, user_dic = user_dic, isLogin=isLogin,labels=labels,values=values, sentiment_counts=sentiment_counts)
@app.route("/edit_poem", methods=['GET', 'POST'])
def edit_poem():
	if request.method == 'POST':
		poem_id = request.json.get('poem_id')
		title = request.json.get('title')
		content = request.json.get('content')

		try:
			conn = sqlite3.connect('static/database.db')
			cursor = conn.cursor()

			cursor.execute("UPDATE POEM SET title=?, content=? WHERE id=?", (title,  content, poem_id))

			conn.commit()
			conn.close()

			return jsonify(success=True)
		except Exception as e:
			return jsonify(success=False, error=str(e))
# Main function (Python syntax)
if __name__ == '__main__':
	app.run(debug=True)