import requests
import cmd


class CirculoShell(cmd.Cmd):
    
    intro = "Welcome to the Circulo Shell"
    prompt = '\033[1;32mCirculo$ \033[1;m'
    
    
    def do_action(self, s):
        print "You typed {}".format(s)

    def help_action(self):
        print "Help with the Action command"

    _AVAILABLE_COLORS = ('blue', 'green', 'yellow', 'red', 'black')
    def complete_color(self, text, line, begidx, endidx):
        return [i for i in _AVAILABLE_COLORS if i.startswith(text)]


    def __init__(self):
        cmd.Cmd.__init__(self)

    def default(self, line):
        if line == 'EOF' or line == 'exit':
            self.do_quit(line)
            return True
        else:
            print "*** Command not recognized, try 'help'"

    def preloop(self):
        pass

    def postloop(self):
        pass



url = "http://localhost:8080"



def send_command():
    data = {'sender': 'Alice', 'receiver': 'Bob', 'message': 'We did it!'}
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    r = requests.post(url, data=json.dumps(data), headers=headers)


if __name__ == '__main__':
    CirculoShell().cmdloop()











