namespace MptHub.Domain;

public class DiffusivityConfiguration
{
    public double ImmobileMin { get; set; } = 0.000;
    public double ImmobileMax { get; set; } = 0.199;
    public double SubDiffusiveMin { get; set; } = 0.200;
    public double SubDiffusiveMax { get; set; } = 0.899;
    public double DiffusiveMin { get; set; } = 0.900;
    public double DiffusiveMax { get; set; } = 1.199;
    public double ActiveMin { get; set; } = 1.200;
}