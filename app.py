import csv
from statistics import mean
from flask import Flask, render_template, request, send_file
from requests import get as req_get

app = Flask(__name__, template_folder='static//templates')
DATA = []
PARAMETERS = ['T2M', 'T2M_MAX', 'T2M_MIN', 'PRECTOTCORR', 'WD10M', 'WS10M', 'PS', 'QV2M']
LAT, LONG = None, None
START_YEAR, END_YEAR = 1990, 2025

@app.route('/', methods=['POST', 'GET'])
def index():
  if request.method == 'POST':
    LAT, LONG, date = request.form.get('latitude'), float(request.form.get('longitude'))%360, request.form.get('date')
    print('\n'*4, date, '\n'*4)
    print(LAT, LONG)
    RESPONSE = req_get(
      'https://power.larc.nasa.gov/api/temporal/daily/point' +
      f'?parameters={','.join(PARAMETERS)}&community=RE&latitude={LAT}&longitude={LONG if LONG <= 180 else 360-LONG}&start={START_YEAR}0101&end={END_YEAR}0101&format=JSON'
    ).json()
    print(RESPONSE)
    RESPONSE = RESPONSE['properties']['parameter']

    DATA = {}
    for param, recs in RESPONSE.items():
      DATA[param] = {}
      for day, value in recs.items():
        if day[4:] == date.replace('-','')[4:]:
          DATA[param][day] = value

    print('\n'*4, DATA, '\n'*4)

    param_entries = []
    for i in range(len(PARAMETERS)):
      param_entries.append([])

    for index, (param, vals) in enumerate(list(DATA.items())):
      print('VAALSVALSVASL: ', vals.items())
      for _, value in enumerate(list(vals.items())):
        param_entries[index] += [value[1]]

    print(param_entries)
    param_avg = [f"{mean(e):.2f}" for e in param_entries]
    
    return render_template('results.html',
      param_entries=param_entries,
      params=PARAMETERS,
      param_num=len(PARAMETERS),
      avgs=param_avg,
      date=date,
      lat=LAT,
      long=LONG,
      start_year=START_YEAR
    )

  else:
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download():
  print(DATA)
  with open('out.csv', 'w', newline='') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=['Year'] + PARAMETERS)
    writer.writeheader()
    for r in DATA:
      dtw = r.copy()

      for k in dtw.keys():
        print(dtw[k])
        dtw[k] = list(dtw[k].items())[0][1]

      print(dtw)
      dtw.update({'Year': dtw['_']})
      del dtw['_']

      writer.writerow(dtw)


  return send_file('out.csv', as_attachment=True)

@app.route('/graph', methods=['POST'])
def graph():
  param = request.form.get('parameter')
  lat, long = request.form.get('lat'), request.form.get('long')
  return req_get(
    'https://power.larc.nasa.gov/api/toolkit/power/visualizations/heatmaps?operation=climatological-days' +
    f'&start=1990-01-01T00%3A00%3A00&end=2024-01-01T00%3A00%3A00&latitude={lat}&longitude={long}&community=ag&parameter={param}&format=html&units=metric'
  ).text

@app.route('/about-us')
def about_us():
  return render_template('about-us.html')


if __name__ == '__main__':
  app.run(port=8080, host='127.0.0.5', debug=True)
