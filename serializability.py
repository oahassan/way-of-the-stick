import stick
import animation
from movesetdata import Moveset
from wotsprot.rencode import serializable
from record import Recording
from simulation import SimulationRenderingInfo, PlayerRenderingInfo, AttackResultRenderingInfo
from physics import Model

serializable.register(SimulationRenderingInfo)
serializable.register(PlayerRenderingInfo)
serializable.register(AttackResultRenderingInfo)
serializable.register(Model)
serializable.register(Recording)
serializable.register(stick.Point)
serializable.register(stick.Line)
serializable.register(stick.Circle)
serializable.register(animation.Animation)
serializable.register(animation.Frame)
serializable.register(Moveset)
