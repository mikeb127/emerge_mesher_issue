import emerge as em
import numpy as np

mm = 0.001              # meters per millimeter
model = em.Simulation('PlaneWave', loglevel='DEBUG')

hght = 45 * mm
wdth = 45 * mm
dpt = 130 * mm

air = em.geo.Box(dpt, hght, wdth,  position=(0, -hght/2, -wdth/2)).background()

model.commit_geometry()
model.settings.check_ram = False

model.mw.set_frequency(27e9)

model.generate_mesh()
scat = model.mw.bc.ScatteredField(air.boundary())

# +Y Polarization
scat.set_excitations(polarizations=[0,0,0])

model.view(plot_mesh=True, volume_mesh=False)
model.view(bc=True)

data = model.mw.run_scattered()

model.display.add_object(air)
model.display.animate().add_field(data.field[0].cutplane(1*mm, z=0).scalar('Ez','complex'), symmetrize=True)
model.display.show()