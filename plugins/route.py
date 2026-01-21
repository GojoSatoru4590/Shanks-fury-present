from aiohttp import web

# Basic routes for web server
routes = web.RouteTableDef()


@routes.get("/")
async def index(request):
    """Health check endpoint"""
    return web.Response(text="Bot is running!", status=200)


@routes.get("/health")
async def health(request):
    """Health check endpoint"""
    return web.json_response({"status": "ok", "message": "Bot is healthy"})
