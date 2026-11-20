from flask import Flask, render_template, request, redirect

app = Flask(__name__)

return_requests = []


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/return', methods=['GET', 'POST'])
def return_form():

    if request.method == 'POST':

        customer = request.form['customer']
        product = request.form['product']
        reason = request.form['reason']
        request_type = request.form['request_type']
        description = request.form['description']

        new_request = {
            'customer': customer,
            'product': product,
            'reason': reason,
            'request_type': request_type,
            'description': description,
            'status': 'Pending'
        }

        return_requests.append(new_request)

        return redirect('/requests')

    return render_template('return_form.html')


@app.route('/requests')
def requests_page():

    return render_template(
        'requests.html',
        requests=return_requests
    )


if __name__ == '__main__':
    app.run(debug=True)