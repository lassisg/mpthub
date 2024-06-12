namespace MptHub.Domain;

public class AnalysisConfiguration
{
    public double ParticleSize { get; set; } = 200.00;
    public int MinimumFrames { get; set; } = 590;
    public double FPS { get; set; } = 30.00;
    public double DeltaT { get; set; } = 33.00;
    public int TotalFrames { get; set; } = 606;
    public int Width { get; set; } = 512;
    public double WidthSI { get; set; } = 160.00;
    public double Time { get; set; } = 10.00;
    public double TemperatureInCelsius { get; set; } = 37.00;
}