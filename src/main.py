##
# Student: Jael Dubey & Robel Teklehaimanot
# Date   : 10.05.2020
# Title  : Lab 3 - Color Mapping
# File   : main.py
##
from math import cos, radians, sin

import vtk

LONG_LARG = 3001
NB_POINTS = LONG_LARG * LONG_LARG
EARTH_RADIUS = 6371009
DIST_BETWEEN_POINTS = 2.5 / LONG_LARG


def read_altitude_file(altitudes):
    f = open("../altitudes.txt", "r")
    lines = f.readlines()

    # Strips the newline character
    for line in lines:
        if len(line) > 20:  # skip first line
            altitudes.append(line.strip().split())
    f.close()


def create_geometry(x_pts, altitudes):
    for i in range(LONG_LARG):
        for j in range(LONG_LARG):
            alt = float(altitudes[i][j])

            # https://fr.wikipedia.org/wiki/Coordonn%C3%A9es_sph%C3%A9riques#Conventions
            x = (EARTH_RADIUS + alt) * cos(radians(i * DIST_BETWEEN_POINTS)) * cos(radians(j * DIST_BETWEEN_POINTS))
            y = (EARTH_RADIUS + alt) * cos(radians(i * DIST_BETWEEN_POINTS)) * sin(radians(j * DIST_BETWEEN_POINTS))
            z = (EARTH_RADIUS + alt) * sin(radians(i * DIST_BETWEEN_POINTS))

            x_pts.append((x, y, -z))


def create_topology(pts):
    for i in range(NB_POINTS):
        pts.append((i, i + 1, i - (LONG_LARG - 1), i - LONG_LARG))


def is_lake(altitudes, x, y):
    current_alt = altitudes[x][y]

    if x == 0:  # Côté gauche
        if y == 0:  # Coin supérieur gauche
            return altitudes[x + 1][y] == current_alt and altitudes[x][y + 1] == current_alt
        if y == LONG_LARG - 1:  # Coin inférieur gauche
            return altitudes[x + 1][y] == current_alt and altitudes[x][y - 1] == current_alt
        return altitudes[x + 1][y] == current_alt and altitudes[x][y + 1] == current_alt and altitudes[x][
            y - 1] == current_alt

    if x == LONG_LARG - 1:  # Côté droit
        if y == 0:  # Coin supérieur droit
            return altitudes[x - 1][y] == current_alt and altitudes[x][y + 1] == current_alt
        if y == LONG_LARG - 1:  # Coin inférieur droit
            return altitudes[x - 1][y] == current_alt and altitudes[x][y - 1] == current_alt
        return altitudes[x][y - 1] == current_alt and altitudes[x][y + 1] == current_alt and altitudes[x - 1][
            y] == current_alt

    if y == 0:  # Côté supérieur
        return altitudes[x - 1][y] == current_alt and altitudes[x + 1][y] == current_alt and altitudes[x][
            y + 1] == current_alt

    if y == LONG_LARG - 1:  # Côté inférieur
        return altitudes[x - 1][y] == current_alt and altitudes[x + 1][y] == current_alt and altitudes[x][
            y - 1] == current_alt

    # Cas général
    return altitudes[x - 1][y] == current_alt and altitudes[x + 1][y] == current_alt and altitudes[x][
        y - 1] == current_alt and altitudes[x][y + 1] == current_alt and altitudes[x + 1][y + 1] == current_alt and \
           altitudes[x + 1][y - 1] == current_alt and altitudes[x - 1][y + 1] == current_alt and altitudes[x - 1][
               y - 1] == current_alt


if __name__ == '__main__':
    altitudes = []
    x = []
    pts = []

    read_altitude_file(altitudes)
    create_geometry(x, altitudes)
    create_topology(pts)

    # Create the VTK datasets - We use a vtkPolyData mainly because we have already use it in the last lab (cube). We
    # choose to create square surface, because it was more simple to map with the altitudes files, which is a
    # 3001x3001 matrix. And finally we heard in your presentation video that the Polydata can be used for this kind of
    # project.
    geometry = vtk.vtkPoints()
    topology = vtk.vtkCellArray()
    scalars = vtk.vtkFloatArray()
    map_topo = vtk.vtkPolyData()

    for i in range(NB_POINTS):
        geometry.InsertPoint(i, x[i])
        # To create the map with the sea level at 370 meters, add the code in comment below
        if is_lake(altitudes, int(i / LONG_LARG), i % LONG_LARG):  # or float(altitudes[int(i / LONG_LARG)][i % LONG_LARG]) <= 370:
            scalars.InsertTuple1(i, -1)
        else:
            scalars.InsertTuple1(i, float(altitudes[int(i / LONG_LARG)][i % LONG_LARG]))

    for i in range(1, LONG_LARG):
        for j in range(LONG_LARG - 1):
            topology.InsertNextCell(len(pts[i]), pts[(i) * LONG_LARG + j])

    map_topo.SetPoints(geometry)
    map_topo.SetPolys(topology)
    map_topo.GetPointData().SetScalars(scalars)

    # Map the map
    mapMapper = vtk.vtkPolyDataMapper()
    mapMapper.SetInputData(map_topo)

    # Create the Lookup Table (inspired by https://danstoj.pythonanywhere.com/article/vtk-1)

    lookup_table = vtk.vtkLookupTable()
    lookup_table.SetHueRange(0.0, 1.0)
    lookup_table.SetSaturationRange(0.0, 0.5)
    lookup_table.SetValueRange(0.25, 1.0)
    lookup_table.SetTableRange(0.0, 3000.0)
    N = 256
    lookup_table.SetNumberOfColors(N)

    ctransfer = vtk.vtkColorTransferFunction()
    ctransfer.AddRGBPoint(0.0, 0.1, 0.58, 0.0)
    ctransfer.AddRGBPoint(3000.0, 1.0, 1.0, 0.75)

    for i in range(N):
        new_colour = ctransfer.GetColor((i * ((5000) / N)))
        lookup_table.SetTableValue(i, *new_colour)

    lookup_table.SetBelowRangeColor(0.0, 0.0, 0.60, 1)
    lookup_table.UseBelowRangeColorOn()

    lookup_table.Build()
    mapMapper.SetLookupTable(lookup_table)
    mapMapper.UseLookupTableScalarRangeOn()

    # Create actor
    mapActor = vtk.vtkActor()
    mapActor.SetMapper(mapMapper)

    # Create the Renderer and assign actors to it. A renderer is like a
    # viewport. It is part or all of a window on the screen and it is responsible
    # for drawing the actors it has.  We also set the background color here.
    #
    ren1 = vtk.vtkRenderer()
    ren1.AddActor(mapActor)
    ren1.SetBackground(0.1, 0.1, 0.1)  # gris sidéral

    #
    # Finally we create the render window which will show up on the screen
    # We put our renderer into the render window using AddRenderer. We also
    # set the size to be 300 pixels by 300.
    #
    renWin = vtk.vtkRenderWindow()
    renWin.AddRenderer(ren1)
    renWin.SetSize(600, 600)

    #
    # The vtkRenderWindowInteractor class watches for events (e.g., keypress,
    # mouse) in the vtkRenderWindow. These events are translated into
    # event invocations that VTK understands (see VTK/Common/vtkCommand.h
    # for all events that VTK processes). Then observers of these VTK
    # events can process them as appropriate.
    iren = vtk.vtkRenderWindowInteractor()
    iren.SetRenderWindow(renWin)

    #
    # By default the vtkRenderWindowInteractor instantiates an instance
    # of vtkInteractorStyle. vtkInteractorStyle translates a set of events
    # it observes into operations on the camera, actors, and/or properties
    # in the vtkRenderWindow associated with the vtkRenderWinodwInteractor.
    # Here we specify a particular interactor style.
    style = vtk.vtkInteractorStyleTrackballCamera()
    iren.SetInteractorStyle(style)

    #
    # Unlike the previous scripts where we performed some operations and then
    # exited, here we leave an event loop running. The user can use the mouse
    # and keyboard to perform the operations on the scene according to the
    # current interaction style.
    #

    #
    # Initialize and start the event loop. Once the render window appears, mouse
    # in the window to move the camera. The Start() method executes an event
    # loop which listens to user mouse and keyboard events. Note that keypress-e
    # exits the event loop. (Look in vtkInteractorStyle.h for a summary of events, or
    # the appropriate Doxygen documentation.)
    #
    iren.Initialize()
    iren.Start()
