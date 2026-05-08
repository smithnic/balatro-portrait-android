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
	t.window.resizable = true
end
