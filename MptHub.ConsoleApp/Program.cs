using MptHub.Domain;

var frame1 = new Frame() { Coordinates = 
    {
        new Coordinate { X = 0.001, Y = 0.002 },
        new Coordinate { X = 0.001, Y = 0.002 }
    } };

var frame2 = new Frame() { 
    Coordinates = 
    {
        new Coordinate { X = 0.002, Y = 0.004 },
        new Coordinate { X = 0.002, Y = 0.005 }
    } };


var traj = new Trajectory()
{
    Frames = { frame1, frame2 }
};

Console.WriteLine(traj);
Console.ReadLine();