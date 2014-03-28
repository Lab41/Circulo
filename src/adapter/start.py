import cherrypy
import webbrowser
import os
import simplejson as json
import sys


class HelloWorld(object):
    
    @cherrypy.expose
    def index(self):
        return """
            <html>
                <script type="text/javascript" src="http://ajax.googleapis.com/ajax/libs/jquery/1.4.2/jquery.min.js"></script>
                <script type='text/javascript'>
                function Update() {
                    $.ajax({
                      type: 'POST',
                        url: "update",
                        contentType: "application/json",
                        processData: false,
                        data: $('#updatebox').val(),
                            success: function(data) {alert(data);},
                            dataType: "text"
                    });
                }
                </script>
                <body>
                <input type='textbox' id='updatebox' value='{}' size='20' />
                <input type='submit' value='Update' onClick='Update(); return false' />
                </body>
            </html>
            """


        
        return "Hello world!"


    @cherrypy.expose
    def update(self):
        print "Received Update request"
        cl = cherrypy.request.headers['Content-Length']
        rawbody = cherrypy.request.body.read(int(cl))
        print "Raw"
        print rawbody
       
        try:
            body = json.loads(rawbody)
            # do_something_with(body)
        
        except json.JSONDecodeError:
            return "Error decoding json"
        
        return "Updated %r." % (body,)


    @cherrypy.expose
    def run_snap(self)
        print "Running snap centrality"


cherrypy.quickstart(HelloWorld())


