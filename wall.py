from mathutils import Vector, Euler, Matrix
import math


def clamp(diff, minv, maxv):
    newx = max(minv.x, min(maxv.x, diff.x))
    newy = max(minv.y, min(maxv.y, diff.y))
    newz = max(minv.z, min(maxv.z, diff.z))
    return Vector((newx, newy, newz))

class Wall():
    def __init__(self, obj, length, width, height):
        self.length = length
        self.width = width
        self.height = height
        self.center = obj.location

    def checkCollision(self, center, radius):
        aabb_half = Vector((self.length, self.width, self.height))
        diff = center - self.center
        clamped = clamp(diff, -aabb_half, aabb_half)
        closet = self.center + clamped
        diff = closet - center
        return diff.length < radius






        