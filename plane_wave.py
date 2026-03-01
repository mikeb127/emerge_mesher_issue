import emerge as em
import numpy as np

mm = 0.001              # meters per millimeter
model = em.Simulation('PlaneWave')

hght = 70 * mm
wdth = 70 * mm
dpt = 125 * mm

outer_box = em.geo.Box(hght*1.25, wdth*1.25, dpt*1.15, position=(-hght/2 * 1.25, -wdth/2 * 1.25, 0)).background()
metal_box= em.geo.Box(25*mm, 25*mm, 25*mm, position=(-12.5*mm, -12.5*mm, 100.0*mm))
air_tool_box = em.geo.Box(23*mm, 23*mm, 23*mm, position=(-11.5*mm, -11.5*mm, 99*mm))
cut_box = em.geo.subtract(metal_box, air_tool_box)
air = em.geo.Box(hght, wdth, dpt,  position=(-hght/2, -wdth/2, 0)).background()

#ITO_sheet = em.geo.XYPlate(25*mm, 25*mm,
#                           position=(-12.5*mm, -12.5*mm, 100*mm))
ITO_sheet = em.geo.Box(23*mm, 23*mm, .0002*mm,position=(-11.5*mm, -11.5*mm, 100.02*mm))
#ITO_sheet = em.geo.Box(25*mm, 25*mm, 1*mm,position=(-12.5*mm, -12.5*mm, 99*mm))
#ITO_sheet.max_meshsize = .1

#ITO_sheet2 = em.geo.XYPlate(23*mm, 23*mm,
#                           position=(-11.5*mm, -11.5*mm, 101.5*mm))
model.commit_geometry()

#model.view(use_gmsh=True)

# create ITO - I'm not sure whether I need to set both the impedance and the material here - EDIT - looks like I do
ITO = em.Material(3, 1, cond=1000000)
ITO_sheet.set_material(ITO)
#ITO_sheet2.set_material(ITO)
Titanium = em.Material(1,1,cond=1820000)
#sur = model.mw.bc.SurfaceImpedance(ITO_sheet, material=ITO, surface_conductance=1000000, thickness=2e-7)
#sur2 = model.mw.bc.SurfaceImpedance(ITO_sheet2, material=ITO, surface_conductance=1000000, thickness=2e-7)
cut_box.set_material(Titanium)

model.mw.set_frequency(27e9)
#model.mw.set_resolution(.05)
# Then we can generate the mesh
model.view(use_gmsh=True)

model.generate_mesh()

# Dodgy hack to approximate plane wave. Won't be perfect but probably 'good enough' as I am only testing
# shielding and not RCS or anything. Make it wide enough should be ok.
def Ey_field(k0, x, y, z):

    return 1.0 * np.exp(1j*k0*z)


boundary_selection = outer_box.boundary()
abc = model.mw.bc.AbsorbingBoundary(boundary_selection)
p1 = model.mw.bc.UserDefinedPort(air.bottom, 1, Ey=Ey_field)

model.view(plot_mesh=True, volume_mesh=False)
model.view(bc=True)
data = model.mw.run_sweep()

model.display.add_object(air)
# Interpolated points inside the box
a = data.field[0].grid().E[:, 8:11, 8:11, 22:24]
# E-field magnitude
a_reduce = np.sqrt(np.power(np.real(a[0, :, :, :]), 2) + np.power(np.real(a[1, :, :, :]), 2) +
                   np.power(np.real(a[2, :, :, :]), 2))
max_val = np.max(a_reduce)
max_indx = np.argmax(a_reduce)
print(max_indx) # in case needed for checks
print(max_val) # This should be maximum value of interpolated E-Field values - 20 * log10(1/max_val) is our SE
model.display.animate().add_field(data.field[0].cutplane(1*mm, y=0).scalar('Ey', 'complex'), symmetrize=True)
# With these two plots we can show the field mode that we created.
model.display.add_portmode(p1, k0=data.field[0].k0)
# Finally we display our animation.
model.display.show()
