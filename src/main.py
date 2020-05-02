##
# Student: Jael Dubey & Robel Teklehaimanot
# Date   : 11.04.2020
# Title  : Lab 2 - Simple Cube
# File   : SimpleCube.py
##

import vtk

NB_POINTS = 3001 * 3001


def read_altitude_file(altitudes):
    f = open("../altitudes.txt", "r")
    lines = f.readlines()

    # Strips the newline character
    for line in lines:
        if len(line) > 20: # skip first line
            altitudes.append(line.strip().split())


def create_geometry(x, altitudes):
    lat = (2.5 / 2) * (111 * 1000) * (-1)
    long = lat
    incr = (2.5 * 111 * 1000) / 3001

    for i in range(3001):
        for j in range(3001):
            x.append((lat, long, float(altitudes[i][j])))
            lat += incr
        long += incr


def create_topology(pts):
    for i in range(NB_POINTS):
        pts.append((i, i + 1, i + 3001, i + 3002))


if __name__ == '__main__':
    altitudes = []
    x = []
    pts = []

    read_altitude_file(altitudes)
    create_geometry(x, altitudes)
    create_topology(pts)

    # Create the VTK datasets
    geometry = vtk.vtkPoints()
    topology = vtk.vtkCellArray()
    scalars = vtk.vtkFloatArray()
    map_topo = vtk.vtkPolyData()

    for i in range(NB_POINTS):
        geometry.InsertPoint(i, x[i])
    for i in range(len(pts)):
        topology.InsertNextCell(len(pts[i]), pts[i])
    for i in range(NB_POINTS):
        scalars.InsertTuple1(i, i)

    map_topo.SetPoints(geometry)

    map_topo.GetPointData().SetScalars(scalars)

    # Map the map
    mapMapper = vtk.vtkPolyDataMapper()
    mapMapper.SetScalarRange(0, 7)
    mapMapper.SetInputConnection(map_topo.GetOutputPort())

    # Create actor
    mapActor = vtk.vtkActor()
    mapActor.SetMapper(mapMapper)

    # Create the Renderer and assign actors to it. A renderer is like a
    # viewport. It is part or all of a window on the screen and it is responsible
    # for drawing the actors it has.  We also set the background color here.
    #
    ren1 = vtk.vtkRenderer()
    ren1.AddActor(mapActor)
    ren1.SetBackground(0.1, 0.1, 0.1) #gris sidéral

    #
    # Finally we create the render window which will show up on the screen
    # We put our renderer into the render window using AddRenderer. We also
    # set the size to be 300 pixels by 300.
    #
    renWin = vtk.vtkRenderWindow()
    renWin.AddRenderer(ren1)
    renWin.SetSize(400, 400)

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