import tornado.ioloop
import tornado.web
from whatsapp_inbound_handler import WhatsappInboundHandler
from whatsapp_outbound_handler import WhatsappOutboundHandler


class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/outbound", WhatsappOutboundHandler),
            (r"/inbound", WhatsappInboundHandler)
        ]
        settings = dict(
            debug=True,
        )
        tornado.web.Application.__init__(self, handlers, **settings)


if __name__ == "__main__":
    app = tornado.httpserver.HTTPServer(Application())
    app.listen(8888)
    print("Server running on http://localhost:8888")
    tornado.ioloop.IOLoop.current().start()
