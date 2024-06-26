from flask import Flask, render_template, request,jsonify, url_for, flash, redirect, session # flask: like library, python programme, connects frontend & backend
import sqlite3 #library that connects python & database
import bcrypt
from datetime import timedelta, datetime
from helper import haiku_is_standard, is_acroustic, is_sonnet, isSimilar_theme,cnt_word_syll
from profanity import profanity
from textblob import TextBlob
from collections import Counter
import re
from nltk.corpus import stopwords
from nltk.corpus import cmudict

app = Flask(__name__)
app.secret_key = "randommessage"
app.permanent_session_lifetime = timedelta(seconds=3600)

punctuation = ["@!#$%^&*"]

@app.route('/', methods=['GET']) # / => main homepage; decorator
def index(): #index func calls render_template, showing login.html on website
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


	cursor.execute("SELECT content FROM Poem")
	poems = cursor.fetchall()

	conn.close()

	stop_words = set(stopwords.words('english'))
	words = []
	for poem in poems:
		words.extend([word for word in re.findall(r'\b\w+\b', poem[0].lower()) if word not in stop_words])

	word_freq = Counter(words)

	top_words = word_freq.most_common(7)

	labels_word = [word[0] for word in top_words]
	frequencies = [word[1] for word in top_words]

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
	cursor.execute(
		"SELECT username, SUM(numLikes) FROM Poem GROUP BY username ORDER BY SUM(numLikes) DESC LIMIT 5")
	top_users = cursor.fetchall()
	top_users_dict = {username: total_likes for username, total_likes in top_users}
	labels_username = [user[0] for user in top_users]
	number_likes = [user[1] for user in top_users]
	connection.close()
	print(labels_username)
	return render_template('index.html', poem_dic = poem_dic, user_dic = user_dic, isLogin=isLogin,labels=labels,values=values, sentiment_counts=sentiment_counts, labels_word=labels_word, frequencies=frequencies,labels_username=labels_username,number_likes=number_likes) # html var = python var
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
		conn = sqlite3.connect('static/database.db')
		cursor = conn.cursor()

		# Modify your query to join Poem with Likes
		query = """
			SELECT P.username, P.content, P.date, P.title, P.type,P.id, P.numLikes, P.iamb,
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
		num_likes = []
		iambs = []

		for row in rows:
			usernames.append(row[0])
			contents.append(row[1])
			dates.append(row[2])
			titles.append(row[3])
			if row[4] == "free":
				types.append("Freestyle")
			else:
				types.append(row[4].title())
			likes.append(row[6])
			iambs.append(row[7])

			ids.append(row[5])
			num_likes.append(row[8])

		print("ABCCCCC",iambs)
		if "username" not in session:
			isLogin = False
			return redirect(url_for('login'))
		else:
			isLogin = True

		return render_template('mypage.html',ids=ids, usernames=usernames, contents=contents,
							   dates=dates, titles=titles, types=types, liked_status=likes, iambs=iambs,
							   num_poems=len(usernames), isLogin=isLogin, username = session["username"],num_likes=num_likes)
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
		if username == "" or username is None or password=="" or password is None:
			flash("Invalid username or password!")
			return render_template('login.html')
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
			session["username"] = username #
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
	else: 
		if "username" in session:
			return redirect(url_for('index'))
		return render_template('login.html')

@app.route('/logout', methods=['GET']) # if user presses /logout
def logout():
	session.clear()
	return redirect(url_for('index')) # sends user to /login


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
		isMatch = False
		isBad = False
		isEmpty = False
		lines = request.form.getlist("line") #[line1,line2,line3]
		title = request.form.get('title')
		if len(lines)==0:
			isEmpty = True
			flash("Please write a poem before you submit.")
			return render_template('poem_writing_haiku.html', isLogin=isLogin, lines=lines, title=title,
								   isMatch=isMatch, isBad=isBad, isEmpty=isEmpty)
		for line in lines:
			if len(line) <=9:
				isMatch = True
				flash("Please write appropriate contents.")
				return render_template('poem_writing_haiku.html', isLogin=isLogin, lines=lines, title=title,
									   isMatch=isMatch, isBad=isBad,isEmpty=isEmpty)
			if line == "":
				isEmpty = True
				flash("Please write a poem before you submit.")
				return render_template('poem_writing_haiku.html', isLogin=isLogin, lines=lines, title=title,
									   isMatch=isMatch, isBad=isBad,isEmpty=isEmpty)

		if isSimilar_theme(title,lines) < 0.11:
			isMatch = True
			flash("Please match the title with your contents of poem.")
			# return render_template('poem_writing_haiku.html', isLogin=isLogin, lines=lines, title=title, isMatch=isMatch)

		for line in lines:
			if contains_profanity(line):
				isBad = True
				flash("Do not use any harmful words.")
				break
				# return render_template('poem_writing_haiku.html', isLogin=isLogin, lines=lines, title=title,isBad=isBad)
		if isBad or isMatch or isEmpty:
			return render_template('poem_writing_haiku.html', isLogin=isLogin, lines=lines, title=title, isBad=isBad, isMatch=isMatch)

		result = haiku_is_standard(lines)
		if result:
			username = session["username"]
			content = "\n".join(lines)  # "line1\nline2\nline3\n"
			today_date = datetime.today()
			conn = sqlite3.connect("static/database.db")
			title = request.form.get('title')
			if title is not None:
				title = title.strip()
			cursor = conn.cursor()
			type = "haiku"

			cursor.execute('SELECT MAX(id) FROM Poem')

			largest_id = cursor.fetchone()[0]
			sentiment = get_sentiment(' '.join(lines))
			cursor.execute("Insert INTO Poem (username, content, date,title,type,id,numLikes,sentiment) VALUES (?,?,?,?,?,?,?,?)",
						   (username, content, today_date, title, type, largest_id + 1,0,sentiment))
			conn.commit()
			conn.close()

			return render_template('poem_writing_haiku.html', isLogin=isLogin, showSuccessModal=True, lines=[])
		else:
			isSyll = True
			flash("Please check the number of syllables for each line.")
			return render_template('poem_writing_haiku.html', isLogin=isLogin, lines=lines, title=title,isSyll=isSyll,isMatch = isMatch, isBad = isBad)


	else:
		if "username" not in session:
			return redirect(url_for('login'))
		else:
			isLogin = True

	return render_template('poem_writing_haiku.html', isLogin=isLogin, lines=lines, title=title,isBegin = True)


@app.route('/validate_poem_edit', methods=['POST'])
def validate_poem_edit():
	data = request.json
	poem_type = data['type']
	title = data['title']
	content = data['content'].split("\n")
	if poem_type == 'Haiku':
		if isSimilar_theme(title, content) < 0.11:
			return jsonify(success=False, message="Theme does not match.")
		if any(contains_profanity(line) for line in content):
			return jsonify(success=False, message="Contains prohibited content.")
		if not haiku_is_standard(content):
			return jsonify(success=False, message="Does not meet Haiku standards.")
	if poem_type == 'Acrostic':
		if any(line == "" for line in content):
			return jsonify(success=False, message="All lines must be filled.")

		if len(content) != len(title):
			return jsonify(success=False, message="The number of lines must match the number of characters in the title.")

		if isSimilar_theme(title, content) < 0.11:
			return jsonify(success=False, message="Theme does not match closely enough.")

		if any(contains_profanity(line) for line in content):
			return jsonify(success=False, message="Contains inappropriate content.")

		if not is_acroustic(title, content):
			return jsonify(success=False, message="Does not meet Acrostic structure standards.")
	if poem_type == 'Sonnet':
		isStress = True
		isFinal = False
		isLine = False
		count = 0
		syll_count = 0
		punctuation_pattern = r'[^\w\s]'

		for line in content:
			line = line.strip()
			clean_text = re.sub(punctuation_pattern, '', line)
			words = clean_text.split()
			for word in words:
				syll_count += cnt_word_syll(word)
				if has_stress_pattern(word):
					count += 1
					isStress = False
		if (isStress and count >= 2) or syll_count not in [10, 9, 11]:
			isFinal = True

		if any(len(i) == 0 for i in content):
			isLine = True
			return jsonify(success=False, message="All lines must be filled.")

		if not isSimilar_theme(title, content):
			return jsonify(success=False, message="Theme does not match closely enough.")

		if any(contains_profanity(line) for line in content):
			return jsonify(success=False, message="Contains inappropriate content.")

		if isFinal or isLine:
			return jsonify(success=False, message="Does not meet Sonnet structure standards.")

		if not is_sonnet(content):
			return jsonify(success=False, message="Does not comply with Sonnet requirements.")
	if poem_type == 'Free':
		isStress = True
		count = 0
		syll_count = 0
		punctuation_pattern = r'[^\w\s]'

		toggleStress = data.get('toggleStress', False)  # Adjust based on actual data structure
		if toggleStress:
			for line in content:
				line = line.strip()
				clean_text = re.sub(punctuation_pattern, '', line)
				words = clean_text.split()
				for word in words:
					syll_count += cnt_word_syll(word)
					if has_stress_pattern(word):
						count += 1
						isStress = False
			if (isStress and count >= 2) or syll_count not in [10, 9, 11]:
				return jsonify(success=False, message="Syllable count or stress pattern does not meet the requirements.")

		if isSimilar_theme(title, content) < 0.11:
			return jsonify(success=False, message="Theme does not match closely enough.")

		if any(contains_profanity(line) for line in content):
			return jsonify(success=False, message="Contains inappropriate content.")
	poem_id = request.json.get('poem_id')
	title = request.json.get('title')
	content = request.json.get('content')

	try:
		conn = sqlite3.connect('static/database.db')
		cursor = conn.cursor()
		print("added")
		cursor.execute("UPDATE POEM SET title=?, content=? WHERE id=?", (title,  content, poem_id))

		conn.commit()
		conn.close()
	except Exception as e:
		return jsonify(success=False, error=str(e))
	return jsonify(success=True)


@app.route('/poem_writing_free', methods=['GET','POST'])
def poem_writing_free():
	isLogin = False
	if request.method == "POST":
		print("CALLED")
		isLogin=True
		isMatch = False
		count = 0
		isBad = False
		syll_count = 0
		isStress = True
		isFinal = False
		print(request.form)  # See all form data
		lines = request.form.getlist("line") #["line1", "line2","line3"]
		print(lines)
		title = request.form.get("theme")
		isEmpty = False
		if len(lines)==0:
			isEmpty = True
			flash("Please write a poem before you submit.")
			return render_template('poem_writing_free.html', isLogin=isLogin, lines=lines, title=title,
								   isMatch=isMatch, isBad=isBad, isEmpty=isEmpty)
		for line in lines:
			if line == "":
				isEmpty = True
				flash("Please write a poem before you submit.")
				return render_template('poem_writing_free.html', isLogin=isLogin, lines=lines, title=title,
									    isMatch=isMatch, isBad=isBad,isEmpty=isEmpty)
		if request.form.get('toggleStress') == "checked":
			punctuation_pattern = r'[^\w\s]'
			for line in lines:
				line = line.strip()
				clean_text = re.sub(punctuation_pattern, '', line)
				words = clean_text.split()
				for word in words:
					c = cnt_word_syll(word)
					syll_count += c
					if has_stress_pattern(word):
						count+=1
						isStress = False
			if (isStress == True and count >= 2 ) or syll_count != 10 or syll_count != 9 or syll_count !=11:
				flash("Check your stress pattern.")
				isFinal = True
			# return render_template('poem_writing_free.html', isLogin=isLogin, lines=lines, title=title,isStress=isStress)

		if isSimilar_theme(title,lines) < 0.11:
			isMatch = True
			flash("Poem requires to match the title with your contents of poem.")
			# return render_template('poem_writing_free.html', isLogin=isLogin, lines=lines, title=title, isMatch=isMatch)

		for line in lines:
			if contains_profanity(line):
				isBad = True
				flash("Do not use any harmful words.")
				break
		if isMatch or isBad or isFinal:
				return render_template('poem_writing_free.html', isLogin=isLogin, lines=lines, title=title,isBad=isBad, isMatch=isMatch,isFinal=isFinal ), 300

		username = session["username"]
		content = "\n".join(lines) # "line1\nline2\nline3\n"
		today_date = datetime.today()
		conn = sqlite3.connect("static/database.db")
		cursor = conn.cursor()
		type = "free"
		if title is not None:
				title = title.strip()
		cursor.execute('SELECT MAX(id) FROM Poem')

		largest_id = cursor.fetchone()[0]
		sentiment = get_sentiment(' '.join(lines))
		if request.form.get('toggleStress') == "checked":
			cursor.execute("Insert INTO Poem (username, content, date,title,type,id,numLikes,sentiment,iamb) VALUES (?,?,?,?,?,?,?,?,?)",
						   (username, content, today_date, title, type, largest_id + 1,0,sentiment,1))
		else:
			cursor.execute("Insert INTO Poem (username, content, date,title,type,id,numLikes,sentiment,iamb) VALUES (?,?,?,?,?,?,?,?,?)",
						   (username, content, today_date, title, type, largest_id + 1,0,sentiment,0))
		conn.commit()
		conn.close()
		print("SSSSS")
		return render_template('poem_writing_free.html', isLogin=isLogin, showSuccessModal=True, lines=[])
	else:
		if "username" not in session:
			return redirect(url_for('login'))
		else:
			isLogin=True
		return render_template('poem_writing_free.html',isLogin=isLogin,isBegin = True)
@app.route('/submission_success')
def submission_success():
    if "username" not in session:
        return redirect(url_for('login'))
    return render_template('submission_success.html')

@app.route('/delete_poem', methods=['POST'])
def delete_poem():
    data = request.json
    poem_id = data['poem_id']

    conn = sqlite3.connect('static/database.db')
    cur = conn.cursor()

    try:
        cur.execute("DELETE FROM Poem WHERE id = ?", (poem_id,))
        conn.commit()
        response = {'success': True}
    except Exception as e:
        print(e)
        response = {'success': False}

    conn.close()
    return jsonify(response)
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
		isLine = False
		isMatch = False
		isBad = False
		isEmpty = False
		lines = request.form.getlist("line")
		title = request.form.get('theme')
		if len(lines)==0:
			isEmpty = True
			flash("Please write a poem before you submit.")
			return render_template('poem_writing_acrostic.html', isLogin=isLogin, lines=lines, title=title,
								   isLine=isLine, isMatch=isMatch, isBad=isBad, isEmpty=isEmpty)
		for line in lines:
			if line == "":
				isEmpty = True
				flash("Please write a poem before you submit.")
				return render_template('poem_writing_acrostic.html', isLogin=isLogin, lines=lines, title=title,
									   isLine=isLine, isMatch=isMatch, isBad=isBad,isEmpty=isEmpty)
		if len(lines[0]) == 0:
			isLine = True
			flash("You have not completed your poem.")
			return render_template('poem_writing_acrostic.html', isLogin=isLogin, lines=lines, title=title, isLine = isLine, isMatch=isMatch, isBad = isBad )

		for i in lines:
			if len(lines) == len(title) and len(i) == 0:
				isLine = True
				print(lines)
				# flash("Wrong!")
				# return render_template('poem_writing_sonnet.html', isLogin=isLogin, lines=lines, title=title,
				# 					   isLine=isLine)
		if isSimilar_theme(title,lines) < 0.11:
			isMatch = True
			flash("Acrostic requires to match the theme with your contents of poem.")
			# return render_template('poem_writing_acrostic.html', isLogin=isLogin, lines=lines, title=title, isMatch=isMatch)

		for line in lines:
			if contains_profanity(line):
				isBad = True
				flash("Do not use any harmful words.")
				break
				# return render_template('poem_writing_acrostic.html', isLogin=isLogin, lines=lines, title=title,isBad=isBad)

		result = is_acroustic(title,lines)
		if result:
			username = session["username"]
			content = "\n".join(lines)  # "line1\nline2\nline3\n"
			today_date = datetime.today()
			conn = sqlite3.connect("static/database.db")
			title = request.form.get('theme')
			if title is not None:
				title = title.strip()
			cursor = conn.cursor()
			type = "acrostic"

			cursor.execute('SELECT MAX(id) FROM Poem')
			sentiment = get_sentiment(' '.join(lines))
			largest_id = cursor.fetchone()[0]

			cursor.execute("Insert INTO Poem (username, content, date,title,type,id,numLikes,sentiment) VALUES (?,?,?,?,?,?,?,?)",
						   (username, content, today_date, title, type, largest_id + 1,0,sentiment))
			conn.commit()
			conn.close()

			return render_template('poem_writing_acrostic.html', isLogin=isLogin, showSuccessModal=True, lines=[])
		else:
			isWrong = True
			flash("Each line should start with each character of the theme.")

			return render_template('poem_writing_acrostic.html', isLogin=isLogin, lines=lines, title=title, isWrong = isWrong,isLine = isLine, isMatch=isMatch, isBad = isBad )
	else:
		if "username" not in session:
			return redirect(url_for('login'))
		else:
			isLogin = True

	return render_template('poem_writing_acrostic.html', isLogin=isLogin, lines=lines, title=title,isBegin = True)

# Function to check if a word has a stress pattern of stress, unstress, stress
def has_stress_pattern(word):
	d = cmudict.dict()

	if word.lower() in d:
		pronunciation = d[word.lower()][0]

		stress_pattern = ''.join(['S' if re.search(r'\d', phoneme) else 'U' for phoneme in pronunciation])

		if re.search(r'SUS', stress_pattern):
			return True

	return False
@app.route('/poem_writing_sonnet', methods=['GET', 'POST'])
def poem_writing_sonnet():
	isLogin = False
	lines = []
	title = ""

	if request.method == "POST":
		title = request.form.get('theme')
		isLogin = True
		isFinal = False
		lines = request.form.getlist("line")
		isStress = True
		isMatch = False
		isBad = False
		isLine = False
		count = 0
		syll_count = 0
		isEmpty = False
		for line in lines:
			if line == "":
				isEmpty = True
				flash("Please write a poem before you submit.")
				return render_template('poem_writing_sonnet.html', isLogin=isLogin, lines=lines, title=title,
									   isLine=isLine, isMatch=isMatch, isBad=isBad,isEmpty=isEmpty)
		for line in lines:
			if len(line) <=9:
				isMatch = True
				flash("Please write appropriate contents.")
				return render_template('poem_writing_haiku.html', isLogin=isLogin, lines=lines, title=title,
									   isMatch=isMatch, isBad=isBad,isEmpty=isEmpty)
		if request.form.get('toggleStress') == "checked":
			punctuation_pattern = r'[^\w\s]'
			for line in lines:
				line = line.strip()
				clean_text = re.sub(punctuation_pattern, '', line)
				words = clean_text.split()
				for word in words:
					c = cnt_word_syll(word)
					syll_count += c
					if has_stress_pattern(word):
						count+=1
						isStress = False
			if (isStress == True and count >= 2) or syll_count != 10 or syll_count != 9 or syll_count !=11:
				isFinal = True
				flash("Check your stress pattern.")

				return render_template('poem_writing_sonnet.html', isLogin=isLogin, lines=lines, title=title,
									   isBad=isBad, isMatch=isMatch, isFinal=isFinal, isLine=isLine)

		for i in lines:
			if len(i) == 0:
				isLine = True
				flash("Sonnet needs to have 14 lines.")
				# return render_template('poem_writing_sonnet.html', isLogin=isLogin, lines=lines, title=title,
				# 					   isLine=isLine)

		title = request.form.get('theme')

		if not isSimilar_theme(title,lines):
			isMatch = True
			flash("Please match the title with your contents of poem.")
			# return render_template('poem_writing_sonnet.html', isLogin=isLogin, lines=lines, title=title, isMatch=isMatch)

		for line in lines:
			if contains_profanity(line):
				isBad = True
				flash("Do not use any harmful words.")
				break
				# return render_template('poem_writing_sonnet.html', isLogin=isLogin, lines=lines, title=title,isBad=isBad)
		if isBad or isMatch or isFinal or isLine:
			return render_template('poem_writing_sonnet.html', isLogin=isLogin, lines=lines, title=title, isBad=isBad, isMatch=isMatch, isFinal = isFinal, isLine = isLine)

		result = is_sonnet(lines)
		if result:
			username = session["username"]
			content = "\n".join(lines)  # "line1\nline2\nline3\n"
			today_date = datetime.today()
			conn = sqlite3.connect("static/database.db")
			title = request.form.get('theme')
			cursor = conn.cursor()
			type = "sonnet"
			if title is not None:
				title = title.strip()
			cursor.execute('SELECT MAX(id) FROM Poem')

			largest_id = cursor.fetchone()[0]
			sentiment = get_sentiment(' '.join(lines))
			if request.form.get('toggleStress') == "checked":
				cursor.execute(
					"Insert INTO Poem (username, content, date,title,type,id,numLikes,sentiment,iamb) VALUES (?,?,?,?,?,?,?,?,?)",
					(username, content, today_date, title, type, largest_id + 1, 0, sentiment, 1))
			else:
				cursor.execute(
					"Insert INTO Poem (username, content, date,title,type,id,numLikes,sentiment,iamb) VALUES (?,?,?,?,?,?,?,?,?)",
					(username, content, today_date, title, type, largest_id + 1, 0, sentiment, 0))
			conn.commit()
			conn.close()

			return render_template('poem_writing_sonnet.html', isLogin=isLogin, showSuccessModal=True, lines=[])
		else:
			flash("Please check your rhymes.")
			isWrong = True
			return render_template('poem_writing_sonnet.html', isLogin=isLogin, lines=lines, title=title, isWrong=isWrong)


	else:
		if "username" not in session:
			return redirect(url_for('login'))
		else:
			isLogin = True

	return render_template('poem_writing_sonnet.html', isLogin=isLogin, lines=lines, title=title,isBegin = True)
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
			SELECT P.username, P.content, P.date, P.title, P.type,P.id, P.numLikes, P.iamb,
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
		iambs = []

		for row in rows:
			usernames.append(row[0])
			contents.append(row[1])
			dates.append(row[2])
			titles.append(row[3])
			if row[4] == "free":
				types.append("Freestyle")
			else:
				types.append(row[4].title())
			likes.append(row[8])
			num_likes.append(row[6])
			iambs.append(row[7])

			ids.append(row[5])
		print(likes)
		print(ids)

		print("AAAAA",num_poems)
		if "username" not in session:
			isLogin = False
			return redirect(url_for('login'))
		else:
			isLogin = True

		return render_template('board.html',ids=ids,iambs=iambs, usernames=usernames, contents=contents,
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


		cursor.execute("SELECT content FROM Poem")
		poems = cursor.fetchall()

		conn.close()

		stop_words = set(stopwords.words('english'))
		words = []
		for poem in poems:
			words.extend([word for word in re.findall(r'\b\w+\b', poem[0].lower()) if word not in stop_words])

		word_freq = Counter(words)

		top_words = word_freq.most_common(7)

		labels_word = [word[0] for word in top_words]
		frequencies = [word[1] for word in top_words]

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
		cursor.execute(
			"SELECT username, SUM(numLikes) FROM Poem GROUP BY username ORDER BY SUM(numLikes) DESC LIMIT 5")
		top_users = cursor.fetchall()
		top_users_dict = {username: total_likes for username, total_likes in top_users}
		labels_username = [user[0] for user in top_users]
		number_likes = [user[1] for user in top_users]
		connection.close()
		print(labels_username)
		return render_template('statistics.html', poem_dic = poem_dic, user_dic = user_dic, isLogin=isLogin,labels=labels,values=values, sentiment_counts=sentiment_counts, labels_word=labels_word, frequencies=frequencies,labels_username=labels_username,number_likes=number_likes)
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

@app.route('/statword')
def statword():
	conn = sqlite3.connect('static/database.db')
	c = conn.cursor()

	c.execute("SELECT content FROM Poem")
	poems = c.fetchall()

	conn.close()

	words = []
	for poem in poems:
		words.extend(re.findall(r'\b\w+\b', poem[0].lower()))

	word_freq = Counter(words)

	top_words = word_freq.most_common(7)

	labels = [word[0] for word in top_words]
	frequencies = [word[1] for word in top_words]

	return render_template('statistics.html', labels=labels, frequencies=frequencies)

# Main function (Python syntax)
if __name__ == '__main__':
	app.run(debug=True)