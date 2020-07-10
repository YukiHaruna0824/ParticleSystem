from mathutils import Vector, Euler, Matrix

class Spring():
    def __init__(self, obj, ks, kd, rest_length, ptc1, ptc2):
        self.ks = ks
        self.kd = kd
        self.rest_length = rest_length

        self.ptc1 = ptc1
        self.ptc2 = ptc2

        self.obj = obj
    
    def getForce(self, ptc):
        delta_position = self.ptc1.simPos - self.ptc2.simPos
        cur_len = delta_position.length
        delta_velocity = self.ptc1.simVel - self.ptc2.simVel

        spring_force = float(-1 * (self.ks * (cur_len - self.rest_length) + self.kd * ((delta_velocity.dot(delta_position)) / cur_len)))
        spring_force = spring_force * (delta_position / cur_len)

        isMinus = 1
        if ptc == self.ptc2:
            isMinus = -1
        
        return spring_force * isMinus
    
    def update(self):
        spline = self.obj.data.splines[0]
        spline.points[0].co = (self.ptc1.obj.location.x, self.ptc1.obj.location.y, self.ptc1.obj.location.z, 1)
        spline.points[1].co = (self.ptc2.obj.location.x, self.ptc2.obj.location.y, self.ptc2.obj.location.z, 1)