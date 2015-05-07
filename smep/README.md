# SMEP - Some More Enterpricey Python

SMEP is a very basic threaded HTTP server. Use like it:

    from brilliant.smep import SMEPHandler, start_smep
    
    class Handler(SMEPHandler):
        def post(self, args):
            try:
                self.respond('Your name is %s' % (args['name'], ))
            except KeyError:
                self.respond('No name given', 400)

    start_smep(('', 80), Handler)