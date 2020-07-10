from mathutils import Vector, Euler, Matrix

class Particle():
    def __init__(self, obj, pos, mass, radius, kinematic):
        self.mass = mass
        self.velocity = Vector((0, 0, 0))
        self.kinematic = kinematic

        self.radius = radius

        #store blender object
        self.obj = obj
        self.obj.location = pos

        # all force in this object
        self.force = Vector()

        self.simPos = self.obj.location
        self.simVel = Vector()

        self.springs = []

        self.accel = Vector()
        self.next_accel = Vector()

        self.k2 = 0
        self.k3 = 0
    
    def addForce(self, force):
        self.force += force 

    def computeDeltaVelocity(self, difftime):
        return 0

    def euler(self, delta, mode):
        if self.kinematic:
            return
        
        from .interface import EnvironmentManager, WallManager
        if mode == 0:
            f = Vector()
            for spring in self.springs:
                f += spring.getForce(self)
            self.accel = f / self.mass + Vector((0, 0, -9.8)) * EnvironmentManager.gravity_scale
        elif mode == 1:
            self.simVel = self.velocity + self.accel * delta
            self.simPos = self.obj.location + self.velocity * delta
            wall_list = WallManager.walls
            for wall in wall_list:
                if wall.checkCollision(self.simPos, self.radius):
                    self.simVel *= -0.5
                    self.simPos = self.obj.location - self.velocity * delta
                    break


    def runge_kutta2(self, delta, mode):
        if self.kinematic:
            return
        from .interface import EnvironmentManager

        if mode == 0:
            f = Vector()
            for spring in self.springs:
                f += spring.getForce(self)
            self.accel = f / self.mass + Vector((0, 0, -9.8)) * EnvironmentManager.gravity_scale
        elif mode == 1:
            self.simVel = self.velocity + self.accel * delta * 0.5
            self.simPos = self.obj.location + self.velocity * delta * 0.5
        elif mode == 2:
            f = Vector()
            for spring in self.springs:
                f += spring.getForce(self)
            self.accel = f / self.mass + Vector((0, 0, -9.8)) * EnvironmentManager.gravity_scale
        elif mode == 3:
            self.simVel = self.velocity + self.accel * delta
            self.simPos = self.obj.location + self.simVel * delta

    def runge_kutta4(self, delta, mode):
        if self.kinematic:
            return

        from .interface import EnvironmentManager

        k1 = self.velocity
        if mode == 0:
            f = Vector()
            for spring in self.springs:
                f += spring.getForce(self)
            self.accel = f / self.mass + Vector((0, 0, -9.8)) * EnvironmentManager.gravity_scale
        elif mode == 1:
            self.simVel = self.velocity + self.accel * delta * 0.5
            self.simPos = self.obj.location + self.velocity * delta * 0.5
        elif mode == 2:
            f = Vector()
            for spring in self.springs:
                f += spring.getForce(self)
            self.accel = f / self.mass + Vector((0, 0, -9.8)) * EnvironmentManager.gravity_scale
        elif mode == 3:
            self.k2 = k1 + self.accel * delta * 0.5
            self.simVel = self.k2
            self.simPos = self.obj.location + self.simVel * delta * 0.5
        elif mode == 4:
            f = Vector()
            for spring in self.springs:
                f += spring.getForce(self)
            self.accel = f / self.mass + Vector((0, 0, -9.8)) * EnvironmentManager.gravity_scale
        elif mode == 5:
            self.k3 = k1 + self.accel * delta * 0.5
            self.simVel = self.k3
            self.simPos = self.obj.location + self.simVel * delta * 0.5
        elif mode == 6:
            f = Vector()
            for spring in self.springs:
                f += spring.getForce(self)
            self.accel = f / self.mass + Vector((0, 0, -9.8)) * EnvironmentManager.gravity_scale
        elif mode == 7:
            k4 = k1 + self.accel * delta
            self.simVel = (k1 + 2 * self.k2 + 2 * self.k3 + k4) / 6
            self.simPos = self.obj.location + self.simVel * delta

    def verlet(self, delta, mode):
        if self.kinematic:
            return
        from .interface import EnvironmentManager

        if mode == 0:
            f = Vector()
            for spring in self.springs:
                f += spring.getForce(self)
            self.accel = f / self.mass + Vector((0, 0, -9.8)) * EnvironmentManager.gravity_scale
        elif mode == 1:
            self.simVel = self.velocity + self.accel * delta
            self.simPos = self.obj.location + self.velocity * delta
        elif mode == 2:
            f = Vector()
            for spring in self.springs:
                f += spring.getForce(self)
            self.next_accel = f / self.mass + Vector((0, 0, -9.8)) * EnvironmentManager.gravity_scale
            self.accel += self.next_accel
        elif mode == 3:
            self.simVel = self.velocity + self.accel / 2.0 * delta
            self.simPos = self.obj.location + self.simVel * delta

    def leapfrog(self, delta, mode):
        if self.kinematic:
            return
        from .interface import EnvironmentManager
        if mode == 0:
            f = Vector()
            for spring in self.springs:
                f += spring.getForce(self)
            self.accel = f / self.mass + Vector((0, 0, -9.8)) * EnvironmentManager.gravity_scale
        elif mode == 1:
            self.simVel = self.velocity + self.accel * delta
            self.simPos = self.obj.location + self.velocity * delta
        elif mode == 2:
            f = Vector()
            for spring in self.springs:
                f += spring.getForce(self)
            self.next_accel = f / self.mass + Vector((0, 0, -9.8)) * EnvironmentManager.gravity_scale
        elif mode == 3:
            self.simVel = self.velocity + (self.accel + self.next_accel) / 2.0 * delta
            self.simPos = self.obj.location + self.simVel * delta + self.accel * delta * delta / 2

    def symplectic(self, delta, mode):
        if self.kinematic:
            return
        from .interface import EnvironmentManager

        if mode == 0:
            f = Vector()
            for spring in self.springs:
                f += spring.getForce(self)
            self.accel = f / self.mass + Vector((0, 0, -9.8)) * EnvironmentManager.gravity_scale
        elif mode == 1:
            self.simVel = self.velocity + self.accel * delta
            self.simPos = self.obj.location + self.simVel * delta 


    def update(self):
        if not self.kinematic:
            self.velocity = self.simVel
            self.obj.location = self.simPos