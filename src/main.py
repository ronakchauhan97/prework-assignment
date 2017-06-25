from flask import Flask
from flask import request
from flask import render_template
from flask_pymongo import PyMongo

app = Flask(__name__)
app.config['MONGO_DBNAME'] = 'portaldb'
app.config['MONGO_URI'] = 'mongodb://punk:qwerty12345@ds039125.mlab.com:39125/portaldb'

mongo = PyMongo(app)


@app.route('/')
def index():
	''' Index (front page) '''
	return render_template('index.html', count_ops=mongo.db.opportunities.count())


@app.route('/create_vol_op')
def vol_op():
	''' Create volunteering oportunity '''
	return render_template('create_vol_op.html')


@app.route('/search_ops')
def search_ops():
	''' Search for volunteering oportunity '''
	return render_template('search_ops.html')


# Since python doesn't support static variables, a list is used 
# as a workaround (any mutable object would to the job)
@app.route('/send', methods=['GET', 'POST'])
def send(count=[0]):
	''' Receive information from the form '''
	count[0] = mongo.db.opportunities.count()
	if request.method == 'POST':
		op_name = request.form['op_name']
		op_location = request.form['op_location']
		op_availability = request.form['op_availability']
		op_description = request.form['op_description']
		op_email = request.form['op_email']

		# check for empty search box
		if(len(op_name) * len(op_location) * len(op_availability) * len(op_description) * len(op_email) == 0) :
			return render_template('error.html', parameter=0)

		# adding all fields for volunteering opportunities to a dictionary
		op_dict = dict()
		op_dict['op_title'] = op_name.title()
		op_dict['op_loc'] = op_location.title()
		op_dict['op_avail'] = op_availability.title()
		op_dict['op_email_id'] = op_email
		op_dict['op_desc'] = op_description

		opportunity = mongo.db.opportunities
		opportunity.insert(op_dict)

		count[0] += 1
		return render_template('index.html', count_ops=count[0])
		
	else :
		return render_template('error.html', length=500)




# FOLLOWING PART IS ALL RELATED TO SEARCH AND SEARCH RESULTS
# AND THE IMPLEMENTATION IS VERY CRUDE AND INEFFICIENT
def results_HTML(cursor_obj, found, cursor_count):
	''' Returns an HTML string with search results which is rendered by the browser as a proper HTML page '''
	output_string = '	<!DOCTYPE html>\
<html lang="en"> \
<head> \
	<title> Search Results </title> \
	\
	<link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css" integrity="sha384-BVYiiSIFeK1dGmJRAkycuHAHRg32OmUcww7on3RYdg4Va+PmSTsz/K68vbdEjh4u" crossorigin="anonymous">\
</head> <body> '

	if cursor_count == 0 or found == False :
		output_string += '<h1> <center> No opportunity matched your search query :( </center> </h1> <hr>'

	else :
		output_string += '<h1> <center> Following opportunities matched your search query </center> </h1> <hr> <p>'	 
		for opportunity in cursor_obj:
			output_string += '<b> &emsp; &emsp; &emsp; &emsp; Title : </b> ' + ' -- ' + opportunity['op_title'] + '  <br><br>	'
			output_string += '<b> &emsp; &emsp; &emsp; &emsp; Description : </b> ' + ' -- ' + opportunity['op_desc'] + '  <br><br>'
			output_string += '<b> &emsp; &emsp; &emsp; &emsp; Location : </b> ' + ' -- ' + opportunity['op_loc'] + '  <br><br>'
			output_string += '<b> &emsp; &emsp; &emsp; &emsp; Availability : </b> ' + ' -- ' + opportunity['op_avail'] + '  <br><br>'
			output_string += '<b> &emsp; &emsp; &emsp; &emsp; Email-ID : </b> ' + ' -- ' + opportunity['op_email_id'] + '  <br><br><br><br>'

	output_string += '</p></body> </html>'
	return output_string


@app.route('/search_results', methods=['GET', 'POST'])
def search_results():
	''' Search for info in the db '''
	if request.method == 'POST':
		op_fields = request.form['op_fields']
		search_terms = request.form['search_terms']

		if (len(op_fields) * len(search_terms)) == 0 :
			return render_template('error.html', parameter=0)

		field_list = op_fields.split(';')
		search_terms = search_terms.split(';')

		# getting the search fields and stripping out all 
		# the leading and tailing spaces
		for i in range(len(field_list)) :
			s, e = 0, len(field_list[i])-1
			while(field_list[i][s] == ' ') : s += 1
			while(field_list[i][e] == ' ') : e -= 1

			field_list[i] = (field_list[i][s:e+1]).title()
		
		# getting the search terms and stripping out all 
		# the leading and tailing spaces
		for i in range(len(search_terms)) :
			s, e = 0, len(search_terms[i])-1
			while(search_terms[i][s] == ' ') : s += 1
			while(search_terms[i][e] == ' ') : e -= 1

			search_terms[i] = (search_terms[i][s:e+1]).title()

		# #search_fields and #search_terms need to be the same
		if(len(field_list) != len(search_terms)) :
			return render_template('error.html', parameter=1)

		final_search_term = dict()
		for i in range(len(field_list)):
			if field_list[i] == 'Title':
				final_search_term['op_title'] = { '$regex' : '.*' + search_terms[i] + '.*'}

			elif field_list[i] == 'Location':
				final_search_term['op_loc'] = { '$regex' : '.*' + search_terms[i] + '.*'}
				
			elif field_list[i] == 'Availability': 
				final_search_term['op_avail'] = { '$regex' : '.*' + search_terms[i] + '.*'}


		op_collection = mongo.db.opportunities
		search_results = op_collection.find(final_search_term)
 
 		# check for invalid fields
		if len(final_search_term) != len(field_list) :
			return results_HTML(search_results, False, search_results.count())
		
		return results_HTML(search_results, True, search_results.count())
	
	else :
		return render_template('error.html', parameter=500)


if __name__ == '__main__':
	app.run(debug=True)

