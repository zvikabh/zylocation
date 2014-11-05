import cgi
import datetime
import math
import webapp2

from google.appengine.api import users
from google.appengine.ext import db


class UserLocation(db.Model):
  user_email = db.StringProperty(required=True)
  lat = db.FloatProperty(default=0.0)
  lng = db.FloatProperty(default=0.0)
  accuracy = db.FloatProperty(default=-1.0)
  color = db.StringProperty(default='#AA0000')
  last_update = db.DateTimeProperty(default=datetime.datetime.now())
  viewer_emails = db.StringProperty()
  user_id = db.StringProperty()


HTML_HOMEPAGE = """
<!DOCTYPE html>
<html>
<head>
  <meta name="viewport" content="width=device-width">
  <style type="text/css">
  .map { height: 600px; }
  </style>
  <script type="text/javascript"
    src="https://maps.googleapis.com/maps/api/js?key=AIzaSyDSol6TeOm7EdQxtk4qx20A9reE6h_xbeI&sensor=false">
  </script>
  <script type="text/javascript">
    function initialize() {
      var coords = [
%s      ];
      var min_lat = Math.min.apply(null, coords.map(function(coord) {return coord.lat;}));
      var max_lat = Math.max.apply(null, coords.map(function(coord) {return coord.lat;}));
      var min_lng = Math.min.apply(null, coords.map(function(coord) {return coord.lng;}));
      var max_lng = Math.max.apply(null, coords.map(function(coord) {return coord.lng;}));

      var mapOptions = {
        center: new google.maps.LatLng((min_lat+max_lat)/2.0, (min_lng+max_lng)/2.0),
        zoom: 18,
        mapTypeId: google.maps.MapTypeId.ROADMAP
      };
      var map = new google.maps.Map(document.getElementById("map-canvas"),
          mapOptions);

      var southWest = new google.maps.LatLng(min_lat,min_lng);
      var northEast = new google.maps.LatLng(max_lat,max_lng);
      map.fitBounds(new google.maps.LatLngBounds(southWest,northEast));

      for (var i = 0; i < coords.length; i++) {
        var center = new google.maps.LatLng(coords[i].lat, coords[i].lng);
        var markerSpec = {
          position: center,
          map: map,
          title: coords[i].title
        };
        if (coords[i].hasOwnProperty('image')) {
          markerSpec.icon = coords[i].image;
        }
        var marker = new google.maps.Marker(markerSpec);
        addEventListeners(map, marker, coords[i].title);
        new google.maps.Circle({
          center: center,
          map: map,
          radius: coords[i].accuracy,
          fillColor: coords[i].color
        });
      }
    }
    function addEventListeners(map, marker, message) {
      var infowindow = new google.maps.InfoWindow({
        content: message,
        size: new google.maps.Size(50,50)
      });
      google.maps.event.addListener(marker, 'click', function() {
        infowindow.open(map, marker);
      });
      google.maps.event.addListener(marker, 'dblclick', function() {
        map.setCenter(marker.position);
        map.setZoom(18);
      });
    }
    google.maps.event.addDomListener(window, 'load', initialize);
  </script>
  <title>ZYLocation</title>
</head>
<body>
<div id="map-canvas" class="map"/>
</body>
</html>
"""

HTML_NOT_AUTHORIZED = """
<html>
<body>
<p>You are not authorized to use this website.</p>
</body>
</html>
"""


class HomePage(webapp2.RequestHandler):
  _COORDS_JS = ('        {lat: %f, lng: %f, accuracy: %f,'
                ' color: "%s", title: "%s"%s},\n')
  
  def TimeDelta(self, last_update):
    delta = datetime.datetime.now() - last_update
    delta_sec = delta.total_seconds()
    if delta_sec < 60:
      return '%.0f sec ago' % delta_sec
    delta_min = delta_sec / 60
    if delta_min < 60:
      return '%.0f min ago' % delta_min
    delta_hour = delta_min / 60
    if delta_hour < 24:
      return '%.0f hours ago' % delta_hour
    return str(delta)

  def GetUserImage(self, user_id):
    if not user_id:
      return ''
    return ', image: "http://plus.google.com/s2/photos/profile/%s?sz=50"' % (
        user_id)
  
  def GetMapParams(self, viewer_email):
    js = ''
    query = UserLocation.all()
    user_locations = query.fetch(1000)
    for user_location in user_locations:
      if user_location.viewer_emails:
        allowed = (viewer_email in user_location.viewer_emails.split(' '))
      else:
        allowed = True
      if allowed:
        js += self._COORDS_JS % (
            user_location.lat,
            user_location.lng,
            user_location.accuracy,
            user_location.color,
            '%s (%s)' % (user_location.user_email,
                         self.TimeDelta(user_location.last_update)),
            self.GetUserImage(user_location.user_id))
    return js
  
  def get(self):
    user = users.get_current_user()
    if not user:
      self.response.write(HTML_NOT_AUTHORIZED)
      return
    email = user.email()
    self.response.write(HTML_HOMEPAGE % self.GetMapParams(email))


class ReportLocation(webapp2.RequestHandler):
  def get(self):
    user = users.get_current_user()
    if user:
      email = user.email()
    else:
      email = self.request.get('user_email', None)
    if not email:
      self.response.write(HTML_NOT_AUTHORIZED)
      return
    self.response.write("<pre>%s</pre>" % email)
    try:
      lat = float(self.request.get('lat', None))
      lng = float(self.request.get('lng', None))
      accuracy = float(self.request.get('accuracy', -1.0))
    except TypeError, ValueError:
      self.response.write('Invalid location specified.')
      return
    self.response.write("<pre>%f, %f, %f</pre>" % (lat,lng,accuracy))
    
    # Find this user, or create if this is their first report.
    query = UserLocation.all()
    query.filter('user_email =', email)
    user_location = query.get()
    if user_location:
      self.response.write("Found user.<p>");
    if not user_location:
      self.response.write("Creating user.<p>");
      user_location = UserLocation(user_email=email, viewer_emails=email,
                                   user_id="", color="#AA0000")
    user_location.lat = lat
    user_location.lng = lng
    user_location.accuracy = accuracy
    user_location.last_update = datetime.datetime.now()
    user_location.put()
    self.response.write("Location stored successfully.");


class GetLocation(webapp2.RequestHandler):
  _GET_HTML = """
  <!DOCTYPE html>
  <html>
  <head>
    <title>ZY Location - Location Reporting Page</title>
    <script>
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(function(position) {
        var form = document.createElement('form');
        form.setAttribute('method', 'get');
        form.setAttribute('action', '/report');
        params = { 'lat': position.coords.latitude,
                   'lng': position.coords.longitude };
        for (var key in params) {
          if (params.hasOwnProperty(key)) {
            var hiddenField = document.createElement('input');
            hiddenField.setAttribute('type', 'hidden');
            hiddenField.setAttribute('name', key);
            hiddenField.setAttribute('value', params[key]);
            form.appendChild(hiddenField);
          }
        }
        document.body.appendChild(form);
        form.submit();
      },
      function() {
        setResponse('Error: The Geolocation service failed.');
      });
    } else {
      setResponse('Error: Your browser doesn\\'t support geolocation.');
    }

    function setResponse(response) {
      document.getElementById('response').innerHTML = response;
    }
    </script>
  </head>
  <body>
    <div id="response"></div>
  </body>
  </html>
  """
  def get(self):
    self.response.write(self._GET_HTML)
    

application = webapp2.WSGIApplication([
    ('/', HomePage),
    ('/get', GetLocation),
    ('/report', ReportLocation)
], debug=True)
