from flask import Flask, render_template, request, redirect

app = Flask(__name__, template_folder='static//templates')

@app.route('/', methods=['POST', 'GET'])
def index():
  if request.method == 'POST':
    print(request.form.get('latitude'))
    print(request.form.get('longitude'))
    return redirect('/')
  else:
    return render_template('index.html')

if __name__ == '__main__':
  app.run(port=8080, host='0.0.0.0', debug=True)
