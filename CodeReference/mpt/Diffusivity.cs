namespace DefaultNamespace;

public class Diffusivity
{
    public decimal ImmobileMin { get; set; } = 0.000;
    public decimal ImmobileMax { get; set; } = 0.199;
    public decimal SubDiffusiveMin { get; set; } = 0.200;
    public decimal SubDiffusiveMax { get; set; } = 0.899;
    public decimal DiffusiveMin { get; set; } = 0.900;
    public decimal DiffusiveMax { get; set; } = 1.199;
    public decimal ActiveMin { get; set; } = 1.200;
}