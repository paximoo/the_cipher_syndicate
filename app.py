from statistics import mean
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
    PARAMETERS = ['T2M', 'T2M_MAX', 'T2M_MIN', 'PRECTOTCORR', 'CLOUD_AMT', 'WD10M', 'WS10M', 'PS', 'QV2M']
    for i in range(2022, 2024):
      curr_date = str(i) + date.replace('-', '')#{i}{date.replace('-', '')
      curr_data = {'_': {'_': curr_date[:4]}}
      try:
        curr_data.update(req_get(
          'https://power.larc.nasa.gov/api/temporal/daily/point' +
          f'?parameters={','.join(PARAMETERS)}&community=RE&latitude={lat}&longitude={long}&start={curr_date}&end={curr_date}&format=JSON')
          .json()['properties']['parameter'])
      except Exception as e:
        print(e)
       
      data.append(curr_data)

    param_entries = []
    for i in range(len(PARAMETERS)):
      param_entries.append([])

    for r in data:
      for index, field in enumerate(list(r.items())[1:]):
        param_entries[index] += list(field[1].values())

    param_avg = [f"{mean(e):.2f}" for e in param_entries]
    print(param_avg)

    print(param_entries)
    
    return render_template('results.html',
      data=data,
      params=PARAMETERS,
      param_num=len(PARAMETERS),
      avgs=param_avg
    )

  else:
    return render_template('index.html')

if __name__ == '__main__':
  app.run(port=8080, host='0.0.0.0', debug=True)
