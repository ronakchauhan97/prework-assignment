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
	''' index '''
	return render_template('index.html', count_ops=0)


@app.route('/create_vol_op')
def vol_op():
	''' Create volunteering oportunity '''
	return render_template('create_vol_op.html')


# Since python doesn't support static variables, a list is used 
# as a workaround (any mutable object would to the job)
@app.route('/send', methods= ['GET', 'POST'])
def send(count=[0]):
	'''receive information from the form'''
	if request.method == 'POST':
		op_name = request.form['op_name']
		op_location = request.form['op_location']
		op_availability = request.form['op_availability']
		op_description = request.form['op_description']
		op_email = request.form['op_email']

		# adding all fields for volunteering opportunities to a dictionary
		op_dict = dict()
		op_dict['op_title'] = op_name
		op_dict['op_loc'] = op_location
		op_dict['op_avail'] = op_availability
		op_dict['op_email_id'] = op_email

		opportunity = mongo.db.opportunities
		opportunity.insert(op_dict)

		count[0] += 1
		return render_template('index.html', count_ops=count[0])
		
	else :
		return render_template('error.html')


if __name__ == '__main__':
	app.run(debug = True)