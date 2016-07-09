import urllib, urllib2, urlparse, json
import datetime as dt

api_key = "5f757eb035b6bea5"
query = {}

url = "https://api.cyclestreets.net/v2/photomap.locations?"
query['key']          = api_key
# query['category']     = 'cycleparking'
query['metacategory'] = 'bad'
query['limit']        = 0
query['fields']       = "id,hasPhoto,thumbnailUrl,license,caption,datetime"
query['bbox']         = "-0.004807,52.079928,0.342636,52.25597"

s = urllib.urlencode(query)
s = url + s

j = json.load(urllib2.urlopen(s))

print len(j['features'])

now = dt.datetime.now()

i = 0
reports = []
for feature in j['features']:
	t_epoch = feature['properties']['datetime']
	feature_date = dt.datetime.fromtimestamp(t_epoch)
	if now - feature_date < dt.timedelta(weeks=1):
		print json.dumps(feature, indent=2)
		reports.append(feature)
		i += 1

print i

# print json.dumps(j['features'][0], indent=2)
# print json.dumps(j, indent=2)

from jinja2 import Template, Environment, FileSystemLoader
from os import path
import webbrowser

env = Environment(loader=FileSystemLoader('.'), trim_blocks=True, lstrip_blocks=True)
template = env.get_template("newsletter.jinja")

title = 'CycleStreet User Reports Week {} {}'.format(now.isocalendar()[1], now.isocalendar()[0])
html = template.render(reports=reports, title=title)
print html

with open("newsletter.html", 'w') as fd:
	fd.write(html)

webbrowser.open_new_tab("file://"+path.abspath("newsletter.html"))

# Import smtplib for the actual sending function
import smtplib
from getpass import getpass

# Import the email modules we'll need
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Create a text/plain message
msg = MIMEMultipart('alternative')
text = "This is a multimedia message"
part1 = MIMEText(text, 'plain')
part2 = MIMEText(html, 'html')

me = "cyclehack.cambridge@gmail.com"
you = [me, "noel.kavanagh@cambridgeshire.gov.uk", "anna.smith@cambridge.gov.uk"]
msg['Subject'] = title
msg['From'] = me

msg.attach(part1)
msg.attach(part2)

# Send the message via our own SMTP server, but don't include the
# envelope header.
login, password = me, "cyclehack2016"#getpass('Gmail password:')
s = smtplib.SMTP_SSL('smtp.gmail.com', 465, timeout=10)
try:
	s.login(login, password)
	for y in you:
		msg['To'] = y
		s.sendmail(me, [y], msg.as_string())
finally:
	s.quit()
