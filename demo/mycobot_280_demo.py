from pymycobot import MyCobot280

mc = MyCobot280("COM23")
# mc.go_home()
# mc.release_all_servos()
# mc.focus_all_servos()
# mc.send_coord(6,100,10)
mc.send_angles([0,0,-90,0,0,0],10)