namespace MptHub.Domain;

public class GeneralConfiguration
{
    private static readonly string _homePath = Environment.GetFolderPath(Environment.SpecialFolder.UserProfile);
    private static string _basePath { get; set; } = Path.Join(_homePath, ".mpt");
    private static string _dbName { get; set; } = "config.db";
    
    public string ApplicationPath { get; set; } = Environment.CurrentDirectory;
    public string IconPath { get; set; } = Path.Join(Environment.CurrentDirectory, "mpt", "assets");
    public string DbPath { get; set; } = Path.Join(_basePath, _dbName);
    public string ExportPath { get; set; } = Path.Join(_basePath, "export");
    public string OpenFolder { get; set; } = _homePath;
    public string SaveFolder { get; set; } = _homePath;
}