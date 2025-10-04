from flask import Flask, render_template, request, redirect
from requests import get as req_get

app = Flask(__name__, template_folder='static//templates')

@app.route('/', methods=['POST', 'GET'])
def index():
  if request.method == 'POST':
    lat, long, date = request.form.get('latitude'), request.form.get('longitude'), request.form.get('date')
    date = date[5:]
    print(lat, long, date)
    data = []
    PARAMETERS = ['T2M', 'T2M_MAX', 'T2M_MIN', 'PRECTOTCORR', 'CLOUD_AMT', 'WD10M', 'WS10M']
    for i in range(2000, 2002):
      curr_date = str(i) + date.replace('-', '')#{i}{date.replace('-', '')
      curr_data = {'_': {'_': curr_date[:4]}}
      curr_data.update(req_get(
        'https://power.larc.nasa.gov/api/temporal/daily/point' +
        f'?parameters={','.join(PARAMETERS)}&community=RE&latitude={lat}&longitude={long}&start={curr_date}&end={curr_date}&format=JSON')
        .json()['properties']['parameter'])
       
      print('BEFORE: ', curr_data)
      print('AFTER: ', curr_data)
      data.append(curr_data)

    param_entries = dict.fromkeys(PARAMETERS, [])
    print(param_entries)
    # for record in data:
    #   for param, value in record.items():
    #     print(param, value)
    #     print(param_entries[param])
    #     param_entries[param] += [value]
        # print(param, value.items()[0][1])

    print(param_entries)
    
    # print(data)
    return render_template('results.html', data=data, params=PARAMETERS)

  else:
    return render_template('index.html')

if __name__ == '__main__':
  app.run(port=8080, host='0.0.0.0', debug=True)
