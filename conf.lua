_RELEASE_MODE = true
_DEMO = false

function love.conf(t)
	t.console = not _RELEASE_MODE
	t.title = 'Balatro'
	-- Samsung S23 Ultra logical resolution (412x912 dp)
	t.window.width = 412
	t.window.height = 912
	t.window.minwidth = 100
	t.window.minheight = 100
	-- On Android/iOS, SDL locks orientation from the window: non-resizable + w<h = portrait only.
	-- A resizable window lets the device rotate freely into landscape, which this layout doesn't support.
	t.window.resizable = not (love._os == 'Android' or love._os == 'iOS')
end
